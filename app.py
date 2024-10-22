from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from blockchain import Blockchain

# Tạo một blockchain toàn cục
blockchain = Blockchain()


app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Kết nối đến cơ sở dữ liệu
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    balance = get_balance(session['username'])
    return render_template('index.html', balance=balance)

def get_balance(username):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT balance FROM users WHERE username = ?", (username,))
    balance = c.fetchone()[0]
    conn.close()
    return balance

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        
        if user:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            flash('Đăng nhập không thành công.')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
            conn.commit()
            flash('Đăng ký thành công!')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Tài khoản đã tồn tại!')
        finally:
            conn.close()
    
    return render_template('register.html')

@app.route('/transfer', methods=['POST'])
def transfer():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    sender = session['username']
    receiver = request.form['receiver']
    amount = float(request.form['amount'])
    
    # Kiểm tra số dư và thực hiện chuyển khoản
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cập nhật số dư của người gửi
    cursor.execute('SELECT balance FROM users WHERE username = ?', (sender,))
    sender_balance = cursor.fetchone()[0]
    
    if sender_balance >= amount:
        cursor.execute('UPDATE users SET balance = balance - ? WHERE username = ?', (amount, sender))
        cursor.execute('UPDATE users SET balance = balance + ? WHERE username = ?', (amount, receiver))
        
        # Ghi lại giao dịch trong cơ sở dữ liệu
        cursor.execute('INSERT INTO transactions (sender, receiver, amount) VALUES (?, ?, ?)', (sender, receiver, amount))
        
        # Thêm giao dịch vào blockchain
        transaction = {
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        }
        blockchain.add_block([transaction])
        
        conn.commit()
        flash('Chuyển khoản thành công và giao dịch đã được thêm vào blockchain!')
    else:
        flash('Số dư không đủ để thực hiện chuyển khoản.')
    
    conn.close()
    return redirect(url_for('index'))


@app.route('/transactions')
def transactions():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Lấy lịch sử giao dịch cho người dùng
    cursor.execute('SELECT * FROM transactions WHERE sender = ? OR receiver = ?', (session['username'], session['username']))
    transactions = cursor.fetchall()
    
    conn.close()
    return render_template('transactions.html', transactions=transactions)

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))
@app.route('/blockchain')
def show_blockchain():
    if 'username' not in session:
        return redirect(url_for('login'))

    # Chỉ admin có thể xem toàn bộ blockchain
    if session['username'] != 'admin':
        flash('Bạn không có quyền truy cập!')
        return redirect(url_for('index'))

    return render_template('blockchain.html', blockchain=blockchain.chain)


if __name__ == '__main__':
    app.run(debug=True)
