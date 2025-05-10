import sys
import uuid
import os
from datetime import datetime
import numpy as np
import pandas as pd
import mysql.connector
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QLineEdit, QComboBox, QTableWidget,
                             QTableWidgetItem, QHeaderView, QFrame, QTextEdit,
                             QRadioButton, QFileDialog, QMessageBox, QDateEdit, QStackedWidget,
                             QScrollArea, QCompleter)
from PyQt5.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt5.QtCore import Qt, QDate, QSize, QStringListModel

class LibraryManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CBCA Library Management System")
        self.setGeometry(100, 100, 1200, 800)

        # Set global font with increased size
        app = QApplication.instance()
        app.setFont(QFont("Helvetica, Arial, sans-serif", 15))

        # Updated stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f2f5;
            }
            QFrame {
                background-color: white;
                border: none;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            QFrame#loginFrame {
                border: 3px solid #e5e7eb;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #4f46e5);
                color: white;
                border-radius: 5px;
                padding: 12px;
                font-size: 16pt;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #818cf8, stop:1 #6366f1);
            }
            QLineEdit, QComboBox, QDateEdit {
                border: 1px solid #d1d5db;
                border-radius: 5px;
                padding: 10px;
                font-size: 15pt;
                background-color: #ffffff;
                min-height: 50px;
            }
            QLineEdit:focus, QComboBox:focus, QDateEdit:focus {
                border: 1px solid #6366f1;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: none;
                width: 14px;
                height: 14px;
            }
            QComboBox QAbstractItemView {
                background-color: #ffffff;
                color: #1f2937;
                selection-background-color: #6366f1;
                selection-color: white;
                border: 1px solid #d1d5db;
                padding: 5px;
                font-size: 15pt;
            }
            QTableWidget {
                border: none;
                border-radius: 5px;
                font-size: 15pt;
                background-color: white;
            }
            QTableWidget::item {
                padding: 12px;
            }
            QHeaderView::section {
                background: #6366f1;
                color: white;
                padding: 12px;
                font: bold 16pt;
                border: none;
            }
            QLabel {
                color: #1f2937;
                font-size: 15pt;
                border: none;
                background: transparent;
            }
            QTextEdit {
                border: 1px solid #d1d5db;
                border-radius: 5px;
                font-size: 14pt;
                background-color: #f9fafb;
            }
        """)

        # Database connection
        try:
            self.db = mysql.connector.connect(
                host="localhost",
                user="root",
                password="12345",
                database="library_db"
            )
            self.create_tables()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Failed to connect to database: {err}")
            sys.exit(1)

        # Main layout
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)

        # Sidebar (initially hidden)
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(250)
        self.sidebar.setVisible(False)
        self.sidebar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #4f46e5, stop:1 #6366f1);
                border-radius: 0;
                border: none;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            QPushButton {
                background: transparent;
                text-align: left;
                padding: 16px;
                font-size: 16pt;
                border: none;
                color: white;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.1);
            }
        """)
        sidebar_layout = QVBoxLayout(self.sidebar)
        sidebar_layout.setContentsMargins(15, 30, 15, 30)
        sidebar_layout.setSpacing(15)

        # Sidebar buttons
        sidebar_buttons = [
            ("🏠 Home", lambda: self.show_page("HomePage")),
            ("👤 Users", lambda: self.show_page("CreateUserPage")),
            ("📚 Books", lambda: self.show_page("BookAuthorPage")),
            ("🔄 Transactions", lambda: self.show_page("AssignReturnPage")),
            ("🔧 Admin", lambda: self.show_page("AdminPanelPage")),
            ("📊 Reports", lambda: self.show_page("ReportPage")),
            ("🚪 Logout", lambda: self.logout())
        ]

        for text, command in sidebar_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(command)
            sidebar_layout.addWidget(btn)
        sidebar_layout.addStretch()

        self.main_layout.addWidget(self.sidebar)

        # Content area
        self.content_area = QStackedWidget()
        self.main_layout.addWidget(self.content_area)

        # Pages
        self.pages = {
            "LoginPage": LoginPage(self),
            "HomePage": HomePage(self),
            "CreateUserPage": CreateUserPage(self),
            "BookAuthorPage": BookAuthorPage(self),
            "AssignReturnPage": AssignReturnPage(self),
            "AdminPanelPage": AdminPanelPage(self),
            "ReportPage": ReportPage(self)
        }

        for page in self.pages.values():
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setWidget(page)
            self.content_area.addWidget(scroll)

        self.show_page("LoginPage")

    def show_page(self, page_name):
        try:
            self.content_area.setCurrentWidget(self.content_area.widget(list(self.pages.keys()).index(page_name)))
            if hasattr(self.pages[page_name], 'refresh'):
                self.pages[page_name].refresh()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to show page: {e}")

    def logout(self):
        self.sidebar.setVisible(False)
        self.show_page("LoginPage")

    def create_tables(self):
        cursor = self.db.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                serial_number VARCHAR(255) UNIQUE NOT NULL,
                dob DATE,
                password VARCHAR(255) NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE NOT NULL,
                details TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                serial_number VARCHAR(255) UNIQUE NOT NULL,
                title VARCHAR(255) NOT NULL,
                author_id INT,
                FOREIGN KEY (author_id) REFERENCES authors(id)
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT,
                book_id INT,
                issue_date DATE,
                return_date DATE,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (book_id) REFERENCES books(id)
            )
        """)
        cursor.execute("SELECT * FROM users WHERE name='admin'")
        if not cursor.fetchone():
            cursor.execute("""
                INSERT INTO users (name, serial_number, password, is_admin)
                VALUES (%s, %s, %s, %s)
            """, ("admin", "0000", "admin", True))
        self.db.commit()
        cursor.close()

    def closeEvent(self, event):
        if hasattr(self, 'db') and self.db.is_connected():
            self.db.close()
        event.accept()

class LoginPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Logo
        logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path).scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label = QLabel()
            logo_label.setPixmap(pixmap)
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)
        else:
            logo_label = QLabel("CBCA Library")
            logo_label.setFont(QFont("Helvetica, Arial, sans-serif", 40, QFont.Bold))
            logo_label.setAlignment(Qt.AlignCenter)
            layout.addWidget(logo_label)

        # Login card
        frame = QFrame()
        frame.setObjectName("loginFrame")
        frame.setFixedSize(500, 450)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Sign In")
        title.setStyleSheet("font-size: 32pt; font-weight: bold; color: #1f2937; border: none;")
        frame_layout.addWidget(title)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.setMinimumHeight(50)
        frame_layout.addWidget(self.username)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("Password")
        self.password.setMinimumHeight(50)
        frame_layout.addWidget(self.password)

        login_btn = QPushButton("Login")
        login_btn.setMinimumHeight(50)
        login_btn.clicked.connect(self.login)
        frame_layout.addWidget(login_btn)

        layout.addStretch()
        layout.addWidget(frame, alignment=Qt.AlignCenter)
        layout.addStretch()

    def login(self):
        try:
            username = self.username.text().strip()
            password = self.password.text().strip()

            if not username or not password:
                QMessageBox.critical(self, "Error", "Please enter both username and password")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT * FROM users WHERE name=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            cursor.close()

            if user:
                self.controller.sidebar.setVisible(True)
                self.controller.show_page("HomePage")
                self.username.clear()
                self.password.clear()
            else:
                QMessageBox.critical(self, "Error", "Invalid credentials")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Login failed: {e}")

class HomePage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Title
        title = QLabel("Library Dashboard")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # Cards
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)

        buttons = [
            ("👤 Manage Users", lambda: self.controller.show_page("CreateUserPage")),
            ("📚 Manage Books", lambda: self.controller.show_page("BookAuthorPage")),
            ("🔄 Transactions", lambda: self.controller.show_page("AssignReturnPage")),
            ("📊 Reports", lambda: self.controller.show_page("ReportPage"))
        ]

        for text, command in buttons:
            card = QFrame()
            card_layout = QVBoxLayout(card)
            card_layout.setAlignment(Qt.AlignCenter)
            card_layout.setSpacing(15)

            icon = QLabel(text.split()[0])
            icon.setFont(QFont("Helvetica, Arial, sans-serif", 32))
            card_layout.addWidget(icon)

            label = QLabel(text.split()[1])
            label.setFont(QFont("Helvetica, Arial, sans-serif", 18, QFont.Bold))
            card_layout.addWidget(label)

            btn = QPushButton("Go")
            btn.setFixedWidth(150)
            btn.setMinimumHeight(50)
            btn.clicked.connect(command)
            card_layout.addWidget(btn)

            cards_layout.addWidget(card)

        layout.addLayout(cards_layout)
        layout.addStretch()

    def refresh(self):
        pass

class CreateUserPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_page = 1
        self.users_per_page = 10
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Manage Users")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        create_btn = QPushButton("New User")
        create_btn.setFixedWidth(180)
        create_btn.setMinimumHeight(50)
        create_btn.clicked.connect(self.show_create_form)
        header_layout.addWidget(create_btn)

        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.setMinimumHeight(50)
        self.search_input.textChanged.connect(self.search_users)
        layout.addWidget(self.search_input)

        # Users table
        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Full Name', 'Serial Number', 'Date of Birth'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Pagination
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(50)
        prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(prev_btn)

        self.page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.page_label)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(50)
        next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_btn)

        layout.addWidget(pagination_frame)

        self.refresh()

    def refresh(self):
        self.load_users()

    def load_users(self, search_term=""):
        try:
            self.table.setRowCount(0)
            cursor = self.controller.db.cursor()
            query = "SELECT name, serial_number, dob FROM users"
            params = ()
            if search_term:
                query += " WHERE name LIKE %s OR serial_number LIKE %s"
                params = (f"%{search_term}%", f"%{search_term}%")

            cursor.execute(query, params)
            users = cursor.fetchall()
            cursor.close()

            start = (self.current_page - 1) * self.users_per_page
            end = start + self.users_per_page
            self.table.setRowCount(min(self.users_per_page, len(users[start:end])))

            for row_idx, user in enumerate(users[start:end]):
                self.table.setItem(row_idx, 0, QTableWidgetItem(user[0]))
                self.table.setItem(row_idx, 1, QTableWidgetItem(user[1]))
                dob = user[2].strftime('%Y-%m-%d') if user[2] else ''
                self.table.setItem(row_idx, 2, QTableWidgetItem(dob))

            self.page_label.setText(f"Page {self.current_page}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load users: {e}")

    def search_users(self):
        self.current_page = 1
        self.load_users(self.search_input.text())

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_users(self.search_input.text())

    def next_page(self):
        try:
            cursor = self.controller.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM users")
            total_users = cursor.fetchone()[0]
            cursor.close()
            if self.current_page * self.users_per_page < total_users:
                self.current_page += 1
                self.load_users(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {e}")

    def show_create_form(self):
        dialog = QWidget()
        dialog.setWindowTitle("Create User")
        dialog.setFixedSize(500, 500)
        dialog.setStyleSheet("background-color: #f0f2f5;")

        layout = QVBoxLayout(dialog)
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Create New User")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        frame_layout.addWidget(title)

        name = QLineEdit()
        name.setPlaceholderText("Full Name")
        name.setMinimumHeight(50)
        frame_layout.addWidget(name)

        serial = QLineEdit()
        serial.setPlaceholderText("Serial Number")
        serial.setMinimumHeight(50)
        frame_layout.addWidget(serial)

        dob = QDateEdit()
        dob.setCalendarPopup(True)
        dob.setDisplayFormat("yyyy-MM-dd")
        dob.setMinimumHeight(50)
        frame_layout.addWidget(dob)

        submit_btn = QPushButton("Create User")
        submit_btn.setMinimumHeight(50)
        submit_btn.clicked.connect(lambda: self.submit_user(name.text(), serial.text(), dob.date().toPyDate(), dialog))
        frame_layout.addWidget(submit_btn)

        layout.addWidget(frame)
        dialog.show()

    def submit_user(self, name, serial, dob, dialog):
        try:
            if not name or not serial:
                QMessageBox.critical(self, "Error", "Name and serial number are required")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("""
                INSERT INTO users (name, serial_number, dob, password)
                VALUES (%s, %s, %s, %s)
            """, (name, serial, dob, str(uuid.uuid4())[:8]))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "User created successfully")
            self.refresh()
            dialog.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

class BookAuthorPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.current_page = 1
        self.books_per_page = 10
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Manage Books")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        view_authors_btn = QPushButton("View Authors")
        view_authors_btn.setFixedWidth(200)
        view_authors_btn.setMinimumHeight(50)
        view_authors_btn.clicked.connect(self.show_view_authors)
        header_layout.addWidget(view_authors_btn)

        add_author_btn = QPushButton("Add New Author")
        add_author_btn.setFixedWidth(200)
        add_author_btn.setMinimumHeight(50)
        add_author_btn.clicked.connect(self.show_add_author_form)
        header_layout.addWidget(add_author_btn)

        add_book_btn = QPushButton("Add New Book")
        add_book_btn.setFixedWidth(200)
        add_book_btn.setMinimumHeight(50)
        add_book_btn.clicked.connect(self.show_add_book_form)
        header_layout.addWidget(add_book_btn)

        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books...")
        self.search_input.setMinimumHeight(50)
        self.search_input.textChanged.connect(self.search_books)
        layout.addWidget(self.search_input)

        # Books table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Serial', 'Author', 'Book Title', 'Book Serial', 'Occupied By'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Pagination
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(50)
        prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(prev_btn)

        self.page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.page_label)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(50)
        next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_btn)

        layout.addWidget(pagination_frame)

        self.refresh()

    def refresh(self):
        self.load_books()

    def load_books(self, search_term=""):
        try:
            self.table.setRowCount(0)
            cursor = self.controller.db.cursor()
            query = """
                SELECT b.serial_number, a.name, b.title, b.serial_number, 
                       COALESCE(u.name, 'Library') as occupied_by
                FROM books b
                JOIN authors a ON b.author_id = a.id
                LEFT JOIN transactions t ON b.id = t.book_id AND t.return_date IS NULL
                LEFT JOIN users u ON t.user_id = u.id
            """
            params = ()
            if search_term:
                query += " WHERE b.title LIKE %s OR a.name LIKE %s"
                params = (f"%{search_term}%", f"%{search_term}%")

            cursor.execute(query, params)
            books = cursor.fetchall()
            cursor.close()

            start = (self.current_page - 1) * self.books_per_page
            end = start + self.books_per_page
            self.table.setRowCount(min(self.books_per_page, len(books[start:end])))

            for row_idx, book in enumerate(books[start:end]):
                for col_idx, value in enumerate(book):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))

            self.page_label.setText(f"Page {self.current_page}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load books: {e}")

    def search_books(self):
        self.current_page = 1
        self.load_books(self.search_input.text())

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_books(self.search_input.text())

    def next_page(self):
        try:
            cursor = self.controller.db.cursor()
            query = "SELECT COUNT(*) FROM books"
            if self.search_input.text():
                query += " WHERE title LIKE %s OR author_id IN (SELECT id FROM authors WHERE name LIKE %s)"
                cursor.execute(query, (f"%{self.search_input.text()}%", f"%{self.search_input.text()}%"))
            else:
                cursor.execute(query)
            total_books = cursor.fetchone()[0]
            cursor.close()
            if self.current_page * self.books_per_page < total_books:
                self.current_page += 1
                self.load_books(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {e}")

    def show_view_authors(self):
        dialog = QWidget()
        dialog.setWindowTitle("View Authors")
        dialog.setFixedSize(600, 600)
        dialog.setStyleSheet("background-color: #f0f2f5;")

        layout = QVBoxLayout(dialog)
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Authors List")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        frame_layout.addWidget(title)

        # Authors table
        self.authors_table = QTableWidget()
        self.authors_table.setColumnCount(2)
        self.authors_table.setHorizontalHeaderLabels(['Author Name', 'Details'])
        self.authors_table.horizontalHeader().setStretchLastSection(True)
        self.authors_table.setAlternatingRowColors(True)
        frame_layout.addWidget(self.authors_table)

        # Pagination
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(50)
        prev_btn.clicked.connect(lambda: self.prev_author_page(dialog))
        pagination_layout.addWidget(prev_btn)

        self.author_page_label = QLabel("Page 1")
        pagination_layout.addWidget(self.author_page_label)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(50)
        next_btn.clicked.connect(lambda: self.next_author_page(dialog))
        pagination_layout.addWidget(next_btn)

        frame_layout.addWidget(pagination_frame)

        layout.addWidget(frame)
        self.current_author_page = 1
        self.authors_per_page = 10
        self.load_authors(dialog)
        dialog.show()

    def load_authors(self, dialog):
        try:
            self.authors_table.setRowCount(0)
            cursor = self.controller.db.cursor()
            cursor.execute("SELECT name, details FROM authors")
            authors = cursor.fetchall()
            cursor.close()

            start = (self.current_author_page - 1) * self.authors_per_page
            end = start + self.authors_per_page
            self.authors_table.setRowCount(min(self.authors_per_page, len(authors[start:end])))

            for row_idx, author in enumerate(authors[start:end]):
                self.authors_table.setItem(row_idx, 0, QTableWidgetItem(author[0]))
                self.authors_table.setItem(row_idx, 1, QTableWidgetItem(author[1] if author[1] else ''))

            self.author_page_label.setText(f"Page {self.current_author_page}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load authors: {e}")

    def prev_author_page(self, dialog):
        if self.current_author_page > 1:
            self.current_author_page -= 1
            self.load_authors(dialog)

    def next_author_page(self, dialog):
        try:
            cursor = self.controller.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM authors")
            total_authors = cursor.fetchone()[0]
            cursor.close()
            if self.current_author_page * self.authors_per_page < total_authors:
                self.current_author_page += 1
                self.load_authors(dialog)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {e}")

    def show_add_author_form(self):
        dialog = QWidget()
        dialog.setWindowTitle("Add Author")
        dialog.setFixedSize(500, 550)
        dialog.setStyleSheet("background-color: #f0f2f5;")

        layout = QVBoxLayout(dialog)
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Add New Author")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        frame_layout.addWidget(title)

        self.author_name = QLineEdit()
        self.author_name.setPlaceholderText("Author Name")
        self.author_name.setMinimumHeight(50)
        frame_layout.addWidget(self.author_name)

        self.author_details = QTextEdit()
        self.author_details.setPlaceholderText("Author Details (e.g., bio, nationality)")
        self.author_details.setMinimumHeight(120)
        frame_layout.addWidget(self.author_details)

        add_author_btn = QPushButton("Add Author")
        add_author_btn.setMinimumHeight(50)
        add_author_btn.clicked.connect(lambda: self.add_author(dialog))
        frame_layout.addWidget(add_author_btn)

        layout.addWidget(frame)
        dialog.show()

    def show_add_book_form(self):
        dialog = QWidget()
        dialog.setWindowTitle("Add Book")
        dialog.setFixedSize(500, 500)
        dialog.setStyleSheet("background-color: #f0f2f5;")

        layout = QVBoxLayout(dialog)
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("Add New Book")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        frame_layout.addWidget(title)

        self.author_dropdown = QComboBox()
        self.author_dropdown.setMinimumHeight(50)
        self.refresh_authors()
        frame_layout.addWidget(self.author_dropdown)

        self.book_title = QLineEdit()
        self.book_title.setPlaceholderText("Book Title")
        self.book_title.setMinimumHeight(50)
        frame_layout.addWidget(self.book_title)

        self.book_serial = QLineEdit()
        self.book_serial.setPlaceholderText("Book Serial")
        self.book_serial.setMinimumHeight(50)
        frame_layout.addWidget(self.book_serial)

        add_book_btn = QPushButton("Add Book")
        add_book_btn.setMinimumHeight(50)
        add_book_btn.clicked.connect(lambda: self.add_book(dialog))
        frame_layout.addWidget(add_book_btn)

        layout.addWidget(frame)
        dialog.show()

    def refresh_authors(self):
        try:
            self.author_dropdown.clear()
            cursor = self.controller.db.cursor()
            cursor.execute("SELECT name FROM authors")
            authors = [row[0] for row in cursor.fetchall()]
            self.author_dropdown.addItems(authors)
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh authors: {e}")

    def add_author(self, dialog):
        try:
            name = self.author_name.text().strip()
            details = self.author_details.toPlainText().strip()

            if not name:
                QMessageBox.critical(self, "Error", "Author name is required")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("INSERT INTO authors (name, details) VALUES (%s, %s)", (name, details))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Author added successfully")
            self.author_name.clear()
            self.author_details.clear()
            self.refresh_authors()
            dialog.close()
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

    def add_book(self, dialog):
        try:
            author_name = self.author_dropdown.currentText()
            title = self.book_title.text().strip()
            serial = self.book_serial.text().strip()

            if not all([author_name, title, serial]):
                QMessageBox.critical(self, "Error", "All fields are required")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT id FROM authors WHERE name=%s", (author_name,))
            result = cursor.fetchone()
            if not result:
                QMessageBox.critical(self, "Error", "Author not found")
                cursor.close()
                return
            author_id = result[0]

            cursor.execute("""
                INSERT INTO books (serial_number, title, author_id)
                VALUES (%s, %s, %s)
            """, (serial, title, author_id))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Book added successfully")
            self.book_title.clear()
            self.book_serial.clear()
            self.author_dropdown.setCurrentIndex(-1)
            dialog.close()
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

class AssignReturnPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Header
        title = QLabel("Book Transactions")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(title)

        # Split layout
        split_layout = QHBoxLayout()
        split_layout.setSpacing(30)

        # Assign frame
        assign_frame = QFrame()
        assign_layout = QVBoxLayout(assign_frame)
        assign_layout.setSpacing(20)
        assign_layout.setContentsMargins(30, 30, 30, 30)

        assign_title = QLabel("Assign Book")
        assign_title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
        assign_title.setStyleSheet("color: #1f2937; border: none;")
        assign_layout.addWidget(assign_title)

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type to select user...")
        self.user_input.setMinimumHeight(50)
        assign_layout.addWidget(self.user_input)

        self.book_input = QLineEdit()
        self.book_input.setPlaceholderText("Type to select book...")
        self.book_input.setMinimumHeight(50)
        assign_layout.addWidget(self.book_input)

        self.issue_date = QDateEdit()
        self.issue_date.setCalendarPopup(True)
        self.issue_date.setDisplayFormat("yyyy-MM-dd")
        self.issue_date.setMinimumHeight(50)
        assign_layout.addWidget(self.issue_date)

        assign_btn = QPushButton("Assign Book")
        assign_btn.setMinimumHeight(50)
        assign_btn.clicked.connect(self.assign_book)
        assign_layout.addWidget(assign_btn)

        split_layout.addWidget(assign_frame)

        # Return frame
        return_frame = QFrame()
        return_layout = QVBoxLayout(return_frame)
        return_layout.setSpacing(20)
        return_layout.setContentsMargins(30, 30, 30, 30)

        return_title = QLabel("Return Book")
        return_title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
        return_title.setStyleSheet("color: #1f2937; border: none;")
        return_layout.addWidget(return_title)

        self.return_user_input = QLineEdit()
        self.return_user_input.setPlaceholderText("Type to select user...")
        self.return_user_input.setMinimumHeight(50)
        self.return_user_input.textChanged.connect(self.update_return_books)
        return_layout.addWidget(self.return_user_input)

        self.return_book_input = QLineEdit()
        self.return_book_input.setPlaceholderText("Type to select book...")
        self.return_book_input.setMinimumHeight(50)
        return_layout.addWidget(self.return_book_input)

        self.return_date = QDateEdit()
        self.return_date.setCalendarPopup(True)
        self.return_date.setDisplayFormat("yyyy-MM-dd")
        self.return_date.setMinimumHeight(50)
        return_layout.addWidget(self.return_date)

        return_btn = QPushButton("Return Book")
        return_btn.setMinimumHeight(50)
        return_btn.clicked.connect(self.return_book)
        return_layout.addWidget(return_btn)

        split_layout.addWidget(return_frame)
        layout.addLayout(split_layout)
        layout.addStretch()

        self.refresh()

    def refresh(self):
        self.setup_completers()
        self.update_return_books()
        self.user_input.clear()
        self.book_input.clear()
        self.return_user_input.clear()
        self.return_book_input.clear()
        self.issue_date.setDate(QDate.currentDate())
        self.return_date.setDate(QDate.currentDate())

    def setup_completers(self):
        try:
            cursor = self.controller.db.cursor()
            cursor.execute("SELECT name FROM users")
            users = [row[0] for row in cursor.fetchall()]
            cursor.execute("SELECT title FROM books")
            books = [row[0] for row in cursor.fetchall()]
            cursor.close()

            user_model = QStringListModel(users)
            book_model = QStringListModel(books)

            user_completer = QCompleter(user_model, self)
            user_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.user_input.setCompleter(user_completer)
            self.return_user_input.setCompleter(user_completer)

            book_completer = QCompleter(book_model, self)
            book_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.book_input.setCompleter(book_completer)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to setup completers: {e}")

    def update_return_books(self):
        try:
            user_name = self.return_user_input.text().strip()
            if not user_name:
                self.return_book_input.clear()
                self.return_book_input.setCompleter(None)
                return

            cursor = self.controller.db.cursor()
            cursor.execute("""
                SELECT b.title 
                FROM books b
                JOIN transactions t ON b.id = t.book_id
                JOIN users u ON t.user_id = u.id
                WHERE u.name = %s AND t.return_date IS NULL
            """, (user_name,))
            books = [row[0] for row in cursor.fetchall()]
            cursor.close()

            book_model = QStringListModel(books)
            book_completer = QCompleter(book_model, self)
            book_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self.return_book_input.setCompleter(book_completer)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh return books: {e}")

    def assign_book(self):
        try:
            user_name = self.user_input.text().strip()
            book_title = self.book_input.text().strip()
            issue_date = self.issue_date.date().toPyDate()

            if not user_name or not book_title:
                QMessageBox.critical(self, "Error", "Please select both user and book")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT id FROM users WHERE name=%s", (user_name,))
            user_result = cursor.fetchone()
            if not user_result:
                QMessageBox.critical(self, "Error", "User not found")
                cursor.close()
                return
            user_id = user_result[0]

            cursor.execute("SELECT id FROM books WHERE title=%s", (book_title,))
            book_result = cursor.fetchone()
            if not book_result:
                QMessageBox.critical(self, "Error", "Book not found")
                cursor.close()
                return
            book_id = book_result[0]

            cursor.execute("""
                INSERT INTO transactions (user_id, book_id, issue_date)
                VALUES (%s, %s, %s)
            """, (user_id, book_id, issue_date))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Book assigned")
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to assign book: {e}")

    def return_book(self):
        try:
            user_name = self.return_user_input.text().strip()
            book_title = self.return_book_input.text().strip()
            return_date = self.return_date.date().toPyDate()

            if not user_name or not book_title:
                QMessageBox.critical(self, "Error", "Please select both user and book")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT id FROM users WHERE name=%s", (user_name,))
            user_result = cursor.fetchone()
            if not user_result:
                QMessageBox.critical(self, "Error", "User not found")
                cursor.close()
                return
            user_id = user_result[0]

            cursor.execute("SELECT id FROM books WHERE title=%s", (book_title,))
            book_result = cursor.fetchone()
            if not book_result:
                QMessageBox.critical(self, "Error", "Book not found")
                cursor.close()
                return
            book_id = book_result[0]

            cursor.execute("""
                UPDATE transactions 
                SET return_date=%s 
                WHERE user_id=%s AND book_id=%s AND return_date IS NULL
            """, (return_date, user_id, book_id))
            if cursor.rowcount == 0:
                QMessageBox.critical(self, "Error", "No active transaction found for this book and user")
                cursor.close()
                return
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Book returned")
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to return book: {e}")

class AdminPanelPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Header
        title = QLabel("Admin Panel")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        layout.addWidget(title)

        # Form
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        self.user_dropdown = QComboBox()
        self.user_dropdown.setMinimumHeight(50)
        frame_layout.addWidget(self.user_dropdown)

        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.Password)
        self.password.setPlaceholderText("New Password")
        self.password.setMinimumHeight(50)
        frame_layout.addWidget(self.password)

        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setPlaceholderText("Confirm Password")
        self.confirm_password.setMinimumHeight(50)
        frame_layout.addWidget(self.confirm_password)

        make_admin_btn = QPushButton("Grant Admin Access")
        make_admin_btn.setMinimumHeight(50)
        make_admin_btn.clicked.connect(self.make_admin)
        frame_layout.addWidget(make_admin_btn)

        layout.addWidget(frame)
        layout.addStretch()

        self.refresh_users()

    def refresh(self):
        self.refresh_users()
        self.user_dropdown.setCurrentIndex(-1)
        self.password.clear()
        self.confirm_password.clear()

    def refresh_users(self):
        try:
            self.user_dropdown.clear()
            cursor = self.controller.db.cursor()
            cursor.execute("SELECT name FROM users WHERE is_admin=FALSE")
            users = [row[0] for row in cursor.fetchall()]
            self.user_dropdown.addItems(users)
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh users: {e}")

    def make_admin(self):
        try:
            user_name = self.user_dropdown.currentText()
            password = self.password.text().strip()
            confirm_password = self.confirm_password.text().strip()

            if not user_name:
                QMessageBox.critical(self, "Error", "Please select a user")
                return
            if not password or password != confirm_password:
                QMessageBox.critical(self, "Error", "Passwords don't match or are empty")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_admin=TRUE, password=%s 
                WHERE name=%s
            """, (password, user_name))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Admin privileges granted")
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to grant admin access: {e}")

