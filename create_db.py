import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS employees(
id INTEGER PRIMARY KEY AUTOINCREMENT,
name TEXT,
email TEXT,
department TEXT,
salary INTEGER
)
""")

conn.commit()
conn.close()

print("Database Created")