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
                             QScrollArea, QDialog)
from PyQt5.QtGui import QPixmap, QFont, QImage, QIcon
from PyQt5.QtCore import Qt, QDate, QSize

class LibraryManagementSystem(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CBCA Library Management System")
        self.setGeometry(100, 100, 1200, 800)

        # Set global font with increased size
        app = QApplication.instance()
        app.setFont(QFont("Helvetica, Arial, sans-serif", 15))

        # Updated stylesheet with explicit button styling for dialogs
        self.setStyleSheet("""
            QMainWindow, QDialog {
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
            QDialog QPushButton, QFrame QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6366f1, stop:1 #4f46e5) !important;
                color: white !important;
                border-radius: 5px;
                padding: 12px;
                font-size: 16pt;
                border: none;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #818cf8, stop:1 #6366f1);
            }
            QPushButton#refreshButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4CAF50, stop:1 #45a049);
                color: white;
                border-radius: 5px;
                padding: 12px;
                font-size: 16pt;
                border: none;
            }
            QPushButton#refreshButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #66bb6a, stop:1 #4CAF50);
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
                selection-background-color: green;
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
                name VARCHAR(255),
                serial_number VARCHAR(255) UNIQUE,
                phone_number VARCHAR(20),
                address TEXT,
                password VARCHAR(255),
                is_admin BOOLEAN DEFAULT FALSE
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS authors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) UNIQUE,
                details TEXT
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INT AUTO_INCREMENT PRIMARY KEY,
                serial_number VARCHAR(255) UNIQUE,
                title VARCHAR(255),
                author_id INT,
                location TEXT,
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

        # Header with Refresh Button
        header_layout = QHBoxLayout()
        title = QLabel("Library Dashboard")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setFixedWidth(180)
        refresh_btn.setMinimumHeight(50)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

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
        pass  # No data to refresh on HomePage, but included for consistency

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

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setFixedWidth(180)
        refresh_btn.setMinimumHeight(50)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search users...")
        self.search_input.setMinimumHeight(50)
        self.search_input.textChanged.connect(self.search_users)
        layout.addWidget(self.search_input)

        # Users table
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(['Full Name', 'Serial Number', 'Phone Number', 'Address', 'Actions'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.show_update_user_form)
        layout.addWidget(self.table)

        # Pagination
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(50)
        prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(prev_btn)

        self.page_label = QLabel("Page 1 of 1")
        pagination_layout.addWidget(self.page_label)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(50)
        next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_btn)

        layout.addWidget(pagination_frame)

        self.refresh()

    def refresh(self):
        self.current_page = 1
        self.search_input.clear()
        self.load_users()

    def load_users(self, search_term=""):
        try:
            self.table.setRowCount(0)
            cursor = self.controller.db.cursor()
            query = "SELECT name, serial_number, phone_number, address FROM users"
            params = ()
            if search_term:
                query += " WHERE name LIKE %s OR serial_number LIKE %s"
                params = (f"%{search_term}%", f"%{search_term}%")

            cursor.execute(query, params)
            users = cursor.fetchall()

            # Calculate total pages
            total_users = len(users)
            total_pages = max(1, (total_users + self.users_per_page - 1) // self.users_per_page)

            start = (self.current_page - 1) * self.users_per_page
            end = start + self.users_per_page
            self.table.setRowCount(min(self.users_per_page, len(users[start:end])))

            for row_idx, user in enumerate(users[start:end]):
                for col_idx, value in enumerate(user):
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value else ''))
                update_btn = QPushButton("Update")
                update_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #4CAF50;
                        color: white;
                        border-radius: 5px;
                        padding: 8px;
                        font-size: 14pt;
                        min-width: 100px;
                    }
                    QPushButton:hover {
                        background-color: #45a049;
                    }
                """)
                update_btn.clicked.connect(lambda _, r=row_idx: self.show_update_user_form(r, 0))
                self.table.setCellWidget(row_idx, 4, update_btn)

            self.page_label.setText(f"Page {self.current_page} of {total_pages}")
            cursor.close()
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
            query = "SELECT COUNT(*) FROM users"
            if self.search_input.text():
                query += " WHERE name LIKE %s OR serial_number LIKE %s"
                cursor.execute(query, (f"%{self.search_input.text()}%", f"%{self.search_input.text()}%"))
            else:
                cursor.execute(query)
            total_users = cursor.fetchone()[0]
            cursor.close()
            total_pages = max(1, (total_users + self.users_per_page - 1) // self.users_per_page)
            if self.current_page < total_pages:
                self.current_page += 1
                self.load_users(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {e}")

    def show_create_form(self):
        dialog = QDialog(self.controller)
        dialog.setWindowTitle("Create User")
        dialog.setFixedSize(500, 600)
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

        phone = QLineEdit()
        phone.setPlaceholderText("Phone Number")
        phone.setMinimumHeight(50)
        frame_layout.addWidget(phone)

        address = QTextEdit()
        address.setPlaceholderText("Address")
        address.setMinimumHeight(120)
        frame_layout.addWidget(address)

        submit_btn = QPushButton("Create User")
        submit_btn.setMinimumHeight(50)
        submit_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font: 14pt "Helvetica";
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        submit_btn.clicked.connect(lambda: self.submit_user(name.text(), serial.text(), phone.text(), address.toPlainText(), dialog))
        frame_layout.addWidget(submit_btn)

        layout.addWidget(frame)
        dialog.exec_()

    def show_update_user_form(self, row, col):
        try:
            serial_number = self.table.item(row, 1).text() if self.table.item(row, 1) else ""
            if not serial_number:
                QMessageBox.critical(self, "Error", "No serial number found for this user")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT name, serial_number, phone_number, address FROM users WHERE serial_number=%s", (serial_number,))
            user = cursor.fetchone()
            cursor.close()

            if not user:
                QMessageBox.critical(self, "Error", "User not found")
                return

            dialog = QDialog(self.controller)
            dialog.setWindowTitle("Update User")
            dialog.setFixedSize(500, 600)
            dialog.setStyleSheet("background-color: #f0f2f5;")

            layout = QVBoxLayout(dialog)
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setSpacing(20)
            frame_layout.setContentsMargins(30, 30, 30, 30)

            title = QLabel("Update User")
            title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
            title.setStyleSheet("color: #1f2937; border: none;")
            frame_layout.addWidget(title)

            name = QLineEdit(user[0] or "")
            name.setPlaceholderText("Full Name")
            name.setMinimumHeight(50)
            frame_layout.addWidget(name)

            serial = QLineEdit(user[1] or "")
            serial.setPlaceholderText("Serial Number")
            serial.setMinimumHeight(50)
            frame_layout.addWidget(serial)

            phone = QLineEdit(user[2] or "")
            phone.setPlaceholderText("Phone Number")
            phone.setMinimumHeight(50)
            frame_layout.addWidget(phone)

            address = QTextEdit(user[3] or "")
            address.setPlaceholderText("Address")
            address.setMinimumHeight(120)
            frame_layout.addWidget(address)

            update_btn = QPushButton("Update User")
            update_btn.setMinimumHeight(50)
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font: 14pt "Helvetica";
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            update_btn.clicked.connect(lambda: self.update_user(user[1], name.text(), serial.text(), phone.text(), address.toPlainText(), dialog))
            frame_layout.addWidget(update_btn)

            layout.addWidget(frame)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load user data: {e}")

    def submit_user(self, name, serial, phone, address, dialog):
        try:
            if not name or not serial:
                QMessageBox.critical(self, "Error", "Name and serial number are required")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT id FROM users WHERE serial_number=%s", (serial,))
            if cursor.fetchone():
                cursor.close()
                QMessageBox.critical(self, "Error", "Serial number already exists")
                return

            cursor.execute("""
                INSERT INTO users (name, serial_number, phone_number, address, password)
                VALUES (%s, %s, %s, %s, %s)
            """, (name or None, serial, phone or None, address or None, str(uuid.uuid4())[:8]))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "User created successfully")
            self.refresh()
            dialog.accept()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

    def update_user(self, old_serial, name, serial, phone, address, dialog):
        try:
            if not name or not serial:
                QMessageBox.critical(self, "Error", "Name and serial number are required")
                return

            cursor = self.controller.db.cursor()
            if serial != old_serial:
                cursor.execute("SELECT id FROM users WHERE serial_number=%s", (serial,))
                if cursor.fetchone():
                    cursor.close()
                    QMessageBox.critical(self, "Error", "Serial number already exists")
                    return

            cursor.execute("""
                UPDATE users 
                SET name=%s, serial_number=%s, phone_number=%s, address=%s
                WHERE serial_number=%s
            """, (name or None, serial, phone or None, address or None, old_serial))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "User updated successfully")
            self.refresh()
            dialog.accept()
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

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setFixedWidth(200)
        refresh_btn.setMinimumHeight(50)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Search bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search books...")
        self.search_input.setMinimumHeight(50)
        self.search_input.textChanged.connect(self.search_books)
        layout.addWidget(self.search_input)

        # Books table
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(['Serial', 'Author', 'Book Title', 'Book Serial', 'Occupied By', 'Location', 'Actions'])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellDoubleClicked.connect(self.show_update_book_form)
        layout.addWidget(self.table)

        # Pagination
        pagination_frame = QFrame()
        pagination_layout = QHBoxLayout(pagination_frame)
        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(50)
        prev_btn.clicked.connect(self.prev_page)
        pagination_layout.addWidget(prev_btn)

        self.page_label = QLabel("Page 1 of 1")
        pagination_layout.addWidget(self.page_label)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(50)
        next_btn.clicked.connect(self.next_page)
        pagination_layout.addWidget(next_btn)

        layout.addWidget(pagination_frame)

        self.refresh()

    def refresh(self):
        self.current_page = 1
        self.search_input.clear()
        self.load_books()

    def load_books(self, search_term=""):
        try:
            self.table.setRowCount(0)
            cursor = self.controller.db.cursor()
            query = """
                SELECT b.serial_number, a.name, b.title, b.serial_number, 
                       COALESCE(u.name, 'Library') as occupied_by,
                       COALESCE(u.address, b.location) as location,
                       b.id
                FROM books b
                JOIN authors a ON b.author_id = a.id
                LEFT JOIN transactions t ON b.id = t.book_id AND t.return_date IS NULL
                LEFT JOIN users u ON t.user_id = u.id
            """
            params = ""
            if search_term:
                query += " WHERE b.title LIKE %s OR a.name LIKE %s"
                params = (f"%{search_term}%", f"%{search_term}%")

            cursor.execute(query, params)
            books = cursor.fetchall()

            # Calculate total pages
            total_books = len(books)
            total_pages = max(1, (total_books + self.books_per_page - 1) // self.books_per_page)

            start = (self.current_page - 1) * self.books_per_page
            end = start + self.books_per_page
            self.table.setRowCount(min(self.books_per_page, len(books[start:end])))

            for row_idx, book in enumerate(books[start:end]):
                for col_idx, value in enumerate(book[:-1]):  # Exclude book_id from display
                    self.table.setItem(row_idx, col_idx, QTableWidgetItem(str(value) if value else ''))
                # Add Update button
                update_btn = QPushButton("Update")
                update_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #2196F3;
                        color: white;
                        border-radius: 5px;
                        padding: 8px;
                        font-size: 14pt;
                    }
                    QPushButton:hover {
                        background-color: #1976D2;
                    }
                """)
                update_btn.clicked.connect(lambda _, r=row_idx: self.show_update_book_form(r, 0))
                self.table.setCellWidget(row_idx, 6, update_btn)

            self.page_label.setText(f"Page {self.current_page} of {total_pages}")
            cursor.close()
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
            total_pages = max(1, (total_books + self.books_per_page - 1) // self.books_per_page)
            if self.current_page < total_pages:
                self.current_page += 1
                self.load_books(self.search_input.text())
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {e}")

    def show_view_authors(self):
        dialog = QDialog(self.controller)
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

        # Search bar
        self.author_search_input = QLineEdit()
        self.author_search_input.setPlaceholderText("Search authors...")
        self.author_search_input.setMinimumHeight(50)
        self.author_search_input.textChanged.connect(lambda: self.load_authors(dialog))
        frame_layout.addWidget(self.author_search_input)

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

        green_button_style = """
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font: 12pt "Helvetica";
                border-radius: 5px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """

        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(50)
        prev_btn.setStyleSheet(green_button_style)
        prev_btn.clicked.connect(lambda: self.prev_author_page(dialog))
        pagination_layout.addWidget(prev_btn)

        pagination_layout.addStretch(1)

        self.author_page_label = QLabel("Page 1 of 1")
        self.author_page_label.setStyleSheet("font: 12pt 'Helvetica'; color: #2c3e50;")
        self.author_page_label.setAlignment(Qt.AlignCenter)
        pagination_layout.addWidget(self.author_page_label)

        pagination_layout.addStretch(1)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(50)
        next_btn.setStyleSheet(green_button_style)
        next_btn.clicked.connect(lambda: self.next_author_page(dialog))
        pagination_layout.addWidget(next_btn)

        frame_layout.addWidget(pagination_frame)

        layout.addWidget(frame)
        self.current_author_page = 1
        self.authors_per_page = 10
        self.load_authors(dialog)
        dialog.exec_()

    def load_authors(self, dialog):
        try:
            self.authors_table.setRowCount(0)
            cursor = self.controller.db.cursor()
            query = "SELECT name, details FROM authors"
            params = ""
            search_term = self.author_search_input.text().strip()
            if search_term:
                query += " WHERE name LIKE %s"
                params = (f"%{search_term}%",)

            cursor.execute(query, params)
            authors = cursor.fetchall()

            # Calculate total pages
            total_authors = len(authors)
            total_pages = max(1, (total_authors + self.authors_per_page - 1) // self.authors_per_page)

            start = (self.current_author_page - 1) * self.authors_per_page
            end = start + self.authors_per_page
            self.authors_table.setRowCount(min(self.authors_per_page, len(authors[start:end])))

            for row_idx, author in enumerate(authors[start:end]):
                self.authors_table.setItem(row_idx, 0, QTableWidgetItem(author[0] if author[0] else ''))
                self.authors_table.setItem(row_idx, 1, QTableWidgetItem(author[1] if author[1] else ''))

            self.author_page_label.setText(f"Page {self.current_author_page} of {total_pages}")
            cursor.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load authors: {e}")

    def prev_author_page(self, dialog):
        if self.current_author_page > 1:
            self.current_author_page -= 1
            self.load_authors(dialog)

    def next_author_page(self, dialog):
        try:
            cursor = self.controller.db.cursor()
            query = "SELECT COUNT(*) FROM authors"
            if self.author_search_input.text():
                query += " WHERE name LIKE %s"
                cursor.execute(query, (f"%{self.author_search_input.text()}%",))
            else:
                cursor.execute(query)
            total_authors = cursor.fetchone()[0]
            cursor.close()
            total_pages = max(1, (total_authors + self.authors_per_page - 1) // self.authors_per_page)
            if self.current_author_page < total_pages:
                self.current_author_page += 1
                self.load_authors(dialog)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to navigate: {e}")

    def show_add_author_form(self):
        dialog = QDialog(self.controller)
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
        add_author_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font: 14pt "Helvetica";
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_author_btn.clicked.connect(lambda: self.add_author(dialog))
        frame_layout.addWidget(add_author_btn)

        layout.addWidget(frame)
        dialog.exec_()

    def show_add_book_form(self):
        dialog = QDialog(self.controller)
        dialog.setWindowTitle("Add Book")
        dialog.setFixedSize(500, 600)
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
        self.author_dropdown.setStyleSheet("""
            QComboBox {
                color: #000000;
                font: 14pt "Helvetica";
                padding: 6px;
            }
            QComboBox QAbstractItemView {
                font: 14pt "Helvetica";
                color: #000000;
                background-color: #ffffff;
                selection-background-color: #c8f7c5;
            }
        """)
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

        self.book_location = QLineEdit()
        self.book_location.setPlaceholderText("Book Location")
        self.book_location.setMinimumHeight(50)
        frame_layout.addWidget(self.book_location)

        add_book_btn = QPushButton("Add Book")
        add_book_btn.setMinimumHeight(50)
        add_book_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font: 14pt "Helvetica";
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        add_book_btn.clicked.connect(lambda: self.add_book(dialog))
        frame_layout.addWidget(add_book_btn)

        layout.addWidget(frame)
        dialog.exec_()

    def show_update_book_form(self, row, col):
        try:
            serial_number = self.table.item(row, 3).text() if self.table.item(row, 3) else ""
            if not serial_number:
                QMessageBox.critical(self, "Error", "No serial number found for this book")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("""
                SELECT b.title, b.serial_number, b.location, a.name, COALESCE(u.name, 'Library') as occupied_by
                FROM books b
                JOIN authors a ON b.author_id = a.id
                LEFT JOIN transactions t ON b.id = t.book_id AND t.return_date IS NULL
                LEFT JOIN users u ON t.user_id = u.id
                WHERE b.serial_number=%s
            """, (serial_number,))
            book = cursor.fetchone()
            cursor.close()

            if not book:
                QMessageBox.critical(self, "Error", "Book not found")
                return

            dialog = QDialog(self.controller)
            dialog.setWindowTitle("Update Book")
            dialog.setFixedSize(500, 600)
            dialog.setStyleSheet("background-color: #f0f2f5;")

            layout = QVBoxLayout(dialog)
            frame = QFrame()
            frame_layout = QVBoxLayout(frame)
            frame_layout.setSpacing(20)
            frame_layout.setContentsMargins(30, 30, 30, 30)

            title = QLabel("Update Book")
            title.setFont(QFont("Helvetica, Arial, sans-serif", 24, QFont.Bold))
            title.setStyleSheet("color: #1f2937; border: none;")
            frame_layout.addWidget(title)

            # Author (non-editable)
            author_label = QLabel(f"Author: {book[3]}")
            author_label.setStyleSheet("color: #1f2937; font-size: 14pt; border: none;")
            frame_layout.addWidget(author_label)

            # Book Title
            book_title = QLineEdit(book[0] or "")
            book_title.setPlaceholderText("Book Title")
            book_title.setMinimumHeight(50)
            frame_layout.addWidget(book_title)

            # Book Serial
            book_serial = QLineEdit(book[1] or "")
            book_serial.setPlaceholderText("Book Serial")
            book_serial.setMinimumHeight(50)
            frame_layout.addWidget(book_serial)

            # Book Location
            book_location = QLineEdit(book[2] or "")
            book_location.setPlaceholderText("Book Location")
            book_location.setMinimumHeight(50)
            if book[4] != "Library":
                book_location.setEnabled(False)
                book_location.setToolTip("Location cannot be edited while book is issued")
            frame_layout.addWidget(book_location)

            # Occupied By (non-editable)
            occupied_by_label = QLabel(f"Occupied By: {book[4]}")
            occupied_by_label.setStyleSheet("color: #1f2937; font-size: 14pt; border: none;")
            frame_layout.addWidget(occupied_by_label)

            update_btn = QPushButton("Update Book")
            update_btn.setMinimumHeight(50)
            update_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    font: 14pt "Helvetica";
                    border-radius: 5px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            update_btn.clicked.connect(lambda: self.update_book(book[1], book_title.text(), book_serial.text(), book_location.text(), book[4], dialog))
            frame_layout.addWidget(update_btn)

            layout.addWidget(frame)
            dialog.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load book data: {e}")

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
            cursor.execute("INSERT INTO authors (name, details) VALUES (%s, %s)", (name or None, details or None))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Author added successfully")
            self.author_name.clear()
            self.author_details.clear()
            self.refresh_authors()
            dialog.accept()
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

    def add_book(self, dialog):
        try:
            author_name = self.author_dropdown.currentText()
            title = self.book_title.text().strip()
            serial = self.book_serial.text().strip()
            location = self.book_location.text().strip()

            if not all([author_name, title, serial]):
                QMessageBox.critical(self, "Error", "Author, title, and serial are required")
                return

            cursor = self.controller.db.cursor()
            cursor.execute("SELECT id FROM authors WHERE name=%s", (author_name,))
            result = cursor.fetchone()
            if not result:
                QMessageBox.critical(self, "Error", "Author not found")
                cursor.close()
                return
            author_id = result[0]

            cursor.execute("SELECT id FROM books WHERE serial_number=%s", (serial,))
            if cursor.fetchone():
                cursor.close()
                QMessageBox.critical(self, "Error", "Book serial number already exists")
                return

            cursor.execute("""
                INSERT INTO books (serial_number, title, author_id, location)
                VALUES (%s, %s, %s, %s)
            """, (serial, title, author_id, location or None))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Book added successfully")
            self.book_title.clear()
            self.book_serial.clear()
            self.book_location.clear()
            self.author_dropdown.setCurrentIndex(-1)
            dialog.accept()
            self.refresh()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Error", f"Database error: {err}")

    def update_book(self, old_serial, title, serial, location, occupied_by, dialog):
        try:
            if not title or not serial:
                QMessageBox.critical(self, "Error", "Title and serial number are required")
                return

            if occupied_by != "Library" and location != self.table.item(self.table.currentRow(), 5).text():
                QMessageBox.critical(self, "Error", "Location can only be updated when book is in Library")
                return

            cursor = self.controller.db.cursor()
            if serial != old_serial:
                cursor.execute("SELECT id FROM books WHERE serial_number=%s", (serial,))
                if cursor.fetchone():
                    cursor.close()
                    QMessageBox.critical(self, "Error", "Book serial number already exists")
                    return

            cursor.execute("""
                UPDATE books 
                SET title=%s, serial_number=%s, location=%s
                WHERE serial_number=%s
            """, (title, serial, location or None, old_serial))
            self.controller.db.commit()
            cursor.close()
            QMessageBox.information(self, "Success", "Book updated successfully")
            self.refresh()
            dialog.accept()
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
        header_layout = QHBoxLayout()
        title = QLabel("Book Transactions")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setFixedWidth(180)
        refresh_btn.setMinimumHeight(50)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

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

        combo_style = """
            QComboBox {
                color: #000000;
                font: bold 14pt "Helvetica";
                padding: 6px;
            }
            QComboBox QAbstractItemView {
                font: bold 14pt "Helvetica";
                color: #000000;
                background-color: #f0f0f0;
                selection-background-color: #a5d6a7;
                selection-color: #000000;
            }
        """

        self.user_dropdown = QComboBox()
        self.user_dropdown.setMinimumHeight(50)
        self.user_dropdown.setStyleSheet(combo_style)
        self.user_dropdown.setPlaceholderText("Select user...")
        assign_layout.addWidget(self.user_dropdown)

        self.book_dropdown = QComboBox()
        self.book_dropdown.setMinimumHeight(50)
        self.book_dropdown.setStyleSheet(combo_style)
        self.book_dropdown.setPlaceholderText("Select book...")
        assign_layout.addWidget(self.book_dropdown)

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

        self.return_user_dropdown = QComboBox()
        self.return_user_dropdown.setMinimumHeight(50)
        self.return_user_dropdown.setStyleSheet(combo_style)
        self.return_user_dropdown.setPlaceholderText("Select user...")
        self.return_user_dropdown.currentTextChanged.connect(self.update_return_books)
        return_layout.addWidget(self.return_user_dropdown)

        self.return_book_dropdown = QComboBox()
        self.return_book_dropdown.setMinimumHeight(50)
        self.return_book_dropdown.setStyleSheet(combo_style)
        self.return_book_dropdown.setPlaceholderText("Select book...")
        return_layout.addWidget(self.return_book_dropdown)

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
        self.populate_dropdowns()
        self.update_return_books()
        self.user_dropdown.setCurrentIndex(-1)
        self.book_dropdown.setCurrentIndex(-1)
        self.return_user_dropdown.setCurrentIndex(-1)
        self.return_book_dropdown.setCurrentIndex(-1)
        self.issue_date.setDate(QDate.currentDate())
        self.return_date.setDate(QDate.currentDate())

    def populate_dropdowns(self):
        try:
            cursor = self.controller.db.cursor()
            # Load users
            cursor.execute("SELECT name FROM users")
            users = [row[0] for row in cursor.fetchall()]
            # Load available books (not currently issued)
            cursor.execute("""
                SELECT b.title 
                FROM books b
                LEFT JOIN transactions t ON b.id = t.book_id AND t.return_date IS NULL
                WHERE t.id IS NULL
            """)
            books = [row[0] for row in cursor.fetchall()]
            cursor.close()

            self.user_dropdown.clear()
            self.return_user_dropdown.clear()
            self.book_dropdown.clear()
            if users:
                self.user_dropdown.addItems(users)
                self.return_user_dropdown.addItems(users)
            else:
                self.user_dropdown.addItem("No users found")
                self.return_user_dropdown.addItem("No users found")
                QMessageBox.warning(self, "Warning", "No users found in the database.")

            if books:
                self.book_dropdown.addItems(books)
            else:
                self.book_dropdown.addItem("No books available")
                QMessageBox.warning(self, "Warning", "No available books found in the database.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to populate dropdowns: {e}")

    def update_return_books(self):
        try:
            user_name = self.return_user_dropdown.currentText().strip()
            self.return_book_dropdown.clear()

            if not user_name or user_name == "No users found":
                self.return_book_dropdown.addItem("No books available")
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

            if books:
                self.return_book_dropdown.addItems(books)
            else:
                self.return_book_dropdown.addItem("No issued books")
                QMessageBox.warning(self, "Warning", f"No issued books found for user '{user_name}'.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to refresh return books: {e}")

    def assign_book(self):
        try:
            user_name = self.user_dropdown.currentText().strip()
            book_title = self.book_dropdown.currentText().strip()
            issue_date = self.issue_date.date().toPyDate()

            if not user_name or not book_title or user_name == "No users found" or book_title == "No books available":
                QMessageBox.critical(self, "Error", "Please select both a valid user and book")
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
            user_name = self.return_user_dropdown.currentText().strip()
            book_title = self.return_book_dropdown.currentText().strip()
            return_date = self.return_date.date().toPyDate()

            if not user_name or not book_title or user_name == "No users found" or book_title in ["No issued books", "No books available"]:
                QMessageBox.critical(self, "Error", "Please select both a valid user and book")
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
        header_layout = QHBoxLayout()
        title = QLabel("Admin Panel")
        title.setFont(QFont("Helvetica, Arial, sans-serif", 32, QFont.Bold))
        title.setStyleSheet("color: #1f2937; border: none;")
        header_layout.addWidget(title)
        header_layout.addStretch()

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setFixedWidth(180)
        refresh_btn.setMinimumHeight(50)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Form
        frame = QFrame()
        frame_layout = QVBoxLayout(frame)
        frame_layout.setSpacing(20)
        frame_layout.setContentsMargins(30, 30, 30, 30)

        combo_style = """
            QComboBox {
                color: #000000;
                font: bold 14pt "Helvetica";
                padding: 6px;
            }
            QComboBox QAbstractItemView {
                font: bold 14pt "Helvetica";
                color: #000000;
                background-color: #f0f0f0;
                selection-background-color: #a5d6a7;
                selection-color: #000000;
            }
        """
        self.user_dropdown = QComboBox()
        self.user_dropdown.setMinimumHeight(50)
        self.user_dropdown.setStyleSheet(combo_style)
        self.user_dropdown.setPlaceholderText("Select Member...")
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

        self.refresh()

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

        refresh_btn = QPushButton("Refresh")
        refresh_btn.setObjectName("refreshButton")
        refresh_btn.setFixedWidth(180)
        refresh_btn.setMinimumHeight(50)
        refresh_btn.clicked.connect(self.refresh)
        header_layout.addWidget(refresh_btn)

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
                           u.name as user, COALESCE(u.address, b.location) as location,
                           t.issue_date, t.return_date
                    FROM books b
                    LEFT JOIN authors a ON b.author_id = a.id
                    LEFT JOIN transactions t ON b.id = t.book_id
                    LEFT JOIN users u ON t.user_id = u.id
                    ORDER BY b.title
                """
            elif report_type == "issued_books":
                query = """
                    SELECT b.serial_number, b.title, a.name as author, 
                           u.name as user, u.address as location, t.issue_date
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
                           u.name as user, COALESCE(u.address, b.location) as location,
                           t.issue_date, t.return_date
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