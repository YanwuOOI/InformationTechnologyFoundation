from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QMessageBox, QComboBox,
                             QTextEdit, QSpinBox, QFileDialog, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt
from core.user import UserManager, UserRole, User
from core.book import Book, BookManager
from core.borrow import BorrowManager, BorrowRecord

class RegisterDialog(QDialog):
    def __init__(self, user_manager: UserManager, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('注册新用户')
        self.setFixedSize(300, 300)

        layout = QVBoxLayout(self)

        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码
        password_layout = QHBoxLayout()
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_input)
        layout.addLayout(password_layout)

        # 确认密码
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel('确认密码:')
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)

        # 角色选择
        role_layout = QHBoxLayout()
        role_label = QLabel('角色:')
        self.role_input = QComboBox()
        self.role_input.addItems([role.value for role in UserRole])
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_input)
        layout.addLayout(role_layout)

        # 邮箱
        email_layout = QHBoxLayout()
        email_label = QLabel('邮箱:')
        self.email_input = QLineEdit()
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # 手机
        phone_layout = QHBoxLayout()
        phone_label = QLabel('手机:')
        self.phone_input = QLineEdit()
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)

        # 按钮
        button_layout = QHBoxLayout()
        register_button = QPushButton('注册')
        register_button.clicked.connect(self.register)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(register_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def register(self):
        username = self.username_input.text()
        password = self.password_input.text()
        confirm = self.confirm_input.text()
        role = UserRole(self.role_input.currentText())
        email = self.email_input.text()
        phone = self.phone_input.text()

        if not username or not password:
            QMessageBox.warning(self, '警告', '用户名和密码不能为空！')
            return

        if password != confirm:
            QMessageBox.warning(self, '警告', '两次输入的密码不一致！')
            return

        if self.user_manager.register(username, password, role, email, phone):
            QMessageBox.information(self, '成功', '注册成功！')
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '用户名已存在！')

