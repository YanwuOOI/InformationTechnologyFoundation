from dataclasses import dataclass
from typing import List, Optional
import json
import os

@dataclass
class Book:
    id: str
    title: str
    author: str
    category: str
    quantity: int
    description: Optional[str] = None

class BookManager:
    def __init__(self, data_file: str = "data/books.json"):
        self.data_file = data_file
        self.books: List[Book] = []
        self._load_books()

    def _load_books(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.books = [Book(**book) for book in data]

    def _save_books(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump([vars(book) for book in self.books], f, ensure_ascii=False, indent=2)

    def add_book(self, book: Book) -> bool:
        if any(b.id == book.id for b in self.books):
            return False
        self.books.append(book)
        self._save_books()
        return True

    def remove_book(self, book_id: str) -> bool:
        initial_length = len(self.books)
        self.books = [b for b in self.books if b.id != book_id]
        if len(self.books) != initial_length:
            self._save_books()
            return True
        return False

    def update_book(self, book: Book) -> bool:
        for i, b in enumerate(self.books):
            if b.id == book.id:
                self.books[i] = book
                self._save_books()
                return True
        return False

    def get_book(self, book_id: str) -> Optional[Book]:
        for book in self.books:
            if book.id == book_id:
                return book
        return None

    def search_books(self, keyword: str) -> List[Book]:
        keyword = keyword.lower()
        return [
            book for book in self.books
            if keyword in book.title.lower() or
               keyword in book.author.lower() or
               keyword in book.category.lower()
        ]

    def get_all_books(self) -> List[Book]:
        return self.books.copy()

    def export_to_csv(self, filename: str):
        import csv
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['ID', '书名', '作者', '分类', '数量', '描述'])
            for book in self.books:
                writer.writerow([
                    book.id,
                    book.title,
                    book.author,
                    book.category,
                    book.quantity,
                    book.description or ''
                ]) 