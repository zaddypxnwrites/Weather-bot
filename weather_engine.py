import os

import requests
from datetime import datetime, timedelta, UTC
from urllib.parse import quote

api_key = os.getenv("OPENWEATHER_API_KEY", "")
BASE_URL = "https://api.openweathermap.org"


def get_weather_report(location):
    if not location or not location.strip():
        raise ValueError("Please enter a city name.")

    if not api_key:
        raise RuntimeError("OPENWEATHER_API_KEY is not configured on this server.")

    encoded_location = quote(location.strip())

    geo_url = (
        f"{BASE_URL}/geo/1.0/direct"
        f"?q={encoded_location}&limit=5&appid={api_key}"
    )

    try:
        geo_response = requests.get(geo_url, timeout=10)
        geo_response.raise_for_status()
        geo_data = geo_response.json()

        if not geo_data:
            raise ValueError("Location not found.")

        best_match = geo_data[0]
        lat = best_match["lat"]
        lon = best_match["lon"]

    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Unable to locate that place.") from exc

    weather_url = (
        f"{BASE_URL}/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    )

    try:
        response = requests.get(weather_url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.HTTPError as exc:
        raise RuntimeError("Unable to retrieve weather data.") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Network error. Please check your internet connection.") from exc

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

    timezone = data["timezone"]
    utc_now = datetime.now(UTC)
    local_time = utc_now + timedelta(seconds=timezone)
    sunrise = datetime.fromtimestamp(data["sys"]["sunrise"], tz=UTC) + timedelta(seconds=timezone)
    sunset = datetime.fromtimestamp(data["sys"]["sunset"], tz=UTC) + timedelta(seconds=timezone)

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