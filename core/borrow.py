from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
from datetime import datetime
import logging
from core.book import BookManager

logger = logging.getLogger(__name__)

@dataclass
class BorrowRecord:
    """借阅记录数据类"""
    id: str
    book_id: str
    username: str
    borrow_date: str
    return_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """将借阅记录转换为字典"""
        return vars(self)

class BorrowManager:
    """借阅管理器类"""
    
    def __init__(self, data_file: str = "data/records.json", book_manager: Optional[BookManager] = None):
        """
        初始化借阅管理器
        
        Args:
            data_file: 借阅记录数据文件路径
            book_manager: 图书管理器实例
        """
        self.data_file = data_file
        self.records: List[BorrowRecord] = []
        self.book_manager = book_manager
        self._load_records()

    def _load_records(self) -> None:
        """从文件加载借阅记录"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.records = [BorrowRecord(**record) for record in json.load(f)]
                logger.info(f'成功加载 {len(self.records)} 条借阅记录')
        except Exception as e:
            logger.error(f'加载借阅记录失败: {str(e)}')
            self.records = []

    def _save_records(self) -> None:
        """保存借阅记录到文件"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([record.to_dict() for record in self.records], 
                         f, ensure_ascii=False, indent=2)
            logger.info('借阅记录保存成功')
        except Exception as e:
            logger.error(f'保存借阅记录失败: {str(e)}')

    def _find_active_borrow(self, book_id: str, username: str) -> Optional[BorrowRecord]:
        """
        查找活跃的借阅记录
        
        Args:
            book_id: 图书ID
            username: 用户名
            
        Returns:
            借阅记录对象，如果未找到返回None
        """
        return next(
            (record for record in self.records 
             if record.book_id == book_id 
             and record.username == username 
             and record.return_date is None),
            None
        )

    def borrow_book(self, book_id: str, username: str) -> Optional[BorrowRecord]:
        """
        借阅图书
        
        Args:
            book_id: 图书ID
            username: 用户名
            
        Returns:
            借阅记录对象，如果借阅失败返回None
        """
        if not self.book_manager:
            logger.error('图书管理器未初始化')
            return None

        # 检查图书是否存在且可借
        book = self.book_manager.get_book(book_id)
        if not book:
            logger.warning(f'借阅失败: 图书 {book_id} 不存在')
            return None

        if book.quantity <= 0:
            logger.warning(f'借阅失败: 图书 {book.title} 已无库存')
            return None

        if self._find_active_borrow(book_id, username):
            logger.warning(f'借阅失败: 用户 {username} 已借阅图书 {book_id}')
            return None

        # 创建借阅记录
        record = BorrowRecord(
            id=f"BR{len(self.records) + 1:06d}",
            book_id=book_id,
            username=username,
            borrow_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        # 更新图书数量
        book.quantity -= 1
        if not self.book_manager.update_book(book):
            logger.error(f'更新图书数量失败: {book_id}')
            return None

        # 保存借阅记录
        self.records.append(record)
        self._save_records()
        logger.info(f'用户 {username} 成功借阅图书 {book.title}')
        return record

    def return_book(self, book_id: str, username: str) -> bool:
        """
        归还图书
        
        Args:
            book_id: 图书ID
            username: 用户名
            
        Returns:
            是否归还成功
        """
        if not self.book_manager:
            logger.error('图书管理器未初始化')
            return False

        record = self._find_active_borrow(book_id, username)
        if not record:
            logger.warning(f'归还失败: 用户 {username} 未借阅图书 {book_id}')
            return False

        # 更新图书数量
        book = self.book_manager.get_book(book_id)
        if not book:
            logger.error(f'归还失败: 图书 {book_id} 不存在')
            return False

        # 更新借阅记录
        record.return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._save_records()

        # 更新图书数量
        book.quantity += 1
        if not self.book_manager.update_book(book):
            logger.error(f'更新图书数量失败: {book_id}')
            # 如果更新失败，回滚借阅记录
            record.return_date = None
            self._save_records()
            return False

        logger.info(f'用户 {username} 成功归还图书 {book.title}')
        return True

    def get_user_borrow_history(self, username: str) -> List[BorrowRecord]:
        """
        获取用户借阅历史
        
        Args:
            username: 用户名
            
        Returns:
            借阅记录列表
        """
        return [record for record in self.records if record.username == username]

    def get_active_borrows(self, username: str) -> List[BorrowRecord]:
        """
        获取用户当前借阅的图书
        
        Args:
            username: 用户名
            
        Returns:
            未归还的借阅记录列表
        """
        return [
            record for record in self.records 
            if record.username == username and record.return_date is None
        ] 