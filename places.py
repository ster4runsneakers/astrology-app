"""Greek (and a few international) place presets with lat/lng."""
from __future__ import annotations

PLACE_PRESETS: list[dict] = [
    {"name": "Αθήνα", "latitude": 37.9838, "longitude": 23.7275},
    {"name": "Θεσσαλονίκη", "latitude": 40.6401, "longitude": 22.9444},
    {"name": "Πάτρα", "latitude": 38.2466, "longitude": 21.7346},
    {"name": "Ηράκλειο", "latitude": 35.3387, "longitude": 25.1442},
    {"name": "Λάρισα", "latitude": 39.639, "longitude": 22.4191},
    {"name": "Ιωάννινα", "latitude": 39.665, "longitude": 20.8537},
    {"name": "Ρόδος", "latitude": 36.4349, "longitude": 28.2176},
    {"name": "Λευκωσία", "latitude": 35.1856, "longitude": 33.3823},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278},
    {"name": "New York", "latitude": 40.7128, "longitude": -74.006},
]

PRESET_NAMES = [p["name"] for p in PLACE_PRESETS]


def get_preset(name: str) -> dict | None:
    for p in PLACE_PRESETS:
        if p["name"] == name:
            return p
    return None