class ChangePasswordDialog(QDialog):
    def __init__(self, user_manager: UserManager, username: str, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('修改密码')
        self.setFixedSize(300, 200)

        layout = QVBoxLayout(self)

        # 旧密码
        old_layout = QHBoxLayout()
        old_label = QLabel('旧密码:')
        self.old_input = QLineEdit()
        self.old_input.setEchoMode(QLineEdit.Password)
        old_layout.addWidget(old_label)
        old_layout.addWidget(self.old_input)
        layout.addLayout(old_layout)

        # 新密码
        new_layout = QHBoxLayout()
        new_label = QLabel('新密码:')
        self.new_input = QLineEdit()
        self.new_input.setEchoMode(QLineEdit.Password)
        new_layout.addWidget(new_label)
        new_layout.addWidget(self.new_input)
        layout.addLayout(new_layout)

        # 确认新密码
        confirm_layout = QHBoxLayout()
        confirm_label = QLabel('确认新密码:')
        self.confirm_input = QLineEdit()
        self.confirm_input.setEchoMode(QLineEdit.Password)
        confirm_layout.addWidget(confirm_label)
        confirm_layout.addWidget(self.confirm_input)
        layout.addLayout(confirm_layout)

        # 按钮
        button_layout = QHBoxLayout()
        confirm_button = QPushButton('确认')
        confirm_button.clicked.connect(self.change_password)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(confirm_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def change_password(self):
        old_password = self.old_input.text()
        new_password = self.new_input.text()
        confirm = self.confirm_input.text()

        if not old_password or not new_password:
            QMessageBox.warning(self, '警告', '密码不能为空！')
            return

        if new_password != confirm:
            QMessageBox.warning(self, '警告', '两次输入的新密码不一致！')
            return

        if self.user_manager.change_password(self.username, old_password, new_password):
            QMessageBox.information(self, '成功', '密码修改成功！')
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '旧密码错误！')

class BookDialog(QDialog):
    def __init__(self, book_manager: BookManager, book: Book = None, parent=None):
        super().__init__(parent)
        self.book_manager = book_manager
        self.book = book
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('添加图书' if not self.book else '编辑图书')
        self.setFixedSize(400, 500)

        layout = QVBoxLayout(self)

        # 书名
        title_layout = QHBoxLayout()
        title_label = QLabel('书名:')
        self.title_input = QLineEdit()
        if self.book:
            self.title_input.setText(self.book.title)
        title_layout.addWidget(title_label)
        title_layout.addWidget(self.title_input)
        layout.addLayout(title_layout)

        # 作者
        author_layout = QHBoxLayout()
        author_label = QLabel('作者:')
        self.author_input = QLineEdit()
        if self.book:
            self.author_input.setText(self.book.author)
        author_layout.addWidget(author_label)
        author_layout.addWidget(self.author_input)
        layout.addLayout(author_layout)

        # 分类
        category_layout = QHBoxLayout()
        category_label = QLabel('分类:')
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        categories = ['文学', '科技', '历史', '艺术', '教育', '其他']
        self.category_input.addItems(categories)
        if self.book:
            self.category_input.setCurrentText(self.book.category)
        category_layout.addWidget(category_label)
        category_layout.addWidget(self.category_input)
        layout.addLayout(category_layout)

        # 数量
        quantity_layout = QHBoxLayout()
        quantity_label = QLabel('数量:')
        self.quantity_input = QSpinBox()
        self.quantity_input.setMinimum(0)
        self.quantity_input.setMaximum(9999)
        if self.book:
            self.quantity_input.setValue(self.book.quantity)
        quantity_layout.addWidget(quantity_label)
        quantity_layout.addWidget(self.quantity_input)
        layout.addLayout(quantity_layout)

        # 描述
        description_layout = QVBoxLayout()
        description_label = QLabel('描述:')
        self.description_input = QTextEdit()
        if self.book:
            self.description_input.setText(self.book.description or '')
        description_layout.addWidget(description_label)
        description_layout.addWidget(self.description_input)
        layout.addLayout(description_layout)

        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton('保存')
        save_button.clicked.connect(self.save_book)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def save_book(self):
        title = self.title_input.text()
        author = self.author_input.text()
        category = self.category_input.currentText()
        quantity = self.quantity_input.value()
        description = self.description_input.toPlainText()

        if not title or not author:
            QMessageBox.warning(self, '警告', '书名和作者不能为空！')
            return

        if self.book:  # 编辑现有图书
            self.book.title = title
            self.book.author = author
            self.book.category = category
            self.book.quantity = quantity
            self.book.description = description
            if self.book_manager.update_book(self.book):
                QMessageBox.information(self, '成功', '图书更新成功！')
                self.accept()
            else:
                QMessageBox.warning(self, '错误', '图书更新失败！')
        else:  # 添加新图书
            book = Book(
                id=f"BK{len(self.book_manager.books) + 1:06d}",
                title=title,
                author=author,
                category=category,
                quantity=quantity,
                description=description
            )
            if self.book_manager.add_book(book):
                QMessageBox.information(self, '成功', '图书添加成功！')
                self.accept()
            else:
                QMessageBox.warning(self, '错误', '图书添加失败！')

class BorrowBookDialog(QDialog):
    def __init__(self, book_manager: BookManager, borrow_manager: BorrowManager,
                 username: str, parent=None):
        super().__init__(parent)
        self.book_manager = book_manager
        self.borrow_manager = borrow_manager
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('借阅图书')
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

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
        self.book_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.book_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.book_table)

        # 按钮
        button_layout = QHBoxLayout()
        borrow_button = QPushButton('借阅')
        borrow_button.clicked.connect(self.borrow_book)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(borrow_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.refresh_book_table()

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

    def borrow_book(self):
        selected_items = self.book_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要借阅的图书！')
            return

        row = selected_items[0].row()
        book_id = self.book_table.item(row, 0).text()
        book = self.book_manager.get_book(book_id)

        if not book:
            QMessageBox.warning(self, '错误', '图书不存在！')
            return

        if book.quantity <= 0:
            QMessageBox.warning(self, '警告', '该图书已无可借阅数量！')
            return

        # 检查是否已经借阅且未归还
        active_borrows = self.borrow_manager.get_active_borrows(self.username)
        if any(record.book_id == book_id for record in active_borrows):
            QMessageBox.warning(self, '警告', '您已经借阅了这本书且未归还！')
            return

        # 执行借阅
        record = self.borrow_manager.borrow_book(book_id, self.username)
        if record:
            # 更新图书数量
            book.quantity -= 1
            self.book_manager.update_book(book)
            QMessageBox.information(self, '成功', '借阅成功！')
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '借阅失败！')

