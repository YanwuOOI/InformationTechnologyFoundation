from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QMessageBox)
from PyQt5.QtCore import Qt
from core.user import UserManager, UserRole
from gui.main_window import MainWindow

class LoginWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.user_manager = UserManager()
        self.init_ui()

    def init_ui(self):
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
        self.password_input.setEchoMode(QLineEdit.Password)
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

        # 设置样式
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
        username = self.username_input.text()
        password = self.password_input.text()

        if not username or not password:
            QMessageBox.warning(self, '警告', '用户名和密码不能为空！')
            return

        user = self.user_manager.login(username, password)
        if user:
            self.main_window = MainWindow(user)
            self.main_window.show()
            self.close()
        else:
            QMessageBox.warning(self, '错误', '用户名或密码错误！')

    def show_register_dialog(self):
        from gui.dialogs import RegisterDialog
        dialog = RegisterDialog(self.user_manager, self)
        dialog.exec_() 