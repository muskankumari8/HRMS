import sqlite3

conn = sqlite3.connect("database.db")

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS performance(

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    employee_name TEXT,

    attendance_score REAL,

    task_score REAL,

    feedback_score REAL,

    performance_score REAL,

    performance_level TEXT
)
""")

conn.commit()
conn.close()

print("Performance Table Created")