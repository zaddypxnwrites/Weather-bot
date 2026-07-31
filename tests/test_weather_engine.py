import os
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from weather_engine import (
    format_temperature,
    format_wind_speed,
    get_location_suggestions,
    get_weather_report,
    normalize_units,
    select_best_location,
)


def test_prefers_exact_match_for_nigeria_location():
    candidates = [
        {"name": "Emure Ekiti", "state": "Ekiti", "country": "NG", "lat": 7.44, "lon": 5.47},
        {"name": "Akungba", "state": "Ondo", "country": "NG", "lat": 7.47, "lon": 5.74},
    ]

    result = select_best_location("Akungba", candidates)
    assert result["name"] == "Akungba"


def test_normalize_units_defaults_to_metric():
    assert normalize_units("kelvin") == "metric"
    assert normalize_units("imperial") == "imperial"


def test_format_helpers_follow_selected_units():
    assert format_temperature(21.234, "metric") == "21.2 °C"
    assert format_temperature(71.8, "imperial") == "71.8 °F"
    assert format_wind_speed(5.2, "metric") == "5.2 m/s"
    assert format_wind_speed(11.1, "imperial") == "11.1 mph"


def test_get_location_suggestions_formats_candidates(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, timeout):
        assert "geo/1.0/direct" in url
        return FakeResponse(
            [
                {"name": "London", "state": "England", "country": "GB"},
                {"name": "London", "state": "Ontario", "country": "CA"},
            ]
        )

    monkeypatch.setattr("weather_engine.requests.get", fake_get)

    suggestions = get_location_suggestions("London")

    assert suggestions[0]["display_name"] == "London, England, GB"
    assert suggestions[1]["display_name"] == "London, Ontario, CA"


def test_get_location_suggestions_deduplicates_results(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, timeout):
        return FakeResponse(
            [
                {"name": "Laon", "state": "Hauts-de-France", "country": "FR"},
                {"name": "Laon", "state": "Hauts-de-France", "country": "FR"},
            ]
        )

    monkeypatch.setattr("weather_engine.requests.get", fake_get)

    suggestions = get_location_suggestions("Laon")

    assert len(suggestions) == 1
    assert suggestions[0]["display_name"] == "Laon, Hauts-de-France, FR"


def test_get_weather_report_supports_imperial_units(monkeypatch):
    monkeypatch.setenv("OPENWEATHER_API_KEY", "test-key")

    class FakeResponse:
        def __init__(self, payload):
            self._payload = payload

        def raise_for_status(self):
            return None

        def json(self):
            return self._payload

    def fake_get(url, timeout):
        if "/geo/1.0/direct" in url:
            return FakeResponse([
                {"name": "Austin", "state": "Texas", "country": "US", "lat": 30.27, "lon": -97.74}
            ])
        if "/data/2.5/weather" in url:
            return FakeResponse(
                {
                    "timezone": 0,
                    "sys": {"sunrise": 1000, "sunset": 5000, "country": "US"},
                    "main": {"temp": 71.8, "feels_like": 74.1, "humidity": 44, "pressure": 1012},
                    "wind": {"speed": 11.1, "deg": 90},
                    "visibility": 10000,
                    "weather": [{"main": "Clouds", "description": "scattered clouds"}],
                    "name": "Austin",
                }
            )
        if "/data/2.5/air_pollution" in url:
            return FakeResponse({"list": [{"main": {"aqi": 2}}]})
        if "/data/2.5/forecast" in url:
            return FakeResponse(
                {
                    "list": [
                        {
                            "dt": 2000,
                            "main": {"temp": 72.5},
                            "weather": [{"main": "Clouds", "description": "few clouds"}],
                        },
                        {
                            "dt": 3000,
                            "main": {"temp": 70.2},
                            "weather": [{"main": "Rain", "description": "light rain"}],
                        },
                    ]
                }
            )
        raise AssertionError(f"Unexpected URL: {url}")

    monkeypatch.setattr("weather_engine.requests.get", fake_get)

    report = get_weather_report("Austin", units="imperial")

    assert report["units"] == "imperial"
    assert report["temperature"].endswith("°F")
    assert report["wind_speed"].endswith("mph")
    assert report["forecast"]
    assert report["forecast"][0]["temperature"].endswith("°F")
