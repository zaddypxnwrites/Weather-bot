import os
from pathlib import Path

import requests
from datetime import datetime, timedelta, UTC
from urllib.parse import quote

BASE_URL = "https://api.openweathermap.org"
API_KEY = os.getenv("OPENWEATHER_API_KEY")


def select_best_location(query, candidates):
    if not candidates:
        return None

    def normalize_text(value):
        return " ".join(str(value).lower().replace("-", " ").replace("_", " ").split())

    normalized_query = normalize_text(query)
    query_tokens = set(token for token in normalized_query.split() if len(token) > 1)

    exact_name_matches = [
        candidate
        for candidate in candidates
        if isinstance(candidate, dict)
        and normalize_text(candidate.get("name", "")) == normalized_query
    ]
    if exact_name_matches:
        return exact_name_matches[0]

    def score(candidate):
        if not isinstance(candidate, dict):
            return -9999

        name = str(candidate.get("name", "")).strip()
        state = str(candidate.get("state", "")).strip()
        country = str(candidate.get("country", "")).strip()
        full_name = normalize_text(" ".join(part for part in [name, state, country] if part))
        name_norm = normalize_text(name)
        state_norm = normalize_text(state)
        country_norm = normalize_text(country)

        score_value = 0
        if normalized_query == full_name:
            score_value += 100
        if normalized_query in full_name:
            score_value += 30
        if normalized_query.startswith(name_norm) or name_norm.startswith(normalized_query):
            score_value += 20

        candidate_tokens = set(token for token in full_name.split() if len(token) > 1)
        overlap = len(query_tokens & candidate_tokens)
        score_value += overlap * 12

        if country_norm == "ng" or country_norm == "nigeria":
            score_value += 4

        if normalized_query == name_norm:
            score_value += 25

        if state_norm and normalized_query in state_norm:
            score_value += 8

        return score_value

    best_candidate = max(candidates, key=score)
    if score(best_candidate) <= 0:
        return candidates[0]
    return best_candidate


def _load_dotenv():
    env_path = Path(__file__).resolve().parent / ".env"
    if not env_path.exists():
        return

    with env_path.open("r", encoding="utf-8") as env_file:
        for line in env_file:
            text = line.strip()
            if not text or text.startswith("#") or "=" not in text:
                continue

            key, value = text.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value


if not API_KEY:
    _load_dotenv()
    API_KEY = os.getenv("OPENWEATHER_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "OpenWeatherMap API key is missing. "
        "Set OPENWEATHER_API_KEY in the environment or add it to a local .env file."
    )


def get_weather_report(location):
    if not location or not location.strip():
        raise ValueError("Please enter a city name.")

    encoded_location = quote(location.strip())

    geo_url = (
        f"{BASE_URL}/geo/1.0/direct"
        f"?q={encoded_location}&limit=5&appid={API_KEY}"
    )

    try:
        geo_response = requests.get(geo_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            raise ValueError("Location not found.")

        best_match = select_best_location(location, geo_data)
        if not best_match:
            raise ValueError("Location not found.")

        lat = best_match["lat"]
        lon = best_match["lon"]

    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Unable to locate that place.") from exc

    weather_url = (
        f"{BASE_URL}/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
    )

    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError("Unable to retrieve weather data.") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError(
            "Network error. Please check your internet connection."
        ) from exc

    air_url = (
        f"{BASE_URL}/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={API_KEY}"
    )

    try:
        air_response = requests.get(air_url, timeout=10)
        air_response.raise_for_status()
        air_data = air_response.json()
        aqi = air_data["list"][0]["main"]["aqi"]
    except requests.exceptions.RequestException:
        aqi = None
    except (KeyError, IndexError, ValueError):
        aqi = None

    timezone = data["timezone"]
    utc_now = datetime.now(UTC)
    local_time = utc_now + timedelta(seconds=timezone)
    sunrise = datetime.fromtimestamp(
        data["sys"]["sunrise"], tz=UTC
    ) + timedelta(seconds=timezone)
    sunset = datetime.fromtimestamp(
        data["sys"]["sunset"], tz=UTC
    ) + timedelta(seconds=timezone)

    temp = data["main"]["temp"]
    feels = data["main"]["feels_like"]

    if temp < 10:
        temp_emoji = "🥶"
    elif temp < 30:
        temp_emoji = "🌤️"
    else:
        temp_emoji = "🥵"

    if feels < 10:
        feels_emoji = "🥶"
    elif feels < 30:
        feels_emoji = "🌤️"
    else:
        feels_emoji = "🥵"

    weather = data["weather"][0]["main"]

    weather_icons = {
        "Clear": "☀️",
        "Clouds": "☁️",
        "Rain": "🌧️",
        "Drizzle": "🌦️",
        "Thunderstorm": "⛈️",
        "Snow": "❄️",
        "Mist": "🌫️",
        "Fog": "🌫️",
        "Smoke": "💨",
        "Haze": "🌁",
        "Dust": "🌪️",
        "Sand": "🏜️",
        "Ash": "🌋",
        "Squall": "💨",
        "Tornado": "🌪️",
    }

    weather_emoji = weather_icons.get(weather, "🌍")

    deg = data["wind"]["deg"]
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    direction = directions[round(deg / 45) % 8]

    if aqi == 1:
        air = "🌿 Excellent"
    elif aqi == 2:
        air = "😊 Good"
    elif aqi == 3:
        air = "😷 Moderate"
    elif aqi == 4:
        air = "⚠️ Poor"
    elif aqi == 5:
        air = "☠️ Very Poor"
    else:
        air = "❓ Unavailable"

    visibility_km = data["visibility"] / 1000

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "local_time": local_time.strftime("%I:%M %p"),
        "sunrise": sunrise.strftime("%I:%M %p"),
        "sunset": sunset.strftime("%I:%M %p"),
        "temperature": f"{temp_emoji} {temp:.1f} °C",
        "feels_like": f"{feels_emoji} {feels:.1f} °C",
        "humidity": f"{data['main']['humidity']}%",
        "pressure": f"{data['main']['pressure']} hPa",
        "wind_speed": f"{data['wind']['speed']} m/s",
        "wind_direction": f"{deg}° ({direction})",
        "visibility": f"{visibility_km:.1f} km",
        "latitude": f"{lat:.4f}",
        "longitude": f"{lon:.4f}",
        "air_quality": air,
        "weather": f"{weather_emoji} {data['weather'][0]['description'].title()}",
    }