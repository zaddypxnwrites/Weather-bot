import time
import requests
from config.settings import OPENWEATHER_API_KEY, RAINVIEWER_API_URL

_RAINVIEWER_CACHE = {"timestamp": 0, "url": ""}
_CACHE_TTL = 300  # 5 minutes cache TTL


def get_weather_satellite_layers() -> list[dict]:
    """Retrieve available weather satellite layer overlays with current timestamps."""
    layers = [
        {
            "id": "clouds",
            "name": "Cloud Cover",
            "category": "Satellite",
            "type": "openweathermap",
            "layer_name": "clouds_new",
            "url_template": f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else None,
            "attribution": "Map data &copy; OpenWeatherMap",
            "opacity": 0.65,
            "update_interval": "10-15 minutes",
            "description": "Global infrared cloud cover satellite imagery overlay.",
        },
        {
            "id": "precipitation",
            "name": "Rainfall & Precip Radar",
            "category": "Radar",
            "type": "rainviewer",
            "url_template": get_latest_rainviewer_tile_url(),
            "attribution": "Radar data &copy; RainViewer",
            "opacity": 0.70,
            "update_interval": "10 minutes",
            "description": "Real-time precipitation radar tile overlay sourced from RainViewer network.",
        },
        {
            "id": "temp",
            "name": "Temperature Overlay",
            "category": "Thermodynamic",
            "type": "openweathermap",
            "layer_name": "temp_new",
            "url_template": f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else None,
            "attribution": "Map data &copy; OpenWeatherMap",
            "opacity": 0.50,
            "update_interval": "30 minutes",
            "description": "Global thermal satellite temperature gradient map.",
        },
        {
            "id": "wind",
            "name": "Wind Speed & Vector",
            "category": "Atmospheric",
            "type": "openweathermap",
            "layer_name": "wind_new",
            "url_template": f"https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else None,
            "attribution": "Map data &copy; OpenWeatherMap",
            "opacity": 0.55,
            "update_interval": "30 minutes",
            "description": "Global wind speed velocity layer.",
        },
    ]
    return layers


def get_latest_rainviewer_tile_url() -> str:
    """Fetch the latest RainViewer timestamped radar tile URL template with 5-minute cache."""
    now = time.time()
    if _RAINVIEWER_CACHE["url"] and (now - _RAINVIEWER_CACHE["timestamp"] < _CACHE_TTL):
        return _RAINVIEWER_CACHE["url"]

    try:
        res = requests.get(RAINVIEWER_API_URL, timeout=5)
        res.raise_for_status()
        data = res.json()
        host = data.get("host", "https://tilecache.rainviewer.com")
        radar_past = data.get("radar", {}).get("past", [])
        if radar_past:
            latest = radar_past[-1]
            path = latest.get("path")
            url = f"{host}{path}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
            _RAINVIEWER_CACHE["timestamp"] = now
            _RAINVIEWER_CACHE["url"] = url
            return url
    except Exception:
        pass

    fallback_url = "https://tilecache.rainviewer.com/v2/radar/nowcast/256/{z}/{x}/{y}/2/1_1.png"
    _RAINVIEWER_CACHE["timestamp"] = now
    _RAINVIEWER_CACHE["url"] = fallback_url
    return fallback_url

