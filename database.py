import sqlite3

from werkzeug.security import generate_password_hash

def get_connection():
    conn = sqlite3.connect("employee.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        salary REAL NOT NULL,
        joining_date TEXT NOT NULL
    )
    """)

    conn.commit()
    conn.close()

def init_db():
    conn = get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        phone TEXT NOT NULL,
        department TEXT NOT NULL,
        designation TEXT NOT NULL,
        salary REAL NOT NULL,
        joining_date TEXT NOT NULL
    )
    """)

    # ===== Paste Step 24 HERE =====

    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute(
        "SELECT * FROM admin WHERE username=?",
        ("admin",)
    )

    admin = cursor.fetchone()

    if not admin:
        cursor.execute(
            "INSERT INTO admin(username,password) VALUES(?,?)",
            (
                "admin",
                generate_password_hash("admin123")
            )
        )

    # ===== End of Step 24 =====

    conn.commit()
    conn.close()
    
    


if __name__ == "__main__":
    init_db()