"""Greek (and a few international) place presets with lat/lng + IANA timezone."""
from __future__ import annotations

PLACE_PRESETS: list[dict] = [
    {"name": "Αθήνα", "latitude": 37.9838, "longitude": 23.7275, "timezone": "Europe/Athens"},
    {"name": "Θεσσαλονίκη", "latitude": 40.6401, "longitude": 22.9444, "timezone": "Europe/Athens"},
    {"name": "Πάτρα", "latitude": 38.2466, "longitude": 21.7346, "timezone": "Europe/Athens"},
    {"name": "Ηράκλειο", "latitude": 35.3387, "longitude": 25.1442, "timezone": "Europe/Athens"},
    {"name": "Λάρισα", "latitude": 39.639, "longitude": 22.4191, "timezone": "Europe/Athens"},
    {"name": "Ιωάννινα", "latitude": 39.665, "longitude": 20.8537, "timezone": "Europe/Athens"},
    {"name": "Ρόδος", "latitude": 36.4349, "longitude": 28.2176, "timezone": "Europe/Athens"},
    {"name": "Λευκωσία", "latitude": 35.1856, "longitude": 33.3823, "timezone": "Asia/Nicosia"},
    {"name": "Βουκουρέστι", "latitude": 44.4268, "longitude": 26.1025, "timezone": "Europe/Bucharest"},
    {"name": "London", "latitude": 51.5074, "longitude": -0.1278, "timezone": "Europe/London"},
    {"name": "New York", "latitude": 40.7128, "longitude": -74.006, "timezone": "America/New_York"},
]

PRESET_NAMES = [p["name"] for p in PLACE_PRESETS]

# Common IANA zones for manual override
TIMEZONE_OPTIONS = [
    "Europe/Athens",
    "Europe/Bucharest",
    "Asia/Nicosia",
    "Europe/London",
    "Europe/Berlin",
    "Europe/Paris",
    "America/New_York",
    "America/Los_Angeles",
    "UTC",
]


def get_preset(name: str) -> dict | None:
    for p in PLACE_PRESETS:
        if p["name"] == name:
            return p
    return None
