import os
from pathlib import Path

import requests
from datetime import datetime, timedelta, UTC
from urllib.parse import quote

BASE_URL = "https://api.openweathermap.org"
PROJECT_VERSION = "1.0.0"
DEFAULT_UNITS = "metric"

UNIT_CONFIG = {
    "metric": {"temperature_symbol": "°C", "wind_speed_unit": "m/s", "label": "Celsius"},
    "imperial": {"temperature_symbol": "°F", "wind_speed_unit": "mph", "label": "Fahrenheit"},
}


def get_api_key():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if api_key:
        return api_key

    _load_dotenv()
    api_key = os.getenv("OPENWEATHER_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OpenWeatherMap API key is missing. "
            "Set OPENWEATHER_API_KEY in the environment or add it to a local .env file."
        )

    return api_key


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


def normalize_units(units):
    normalized = str(units or DEFAULT_UNITS).strip().lower()
    if normalized not in UNIT_CONFIG:
        return DEFAULT_UNITS
    return normalized


def format_temperature(value, units):
    config = UNIT_CONFIG[normalize_units(units)]
    return f"{value:.1f} {config['temperature_symbol']}"


def format_wind_speed(value, units):
    config = UNIT_CONFIG[normalize_units(units)]
    return f"{value:.1f} {config['wind_speed_unit']}"


def country_code_to_flag(country_code):
    code = str(country_code or "").strip().upper()
    if len(code) != 2 or not code.isalpha():
        return "🌍"
    return "".join(chr(127397 + ord(char)) for char in code)


def build_wear_advice(temp_value, weather_main, weather_description, wind_speed, units):
    temp_c = float(temp_value)
    if normalize_units(units) == "imperial":
        temp_c = (temp_c - 32) * 5 / 9

    lower_desc = str(weather_description or "").lower()
    lower_main = str(weather_main or "").lower()
    tips = []

    if temp_c < 0:
        tips.append("Heavy coat, thermal layers, gloves, and warm boots.")
    elif temp_c < 10:
        tips.append("Jacket or hoodie with full-length trousers.")
    elif temp_c < 18:
        tips.append("Light sweater or long-sleeve with comfortable layers.")
    elif temp_c < 27:
        tips.append("T-shirt or light top with breathable layers.")
    else:
        tips.append("Very light, breathable outfit and stay hydrated.")

    if any(token in lower_desc for token in ["rain", "drizzle", "thunder", "shower"]):
        tips.append("Carry an umbrella or rain jacket.")
    if "snow" in lower_desc or "ice" in lower_desc:
        tips.append("Use waterproof boots and insulated outerwear.")
    if "mist" in lower_desc or "fog" in lower_desc or "haze" in lower_desc:
        tips.append("Wear visible layers for low-visibility conditions.")

    wind_value = float(wind_speed or 0)
    windy_threshold = 7 if normalize_units(units) == "metric" else 16
    if wind_value >= windy_threshold:
        tips.append("Add a windproof outer layer.")

    if not tips:
        tips.append("Comfortable casual wear should be fine.")

    return " ".join(tips[:3])


def wind_direction_from_degrees(degrees):
    directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return directions[round(float(degrees) / 45) % 8]


def get_location_suggestions(query, limit=5):
    if not query or not query.strip():
        return []

    api_key = get_api_key()
    encoded_location = quote(query.strip())
    geo_url = (
        f"{BASE_URL}/geo/1.0/direct"
        f"?q={encoded_location}&limit={max(1, min(int(limit), 8))}&appid={api_key}"
    )

    try:
        response = requests.get(geo_url, timeout=10)
        response.raise_for_status()
        candidates = response.json()
    except requests.exceptions.RequestException:
        return []

    suggestions = []
    seen = set()
    for candidate in candidates[: max(1, min(int(limit), 8))]:
        if not isinstance(candidate, dict):
            continue

        parts = [candidate.get("name", "")]
        if candidate.get("state"):
            parts.append(candidate["state"])
        if candidate.get("country"):
            parts.append(candidate["country"])

        display_name = ", ".join(part for part in parts if part)
        key = display_name.lower()
        if not display_name or key in seen:
            continue
        seen.add(key)
        suggestions.append(
            {
                "name": candidate.get("name", ""),
                "state": candidate.get("state", ""),
                "country": candidate.get("country", ""),
                "display_name": display_name,
            }
        )

    return suggestions


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


