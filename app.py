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
    except RuntimeError as exc:
        message = str(exc)
        if 'OpenWeatherMap API key is missing' in message:
            message = (
                'Server configuration error: OPENWEATHER_API_KEY is not set. '
                'Please configure this secret in Render or local .env.'
            )
        return render_template('index.html', result=None, error=message, version=PROJECT_VERSION)
    except Exception:
        return render_template(
            'index.html',
            result=None,
            error='Sorry, something went wrong. Please try again later.',
            version=PROJECT_VERSION,
        )
    return render_template('index.html', result=result, error=None, version=PROJECT_VERSION)


@app.errorhandler(500)
def handle_internal_error(error):
    return render_template(
        'index.html',
        result=None,
        error='An unexpected server error occurred. Please refresh and try again.',
        version=PROJECT_VERSION,
    ), 500


@app.route('/service-worker.js')
def service_worker():
    return send_from_directory(app.static_folder, 'service-worker.js', mimetype='application/javascript')


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
