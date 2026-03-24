from flask import Flask, render_template, request

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

        print("Workout Submitted:")
        print("Lift:", lift)
        print("Weight:", weight)
        print("Reps:", reps)
        print("Sets:", sets)

    return render_template("addWorkout.html")

@app.route("/history")
def history():
    return render_template("history.html")

if __name__ == "__main__":
    app.run(debug=True)