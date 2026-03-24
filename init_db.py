import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    date TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE exercises (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    exercise_name TEXT NOT NULL,
    FOREIGN KEY (workout_id) REFERENCES workouts(id)
)
""")

cursor.execute("""
CREATE TABLE sets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    exercise_id INTEGER NOT NULL,
    weight INTEGER NOT NULL,
    reps INTEGER NOT NULL,
    FOREIGN KEY (exercise_id) REFERENCES exercises(id)
)
""")

conn.commit()
conn.close()

print("Database initialized.")