from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
import hashlib
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = "admin"
    USER = "user"

@dataclass
class User:
    """用户数据类"""
    username: str
    password_hash: str
    role: UserRole
    email: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """将用户对象转换为字典"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'email': self.email,
            'phone': self.phone
        }

class UserManager:
    """用户管理器类"""
    
    def __init__(self, data_file: str = "data/users.json"):
        """
        初始化用户管理器
        
        Args:
            data_file: 用户数据文件路径
        """
        self.data_file = data_file
        self.users: List[User] = []
        self._load_users()

    def _load_users(self) -> None:
        """从文件加载用户数据"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.users = [
                        User(
                            username=user['username'],
                            password_hash=user['password_hash'],
                            role=UserRole(user['role']),
                            email=user.get('email'),
                            phone=user.get('phone')
                        )
                        for user in json.load(f)
                    ]
                logger.info(f'成功加载 {len(self.users)} 个用户')
        except Exception as e:
            logger.error(f'加载用户数据失败: {str(e)}')
            self.users = []

    def _save_users(self) -> None:
        """保存用户数据到文件"""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [user.to_dict() for user in self.users],
                    f,
                    ensure_ascii=False,
                    indent=2
                )
            logger.info('用户数据保存成功')
        except Exception as e:
            logger.error(f'保存用户数据失败: {str(e)}')

    def _find_user(self, username: str) -> Optional[User]:
        """
        查找用户
        
        Args:
            username: 用户名
            
        Returns:
            用户对象，如果未找到返回None
        """
        return next((user for user in self.users if user.username == username), None)

    @staticmethod
    def hash_password(password: str) -> str:
        """
        对密码进行哈希处理
        
        Args:
            password: 原始密码
            
        Returns:
            哈希后的密码
        """
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str, role: UserRole = UserRole.USER,
                email: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """
        注册新用户
        
        Args:
            username: 用户名
            password: 密码
            role: 用户角色
            email: 邮箱
            phone: 手机号
            
        Returns:
            是否注册成功
        """
        if self._find_user(username):
            logger.warning(f'注册失败: 用户名 {username} 已存在')
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
        logger.info(f'成功注册用户: {username}')
        return True

    def login(self, username: str, password: str) -> Optional[User]:
        """
        用户登录
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            用户对象，如果登录失败返回None
        """
        user = self._find_user(username)
        if user and user.password_hash == self.hash_password(password):
            logger.info(f'用户 {username} 登录成功')
            return user
        logger.warning(f'登录失败: 用户名或密码错误')
        return None

    def update_user_info(self, username: str, email: Optional[str] = None,
                        phone: Optional[str] = None) -> bool:
        """
        更新用户信息
        
        Args:
            username: 用户名
            email: 新邮箱
            phone: 新手机号
            
        Returns:
            是否更新成功
        """
        user = self._find_user(username)
        if user:
            user.email = email
            user.phone = phone
            self._save_users()
            logger.info(f'成功更新用户 {username} 的信息')
            return True
        logger.warning(f'更新用户信息失败: 用户 {username} 不存在')
        return False

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        修改用户密码
        
        Args:
            username: 用户名
            old_password: 旧密码
            new_password: 新密码
            
        Returns:
            是否修改成功
        """
        user = self._find_user(username)
        if user and user.password_hash == self.hash_password(old_password):
            user.password_hash = self.hash_password(new_password)
            self._save_users()
            logger.info(f'用户 {username} 成功修改密码')
            return True
        logger.warning(f'修改密码失败: 用户名或旧密码错误')
        return False 