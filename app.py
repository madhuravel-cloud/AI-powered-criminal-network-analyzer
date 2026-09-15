from flask import Flask, render_template, request
from ml.predict import analyze_fir

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def home():

    results = []

    if request.method == "POST":

        person = request.form["person"]
        location = request.form["location"]
        phone = request.form["phone"]
        related_person = request.form["related_person"]
        relationship = request.form["relationship"]

        input_fir = [
            [
                person,
                location,
                phone,
                related_person,
                relationship
            ]
        ]

        results = analyze_fir(input_fir)

    return render_template(
        "index.html",
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)