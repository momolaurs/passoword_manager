import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('passwords.db')

# Create a cursor object
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY,
    email TEXT NOT NULL UNIQUE
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS passwords (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    username TEXT,
    password TEXT,
    FOREIGN KEY(email) REFERENCES emails(email)
)
''')

conn.commit()
conn.close()

print("Database setup completed successfully!")