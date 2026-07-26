import os

from flask import Flask, render_template, request
from weather_engine import get_weather_report

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return render_template("index.html", result=None, error=None)


@app.route("/weather", methods=["POST"])
def weather():
    location = request.form.get("location", "").strip()

    if not location:
        return render_template("index.html", result=None, error="Please enter a city name."), 400

    try:
        result = get_weather_report(location)
    except Exception as exc:
        return render_template("index.html", result=None, error=str(exc))

    return render_template("index.html", result=result, error=None)


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
