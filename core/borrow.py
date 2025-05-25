"""
借阅管理模块

本模块提供图书借阅相关的核心功能：
1. 借阅记录数据结构定义和管理
2. 图书借阅业务流程处理
3. 图书归还业务流程处理
4. 借阅历史记录维护
5. 数据持久化处理

业务规则：
1. 同一本书同时只能被一个用户借阅
2. 借阅时图书必须有可用库存
3. 归还时需要验证借阅记录存在且未归还
4. 每次借阅和归还都会更新图书库存
"""

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
    """
    借阅记录数据类
    
    属性：
        id: 借阅记录唯一标识
        book_id: 相关图书ID
        username: 借阅用户
        borrow_date: 借阅时间
        return_date: 归还时间（未归还为None）
    """
    id: str
    book_id: str
    username: str
    borrow_date: str
    return_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """将借阅记录转换为字典格式，用于数据持久化"""
        return vars(self)

class BorrowManager:
    """
    借阅管理器
    
    职责：
    1. 借阅记录的加载和保存
    2. 处理图书借阅和归还
    3. 管理用户借阅历史
    4. 协调图书库存变化
    """
    
    def __init__(self, data_file: str = "data/records.json", book_manager: Optional[BookManager] = None):
        self.data_file = data_file
        self.records: List[BorrowRecord] = []
        self.book_manager = book_manager
        self._load_records()

    def _load_records(self) -> None:
        """加载借阅记录，初始化时自动调用"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.records = [BorrowRecord(**record) for record in json.load(f)]
                logger.info(f'成功加载 {len(self.records)} 条借阅记录')
        except Exception as e:
            logger.error(f'加载借阅记录失败: {str(e)}')
            self.records = []

    def _save_records(self) -> None:
        """保存借阅记录，在数据变更时自动调用"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([record.to_dict() for record in self.records], 
                         f, ensure_ascii=False, indent=2)
            logger.info('借阅记录保存成功')
        except Exception as e:
            logger.error(f'保存借阅记录失败: {str(e)}')

    def _find_active_borrow(self, book_id: str, username: str) -> Optional[BorrowRecord]:
        """查找用户当前的有效借阅记录"""
        return next(
            (record for record in self.records 
             if record.book_id == book_id 
             and record.username == username 
             and record.return_date is None),
            None
        )

    def borrow_book(self, book_id: str, username: str) -> Optional[BorrowRecord]:
        """
        处理图书借阅请求
        
        业务流程：
        1. 验证图书管理器初始化状态
        2. 检查图书是否存在且有库存
        3. 验证用户是否已借阅此书
        4. 生成借阅记录并分配ID
        5. 更新图书库存数量
        6. 保存借阅记录
        
        异常处理：
        - 图书管理器未初始化时返回None
        - 图书不存在时返回None
        - 库存不足时返回None
        - 重复借阅时返回None
        
        参数：
            book_id: 图书唯一标识
            username: 借阅用户名
            
        返回：
            成功返回借阅记录对象，失败返回None
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
        处理图书归还请求
        
        业务流程：
        1. 验证图书管理器初始化状态
        2. 查找匹配的未归还借阅记录
        3. 验证图书信息
        4. 更新借阅记录归还时间
        5. 增加图书库存数量
        6. 保存数据变更
        
        异常处理：
        - 图书管理器未初始化时返回False
        - 未找到匹配的借阅记录时返回False
        - 图书不存在时返回False
        - 更新图书库存失败时回滚并返回False
        
        事务处理：
        - 如果更新图书库存失败，会回滚借阅记录的修改
        
        参数：
            book_id: 图书唯一标识
            username: 借阅用户名
            
        返回：
            操作是否成功
        """
        if not self.book_manager:
            logger.error('图书管理器未初始化')
            return False

        record = self._find_active_borrow(book_id, username)
        if not record:
            logger.warning(f'归还失败: 用户 {username} 未借阅图书 {book_id}')
            return False

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
        """获取指定用户的所有借阅记录"""
        return [record for record in self.records if record.username == username]

    def get_active_borrows(self, username: str) -> List[BorrowRecord]:
        """获取用户当前正在借阅的图书记录"""
        return [
            record for record in self.records 
            if record.username == username and record.return_date is None
        ]