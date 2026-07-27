import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from weather_engine import select_best_location


def test_prefers_exact_match_for_nigeria_location():
    candidates = [
        {"name": "Emure Ekiti", "state": "Ekiti", "country": "NG", "lat": 7.44, "lon": 5.47},
        {"name": "Akungba", "state": "Ondo", "country": "NG", "lat": 7.47, "lon": 5.74},
    ]

    result = select_best_location("Akungba", candidates)
    assert result["name"] == "Akungba"
