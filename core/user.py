"""
用户管理模块

本模块提供用户管理相关的功能：
1. 用户数据结构定义和维护
2. 用户身份认证和授权管理
3. 用户注册和登录处理
4. 用户信息更新维护
5. 数据持久化处理

业务规则：
1. 用户名全局唯一
2. 密码经过SHA-256加密存储
3. 支持管理员和普通用户两种角色
4. 普通用户只能修改自己的信息
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
import json
import os
import hashlib
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class UserRole(Enum):
    """用户角色枚举，定义系统支持的用户角色类型"""
    ADMIN = "admin"  # 管理员
    USER = "user"    # 普通用户

@dataclass
class User:
    """
    用户数据类
    
    属性:
        username: 用户名（唯一标识）
        password_hash: 密码哈希值
        role: 用户角色
        email: 电子邮箱（可选）
        phone: 手机号码（可选）
    """
    username: str
    password_hash: str
    role: UserRole
    email: Optional[str] = None
    phone: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """将用户对象序列化为字典格式，用于数据持久化"""
        return {
            'username': self.username,
            'password_hash': self.password_hash,
            'role': self.role.value,
            'email': self.email,
            'phone': self.phone
        }

class UserManager:
    """
    用户管理器
    
    负责：
    1. 用户数据的加载和保存
    2. 用户认证（登录、注册）
    3. 用户信息维护
    4. 密码管理
    """
    
    def __init__(self, data_file: str = "data/users.json"):
        self.data_file = data_file
        self.users: List[User] = []
        self._load_users()

    def _load_users(self) -> None:
        """从JSON文件加载用户数据，初始化时自动调用"""
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
        """将用户数据保存到JSON文件，在数据变更时自动调用"""
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
        """根据用户名查找用户"""
        return next((user for user in self.users if user.username == username), None)

    @staticmethod
    def hash_password(password: str) -> str:
        """使用SHA-256算法对密码进行哈希处理"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register(self, username: str, password: str, role: UserRole = UserRole.USER,
                email: Optional[str] = None, phone: Optional[str] = None) -> bool:
        """
        注册新用户
        
        业务流程：
        1. 验证用户名唯一性
        2. 密码加密处理
        3. 创建用户对象
        4. 保存用户数据
        
        数据验证：
        - 用户名不能为空且唯一
        - 密码不能为空
        - 邮箱和电话为可选项
        
        安全处理：
        - 密码使用SHA-256算法加密存储
        
        参数：
            username: 用户名
            password: 原始密码
            role: 用户角色，默认为普通用户
            email: 电子邮箱（可选）
            phone: 手机号码（可选）
            
        返回：
            注册是否成功
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
        用户登录验证
        
        业务流程：
        1. 查找用户记录
        2. 验证密码正确性
        3. 返回登录结果
        
        安全处理：
        - 对输入的密码进行加密后再比对
        - 不返回密码等敏感信息
        
        参数：
            username: 用户名
            password: 原始密码
            
        返回：
            验证通过返回用户对象，失败返回None
        """
        user = self._find_user(username)
        if user and user.password_hash == self.hash_password(password):
            logger.info(f'用户 {username} 登录成功')
            return user
        logger.warning(f'登录失败: 用户名或密码错误')
        return None

    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """
        修改用户密码
        
        业务流程：
        1. 验证用户存在性
        2. 验证旧密码正确性
        3. 加密新密码
        4. 更新并保存数据
        
        安全处理：
        - 验证旧密码防止未授权修改
        - 新密码使用相同的加密算法
        
        数据验证：
        - 新旧密码不能为空
        - 旧密码必须正确
        
        参数：
            username: 用户名
            old_password: 原密码
            new_password: 新密码
            
        返回：
            密码修改是否成功
        """
        user = self._find_user(username)
        if user and user.password_hash == self.hash_password(old_password):
            user.password_hash = self.hash_password(new_password)
            self._save_users()
            logger.info(f'用户 {username} 成功修改密码')
            return True
        logger.warning(f'修改密码失败: 用户名或旧密码错误')
        return False

    def update_user_info(self, username: str, email: Optional[str] = None,
                        phone: Optional[str] = None) -> bool:
        """
        更新用户联系信息
        
        业务流程：
        1. 查找用户记录
        2. 更新非空字段
        3. 保存数据变更
        
        数据处理：
        - 仅更新提供的非None字段
        - 支持单独更新邮箱或电话
        
        参数：
            username: 用户名
            email: 新的电子邮箱（可选）
            phone: 新的手机号码（可选）
            
        返回：
            更新是否成功
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