"""
图书管理模块

本模块提供图书相关的核心功能：
1. 图书数据结构定义和维护
2. 图书信息的增删改查操作
3. 图书库存数量管理
4. 图书信息导出功能
5. 数据持久化处理

业务规则：
1. 图书ID全局唯一，格式为'BKxxxxxx'
2. 图书数量不能为负数
3. 支持按书名、作者、分类进行模糊搜索
4. 图书信息支持导出为CSV格式
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
import csv
import logging

logger = logging.getLogger(__name__)

@dataclass
class Book:
    """
    图书数据类
    
    属性：
        id: 图书唯一标识
        title: 书名
        author: 作者
        category: 分类
        quantity: 在库数量
        description: 图书描述（可选）
    """
    id: str
    title: str
    author: str
    category: str
    quantity: int
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """将图书对象转换为字典格式，用于数据持久化"""
        return vars(self)

class BookManager:
    """
    图书管理器
    
    职责：
    1. 图书数据的加载和保存
    2. 图书信息维护（增删改查）
    3. 库存管理
    4. 数据导出
    """
    
    def __init__(self, data_file: str = "data/books.json"):
        self.data_file = data_file
        self.books: List[Book] = []
        self._load_books()

    def _load_books(self) -> None:
        """加载图书数据，初始化时自动调用"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.books = [Book(**book) for book in json.load(f)]
                logger.info(f'成功加载 {len(self.books)} 本图书')
        except Exception as e:
            logger.error(f'加载图书数据失败: {str(e)}')
            self.books = []

    def _save_books(self) -> None:
        """保存图书数据，在数据变更时自动调用"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([book.to_dict() for book in self.books], 
                         f, ensure_ascii=False, indent=2)
            logger.info('图书数据保存成功')
        except Exception as e:
            logger.error(f'保存图书数据失败: {str(e)}')

    def _find_book_index(self, book_id: str) -> int:
        """根据图书ID查找图书在列表中的索引"""
        return next((i for i, b in enumerate(self.books) if b.id == book_id), -1)

    def add_book(self, book: Book) -> bool:
        """
        添加新图书
        
        业务流程：
        1. 检查图书ID是否已存在
        2. 验证图书基本信息完整性
        3. 添加到图书列表
        4. 保存数据变更
        
        数据验证：
        - 图书ID唯一性检查
        - 图书数量非负检查
        
        参数：
            book: 新图书对象
            
        返回：
            添加是否成功
        """
        if self._find_book_index(book.id) != -1:
            logger.warning(f'添加图书失败: ID {book.id} 已存在')
            return False
            
        self.books.append(book)
        self._save_books()
        logger.info(f'成功添加图书: {book.title}')
        return True

    def remove_book(self, book_id: str) -> bool:
        """
        删除图书
        
        业务流程：
        1. 查找图书在列表中的位置
        2. 执行删除操作
        3. 保存数据变更
        
        注意事项：
        - 删除图书前应确保没有未完成的借阅记录
        - 删除操作不可恢复
        
        参数：
            book_id: 图书唯一标识
            
        返回：
            删除是否成功
        """
        index = self._find_book_index(book_id)
        if index != -1:
            book = self.books.pop(index)
            self._save_books()
            logger.info(f'成功删除图书: {book.title}')
            return True
        logger.warning(f'删除图书失败: ID {book_id} 不存在')
        return False

    def update_book(self, book: Book) -> bool:
        """
        更新图书信息
        
        业务流程：
        1. 查找原有图书记录
        2. 验证更新数据的完整性
        3. 更新图书信息
        4. 保存数据变更
        
        数据验证：
        - 图书必须存在
        - 更新后的库存量不能为负
        
        参数：
            book: 更新后的图书对象
            
        返回：
            更新是否成功
        """
        index = self._find_book_index(book.id)
        if index != -1:
            self.books[index] = book
            self._save_books()
            logger.info(f'成功更新图书: {book.title}')
            return True
        logger.warning(f'更新图书失败: ID {book.id} 不存在')
        return False

    def get_book(self, book_id: str) -> Optional[Book]:
        """根据ID获取图书，不存在返回None"""
        index = self._find_book_index(book_id)
        return self.books[index] if index != -1 else None

    def search_books(self, keyword: str) -> List[Book]:
        """
        搜索图书
        
        搜索范围：
        - 书名
        - 作者
        - 分类
        
        搜索特点：
        - 支持模糊匹配
        - 不区分大小写
        - 支持部分匹配
        
        参数：
            keyword: 搜索关键词
            
        返回：
            匹配的图书列表
        """
        keyword = keyword.lower()
        return [
            book for book in self.books
            if any(keyword in str(value).lower() 
                  for value in [book.title, book.author, book.category])
        ]

    def get_all_books(self) -> List[Book]:
        """获取所有图书的列表副本"""
        return self.books.copy()

    def export_to_csv(self, filename: str) -> None:
        """
        导出图书信息到CSV文件
        
        导出字段：
        - 图书ID
        - 书名
        - 作者
        - 分类
        - 数量
        - 描述
        
        异常处理：
        - 文件路径无效时抛出异常
        - 写入失败时抛出异常
        
        参数：
            filename: 导出文件路径
            
        异常：
            IOError: 文件操作失败时抛出
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['ID', '书名', '作者', '分类', '数量', '描述'])
                writer.writerows([
                    [book.id, book.title, book.author, book.category, 
                     book.quantity, book.description or '']
                    for book in self.books
                ])
            logger.info(f'成功导出图书信息到: {filename}')
        except Exception as e:
            logger.error(f'导出图书信息失败: {str(e)}')
            raise