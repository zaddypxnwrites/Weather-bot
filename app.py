import os

from flask import Flask, jsonify, render_template, request, send_from_directory
from weather_engine import get_location_suggestions, get_weather_report, PROJECT_VERSION, normalize_units
from routes.live_earth import live_earth_bp

app = Flask(__name__)
app.register_blueprint(live_earth_bp)



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


@app.route('/forecast', methods=['GET'])
def forecast_detail():
    location = request.args.get('location', '').strip()
    units = normalize_units(request.args.get('units', 'metric'))
    timestamp_raw = request.args.get('ts', '').strip()
    index_raw = request.args.get('index', '').strip()

    if not location:
        return render_template(
            'forecast_detail.html',
            forecast=None,
            result=None,
            error='Missing location. Please search for a city first.',
            version=PROJECT_VERSION,
            location='',
            selected_units=units,
        )

    try:
        result = get_weather_report(location, units=units)
    except RuntimeError as exc:
        return render_template(
            'forecast_detail.html',
            forecast=None,
            result=None,
            error=str(exc),
            version=PROJECT_VERSION,
            location=location,
            selected_units=units,
        )
    except Exception:
        return render_template(
            'forecast_detail.html',
            forecast=None,
            result=None,
            error='Sorry, something went wrong while loading this forecast.',
            version=PROJECT_VERSION,
            location=location,
            selected_units=units,
        )

    forecast_items = result.get('forecast', [])
    selected = None

    if timestamp_raw:
        try:
            timestamp = int(timestamp_raw)
        except ValueError:
            timestamp = None
        if timestamp is not None:
            selected = next((item for item in forecast_items if item.get('timestamp') == timestamp), None)

    if selected is None and index_raw:
        try:
            index = int(index_raw)
        except ValueError:
            index = -1
        if 0 <= index < len(forecast_items):
            selected = forecast_items[index]

    if selected is None and forecast_items:
        selected = forecast_items[0]

    if selected is None:
        return render_template(
            'forecast_detail.html',
            forecast=None,
            result=result,
            error='Forecast details are unavailable for this location right now.',
            version=PROJECT_VERSION,
            location=location,
            selected_units=units,
        )

    return render_template(
        'forecast_detail.html',
        forecast=selected,
        result=result,
        error=None,
        version=PROJECT_VERSION,
        location=location,
        selected_units=units,
    )


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
