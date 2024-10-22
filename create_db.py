import sqlite3

# Kết nối đến cơ sở dữ liệu
conn = sqlite3.connect('database.db')

# Tạo bảng users nếu chưa tồn tại
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    balance REAL DEFAULT 0
);
''')

# Tạo bảng transactions nếu chưa tồn tại
conn.execute('''
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    receiver TEXT NOT NULL,
    amount REAL NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
''')

# Thêm tài khoản admin nếu chưa tồn tại
try:
    conn.execute('''
    INSERT INTO users (username, password, balance) VALUES (?, ?, ?)
    ''', ('admin', 'admin', 5000))
    conn.commit()
except sqlite3.IntegrityError:
    print("Tài khoản admin đã tồn tại.")

# Đóng kết nối
conn.close()

print("Bảng 'users' và 'transactions' đã được tạo thành công!")
