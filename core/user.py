from dataclasses import dataclass
from typing import List, Optional
import json
import os
import hashlib
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

@dataclass
class User:
    username: str
    password_hash: str
    role: UserRole
    email: Optional[str] = None
    phone: Optional[str] = None

class UserManager:
    def __init__(self, data_file: str = "data/users.json"):
        self.data_file = data_file
        self.users: List[User] = []
        self._load_users()

    def _load_users(self):
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.users = [
                    User(
                        username=user['username'],
                        password_hash=user['password_hash'],
                        role=UserRole(user['role']),
                        email=user.get('email'),
                        phone=user.get('phone')
                    )
                    for user in data
                ]

    def _save_users(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(
                [
                    {
                        'username': user.username,
                        'password_hash': user.password_hash,
                        'role': user.role.value,
                        'email': user.email,
                        'phone': user.phone
                    }
                    for user in self.users
                ],
                f,
                ensure_ascii=False,
                indent=2
            )

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str, role: UserRole = UserRole.USER,
                email: Optional[str] = None, phone: Optional[str] = None) -> bool:
        if any(u.username == username for u in self.users):
            return False
        
        user = User(
            username=username,
            password_hash=self.hash_password(password),
            role=role,
            email=email,
            phone=phone
        )
        self.users.append(user)
        self._save_users()
        return True

    def authenticate(self, username: str, password: str) -> Optional[User]:
        password_hash = self.hash_password(password)
        for user in self.users:
            if user.username == username and user.password_hash == password_hash:
                return user
        return None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        user = self.authenticate(username, old_password)
        if user:
            user.password_hash = self.hash_password(new_password)
            self._save_users()
            return True
        return False

    def get_user(self, username: str) -> Optional[User]:
        for user in self.users:
            if user.username == username:
                return user
        return None

    def update_user_info(self, username: str, email: Optional[str] = None,
                        phone: Optional[str] = None) -> bool:
        user = self.get_user(username)
        if user:
            if email is not None:
                user.email = email
            if phone is not None:
                user.phone = phone
            self._save_users()
            return True
        return False 