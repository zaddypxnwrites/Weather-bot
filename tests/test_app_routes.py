import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import app


def test_forecast_route_selects_timestamp(monkeypatch):
    sample = {
        "city": "London",
        "country": "GB",
        "is_daytime": True,
        "query": "London",
        "forecast": [
            {
                "timestamp": 111,
                "label": "Mon 09 AM",
                "date": "Monday, Jul 31",
                "time": "09:00 AM",
                "icon": "☁️",
                "temperature": "21.0 °C",
                "feels_like": "20.1 °C",
                "description": "Few Clouds",
                "humidity": "80%",
                "pressure": "1008 hPa",
                "wind_speed": "5.0 m/s",
                "wind_direction": "90° (E)",
                "cloudiness": "40%",
                "precipitation_probability": "10%",
                "rain_volume": "0.0 mm",
                "snow_volume": "0.0 mm",
                "visibility": "10.0 km",
            },
            {
                "timestamp": 222,
                "label": "Mon 12 PM",
                "date": "Monday, Jul 31",
                "time": "12:00 PM",
                "icon": "🌧️",
                "temperature": "18.5 °C",
                "feels_like": "17.4 °C",
                "description": "Light Rain",
                "humidity": "88%",
                "pressure": "1002 hPa",
                "wind_speed": "7.0 m/s",
                "wind_direction": "120° (SE)",
                "cloudiness": "76%",
                "precipitation_probability": "66%",
                "rain_volume": "2.1 mm",
                "snow_volume": "0.0 mm",
                "visibility": "8.0 km",
            },
        ],
    }

    monkeypatch.setattr("app.get_weather_report", lambda location, units: sample)

    client = app.test_client()
    response = client.get("/forecast?location=London&units=metric&ts=222")

    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Light Rain" in body
    assert "12:00 PM" in body
    assert "2.1 mm" in body


def test_forecast_route_handles_missing_location():
    client = app.test_client()
    response = client.get("/forecast")

    assert response.status_code == 200
    assert "Missing location" in response.get_data(as_text=True)