class ReportPage(QWidget):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        layout = QVBoxLayout(self)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(30)

        # Header
        header_layout = QHBoxLayout()
        title = QLabel("Library Reports")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        generate_btn = QPushButton("Generate")
        generate_btn.setFixedWidth(180)
        generate_btn.setMinimumHeight(50)
        generate_btn.clicked.connect(self.generate_report)
        header_layout.addWidget(generate_btn)

        export_btn = QPushButton("Export to Excel")
        export_btn.setFixedWidth(180)
        export_btn.setMinimumHeight(50)
        export_btn.clicked.connect(self.export_to_excel)
        header_layout.addWidget(export_btn)

        layout.addLayout(header_layout)

        # Report options
        options_frame = QFrame()
        options_layout = QVBoxLayout(options_frame)
        options_layout.setSpacing(15)
        options_layout.setContentsMargins(30, 30, 30, 30)

        self.all_books = QRadioButton("All Books")
        self.all_books.setChecked(True)
        options_layout.addWidget(self.all_books)

        self.issued_books = QRadioButton("Currently Issued Books")
        options_layout.addWidget(self.issued_books)

        self.transaction_history = QRadioButton("Transaction History")
        options_layout.addWidget(self.transaction_history)

        layout.addWidget(options_frame)

        # Report output
        self.report_text = QTextEdit()
        layout.addWidget(self.report_text)

        self.refresh()

    def refresh(self):
        self.report_text.clear()
        self.all_books.setChecked(True)

    def generate_report(self):
        try:
            cursor = self.controller.db.cursor(dictionary=True)
            if self.all_books.isChecked():
                report_type = "all_books"
            elif self.issued_books.isChecked():
                report_type = "issued_books"
            else:
                report_type = "transaction_history"

            if report_type == "all_books":
                query = """
                    SELECT b.serial_number, b.title, a.name as author, 
                           u.name as user, t.issue_date, t.return_date
                    FROM books b
                    LEFT JOIN authors a ON b.author_id = a.id
                    LEFT JOIN transactions t ON b.id = t.book_id
                    LEFT JOIN users u ON t.user_id = u.id
                    ORDER BY b.title
                """
            elif report_type == "issued_books":
                query = """
                    SELECT b.serial_number, b.title, a.name as author, 
                           u.name as user, t.issue_date
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    JOIN transactions t ON b.id = t.book_id
                    JOIN users u ON t.user_id = u.id
                    WHERE t.return_date IS NULL
                    ORDER BY t.issue_date
                """
            else:
                query = """
                    SELECT b.serial_number, b.title, a.name as author, 
                           u.name as user, t.issue_date, t.return_date
                    FROM books b
                    JOIN authors a ON b.author_id = a.id
                    JOIN transactions t ON b.id = t.book_id
                    JOIN users u ON t.user_id = u.id
                    ORDER BY t.issue_date DESC
                """

            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()

            if not results:
                self.report_text.setText("No data found for the selected report type.")
                return

            self.report_df = pd.DataFrame(results)
            self.report_text.setText(self.report_df.to_string(index=False))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to generate report: {e}")

    def export_to_excel(self):
        try:
            if not hasattr(self, 'report_df') or self.report_df.empty:
                QMessageBox.warning(self, "Warning", "No report data to export. Generate a report first.")
                return

            file_path = QFileDialog.getSaveFileName(self, "Save report as", "", "Excel files (*.xlsx);;All files (*.*)")[0]
            if file_path:
                if not file_path.endswith('.xlsx'):
                    file_path += '.xlsx'
                self.report_df.to_excel(file_path, index=False, engine='openpyxl')
                QMessageBox.information(self, "Success", f"Report successfully exported to {file_path}")
        except ImportError:
            QMessageBox.critical(self, "Error",
                                 "Excel export engine 'openpyxl' not installed. Please install it using 'pip install openpyxl'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to export report: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = LibraryManagementSystem()
    window.show()
    sys.exit(app.exec_())