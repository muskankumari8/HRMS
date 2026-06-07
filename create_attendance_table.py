import sqlite3

conn = sqlite3.connect("database.db")

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS attendance(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT,
    date TEXT,
    status TEXT
)
""")

conn.commit()
conn.close()

print("Attendance Table Created")