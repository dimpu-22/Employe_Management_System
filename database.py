import sqlite3

def get_connection():
    conn = sqlite3.connect("store.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        image TEXT
    )
    """)
    
    

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS cart(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_id INTEGER,
        quantity INTEGER
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL,
        order_date TEXT
    )
    """)
    cursor.execute("""
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER,
    product_id INTEGER
)
""")
    
    cursor.execute("SELECT COUNT(*) FROM products")

    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO products(name, description, price, image)
            VALUES(?,?,?,?)
        """, [
            ("Wireless Mouse", "High precision wireless mouse", 20, "https://via.placeholder.com/250"),
            ("Mechanical Keyboard", "RGB Gaming Keyboard", 45, "https://via.placeholder.com/250"),
            ("Bluetooth Headphones", "Noise Cancelling Headphones", 65, "https://via.placeholder.com/250"),
            ("Smart Watch", "Fitness Smart Watch", 80, "https://via.placeholder.com/250")
        ])

    

    conn.commit()
    conn.close()
    