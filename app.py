from flask import Flask, render_template, request
import sqlite3
import re

app = Flask(__name__)


@app.route("/")
def home():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
        SELECT MAX(s.weight)
        FROM sets s
        JOIN exercises e ON s.exercise_id = e.id
        WHERE e.exercise_name = ?
    """, ("Bench",))
    bench_pr = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MAX(s.weight)
        FROM sets s
        JOIN exercises e ON s.exercise_id = e.id
        WHERE e.exercise_name = ?
    """, ("Squat",))
    squat_pr = cursor.fetchone()[0]

    cursor.execute("""
        SELECT MAX(s.weight)
        FROM sets s
        JOIN exercises e ON s.exercise_id = e.id
        WHERE e.exercise_name = ?
    """, ("Deadlift",))
    deadlift_pr = cursor.fetchone()[0]

    cursor.execute("""
        SELECT w.date, MAX(s.weight)
        FROM sets s
        JOIN exercises e ON s.exercise_id = e.id
        JOIN workouts w ON e.workout_id = w.id
        WHERE e.exercise_name = ?
        GROUP BY w.date
        ORDER BY w.date
    """, ("Bench",))
    bench_data = cursor.fetchall()

    dates = [row[0] for row in bench_data]
    weights = [row[1] for row in bench_data]

    conn.close()

    return render_template(
        "index.html",
        bench_pr=bench_pr,
        squat_pr=squat_pr,
        deadlift_pr=deadlift_pr,
        dates=dates,
        weights=weights
    )


@app.route("/add", methods=["GET", "POST"])
def add_workout():
    if request.method == "POST":
        workout_name = request.form.get("workout_name")
        date = request.form.get("date")

        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO workouts (name, date) VALUES (?, ?)",
            (workout_name, date)
        )
        workout_id = cursor.lastrowid

        exercise_numbers = set()

        for key in request.form.keys():
            match = re.match(r"exercise_name_(\d+)", key)
            if match:
                exercise_numbers.add(int(match.group(1)))

        for exercise_number in sorted(exercise_numbers):
            exercise_name = request.form.get(f"exercise_name_{exercise_number}")

            if exercise_name and exercise_name.strip():
                cursor.execute(
                    "INSERT INTO exercises (workout_id, exercise_name) VALUES (?, ?)",
                    (workout_id, exercise_name.strip())
                )
                exercise_id = cursor.lastrowid

                set_numbers = set()

                for key in request.form.keys():
                    match = re.match(rf"weight_{exercise_number}_(\d+)", key)
                    if match:
                        set_numbers.add(int(match.group(1)))

                for set_number in sorted(set_numbers):
                    weight = request.form.get(f"weight_{exercise_number}_{set_number}")
                    reps = request.form.get(f"reps_{exercise_number}_{set_number}")

                    if weight and reps:
                        cursor.execute(
                            "INSERT INTO sets (exercise_id, weight, reps) VALUES (?, ?, ?)",
                            (exercise_id, weight, reps)
                        )

        conn.commit()
        conn.close()

        print("Workout saved successfully.")

    return render_template("addWorkout.html")


@app.route("/history")
def history():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, date FROM workouts ORDER BY date DESC")
    workouts = cursor.fetchall()

    workout_data = []

    for workout in workouts:
        workout_id = workout[0]
        workout_name = workout[1]
        workout_date = workout[2]

        cursor.execute(
            "SELECT id, exercise_name FROM exercises WHERE workout_id = ?",
            (workout_id,)
        )
        exercises = cursor.fetchall()

        exercise_data = []

        for exercise in exercises:
            exercise_id = exercise[0]
            exercise_name = exercise[1]

            cursor.execute(
                "SELECT weight, reps FROM sets WHERE exercise_id = ?",
                (exercise_id,)
            )
            sets = cursor.fetchall()

            exercise_data.append({
                "exercise_name": exercise_name,
                "sets": sets
            })

        workout_data.append({
            "id": workout_id,
            "name": workout_name,
            "date": workout_date,
            "exercises": exercise_data
        })

    conn.close()

    return render_template("history.html", workouts=workout_data)


@app.route("/edit/<int:workout_id>", methods=["GET", "POST"])
def edit_workout(workout_id):
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if request.method == "POST":
        workout_name = request.form.get("workout_name")
        date = request.form.get("date")

        cursor.execute(
            "UPDATE workouts SET name = ?, date = ? WHERE id = ?",
            (workout_name, date, workout_id)
        )

        cursor.execute(
            "SELECT id FROM exercises WHERE workout_id = ?",
            (workout_id,)
        )
        exercise_ids = cursor.fetchall()

        for exercise in exercise_ids:
            cursor.execute(
                "DELETE FROM sets WHERE exercise_id = ?",
                (exercise[0],)
            )

        cursor.execute(
            "DELETE FROM exercises WHERE workout_id = ?",
            (workout_id,)
        )

        exercise_numbers = set()

        for key in request.form.keys():
            match = re.match(r"exercise_name_(\d+)", key)
            if match:
                exercise_numbers.add(int(match.group(1)))

        for exercise_number in sorted(exercise_numbers):
            exercise_name = request.form.get(f"exercise_name_{exercise_number}")

            if exercise_name and exercise_name.strip():
                cursor.execute(
                    "INSERT INTO exercises (workout_id, exercise_name) VALUES (?, ?)",
                    (workout_id, exercise_name.strip())
                )
                exercise_id = cursor.lastrowid

                set_numbers = set()

                for key in request.form.keys():
                    match = re.match(rf"weight_{exercise_number}_(\d+)", key)
                    if match:
                        set_numbers.add(int(match.group(1)))

                for set_number in sorted(set_numbers):
                    weight = request.form.get(f"weight_{exercise_number}_{set_number}")
                    reps = request.form.get(f"reps_{exercise_number}_{set_number}")

                    if weight and reps:
                        cursor.execute(
                            "INSERT INTO sets (exercise_id, weight, reps) VALUES (?, ?, ?)",
                            (exercise_id, weight, reps)
                        )

        conn.commit()
        print("Workout updated successfully.")

    cursor.execute(
        "SELECT name, date FROM workouts WHERE id = ?",
        (workout_id,)
    )
    workout = cursor.fetchone()

    cursor.execute(
        "SELECT id, exercise_name FROM exercises WHERE workout_id = ?",
        (workout_id,)
    )
    exercises = cursor.fetchall()

    exercise_data = []

    for exercise in exercises:
        exercise_id = exercise[0]
        exercise_name = exercise[1]

        cursor.execute(
            "SELECT weight, reps FROM sets WHERE exercise_id = ?",
            (exercise_id,)
        )
        sets = cursor.fetchall()

        exercise_data.append({
            "exercise_name": exercise_name,
            "sets": sets
        })

    conn.close()

    return render_template(
        "editWorkout.html",
        workout_id=workout_id,
        workout_name=workout[0],
        date=workout[1],
        exercises=exercise_data
    )


if __name__ == "__main__":
    app.run(debug=True)