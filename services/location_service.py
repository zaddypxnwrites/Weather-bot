from functools import lru_cache
import requests
from urllib.parse import quote
from config.settings import OPENWEATHER_API_KEY


@lru_cache(maxsize=128)
def geocode_location(query: str) -> list[dict]:
    """Search for locations using OpenWeatherMap Direct Geocoding API or Nominatim fallback."""
    if not query or not query.strip():
        return []

    q = query.strip()
    results = []

    if OPENWEATHER_API_KEY:
        try:
            encoded_query = quote(q)
            geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={encoded_query}&limit=6&appid={OPENWEATHER_API_KEY}"
            res = requests.get(geo_url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                for item in data:
                    if isinstance(item, dict):
                        name = item.get("name", "")
                        state = item.get("state", "")
                        country = item.get("country", "")
                        lat = item.get("lat", 0.0)
                        lon = item.get("lon", 0.0)
                        parts = [p for p in [name, state, country] if p]
                        results.append({
                            "display_name": ", ".join(parts),
                            "name": name,
                            "state": state,
                            "country": country,
                            "lat": float(lat),
                            "lon": float(lon),
                        })
        except Exception:
            pass

    if not results:
        results = geocode_nominatim(q)

    return results


def geocode_nominatim(query: str) -> list[dict]:
    """Fallback geocoder using OpenStreetMap Nominatim API."""
    try:
        url = f"https://nominatim.openstreetmap.org/search?format=json&q={quote(query)}&limit=6"
        headers = {"User-Agent": "CozyWeatherBot/1.0 (LiveEarthPlatform)"}
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            results = []
            for item in data:
                display_name = item.get("display_name", "")
                lat = float(item.get("lat", 0.0))
                lon = float(item.get("lon", 0.0))
                name = item.get("name") or display_name.split(",")[0]
                results.append({
                    "display_name": display_name,
                    "name": name,
                    "state": "",
                    "country": "",
                    "lat": lat,
                    "lon": lon,
                })
            return results
    except Exception:
        pass
    return []

