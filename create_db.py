import sqlite3

conn = sqlite3.connect("database.db")
cur = conn.cursor()

# USERS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    phone TEXT,
    password TEXT
)
""")

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user TEXT,
    generator TEXT,
    days INTEGER,
    total INTEGER,
    status TEXT
);

# PAYMENTS TABLE
cur.execute("""
CREATE TABLE IF NOT EXISTS payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT,
    generator TEXT,
    days INTEGER,
    total INTEGER,
    address TEXT,
    city TEXT,
    transaction_id TEXT,
    screenshot TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Database ready successfully")
