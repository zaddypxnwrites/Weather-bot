import os

from flask import Flask, render_template, request, send_from_directory
from weather_engine import get_weather_report, PROJECT_VERSION

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template('index.html', result=None, error=None, version=PROJECT_VERSION)


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    location = request.values.get('location', '').strip()
    if not location:
        return render_template('index.html', result=None, error=None, version=PROJECT_VERSION)
    try:
        result = get_weather_report(location)
    except Exception as exc:
        return render_template('index.html', result=None, error=str(exc), version=PROJECT_VERSION)
    return render_template('index.html', result=result, error=None, version=PROJECT_VERSION)


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
