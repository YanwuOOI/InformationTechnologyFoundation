"""
登录窗口模块

本模块提供图书管理系统的登录界面：
1. 用户登录表单和验证
2. 用户注册入口
3. 界面布局和样式定义
4. 登录状态管理

界面结构：
1. 系统标题区域
2. 登录表单区域（用户名、密码输入框）
3. 操作按钮区域（登录、注册按钮）

交互流程：
1. 用户输入凭据
2. 点击登录按钮验证
3. 验证成功跳转主界面
4. 验证失败显示错误提示
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from core.user import UserManager, UserRole
from gui.main_window import MainWindow
from PyQt5.QtGui import QIcon

class LoginWindow(QMainWindow):
    """
    登录窗口类
    
    提供用户登录界面和相关功能：
    - 用户名和密码输入
    - 登录验证
    - 注册新用户入口
    - 界面美化
    """
    
    def __init__(self):
        """
        初始化登录窗口
        
        创建:
        - 用户管理器实例
        - 界面组件和布局
        """
        super().__init__()
        # 设置窗口图标
        self.setWindowIcon(QIcon("resources/book.png"))  
        self.user_manager = UserManager()  # 创建用户管理器实例
        self.init_ui()

    def init_ui(self):
        """
        初始化用户界面
        
        界面布局：
        1. 窗口基本属性设置
           - 标题：图书管理系统 - 登录
           - 固定大小：400x300
           
        2. 界面元素布局
           - 顶部：系统标题
           - 中部：登录表单
           - 底部：操作按钮
           
        3. 样式设置
           - 背景色：浅灰色
           - 按钮：绿色主题
           - 输入框：圆角边框
           - 文字：统一字号
        """
        # 设置窗口基本属性
        self.setWindowTitle('图书管理系统 - 登录')
        self.setFixedSize(400, 300)

        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)

        # 标题
        title_label = QLabel('图书管理系统')
        title_label.setStyleSheet('font-size: 24px; font-weight: bold;')
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # 用户名输入
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码输入
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)  # 设置密码隐藏显示
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 登录按钮
        login_button = QPushButton('登录')
        login_button.clicked.connect(self.login)
        button_layout.addWidget(login_button)

        # 注册按钮
        register_button = QPushButton('注册')
        register_button.clicked.connect(self.show_register_dialog)
        button_layout.addWidget(register_button)

        layout.addLayout(button_layout)

        # 设置界面样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 14px;
            }
            QLineEdit {
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 15px;
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 3px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)

    def login(self):
        """
        处理用户登录事件
        
        交互流程：
        1. 输入验证
           - 检查用户名和密码非空
           - 显示相应错误提示
           
        2. 身份验证
           - 调用用户管理器验证
           - 成功则创建主窗口
           - 失败显示错误消息
           
        3. 界面切换
           - 登录成功关闭登录窗口
           - 显示系统主界面
           
        异常处理：
        - 输入为空时提示用户
        - 验证失败时保留输入内容
        """
        # 获取用户输入
        username = self.username_input.text()
        password = self.password_input.text()

        # 验证输入完整性
        if not username or not password:
            QMessageBox.warning(self, '警告', '用户名和密码不能为空！')
            return

        # 尝试登录
        user = self.user_manager.login(username, password)
        if user:
            # 登录成功，创建并显示主窗口
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, '错误', '用户名或密码错误！')

    def show_register_dialog(self):
        """
        显示用户注册对话框
        
        流程：
        1. 创建注册对话框实例
        2. 显示模态对话框
        3. 用户完成注册后自动关闭
        """
        from gui.dialogs import RegisterDialog
        dialog = RegisterDialog(self.user_manager, self)
        dialog.exec_()