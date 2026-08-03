from datetime import datetime, UTC
from flask import Blueprint, jsonify, render_template, request
from grok_client import query_grok
from services.camera_service import filter_cameras, get_camera_by_id
from services.earth_service import get_earth_imagery_layers
from services.events_service import get_live_natural_events
from services.location_service import geocode_location, reverse_geocode
from services.satellite_service import get_rainviewer_timeline, get_weather_satellite_layers
from weather_engine import PROJECT_VERSION, get_weather_report

live_earth_bp = Blueprint("live_earth", __name__, url_prefix="")


@live_earth_bp.route("/live-earth", methods=["GET"])
def live_earth_index():
    category = request.args.get("category", "all").strip()
    search_q = request.args.get("q", "").strip()
    return render_template(
        "live_earth/index.html",
        category=category,
        search_query=search_q,
        version=PROJECT_VERSION,
    )


@live_earth_bp.route("/api/live-earth/cameras", methods=["GET"])
def api_cameras():
    category = request.args.get("category", "")
    query = request.args.get("q", "")
    cameras = filter_cameras(category=category, query=query)
    return jsonify({
        "status": "success",
        "count": len(cameras),
        "cameras": cameras,
    })


@live_earth_bp.route("/api/live-earth/cameras/<cam_id>", methods=["GET"])
def api_camera_detail(cam_id):
    camera = get_camera_by_id(cam_id)
    if not camera:
        return jsonify({
            "status": "error",
            "message": "No public live camera is available for this location.",
        }), 404
    return jsonify({
        "status": "success",
        "camera": camera,
    })


@live_earth_bp.route("/api/live-earth/satellites", methods=["GET"])
def api_satellites():
    layers = get_weather_satellite_layers()
    return jsonify({
        "status": "success",
        "count": len(layers),
        "layers": layers,
    })


@live_earth_bp.route("/api/live-earth/earth-imagery", methods=["GET"])
def api_earth_imagery():
    layers = get_earth_imagery_layers()
    return jsonify({
        "status": "success",
        "count": len(layers),
        "layers": layers,
    })


@live_earth_bp.route("/api/live-earth/events", methods=["GET"])
def api_events():
    events = get_live_natural_events()
    return jsonify({
        "status": "success",
        "count": len(events),
        "events": events,
    })


@live_earth_bp.route("/api/live-earth/radar-timeline", methods=["GET"])
def api_radar_timeline():
    timeline = get_rainviewer_timeline()
    return jsonify({
        "status": "success",
        "count": len(timeline),
        "timeline": timeline,
    })


@live_earth_bp.route("/api/live-earth/reverse-geocode", methods=["GET"])
def api_reverse_geocode():
    try:
        lat = float(request.args.get("lat", 0.0))
        lon = float(request.args.get("lon", 0.0))
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid lat/lon coordinates"}), 400

    info = reverse_geocode(lat, lon)
    return jsonify({
        "status": "success",
        "location": info,
    })


@live_earth_bp.route("/api/live-earth/weather", methods=["GET"])
def api_weather():
    lat = request.args.get("lat")
    lon = request.args.get("lon")
    q = request.args.get("q")

    try:
        if q and q.strip():
            weather_data = get_weather_report(q.strip())
        elif lat and lon:
            # Geocode reverse first to get city
            loc_info = reverse_geocode(float(lat), float(lon))
            city_name = loc_info.get("city") or f"{float(lat):.2f},{float(lon):.2f}"
            weather_data = get_weather_report(city_name)
        else:
            return jsonify({"status": "error", "message": "Specify q or lat/lon"}), 400

        return jsonify({
            "status": "success",
            "weather": weather_data,
        })
    except Exception as err:
        return jsonify({"status": "error", "message": str(err)}), 500


@live_earth_bp.route("/api/live-earth/ai-assistant", methods=["POST"])
def api_ai_assistant():
    payload = request.get_json() or {}
    user_prompt = payload.get("prompt", "").strip()
    if not user_prompt:
        return jsonify({"status": "error", "message": "Prompt cannot be empty"}), 400

    context = "You are Cozy Earth AI, an intelligent environmental and atmospheric AI assistant. Explain satellite layers, storm tracks, weather anomalies, or travel conditions clearly and professionally."
    ai_response = query_grok(user_prompt, system_context=context)

    return jsonify({
        "status": "success",
        "prompt": user_prompt,
        "response": ai_response,
    })


@live_earth_bp.route("/api/live-earth/search", methods=["GET"])
def api_search():
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({
            "locations": [],
            "cameras": [],
        })
    locations = geocode_location(query)
    cameras = filter_cameras(query=query)
    return jsonify({
        "query": query,
        "locations": locations,
        "cameras": cameras,
    })


@live_earth_bp.route("/api/live-earth/status", methods=["GET"])
def api_status():
    return jsonify({
        "connection_status": "Online",
        "current_source": "Live Earth Multi-Provider Network",
        "last_refresh": datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%S UTC"),
        "providers": [
            "Transport for London (TfL)",
            "NYC DOT",
            "Lagos LASTMA",
            "Shibuya City Traffic",
            "Windy Webcams Network (v3)",
            "NASA EONET Natural Events API",
            "NASA GIBS (EOSDIS)",
            "RainViewer Radar Network",
            "OpenWeatherMap Satellite",
            "CartoDB / OpenStreetMap",
        ],
        "loading_status": "Idle",
    })
