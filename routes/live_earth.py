from datetime import datetime, UTC
from flask import Blueprint, jsonify, render_template, request
from services.camera_service import filter_cameras, get_camera_by_id
from services.earth_service import get_earth_imagery_layers
from services.location_service import geocode_location
from services.satellite_service import get_weather_satellite_layers
from weather_engine import PROJECT_VERSION

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
            "NASA GIBS (EOSDIS)",
            "RainViewer Radar Network",
            "OpenWeatherMap Satellite",
            "CartoDB / OpenStreetMap",
        ],
        "loading_status": "Idle",
    })
