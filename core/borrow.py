from dataclasses import dataclass
from typing import List, Optional
import json
import os
from datetime import datetime

@dataclass
class BorrowRecord:
    id: str
    book_id: str
    username: str
    borrow_date: str
    return_date: Optional[str] = None

class BorrowManager:
    def __init__(self, data_file: str = "data/records.json"):
        self.data_file = data_file
        self.records: List[BorrowRecord] = []
        self._load_records()

    def _load_records(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.records = [BorrowRecord(**record) for record in data]

    def _save_records(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump([vars(record) for record in self.records], f, ensure_ascii=False, indent=2)

    def borrow_book(self, book_id: str, username: str) -> Optional[BorrowRecord]:
        # 检查是否已经借阅且未归还
        for record in self.records:
            if (record.book_id == book_id and 
                record.username == username and 
                record.return_date is None):
                return None

        record = BorrowRecord(
            id=f"BR{len(self.records) + 1:06d}",
            book_id=book_id,
            username=username,
            borrow_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        self.records.append(record)
        self._save_records()
        return record

    def return_book(self, book_id: str, username: str) -> bool:
        for record in self.records:
            if (record.book_id == book_id and 
                record.username == username and 
                record.return_date is None):
                record.return_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self._save_records()
                return True
        return False

    def get_user_borrow_history(self, username: str) -> List[BorrowRecord]:
        return [
            record for record in self.records
            if record.username == username
        ]

    def get_book_borrow_history(self, book_id: str) -> List[BorrowRecord]:
        return [
            record for record in self.records
            if record.book_id == book_id
        ]

    def get_active_borrows(self, username: str) -> List[BorrowRecord]:
        return [
            record for record in self.records
            if record.username == username and record.return_date is None
        ] 