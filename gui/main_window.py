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
    def __init__(self, user: User):
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
        keyword = self.search_input.text()
        if not keyword:
            self.refresh_book_table()
            return

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
        dialog = BookDialog(self.book_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_book_table()

    def edit_book(self):
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
        dialog = BorrowBookDialog(self.book_manager, self.borrow_manager,
                                self.user.username, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_borrow_table()
            self.refresh_book_table()
        
    def return_book(self):
        dialog = ReturnBookDialog(self.book_manager, self.borrow_manager,
                                self.user.username, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_borrow_table()
            self.refresh_book_table()

    def add_user(self):
        dialog = UserDialog(self.user_manager, parent=self)
        if dialog.exec_() == QDialog.Accepted:
            self.refresh_user_table()

    def edit_user(self, user=None):
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
        dialog = ChangePasswordDialog(self.user_manager, self.user.username, self)
        dialog.exec_()

    def logout(self):
        from gui.login_window import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def view_all_borrows(self):
        """管理员查看所有借阅记录"""
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