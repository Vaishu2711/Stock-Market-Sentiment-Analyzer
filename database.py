# database.py
import sqlite3

def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT
    )""")
    c.execute("""CREATE TABLE IF NOT EXISTS portfolio (
        username TEXT,
        stock TEXT
    )""")
    conn.commit()
    conn.close()

def register_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    if c.fetchone():
        return False
    c.execute("INSERT INTO users VALUES (?, ?)", (username, password))
    conn.commit()
    conn.close()
    return True

def login_user(username, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    conn.close()
    return user is not None

def add_stock_to_db(username, stock):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("INSERT INTO portfolio VALUES (?, ?)", (username, stock.upper()))
    conn.commit()
    conn.close()

def remove_stock_from_db(username, stock):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("DELETE FROM portfolio WHERE username=? AND stock=?", (username, stock.upper()))
    conn.commit()
    conn.close()

def get_user_portfolio(username):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT stock FROM portfolio WHERE username=?", (username,))
    data = [row[0] for row in c.fetchall()]
    conn.close()
    return data
