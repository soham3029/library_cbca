import tkinter as tk
from tkinter import ttk, messagebox, Frame, filedialog
from tkcalendar import DateEntry
from PIL import ImageTk, Image
import mysql.connector
import pandas as pd
from datetime import datetime
import uuid
import os

class LibraryManagementSystem:
    def __init__(self, root):
        self.root = root
        self.root.title("CBCA Library Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#e6f3fa")  # Light teal background

        # Database connection
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="12345",
            database="library_db"
        )
        self.create_tables()

        # Styling
        self.style = ttk.Style()
        self.style.configure("TButton", padding=10, font=('Helvetica', 12), background="#f39c12")  # Orange buttons
        self.style.configure("TLabel", font=('Helvetica', 12), background="#e6f3fa", foreground="#2c3e50")
        self.style.configure("TEntry", padding=5)
        self.style.configure("TCombobox", padding=5)
        self.style.configure("Treeview.Heading", font=('Helvetica', 12, 'bold'), background="#3498db")  # Blue headers
        self.style.configure("Treeview", font=('Helvetica', 11))

        # Logo
        logo_path = "logo.png"
        if os.path.exists(logo_path):
            try:
                img = Image.open(logo_path)
                img = img.resize((200, 100), Image.LANCZOS)
                self.logo = ImageTk.PhotoImage(img)
                logo_label = tk.Label(root, image=self.logo, bg="#e6f3fa")
                logo_label.pack(pady=20)
            except Exception as e:
                print(f"Error loading logo: {e}")
                tk.Label(root, text="CBCA Library", font=('Helvetica', 24, 'bold'), bg="#e6f3fa", fg="#2c3e50").pack(pady=20)
        else:
            print(f"Logo file not found at: {os.path.abspath(logo_path)}")
            tk.Label(root, text="CBCA Library", font=('Helvetica', 24, 'bold'), bg="#e6f3fa", fg="#2c3e50").pack(pady=20)

        # Frames
        self.frames = {}
        for F in (LoginPage, HomePage, CreateUserPage, BookAuthorPage, AssignReturnPage, AdminPanelPage, ReportPage):
            page_name = F.__name__
            frame = F(parent=root, controller=self)
            self.frames[page_name] = frame
            frame.place(x=0, y=0, width=1200, height=800)

        self.show_frame("LoginPage")

    def show_frame(self, page_name):
        frame = self.frames[page_name]
        frame.tkraise()
        if hasattr(frame, 'refresh'):
            frame.refresh()

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
                name VARCHAR(255) UNIQUE NOT NULL
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

class LoginPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller

        frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(frame, text="Login", font=('Helvetica', 18, 'bold'), bg="#ffffff", fg="#2c3e50").pack(pady=10)
        tk.Label(frame, text="Username:", bg="#ffffff").pack()
        self.username = ttk.Entry(frame, width=30)
        self.username.pack(pady=5)

        tk.Label(frame, text="Password:", bg="#ffffff").pack()
        self.password = ttk.Entry(frame, show="*", width=30)
        self.password.pack(pady=5)

        ttk.Button(frame, text="Login", command=self.login).pack(pady=20)

    def login(self):
        username = self.username.get()
        password = self.password.get()

        cursor = self.controller.db.cursor()
        cursor.execute("SELECT * FROM users WHERE name=%s AND password=%s", (username, password))
        user = cursor.fetchone()

        if user:
            self.controller.show_frame("HomePage")
            self.username.delete(0, tk.END)
            self.password.delete(0, tk.END)
        else:
            messagebox.showerror("Error", "Invalid credentials")

class HomePage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller

        tk.Label(self, text="Welcome to CBCA Library", font=('Helvetica', 24, 'bold'), bg="#e6f3fa", fg="#2c3e50").pack(pady=20)
        ttk.Button(self, text="Refresh", command=self.refresh).pack(pady=10)
        ttk.Button(self, text="Create User", command=self.create_user).pack(pady=10)
        ttk.Button(self, text="Book/Author Management", command=lambda: controller.show_frame("BookAuthorPage")).pack(pady=10)
        ttk.Button(self, text="Assign/Return Books", command=lambda: controller.show_frame("AssignReturnPage")).pack(pady=10)
        ttk.Button(self, text="Admin Panel", command=lambda: controller.show_frame("AdminPanelPage")).pack(pady=10)
        ttk.Button(self, text="Reports", command=lambda: controller.show_frame("ReportPage")).pack(pady=10)

    def create_user(self):
        self.controller.show_frame("CreateUserPage")

    def refresh(self):
        pass

class CreateUserPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller
        self.current_page = 1
        self.users_per_page = 10

        # Top frame for search and create button
        top_frame = tk.Frame(self, bg="#e6f3fa")
        top_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(top_frame, text="Create User", command=self.show_create_form).pack(side='left')
        ttk.Button(top_frame, text="Refresh", command=self.refresh).pack(side='left', padx=10)
        ttk.Button(top_frame, text="Back", command=lambda: controller.show_frame("HomePage")).pack(side='right')

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(top_frame, textvariable=self.search_var)
        search_entry.pack(side='right', padx=10)
        search_entry.bind('<KeyRelease>', self.search_users)

        # Users table
        self.tree = ttk.Treeview(self, columns=('Name', 'Serial', 'DOB'), show='headings')
        self.tree.heading('Name', text='Full Name')
        self.tree.heading('Serial', text='Serial Number')
        self.tree.heading('DOB', text='Date of Birth')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        # Pagination
        pagination_frame = tk.Frame(self, bg="#e6f3fa")
        pagination_frame.pack(fill='x', pady=10)
        ttk.Button(pagination_frame, text="Previous", command=self.prev_page).pack(side='left', padx=5)
        self.page_label = tk.Label(pagination_frame, text="Page 1", bg="#e6f3fa", fg="#2c3e50")
        self.page_label.pack(side='left', padx=5)
        ttk.Button(pagination_frame, text="Next", command=self.next_page).pack(side='left', padx=5)

        self.refresh()

    def refresh(self):
        self.load_users()

    def load_users(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor = self.controller.db.cursor()
        query = "SELECT name, serial_number, dob FROM users"
        params = ()
        if search_term:
            query += " WHERE name LIKE %s OR serial_number LIKE %s"
            params = (f"%{search_term}%", f"%{search_term}%")

        cursor.execute(query, params)
        users = cursor.fetchall()

        start = (self.current_page - 1) * self.users_per_page
        end = start + self.users_per_page
        for user in users[start:end]:
            dob = user[2].strftime('%Y-%m-%d') if user[2] else ''
            self.tree.insert('', 'end', values=(user[0], user[1], dob))

        self.page_label.config(text=f"Page {self.current_page}")

    def search_users(self, event=None):
        self.current_page = 1
        self.load_users(self.search_var.get())

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_users(self.search_var.get())

    def next_page(self):
        cursor = self.controller.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        if self.current_page * self.users_per_page < total_users:
            self.current_page += 1
            self.load_users(self.search_var.get())

    def show_create_form(self):
        window = tk.Toplevel(bg="#e6f3fa")
        window.title("Create User")
        window.geometry("400x300")

        frame = tk.Frame(window, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        frame.pack(expand=True, fill='both')

        tk.Label(frame, text="Create New User", font=('Helvetica', 16, 'bold'), bg="#ffffff", fg="#2c3e50").pack(pady=10)

        tk.Label(frame, text="Name:", bg="#ffffff").pack()
        name = ttk.Entry(frame)
        name.pack(pady=5, fill='x')

        tk.Label(frame, text="Serial Number:", bg="#ffffff").pack()
        serial = ttk.Entry(frame)
        serial.pack(pady=5, fill='x')

        tk.Label(frame, text="Date of Birth:", bg="#ffffff").pack()
        dob = DateEntry(frame)
        dob.pack(pady=5)

        def submit():
            try:
                cursor = self.controller.db.cursor()
                cursor.execute("""
                    INSERT INTO users (name, serial_number, dob, password)
                    VALUES (%s, %s, %s, %s)
                """, (name.get(), serial.get(), dob.get_date(), str(uuid.uuid4())[:8]))
                self.controller.db.commit()
                messagebox.showinfo("Success", "User created successfully")
                self.refresh()
                window.destroy()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

        ttk.Button(frame, text="Submit", command=submit).pack(pady=20)

class BookAuthorPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller

        # Top buttons
        top_frame = tk.Frame(self, bg="#e6f3fa")
        top_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(top_frame, text="Refresh", command=self.refresh).pack(side='left')
        ttk.Button(top_frame, text="Add New", command=self.show_add_form).pack(side='left', padx=10)
        ttk.Button(top_frame, text="Back", command=lambda: controller.show_frame("HomePage")).pack(side='right')

        # Books table
        self.tree = ttk.Treeview(self, columns=('Serial', 'Author', 'Title', 'BookSerial', 'Occupied'), show='headings')
        self.tree.heading('Serial', text='Serial')
        self.tree.heading('Author', text='Author')
        self.tree.heading('Title', text='Book Title')
        self.tree.heading('BookSerial', text='Book Serial')
        self.tree.heading('Occupied', text='Occupied By')
        self.tree.pack(fill='both', expand=True, padx=10, pady=10)

        self.refresh()

    def refresh(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        cursor = self.controller.db.cursor()
        cursor.execute("""
            SELECT b.serial_number, a.name, b.title, b.serial_number, 
                   COALESCE(u.name, 'Library') as occupied_by
            FROM books b
            JOIN authors a ON b.author_id = a.id
            LEFT JOIN transactions t ON b.id = t.book_id AND t.return_date IS NULL
            LEFT JOIN users u ON t.user_id = u.id
        """)
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def show_add_form(self):
        window = tk.Toplevel(bg="#e6f3fa")
        window.title("Add Book/Author")
        window.geometry("400x400")

        frame = tk.Frame(window, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        frame.pack(expand=True, fill='both')

        tk.Label(frame, text="Add Author/Book", font=('Helvetica', 16, 'bold'), bg="#ffffff", fg="#2c3e50").pack(pady=10)

        tk.Label(frame, text="Author Name:", bg="#ffffff").pack()
        self.author_name = ttk.Entry(frame)
        self.author_name.pack(pady=5, fill='x')

        ttk.Button(frame, text="Add Author", command=self.add_author).pack(pady=10)

        tk.Label(frame, text="Author:", bg="#ffffff").pack()
        self.author_var = tk.StringVar()
        self.author_dropdown = ttk.Combobox(frame, textvariable=self.author_var)
        self.refresh_authors()
        self.author_dropdown.pack(pady=5, fill='x')

        tk.Label(frame, text="Book Title:", bg="#ffffff").pack()
        self.book_title = ttk.Entry(frame)
        self.book_title.pack(pady=5, fill='x')

        tk.Label(frame, text="Book Serial:", bg="#ffffff").pack()
        self.book_serial = ttk.Entry(frame)
        self.book_serial.pack(pady=5, fill='x')

        ttk.Button(frame, text="Add Book", command=self.add_book).pack(pady=20)

    def refresh_authors(self):
        cursor = self.controller.db.cursor()
        cursor.execute("SELECT name FROM authors")
        self.author_dropdown['values'] = [row[0] for row in cursor.fetchall()]

    def add_author(self):
        name = self.author_name.get()
        if name:
            try:
                cursor = self.controller.db.cursor()
                cursor.execute("INSERT INTO authors (name) VALUES (%s)", (name,))
                self.controller.db.commit()
                self.refresh_authors()
                messagebox.showinfo("Success", "Author added")
                self.author_name.delete(0, tk.END)
                self.refresh()
            except mysql.connector.Error as err:
                messagebox.showerror("Error", f"Database error: {err}")

    def add_book(self):
        author_name = self.author_var.get()
        title = self.book_title.get()
        serial = self.book_serial.get()

        if not all([author_name, title, serial]):
            messagebox.showerror("Error", "All fields required")
            return

        cursor = self.controller.db.cursor()
        cursor.execute("SELECT id FROM authors WHERE name=%s", (author_name,))
        result = cursor.fetchone()
        if not result:
            messagebox.showerror("Error", "Author not found")
            return
        author_id = result[0]

        try:
            cursor.execute("""
                INSERT INTO books (serial_number, title, author_id)
                VALUES (%s, %s, %s)
            """, (serial, title, author_id))
            self.controller.db.commit()
            messagebox.showinfo("Success", "Book added")
            self.book_title.delete(0, tk.END)
            self.book_serial.delete(0, tk.END)
            self.author_var.set('')
            self.refresh()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

class AssignReturnPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller

        top_frame = tk.Frame(self, bg="#e6f3fa")
        top_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(top_frame, text="Refresh", command=self.refresh).pack(side='left')
        ttk.Button(top_frame, text="Back", command=lambda: controller.show_frame("HomePage")).pack(side='right')

        # Assign Book Section
        assign_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        assign_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(assign_frame, text="Assign Book", font=('Helvetica', 14, 'bold'), bg="#ffffff", fg="#2c3e50").pack()
        self.user_var = tk.StringVar()
        self.user_dropdown = ttk.Combobox(assign_frame, textvariable=self.user_var)
        self.user_dropdown.pack(pady=5, fill='x')

        self.book_var = tk.StringVar()
        self.book_dropdown = ttk.Combobox(assign_frame, textvariable=self.book_var)
        self.book_dropdown.pack(pady=5, fill='x')

        tk.Label(assign_frame, text="Issue Date:", bg="#ffffff").pack()
        self.issue_date = DateEntry(assign_frame)
        self.issue_date.pack(pady=5)

        ttk.Button(assign_frame, text="Assign Book", command=self.assign_book).pack(pady=10)

        # Return Book Section
        return_frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        return_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(return_frame, text="Return Book", font=('Helvetica', 14, 'bold'), bg="#ffffff", fg="#2c3e50").pack()
        self.return_user_var = tk.StringVar()
        self.return_user_dropdown = ttk.Combobox(return_frame, textvariable=self.return_user_var)
        self.return_user_dropdown.pack(pady=5, fill='x')

        self.return_book_var = tk.StringVar()
        self.return_book_dropdown = ttk.Combobox(return_frame, textvariable=self.return_book_var)
        self.return_book_dropdown.pack(pady=5, fill='x')

        tk.Label(return_frame, text="Return Date:", bg="#ffffff").pack()
        self.return_date = DateEntry(return_frame)
        self.return_date.pack(pady=5)

        ttk.Button(return_frame, text="Return Book", command=self.return_book).pack(pady=10)

        self.refresh()

    def refresh(self):
        self.refresh_users()
        self.refresh_books()
        self.user_var.set('')
        self.book_var.set('')
        self.return_user_var.set('')
        self.return_book_var.set('')
        self.issue_date.set_date(datetime.now())
        self.return_date.set_date(datetime.now())

    def refresh_users(self):
        cursor = self.controller.db.cursor()
        cursor.execute("SELECT name FROM users")
        users = [row[0] for row in cursor.fetchall()]
        self.user_dropdown['values'] = users
        self.return_user_dropdown['values'] = users

    def refresh_books(self):
        cursor = self.controller.db.cursor()
        cursor.execute("SELECT title FROM books")
        books = [row[0] for row in cursor.fetchall()]
        self.book_dropdown['values'] = books
        self.return_book_dropdown['values'] = books

    def assign_book(self):
        user_name = self.user_var.get()
        book_title = self.book_var.get()
        issue_date = self.issue_date.get_date()

        if not user_name or not book_title:
            messagebox.showerror("Error", "Please select both user and book")
            return

        cursor = self.controller.db.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE name=%s", (user_name,))
            user_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM books WHERE title=%s", (book_title,))
            book_id = cursor.fetchone()[0]

            cursor.execute("""
                INSERT INTO transactions (user_id, book_id, issue_date)
                VALUES (%s, %s, %s)
            """, (user_id, book_id, issue_date))
            self.controller.db.commit()
            messagebox.showinfo("Success", "Book assigned")
            self.refresh()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

    def return_book(self):
        user_name = self.return_user_var.get()
        book_title = self.return_book_var.get()
        return_date = self.return_date.get_date()

        if not user_name or not book_title:
            messagebox.showerror("Error", "Please select both user and book")
            return

        cursor = self.controller.db.cursor()
        try:
            cursor.execute("SELECT id FROM users WHERE name=%s", (user_name,))
            user_id = cursor.fetchone()[0]

            cursor.execute("SELECT id FROM books WHERE title=%s", (book_title,))
            book_id = cursor.fetchone()[0]

            cursor.execute("""
                UPDATE transactions 
                SET return_date=%s 
                WHERE user_id=%s AND book_id=%s AND return_date IS NULL
            """, (return_date, user_id, book_id))
            self.controller.db.commit()
            messagebox.showinfo("Success", "Book returned")
            self.refresh()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

class AdminPanelPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller

        frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        top_frame = tk.Frame(frame, bg="#ffffff")
        top_frame.pack(fill='x', pady=10)
        ttk.Button(top_frame, text="Refresh", command=self.refresh).pack(side='left')
        ttk.Button(top_frame, text="Back", command=lambda: controller.show_frame("HomePage")).pack(side='right')

        tk.Label(frame, text="Admin Panel", font=('Helvetica', 16, 'bold'), bg="#ffffff", fg="#2c3e50").pack(pady=10)
        self.user_var = tk.StringVar()
        self.user_dropdown = ttk.Combobox(frame, textvariable=self.user_var)
        self.user_dropdown.pack(pady=10, fill='x')

        tk.Label(frame, text="Password:", bg="#ffffff").pack()
        self.password = ttk.Entry(frame, show="*")
        self.password.pack(pady=5, fill='x')

        tk.Label(frame, text="Confirm Password:", bg="#ffffff").pack()
        self.confirm_password = ttk.Entry(frame, show="*")
        self.confirm_password.pack(pady=5, fill='x')

        ttk.Button(frame, text="Make Admin", command=self.make_admin).pack(pady=20)

        self.refresh_users()

    def refresh(self):
        self.refresh_users()
        self.user_var.set('')
        if hasattr(self, 'password'):
            self.password.delete(0, tk.END)
        if hasattr(self, 'confirm_password'):
            self.confirm_password.delete(0, tk.END)

    def refresh_users(self):
        cursor = self.controller.db.cursor()
        cursor.execute("SELECT name FROM users WHERE is_admin=FALSE")
        self.user_dropdown['values'] = [row[0] for row in cursor.fetchall()]

    def make_admin(self):
        user_name = self.user_var.get()
        password = self.password.get()
        confirm_password = self.confirm_password.get()

        if not user_name:
            messagebox.showerror("Error", "Please select a user")
            return
        if password != confirm_password:
            messagebox.showerror("Error", "Passwords don't match")
            return

        try:
            cursor = self.controller.db.cursor()
            cursor.execute("""
                UPDATE users 
                SET is_admin=TRUE, password=%s 
                WHERE name=%s
            """, (password, user_name))
            self.controller.db.commit()
            messagebox.showinfo("Success", "Admin privileges granted")
            self.refresh()
        except mysql.connector.Error as err:
            messagebox.showerror("Error", f"Database error: {err}")

class ReportPage(Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e6f3fa")
        self.controller = controller

        frame = tk.Frame(self, bg="#ffffff", padx=20, pady=20, relief="groove", bd=2)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        top_frame = tk.Frame(frame, bg="#ffffff")
        top_frame.pack(fill='x', pady=10)
        ttk.Button(top_frame, text="Refresh", command=self.refresh).pack(side='left')
        ttk.Button(top_frame, text="Back", command=lambda: controller.show_frame("HomePage")).pack(side='right')

        tk.Label(frame, text="Library Reports", font=('Helvetica', 16, 'bold'), bg="#ffffff", fg="#2c3e50").pack(pady=10)
        self.report_type = tk.StringVar(value="all_books")
        ttk.Radiobutton(frame, text="All Books", variable=self.report_type, value="all_books").pack(anchor='w', pady=2)
        ttk.Radiobutton(frame, text="Currently Issued Books", variable=self.report_type, value="issued_books").pack(anchor='w', pady=2)
        ttk.Radiobutton(frame, text="Transaction History", variable=self.report_type, value="transaction_history").pack(anchor='w', pady=2)

        ttk.Button(frame, text="Generate Report", command=self.generate_report).pack(pady=10)
        ttk.Button(frame, text="Export to Excel", command=self.export_to_excel).pack(pady=5)
        ttk.Button(frame, text="Logout", command=self.logout).pack(pady=20)

        self.report_text = tk.Text(frame, height=20, width=100, font=('Helvetica', 10))
        self.report_text.pack(pady=10, padx=10)
        scrollbar = tk.Scrollbar(frame, command=self.report_text.yview)
        scrollbar.pack(side='right', fill='y')
        self.report_text.config(yscrollcommand=scrollbar.set)

    def refresh(self):
        self.report_text.delete(1.0, tk.END)
        self.report_type.set("all_books")

    def generate_report(self):
        cursor = self.controller.db.cursor(dictionary=True)
        report_type = self.report_type.get()

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

        if not results:
            self.report_text.delete(1.0, tk.END)
            self.report_text.insert(tk.END, "No data found for the selected report type.")
            return

        self.report_df = pd.DataFrame(results)
        self.report_text.delete(1.0, tk.END)
        self.report_text.insert(tk.END, self.report_df.to_string(index=False))

    def export_to_excel(self):
        if not hasattr(self, 'report_df') or self.report_df.empty:
            messagebox.showwarning("Warning", "No report data to export. Generate a report first.")
            return

        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            title="Save report as"
        )

        if file_path:
            # Ensure the file has .xlsx extension
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            try:
                self.report_df.to_excel(file_path, index=False, engine='openpyxl')
                messagebox.showinfo("Success", f"Report successfully exported to {file_path}")
            except ImportError:
                messagebox.showerror("Error", "Excel export engine 'openpyxl' not installed. Please install it using 'pip install openpyxl'.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report: {str(e)}")

    def logout(self):
        self.controller.show_frame("LoginPage")

if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryManagementSystem(root)
    root.mainloop()