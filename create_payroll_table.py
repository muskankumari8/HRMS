import sqlite3

conn = sqlite3.connect("database.db")

cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS payroll(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    employee_name TEXT,
    basic_salary REAL,
    bonus REAL,
    deduction REAL,
    net_salary REAL
)
""")

conn.commit()
conn.close()

print("Payroll Table Created")