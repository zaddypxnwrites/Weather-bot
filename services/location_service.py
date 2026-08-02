from functools import lru_cache
import requests
from urllib.parse import quote
from config.settings import OPENWEATHER_API_KEY


@lru_cache(maxsize=128)
def geocode_location(query: str) -> list[dict]:
    """Search for locations using OpenWeatherMap Direct Geocoding API or fallback suggestions."""
    if not query or not query.strip():
        return []

    if not OPENWEATHER_API_KEY:
        return []

    encoded_query = quote(query.strip())
    geo_url = f"https://api.openweathermap.org/geo/1.0/direct?q={encoded_query}&limit=6&appid={OPENWEATHER_API_KEY}"

    try:
        res = requests.get(geo_url, timeout=6)
        res.raise_for_status()
        data = res.json()
        results = []
        for item in data:
            if not isinstance(item, dict):
                continue
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
                "lat": lat,
                "lon": lon,
            })
        return results
    except Exception:
        return []
