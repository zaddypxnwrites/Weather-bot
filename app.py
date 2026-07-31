import os

from flask import Flask, jsonify, render_template, request, send_from_directory
from weather_engine import get_location_suggestions, get_weather_report, PROJECT_VERSION, normalize_units

app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return render_template(
        'index.html',
        result=None,
        error=None,
        version=PROJECT_VERSION,
        location=request.args.get('location', '').strip(),
        selected_units=normalize_units(request.args.get('units', 'metric')),
    )


@app.route('/weather', methods=['GET', 'POST'])
def weather():
    location = request.values.get('location', '').strip()
    units = normalize_units(request.values.get('units', 'metric'))
    if not location:
        return render_template(
            'index.html',
            result=None,
            error=None,
            version=PROJECT_VERSION,
            location='',
            selected_units=units,
        )
    try:
        result = get_weather_report(location, units=units)
    except RuntimeError as exc:
        message = str(exc)
        if 'OpenWeatherMap API key is missing' in message:
            message = (
                'Server configuration error: OPENWEATHER_API_KEY is not set. '
                'Please configure this secret in Render or local .env.'
            )
        return render_template(
            'index.html',
            result=None,
            error=message,
            version=PROJECT_VERSION,
            location=location,
            selected_units=units,
        )
    except Exception:
        return render_template(
            'index.html',
            result=None,
            error='Sorry, something went wrong. Please try again later.',
            version=PROJECT_VERSION,
            location=location,
            selected_units=units,
        )
    return render_template(
        'index.html',
        result=result,
        error=None,
        version=PROJECT_VERSION,
        location=location,
        selected_units=units,
    )


@app.route('/api/suggestions', methods=['GET'])
def suggestions():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify([])
    return jsonify(get_location_suggestions(query))


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
