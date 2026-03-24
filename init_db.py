import sqlite3

conn = sqlite3.connect("database.db")

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lift TEXT,
    weight INTEGER,
    reps INTEGER,
    sets INTEGER
)
""")

conn.commit()
conn.close()

print("Database initialized")