def get_weather_report(location, units=DEFAULT_UNITS):
    if not location or not location.strip():
        raise ValueError("Please enter a city name.")

    units = normalize_units(units)
    encoded_location = quote(location.strip())

    api_key = get_api_key()
    geo_url = (
        f"{BASE_URL}/geo/1.0/direct"
        f"?q={encoded_location}&limit=5&appid={api_key}"
    )

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
        f"?lat={lat}&lon={lon}&appid={api_key}&units={units}"
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

    timezone = data["timezone"]
    utc_now = datetime.now(UTC)
    local_time = utc_now + timedelta(seconds=timezone)
    sunrise = datetime.fromtimestamp(
        data["sys"]["sunrise"], tz=UTC
    ) + timedelta(seconds=timezone)
    sunset = datetime.fromtimestamp(
        data["sys"]["sunset"], tz=UTC
    ) + timedelta(seconds=timezone)
    is_daytime = sunrise <= utc_now + timedelta(seconds=timezone) < sunset

    air_url = (
        f"{BASE_URL}/data/2.5/air_pollution"
        f"?lat={lat}&lon={lon}&appid={api_key}"
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

    forecast_url = (
        f"{BASE_URL}/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={api_key}&units={units}"
    )

    forecast_items = []
    try:
        forecast_response = requests.get(forecast_url, timeout=10)
        forecast_response.raise_for_status()
        forecast_data = forecast_response.json()
        for item in forecast_data.get("list", [])[:4]:
            item_time = datetime.fromtimestamp(item["dt"], tz=UTC) + timedelta(seconds=timezone)
            pod = item.get("sys", {}).get("pod")
            if pod in {"d", "n"}:
                forecast_is_daytime = pod == "d"
            else:
                forecast_is_daytime = 6 <= item_time.hour < 18
            wind_deg = item.get("wind", {}).get("deg")
            wind_direction = (
                f"{int(round(wind_deg))}° ({wind_direction_from_degrees(wind_deg)})"
                if wind_deg is not None
                else "N/A"
            )
            pop_value = item.get("pop")
            rain_mm = item.get("rain", {}).get("3h")
            snow_mm = item.get("snow", {}).get("3h")
            visibility_m = item.get("visibility")
            forecast_wear_advice = build_wear_advice(
                item["main"]["temp"],
                item["weather"][0].get("main", ""),
                item["weather"][0].get("description", ""),
                item.get("wind", {}).get("speed", 0),
                units,
            )
            forecast_items.append(
                {
                    "timestamp": item["dt"],
                    "date": item_time.strftime("%A, %b %d"),
                    "time": item_time.strftime("%I:%M %p"),
                    "label": item_time.strftime("%a %I %p"),
                    "icon": weather_icons.get(item["weather"][0]["main"], "🌍"),
                    "is_daytime": forecast_is_daytime,
                    "temperature": format_temperature(item["main"]["temp"], units),
                    "feels_like": format_temperature(item["main"].get("feels_like", item["main"]["temp"]), units),
                    "description": item["weather"][0]["description"].title(),
                    "weather_main": item["weather"][0]["main"],
                    "humidity": f"{item['main'].get('humidity', 0)}%",
                    "pressure": f"{item['main'].get('pressure', 0)} hPa",
                    "wind_speed": format_wind_speed(item.get("wind", {}).get("speed", 0), units),
                    "wind_direction": wind_direction,
                    "cloudiness": f"{item.get('clouds', {}).get('all', 0)}%",
                    "precipitation_probability": f"{(float(pop_value) * 100):.0f}%" if pop_value is not None else "N/A",
                    "rain_volume": f"{float(rain_mm):.1f} mm" if rain_mm is not None else "0.0 mm",
                    "snow_volume": f"{float(snow_mm):.1f} mm" if snow_mm is not None else "0.0 mm",
                    "visibility": f"{(float(visibility_m) / 1000):.1f} km" if visibility_m is not None else "N/A",
                    "wear_advice": forecast_wear_advice,
                }
            )
    except requests.exceptions.RequestException:
        forecast_items = []
    except (KeyError, IndexError, TypeError, ValueError):
        forecast_items = []

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

    weather_emoji = weather_icons.get(weather, "🌍")

    deg = data["wind"]["deg"]
    direction = wind_direction_from_degrees(deg)

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
    unit_config = UNIT_CONFIG[units]
    country_code = data["sys"].get("country", "")
    country_flag = country_code_to_flag(country_code)
    wear_advice = build_wear_advice(
        temp,
        weather,
        data["weather"][0]["description"],
        data["wind"].get("speed", 0),
        units,
    )

    return {
        "city": data["name"],
        "country": country_code,
        "country_flag": country_flag,
        "local_time": local_time.strftime("%I:%M %p"),
        "sunrise": sunrise.strftime("%I:%M %p"),
        "sunset": sunset.strftime("%I:%M %p"),
        "is_daytime": is_daytime,
        "temperature": format_temperature(temp, units),
        "temperature_emoji": temp_emoji,
        "feels_like": format_temperature(feels, units),
        "feels_like_emoji": feels_emoji,
        "humidity": f"{data['main']['humidity']}%",
        "pressure": f"{data['main']['pressure']} hPa",
        "wind_speed": format_wind_speed(data['wind']['speed'], units),
        "wind_direction": f"{deg}° ({direction})",
        "visibility": f"{visibility_km:.1f} km",
        "latitude": f"{lat:.4f}",
        "longitude": f"{lon:.4f}",
        "air_quality": air,
        "weather": f"{weather_emoji} {data['weather'][0]['description'].title()}",
        "weather_icon": weather_emoji,
        "weather_main": weather,
        "weather_description": data["weather"][0]["description"].title(),
        "wear_advice": wear_advice,
        "wind_unit": unit_config["wind_speed_unit"],
        "temperature_unit": unit_config["temperature_symbol"],
        "units": units,
        "units_label": unit_config["label"],
        "forecast": forecast_items,
        "query": location.strip(),
    }