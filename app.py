from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/add", methods=["GET", "POST"])
def add_workout():
    if request.method == "POST":
        lift = request.form.get("lift")
        weight = request.form.get("weight")
        reps = request.form.get("reps")
        sets = request.form.get("sets")

        # connect to database
        conn = sqlite3.connect("database.db")
        cursor = conn.cursor()

        # insert workout
        cursor.execute(
            "INSERT INTO workouts (lift, weight, reps, sets) VALUES (?, ?, ?, ?)",
            (lift, weight, reps, sets)
        )

        conn.commit()
        conn.close()

        print("Workout saved to database")

    return render_template("addWorkout.html")

@app.route("/history")
def history():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM workouts")
    workouts = cursor.fetchall()

    conn.close()

    return render_template("history.html", workouts=workouts)

if __name__ == "__main__":
    app.run(debug=True)