class ReturnBookDialog(QDialog):
    def __init__(self, book_manager: BookManager, borrow_manager: BorrowManager,
                 username: str, parent=None):
        super().__init__(parent)
        self.book_manager = book_manager
        self.borrow_manager = borrow_manager
        self.username = username
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('归还图书')
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        # 借阅记录表格
        self.borrow_table = QTableWidget()
        self.borrow_table.setColumnCount(5)
        self.borrow_table.setHorizontalHeaderLabels(['借阅ID', '图书ID', '书名', '借阅时间', '状态'])
        self.borrow_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.borrow_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.borrow_table.setSelectionMode(QTableWidget.SingleSelection)
        layout.addWidget(self.borrow_table)

        # 按钮
        button_layout = QHBoxLayout()
        return_button = QPushButton('归还')
        return_button.clicked.connect(self.return_book)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(return_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

        self.refresh_borrow_table()

    def refresh_borrow_table(self):
        self.borrow_table.setRowCount(0)
        records = self.borrow_manager.get_active_borrows(self.username)
        for row, record in enumerate(records):
            self.borrow_table.insertRow(row)
            self.borrow_table.setItem(row, 0, QTableWidgetItem(record.id))
            self.borrow_table.setItem(row, 1, QTableWidgetItem(record.book_id))
            
            # 获取图书信息
            book = self.book_manager.get_book(record.book_id)
            book_title = book.title if book else '未知'
            self.borrow_table.setItem(row, 2, QTableWidgetItem(book_title))
            
            self.borrow_table.setItem(row, 3, QTableWidgetItem(record.borrow_date))
            self.borrow_table.setItem(row, 4, QTableWidgetItem('借阅中'))

    def return_book(self):
        selected_items = self.borrow_table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, '警告', '请先选择要归还的图书！')
            return

        row = selected_items[0].row()
        book_id = self.borrow_table.item(row, 1).text()
        book = self.book_manager.get_book(book_id)

        if not book:
            QMessageBox.warning(self, '错误', '图书不存在！')
            return

        # 执行归还
        if self.borrow_manager.return_book(book_id, self.username):
            # 更新图书数量
            book.quantity += 1
            self.book_manager.update_book(book)
            QMessageBox.information(self, '成功', '归还成功！')
            self.accept()
        else:
            QMessageBox.warning(self, '错误', '归还失败！')

class UserDialog(QDialog):
    def __init__(self, user_manager: UserManager, user: User = None, parent=None):
        super().__init__(parent)
        self.user_manager = user_manager
        self.user = user
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('添加用户' if not self.user else '编辑用户')
        self.setFixedSize(400, 300)

        layout = QVBoxLayout(self)

        # 用户名
        username_layout = QHBoxLayout()
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        if self.user:
            self.username_input.setText(self.user.username)
            self.username_input.setReadOnly(True)  # 编辑时不允许修改用户名
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_input)
        layout.addLayout(username_layout)

        # 密码（仅添加用户时显示）
        if not self.user:
            password_layout = QHBoxLayout()
            password_label = QLabel('密码:')
            self.password_input = QLineEdit()
            self.password_input.setEchoMode(QLineEdit.Password)
            password_layout.addWidget(password_label)
            password_layout.addWidget(self.password_input)
            layout.addLayout(password_layout)

            # 确认密码
            confirm_layout = QHBoxLayout()
            confirm_label = QLabel('确认密码:')
            self.confirm_input = QLineEdit()
            self.confirm_input.setEchoMode(QLineEdit.Password)
            confirm_layout.addWidget(confirm_label)
            confirm_layout.addWidget(self.confirm_input)
            layout.addLayout(confirm_layout)

        # 角色
        role_layout = QHBoxLayout()
        role_label = QLabel('角色:')
        self.role_input = QComboBox()
        self.role_input.addItems([role.value for role in UserRole])
        if self.user:
            self.role_input.setCurrentText(self.user.role.value)
        role_layout.addWidget(role_label)
        role_layout.addWidget(self.role_input)
        layout.addLayout(role_layout)

        # 邮箱
        email_layout = QHBoxLayout()
        email_label = QLabel('邮箱:')
        self.email_input = QLineEdit()
        if self.user:
            self.email_input.setText(self.user.email or '')
        email_layout.addWidget(email_label)
        email_layout.addWidget(self.email_input)
        layout.addLayout(email_layout)

        # 手机
        phone_layout = QHBoxLayout()
        phone_label = QLabel('手机:')
        self.phone_input = QLineEdit()
        if self.user:
            self.phone_input.setText(self.user.phone or '')
        phone_layout.addWidget(phone_label)
        phone_layout.addWidget(self.phone_input)
        layout.addLayout(phone_layout)

        # 按钮
        button_layout = QHBoxLayout()
        save_button = QPushButton('保存')
        save_button.clicked.connect(self.save_user)
        cancel_button = QPushButton('取消')
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)

    def save_user(self):
        username = self.username_input.text()
        role = UserRole(self.role_input.currentText())
        email = self.email_input.text() or None
        phone = self.phone_input.text() or None

        if not username:
            QMessageBox.warning(self, '警告', '用户名不能为空！')
            return

        if self.user:  # 编辑用户
            if self.user_manager.update_user_info(username, email, phone):
                QMessageBox.information(self, '成功', '用户信息更新成功！')
                self.accept()
            else:
                QMessageBox.warning(self, '错误', '用户信息更新失败！')
        else:  # 添加用户
            password = self.password_input.text()
            confirm = self.confirm_input.text()

            if not password:
                QMessageBox.warning(self, '警告', '密码不能为空！')
                return

            if password != confirm:
                QMessageBox.warning(self, '警告', '两次输入的密码不一致！')
                return

            if self.user_manager.register(username, password, role, email, phone):
                QMessageBox.information(self, '成功', '用户添加成功！')
                self.accept()
            else:
                QMessageBox.warning(self, '错误', '用户名已存在！') 