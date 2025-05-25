"""
主窗口模块

本模块提供图书管理系统的主要功能界面，实现完整的业务操作流程：

功能模块：
1. 图书管理
   - 图书信息维护（增删改查）
   - 库存管理
   - 数据导出
   
2. 借阅管理
   - 图书借阅
   - 图书归还
   - 借阅历史查询
   
3. 用户管理（管理员专属）
   - 用户账户维护
   - 权限管理
   
4. 个人账户
   - 密码修改
   - 登录状态管理

界面特点：
1. 选项卡式布局，功能分类清晰
2. 表格化数据展示，操作直观
3. 权限分级显示，安全可控
4. 统一的操作风格和响应机制

用户体验：
1. 实时数据更新
2. 友好的错误提示
3. 操作确认机制
4. 快捷功能入口
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox,
                            QTableWidget, QTableWidgetItem, QTabWidget,
                            QComboBox, QHeaderView, QFileDialog, QDialog)
from PyQt5.QtCore import Qt
from core.user import User, UserManager, UserRole
from core.book import Book, BookManager
from core.borrow import BorrowManager, BorrowRecord
from gui.dialogs import ChangePasswordDialog, BookDialog, BorrowBookDialog, ReturnBookDialog, UserDialog

class MainWindow(QMainWindow):
    """
    主窗口类
    
    核心职责：
    1. 界面框架搭建
       - 菜单栏和工具栏
       - 状态栏
       - 核心功能区
       
    2. 数据管理
       - 用户信息维护
       - 图书数据处理
       - 借阅记录管理
       
    3. 业务流程控制
       - 权限检查
       - 操作验证
       - 异常处理
       
    4. 界面交互
       - 事件响应
       - 状态更新
       - 消息提示
    """
    
    def __init__(self, user: User):
        """
        初始化主窗口
        
        初始化流程：
        1. 创建核心管理器
           - 用户管理器
           - 图书管理器
           - 借阅管理器
           
        2. 初始化界面
           - 设置窗口属性
           - 创建功能选项卡
           - 配置操作按钮
           
        3. 权限控制
           - 根据用户角色显示功能
           - 设置操作权限
           
        参数：
            user: 当前登录用户对象
        """
        super().__init__()
        self.user = user
        self.user_manager = UserManager()
        self.book_manager = BookManager()
        self.borrow_manager = BorrowManager(book_manager=self.book_manager)
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle(f'图书管理系统 - {self.user.username}')
        self.setMinimumSize(800, 600)

        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 创建选项卡
        tab_widget = QTabWidget()
        
        # 图书管理选项卡
        book_tab = QWidget()
        self.init_book_tab(book_tab)
        tab_widget.addTab(book_tab, "图书管理")

        # 借阅管理选项卡
        borrow_tab = QWidget()
        self.init_borrow_tab(borrow_tab)
        tab_widget.addTab(borrow_tab, "借阅管理")

        # 如果是管理员，添加用户管理选项卡
        if self.user.role == UserRole.ADMIN:
            user_tab = QWidget()
            self.init_user_tab(user_tab)
            tab_widget.addTab(user_tab, "用户管理")

        layout.addWidget(tab_widget)

        # 添加底部按钮
        bottom_layout = QHBoxLayout()
        change_password_button = QPushButton('修改密码')
        change_password_button.clicked.connect(self.show_change_password_dialog)
        logout_button = QPushButton('退出登录')
        logout_button.clicked.connect(self.logout)
        bottom_layout.addWidget(change_password_button)
        bottom_layout.addWidget(logout_button)
        layout.addLayout(bottom_layout)

    def init_book_tab(self, tab: QWidget):
        """
        初始化图书管理选项卡
        
        界面结构：
        1. 搜索区域
           - 关键词输入框
           - 搜索按钮
           
        2. 图书信息表格
           - ID、书名、作者等字段
           - 自适应列宽
           - 支持排序和选择
           
        3. 操作按钮区
           - 基础操作（借阅、归还）
           - 管理操作（增删改）- 仅管理员可见
           - 数据导出功能
           
        交互特点：
        - 实时搜索响应
        - 多选多操作支持
        - 权限控制显示
        """
        layout = QVBoxLayout(tab)

        # 搜索区域
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('输入书名、作者或分类进行搜索')
        search_button = QPushButton('搜索')
        search_button.clicked.connect(self.search_books)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # 图书表格
        self.book_table = QTableWidget()
        self.book_table.setColumnCount(6)
        self.book_table.setHorizontalHeaderLabels(['ID', '书名', '作者', '分类', '数量', '描述'])
        self.book_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.book_table)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 所有用户都可以借阅和归还图书
        borrow_button = QPushButton('借阅图书')
        borrow_button.clicked.connect(self.borrow_book)
        return_button = QPushButton('归还图书')
        return_button.clicked.connect(self.return_book)
        button_layout.addWidget(borrow_button)
        button_layout.addWidget(return_button)

        # 只有管理员可以管理图书
        if self.user.role == UserRole.ADMIN:
            add_button = QPushButton('添加图书')
            add_button.clicked.connect(self.add_book)
            edit_button = QPushButton('编辑图书')
            edit_button.clicked.connect(self.edit_book)
            delete_button = QPushButton('删除图书')
            delete_button.clicked.connect(self.delete_book)
            export_button = QPushButton('导出图书')
            export_button.clicked.connect(self.export_books)
            button_layout.addWidget(add_button)
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.addWidget(export_button)

        layout.addLayout(button_layout)
        self.refresh_book_table()

    def init_borrow_tab(self, tab: QWidget):
        """
        初始化借阅管理选项卡
        
        界面结构：
        1. 借阅记录表格
           - 借阅ID、图书信息
           - 借阅时间、状态
           - 自适应列宽
           
        2. 操作按钮区
           - 借阅和归还按钮
           - 查看全部记录（管理员）
           
        数据显示：
        - 普通用户仅看到自己的记录
        - 管理员可查看所有记录
        - 支持状态筛选
        """
        layout = QVBoxLayout(tab)

        # 借阅历史表格
        self.borrow_table = QTableWidget()
        self.borrow_table.setColumnCount(5)
        self.borrow_table.setHorizontalHeaderLabels(['借阅ID', '图书ID', '借阅时间', '归还时间', '状态'])
        self.borrow_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.borrow_table)

        # 按钮布局
        button_layout = QHBoxLayout()
        
        # 所有用户都可以借阅和归还图书
        borrow_button = QPushButton('借阅图书')
        borrow_button.clicked.connect(self.borrow_book)
        return_button = QPushButton('归还图书')
        return_button.clicked.connect(self.return_book)
        button_layout.addWidget(borrow_button)
        button_layout.addWidget(return_button)

        # 只有管理员可以查看所有借阅记录
        if self.user.role == UserRole.ADMIN:
            view_all_button = QPushButton('查看所有借阅记录')
            view_all_button.clicked.connect(self.view_all_borrows)
            button_layout.addWidget(view_all_button)

        layout.addLayout(button_layout)
        self.refresh_borrow_table()

    def init_user_tab(self, tab: QWidget):
        """
        初始化用户管理选项卡（管理员专属）
        
        界面结构：
        1. 用户信息表格
           - 基本信息字段
           - 角色和状态
           - 操作列
           
        2. 管理按钮区
           - 添加用户
           - 编辑用户
           - 删除用户
           
        功能特点：
        - 快速编辑支持
        - 批量操作处理
        - 用户状态管理
        """
        layout = QVBoxLayout(tab)

        # 用户表格
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(['用户名', '角色', '邮箱', '手机', '操作'])
        self.user_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.user_table)

        # 用户管理按钮
        button_layout = QHBoxLayout()
        add_user_button = QPushButton('添加用户')
        add_user_button.clicked.connect(self.add_user)
        edit_user_button = QPushButton('编辑用户')
        edit_user_button.clicked.connect(self.edit_user)
        delete_user_button = QPushButton('删除用户')
        delete_user_button.clicked.connect(self.delete_user)
        button_layout.addWidget(add_user_button)
        button_layout.addWidget(edit_user_button)
        button_layout.addWidget(delete_user_button)
        layout.addLayout(button_layout)

        self.refresh_user_table()

    def refresh_book_table(self):
        """
        刷新图书信息表格
        
        功能：
        1. 清空当前表格内容
        2. 获取最新的图书数据
        3. 按顺序填充表格字段：
           - ID：图书唯一标识
           - 书名：图书标题
           - 作者：图书作者
           - 分类：图书类别
           - 数量：在库数量
           - 描述：图书简介
        """
        self.book_table.setRowCount(0)
        books = self.book_manager.get_all_books()
        for row, book in enumerate(books):
            self.book_table.insertRow(row)
            self.book_table.setItem(row, 0, QTableWidgetItem(book.id))
            self.book_table.setItem(row, 1, QTableWidgetItem(book.title))
            self.book_table.setItem(row, 2, QTableWidgetItem(book.author))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.category))
            self.book_table.setItem(row, 4, QTableWidgetItem(str(book.quantity)))
            self.book_table.setItem(row, 5, QTableWidgetItem(book.description or ''))

    def refresh_borrow_table(self):
        """
        刷新借阅记录表格
        
        功能：
        1. 清空当前表格内容
        2. 根据用户角色获取借阅记录：
           - 管理员：显示所有用户的借阅记录
           - 普通用户：只显示自己的借阅记录
        3. 填充表格字段：
           - 借阅ID：记录唯一标识
           - 图书ID：关联的图书
           - 借阅时间：借出时间
           - 归还时间：实际归还时间（未归还显示"未归还"）
           - 状态：已归还/借阅中
        """
        self.borrow_table.setRowCount(0)
        # 管理员可以查看所有借阅记录，普通用户只能查看自己的
        if self.user.role == UserRole.ADMIN:
            records = self.borrow_manager.records
        else:
            records = self.borrow_manager.get_user_borrow_history(self.user.username)
            
        for row, record in enumerate(records):
            self.borrow_table.insertRow(row)
            self.borrow_table.setItem(row, 0, QTableWidgetItem(record.id))
            self.borrow_table.setItem(row, 1, QTableWidgetItem(record.book_id))
            self.borrow_table.setItem(row, 2, QTableWidgetItem(record.borrow_date))
            self.borrow_table.setItem(row, 3, QTableWidgetItem(record.return_date or '未归还'))
            status = '已归还' if record.return_date else '借阅中'
            self.borrow_table.setItem(row, 4, QTableWidgetItem(status))

    def refresh_user_table(self):
        """
        刷新用户信息表格（仅管理员可见）
        
        功能：
        1. 清空当前表格内容
        2. 获取所有用户信息
        3. 填充表格字段：
           - 用户名：账号名称
           - 角色：用户权限级别
           - 邮箱：联系邮箱
           - 手机：联系电话
           - 操作：快捷编辑按钮
        4. 为每行添加编辑按钮，实现快速操作
        """
        self.user_table.setRowCount(0)
        users = self.user_manager.users
        for row, user in enumerate(users):
            self.user_table.insertRow(row)
            self.user_table.setItem(row, 0, QTableWidgetItem(user.username))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.role.value))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.email or ''))
            self.user_table.setItem(row, 3, QTableWidgetItem(user.phone or ''))
            
            # 添加操作按钮
            edit_button = QPushButton('编辑')
            edit_button.clicked.connect(lambda checked, u=user: self.edit_user(u))
            self.user_table.setCellWidget(row, 4, edit_button)

    def search_books(self):
        """
        搜索图书功能
        
        搜索范围：
        - 书名
        - 作者
        - 分类
        
        处理流程：
        1. 获取搜索关键词
        2. 空关键词时显示全部图书
        3. 调用图书管理器执行搜索
        4. 清空并更新表格显示搜索结果
        
        注意：
        - 搜索支持模糊匹配
        - 不区分大小写
        """
        keyword = self.search_input.text()
        if not keyword:
            self.refresh_book_table()
            return

        # 执行搜索并显示结果
        books = self.book_manager.search_books(keyword)
        self.book_table.setRowCount(0)
        for row, book in enumerate(books):
            self.book_table.insertRow(row)
            self.book_table.setItem(row, 0, QTableWidgetItem(book.id))
            self.book_table.setItem(row, 1, QTableWidgetItem(book.title))
            self.book_table.setItem(row, 2, QTableWidgetItem(book.author))
            self.book_table.setItem(row, 3, QTableWidgetItem(book.category))
            self.book_table.setItem(row, 4, QTableWidgetItem(str(book.quantity)))
            self.book_table.setItem(row, 5, QTableWidgetItem(book.description or ''))

    def add_book(self):
        """
        添加新图书
        
        流程：
        1. 打开图书信息编辑对话框
        2. 如果成功添加图书，刷新图书表格
        """
        dialog = BookDialog(self.book_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_book_table()

    def edit_book(self):
        """
        编辑图书信息
        
        流程：
        1. 获取选中的图书
        2. 打开图书编辑对话框
        3. 如果修改成功，刷新图书表格
        """
        selected_items = self.book_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要编辑的图书！')
            return

        row = selected_items[0].row()
        book_id = self.book_table.item(row, 0).text()
        book = self.book_manager.get_book(book_id)
        if book:
            dialog = BookDialog(self.book_manager, book, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_book_table()

    def delete_book(self):
        """
        删除图书
        
        流程：
        1. 确认选择了要删除的图书
        2. 显示删除确认对话框
        3. 如果用户确认，执行删除操作并刷新图书表格
        """
        selected_items = self.book_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要删除的图书！')
            return

        row = selected_items[0].row()
        book_id = self.book_table.item(row, 0).text()
        
        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除这本图书吗？此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            if self.book_manager.remove_book(book_id):
                QMessageBox.information(self, '成功', '图书删除成功！')
                self.refresh_book_table()
            else:
                QMessageBox.warning(self, '错误', '图书删除失败！')

    def export_books(self):
        """
        导出图书信息功能
        
        功能：
        1. 打开文件保存对话框
        2. 指定保存为CSV格式
        3. 调用图书管理器执行导出
        4. 显示导出结果提示
        
        导出字段：
        - 图书ID
        - 书名
        - 作者
        - 分类
        - 数量
        - 描述
        
        异常处理：
        - 导出失败时显示错误信息
        - 用户取消操作时直接返回
        """
        filename, _ = QFileDialog.getSaveFileName(
            self,
            '导出图书信息',
            '',
            'CSV Files (*.csv);;All Files (*)'
        )
        
        if filename:
            try:
                self.book_manager.export_to_csv(filename)
                QMessageBox.information(self, '成功', '图书信息导出成功！')
            except Exception as e:
                QMessageBox.warning(self, '错误', f'图书信息导出失败：{str(e)}')

    def borrow_book(self):
        """
        处理图书借阅操作
        
        流程：
        1. 打开借阅对话框
        2. 如果用户确认借阅，更新借阅表和图书表
        """
        dialog = BorrowBookDialog(self.book_manager, self.borrow_manager,
                                self.user.username, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_borrow_table()
            self.refresh_book_table()
        
    def return_book(self):
        """
        处理图书归还操作
        
        流程：
        1. 打开归还对话框
        2. 如果用户确认归还，更新借阅表和图书表
        """
        dialog = ReturnBookDialog(self.book_manager, self.borrow_manager,
                                self.user.username, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_borrow_table()
            self.refresh_book_table()

    def add_user(self):
        """
        添加新用户
        
        流程：
        1. 打开用户信息编辑对话框
        2. 如果成功添加用户，刷新用户表格
        """
        dialog = UserDialog(self.user_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_user_table()

    def edit_user(self, user=None):
        """
        编辑用户信息
        
        Args:
            user: 要编辑的用户对象，如果为None则从表格选择
            
        流程：
        1. 获取要编辑的用户信息
        2. 打开用户编辑对话框
        3. 如果修改成功，刷新用户表格
        """
        if not user:
            selected_items = self.user_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, '警告', '请先选择要编辑的用户！')
                return

            row = selected_items[0].row()
            username = self.user_table.item(row, 0).text()
            user = self.user_manager.get_user(username)

        if user:
            dialog = UserDialog(self.user_manager, user, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                self.refresh_user_table()

    def delete_user(self):
        """
        删除用户
        
        流程：
        1. 确认选择了要删除的用户
        2. 检查是否为当前登录用户
        3. 检查用户是否有未归还的图书
        4. 确认删除操作
        5. 执行删除并刷新用户表格
        """
        selected_items = self.user_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要删除的用户！')
            return

        row = selected_items[0].row()
        username = self.user_table.item(row, 0).text()
        
        # 不允许删除自己
        if username == self.user.username:
            QMessageBox.warning(self, '警告', '不能删除当前登录的用户！')
            return

        reply = QMessageBox.question(
            self, '确认删除',
            '确定要删除该用户吗？此操作不可恢复！',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 检查用户是否有未归还的图书
            active_borrows = self.borrow_manager.get_active_borrows(username)
            if active_borrows:
                QMessageBox.warning(
                    self, '警告',
                    '该用户还有未归还的图书，请先处理借阅记录！'
                )
                return

            # 从用户列表中删除
            self.user_manager.users = [
                u for u in self.user_manager.users if u.username != username
            ]
            self.user_manager._save_users()
            QMessageBox.information(self, '成功', '用户删除成功！')
            self.refresh_user_table()

    def show_change_password_dialog(self):
        """
        显示修改密码对话框
        """
        dialog = ChangePasswordDialog(self.user_manager, self.user.username, self)
        dialog.exec_()

    def logout(self):
        """
        退出登录
        
        流程：
        1. 显示新的登录窗口
        2. 关闭当前主窗口
        """
        from gui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def view_all_borrows(self):
        """
        管理员查看所有借阅记录
        
        - 清空并重新填充借阅记录表格
        - 显示所有用户的借阅历史
        """
        self.borrow_table.setRowCount(0)
        for record in self.borrow_manager.records:
            row = self.borrow_table.rowCount()
            self.borrow_table.insertRow(row)
            self.borrow_table.setItem(row, 0, QTableWidgetItem(record.id))
            self.borrow_table.setItem(row, 1, QTableWidgetItem(record.book_id))
            self.borrow_table.setItem(row, 2, QTableWidgetItem(record.borrow_date))
            self.borrow_table.setItem(row, 3, QTableWidgetItem(record.return_date or '未归还'))
            status = '已归还' if record.return_date else '借阅中'
            self.borrow_table.setItem(row, 4, QTableWidgetItem(status))