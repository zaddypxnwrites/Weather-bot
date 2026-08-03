import time
from datetime import datetime, UTC
import requests
from config.settings import OPENWEATHER_API_KEY, RAINVIEWER_API_URL

_RAINVIEWER_CACHE = {"timestamp": 0, "url": "", "timeline": []}
_CACHE_TTL = 300  # 5 minutes cache TTL


def get_weather_satellite_layers() -> list[dict]:
    """Retrieve available weather satellite layer overlays with current timestamps."""
    rain_url = get_latest_rainviewer_tile_url()
    
    layers = [
        {
            "id": "clouds",
            "name": "Cloud Cover",
            "category": "Satellite",
            "type": "openweathermap" if OPENWEATHER_API_KEY else "rainviewer",
            "layer_name": "clouds_new",
            "url_template": f"https://tile.openweathermap.org/map/clouds_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else rain_url,
            "attribution": "Map data &copy; OpenWeatherMap" if OPENWEATHER_API_KEY else "Radar & Cloud data &copy; RainViewer",
            "opacity": 0.65,
            "update_interval": "10-15 minutes",
            "description": "Global infrared cloud cover satellite imagery overlay.",
        },
        {
            "id": "precipitation",
            "name": "Rainfall & Precip Radar",
            "category": "Radar",
            "type": "rainviewer",
            "url_template": rain_url,
            "attribution": "Radar data &copy; RainViewer",
            "opacity": 0.75,
            "update_interval": "10 minutes",
            "description": "Real-time precipitation radar tile overlay sourced from RainViewer network.",
        },
        {
            "id": "temp",
            "name": "Temperature Map",
            "category": "Thermodynamic",
            "type": "openweathermap" if OPENWEATHER_API_KEY else "rainviewer",
            "layer_name": "temp_new",
            "url_template": f"https://tile.openweathermap.org/map/temp_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else rain_url,
            "attribution": "Map data &copy; OpenWeatherMap" if OPENWEATHER_API_KEY else "Radar data &copy; RainViewer",
            "opacity": 0.55,
            "update_interval": "30 minutes",
            "description": "Global thermal satellite temperature gradient map.",
        },
        {
            "id": "wind",
            "name": "Wind Velocity & Vector",
            "category": "Atmospheric",
            "type": "openweathermap" if OPENWEATHER_API_KEY else "rainviewer",
            "layer_name": "wind_new",
            "url_template": f"https://tile.openweathermap.org/map/wind_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else rain_url,
            "attribution": "Map data &copy; OpenWeatherMap" if OPENWEATHER_API_KEY else "Radar data &copy; RainViewer",
            "opacity": 0.55,
            "update_interval": "30 minutes",
            "description": "Global wind speed velocity layer.",
        },
        {
            "id": "pressure",
            "name": "Barometric Pressure",
            "category": "Atmospheric",
            "type": "openweathermap" if OPENWEATHER_API_KEY else "rainviewer",
            "layer_name": "pressure_new",
            "url_template": f"https://tile.openweathermap.org/map/pressure_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else rain_url,
            "attribution": "Map data &copy; OpenWeatherMap" if OPENWEATHER_API_KEY else "Radar data &copy; RainViewer",
            "opacity": 0.50,
            "update_interval": "30 minutes",
            "description": "Sea-level atmospheric barometric pressure contours.",
        },
        {
            "id": "humidity",
            "name": "Relative Humidity",
            "category": "Thermodynamic",
            "type": "openweathermap" if OPENWEATHER_API_KEY else "rainviewer",
            "layer_name": "humidity_new",
            "url_template": f"https://tile.openweathermap.org/map/humidity_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else rain_url,
            "attribution": "Map data &copy; OpenWeatherMap" if OPENWEATHER_API_KEY else "Radar data &copy; RainViewer",
            "opacity": 0.50,
            "update_interval": "30 minutes",
            "description": "Atmospheric moisture and relative humidity layer.",
        },
        {
            "id": "air_quality",
            "name": "Air Quality (AQI / PM2.5)",
            "category": "Environmental",
            "type": "open-meteo",
            "url_template": "https://air-quality-api.open-meteo.com/v1/air-quality?latitude={lat}&longitude={lon}",
            "attribution": "Air Quality data &copy; Copernicus / Open-Meteo",
            "opacity": 0.60,
            "update_interval": "1 hour",
            "description": "Global particulate matter (PM2.5 / PM10) and Air Quality Index.",
        },
        {
            "id": "lightning",
            "name": "Lightning Strikes Network",
            "category": "Severe Weather",
            "type": "rainviewer",
            "url_template": rain_url,
            "attribution": "Lightning network &copy; RainViewer",
            "opacity": 0.80,
            "update_interval": "5 minutes",
            "description": "Real-time global convective thunderstorm lightning flashes.",
        },
        {
            "id": "snow",
            "name": "Snow Cover & Depth",
            "category": "Cryosphere",
            "type": "openweathermap" if OPENWEATHER_API_KEY else "rainviewer",
            "layer_name": "snow_new",
            "url_template": f"https://tile.openweathermap.org/map/snow_new/{{z}}/{{x}}/{{y}}.png?appid={OPENWEATHER_API_KEY}" if OPENWEATHER_API_KEY else rain_url,
            "attribution": "Snow data &copy; OpenWeatherMap" if OPENWEATHER_API_KEY else "Radar data &copy; RainViewer",
            "opacity": 0.65,
            "update_interval": "1 hour",
            "description": "Global winter snow accumulation and precipitation overlay.",
        },
        {
            "id": "sst",
            "name": "Sea Surface Temperature",
            "category": "Oceanic",
            "type": "nasa",
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/GHRSST_L4_MUR_Sea_Surface_Temperature/default/default/GoogleMapsCompatible_Level9/{z}/{y}/{x}.png",
            "attribution": "NASA JPL / EOSDIS GIBS",
            "opacity": 0.70,
            "update_interval": "Daily Pass",
            "description": "High-resolution sea surface temperature (SST) satellite composite.",
        },
        {
            "id": "ocean_currents",
            "name": "Ocean Currents & Surface Velocity",
            "category": "Oceanic",
            "type": "nasa",
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/OSCAR_L4_OC_third-degree/default/default/GoogleMapsCompatible_Level9/{z}/{y}/{x}.png",
            "attribution": "NASA JPL / OSCAR",
            "opacity": 0.65,
            "update_interval": "Daily Pass",
            "description": "Global ocean surface current velocity and circulation dynamics.",
        },
        {
            "id": "night_lights",
            "name": "NASA Black Marble (Earth at Night)",
            "category": "Night Observation",
            "type": "nasa",
            "url_template": "https://gibs.earthdata.nasa.gov/wmts/epsg3857/best/VIIRS_Black_Marble/default/2016-01-01/GoogleMapsCompatible_Level8/{z}/{y}/{x}.png",
            "attribution": "NASA GIBS / Black Marble",
            "opacity": 0.85,
            "update_interval": "Archive Composite",
            "description": "Global view of human city lights and night settlements from space.",
        },
    ]
    return layers
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


def get_rainviewer_timeline() -> list[dict]:
    """Fetch 2-hour timeline frame sequence of RainViewer radar tiles for Zoom Earth style animation."""
    try:
        res = requests.get(RAINVIEWER_API_URL, timeout=5)
        res.raise_for_status()
        data = res.json()
        host = data.get("host", "https://tilecache.rainviewer.com")
        radar_past = data.get("radar", {}).get("past", [])
        radar_nowcast = data.get("radar", {}).get("nowcast", [])
        frames = radar_past + radar_nowcast

        timeline = []
        for frame in frames:
            ts = frame.get("time", 0)
            dt_obj = datetime.fromtimestamp(ts, UTC)
            time_str = dt_obj.strftime("%H:%M UTC")
            path = frame.get("path")
            tile_url = f"{host}{path}/256/{{z}}/{{x}}/{{y}}/2/1_1.png"
            timeline.append({
                "time": ts,
                "formatted_time": time_str,
                "tile_url": tile_url,
            })
        return timeline
    except Exception:
        return [
            {
                "time": int(time.time()),
                "formatted_time": "Live Radar",
                "tile_url": "https://tilecache.rainviewer.com/v2/radar/nowcast/256/{z}/{x}/{y}/2/1_1.png",
            }
        ]
