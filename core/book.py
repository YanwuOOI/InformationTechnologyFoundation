from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
import csv
import logging

logger = logging.getLogger(__name__)

@dataclass
class Book:
    """图书数据类"""
    id: str
    title: str
    author: str
    category: str
    quantity: int
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """将图书对象转换为字典"""
        return vars(self)

class BookManager:
    """图书管理器类"""
    
    def __init__(self, data_file: str = "data/books.json"):
        """
        初始化图书管理器
        
        Args:
            data_file: 图书数据文件路径
        """
        self.data_file = data_file
        self.books: List[Book] = []
        self._load_books()

    def _load_books(self) -> None:
        """从文件加载图书数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.books = [Book(**book) for book in json.load(f)]
                logger.info(f'成功加载 {len(self.books)} 本图书')
        except Exception as e:
            logger.error(f'加载图书数据失败: {str(e)}')
            self.books = []

    def _save_books(self) -> None:
        """保存图书数据到文件"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump([book.to_dict() for book in self.books], 
                         f, ensure_ascii=False, indent=2)
            logger.info('图书数据保存成功')
        except Exception as e:
            logger.error(f'保存图书数据失败: {str(e)}')

    def _find_book_index(self, book_id: str) -> int:
        """
        查找图书索引
        
        Args:
            book_id: 图书ID
            
        Returns:
            图书在列表中的索引，如果未找到返回-1
        """
        return next((i for i, b in enumerate(self.books) if b.id == book_id), -1)

    def add_book(self, book: Book) -> bool:
        """
        添加新图书
        
        Args:
            book: 要添加的图书对象
            
        Returns:
            是否添加成功
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
        
        Args:
            book_id: 要删除的图书ID
            
        Returns:
            是否删除成功
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
        
        Args:
            book: 更新后的图书对象
            
        Returns:
            是否更新成功
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
        """
        获取图书信息
        
        Args:
            book_id: 图书ID
            
        Returns:
            图书对象，如果未找到返回None
        """
        index = self._find_book_index(book_id)
        return self.books[index] if index != -1 else None

    def search_books(self, keyword: str) -> List[Book]:
        """
        搜索图书
        
        Args:
            keyword: 搜索关键词
            
        Returns:
            匹配的图书列表
        """
        keyword = keyword.lower()
        return [
            book for book in self.books
            if any(keyword in str(value).lower() 
                  for value in [book.title, book.author, book.category])
        ]

    def get_all_books(self) -> List[Book]:
        """
        获取所有图书
        
        Returns:
            图书列表的副本
        """
        return self.books.copy()

    def export_to_csv(self, filename: str) -> None:
        """
        导出图书信息到CSV文件
        
        Args:
            filename: 导出文件路径
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