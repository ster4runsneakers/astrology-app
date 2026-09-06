"""
Natal chart via Skyfield + JPL DE421 ephemeris (free, no paid APIs).

- Geocentric apparent ecliptic longitudes (tropical).
- Ascendant from local sidereal time + obliquity (when birth time known).
- Equal House cusps when Asc is available.
- Without time: noon local (longitude offset) and approximate=True (no Asc/houses).
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import lru_cache
from pathlib import Path
from typing import Optional

from skyfield.api import Loader
from skyfield.framelib import ecliptic_frame

from zodiac import (
    ZodiacInfo,
    ZodiacSignId,
    degree_in_sign,
    format_degree,
    longitude_to_sign,
    normalize_longitude,
    sun_sign_from_date,
)

# Cache ephemeris under project data/ so Streamlit Cloud reuses it across reruns.
_DATA_DIR = Path(__file__).resolve().parent / "data"
_DATA_DIR.mkdir(parents=True, exist_ok=True)

PLANET_DEFS = [
    ("sun", "Ήλιος", "Sun", "sun"),
    ("moon", "Σελήνη", "Moon", "moon"),
    ("mercury", "Ερμής", "Mercury", "mercury"),
    ("venus", "Αφροδίτη", "Venus", "venus"),
    ("mars", "Άρης", "Mars", "mars"),
    ("jupiter", "Δίας", "Jupiter", "jupiter barycenter"),
    ("saturn", "Κρόνος", "Saturn", "saturn barycenter"),
]


@dataclass
class BirthProfile:
    name: str = ""
    date_of_birth: str = "1990-06-15"  # YYYY-MM-DD
    birth_time: str = "12:00"  # HH:MM
    time_unknown: bool = True
    place_name: str = "Αθήνα"
    latitude: float = 37.9838
    longitude: float = 23.7275


@dataclass
class PlanetPosition:
    id: str
    name_el: str
    name_en: str
    longitude: float
    sign: ZodiacSignId
    sign_el: str
    degree_in_sign: float
    formatted: str


@dataclass
class HouseCusp:
    number: int
    longitude: float
    sign: ZodiacSignId
    sign_el: str
    degree_in_sign: float
    formatted: str


@dataclass
class NatalChart:
    planets: list[PlanetPosition]
    ascendant: Optional[PlanetPosition]
    houses: Optional[list[HouseCusp]]
    approximate: bool
    julian_day: float
    notes: list[str] = field(default_factory=list)


DEFAULT_PROFILE = BirthProfile()


@lru_cache(maxsize=1)
def _load_ephemeris():
    """Load Skyfield timescale + DE421 (downloads once into data/)."""
    load = Loader(str(_DATA_DIR))
    ts = load.timescale()
    eph = load("de421.bsp")
    return ts, eph


def _to_planet_position(pid: str, name_el: str, name_en: str, longitude: float) -> PlanetPosition:
    sign = longitude_to_sign(longitude)
    deg = degree_in_sign(longitude)
    return PlanetPosition(
        id=pid,
        name_el=name_el,
        name_en=name_en,
        longitude=longitude,
        sign=sign.id,
        sign_el=sign.name_el,
        degree_in_sign=deg,
        formatted=f"{sign.symbol} {sign.name_el} {format_degree(longitude)}",
    )


def _parse_profile_datetime(profile: BirthProfile) -> datetime:
    y, m, d = (int(x) for x in profile.date_of_birth.split("-"))
    hour, minute = 12, 0
    if not profile.time_unknown and profile.birth_time:
        parts = profile.birth_time.split(":")
        hour = int(parts[0])
        minute = int(parts[1]) if len(parts) > 1 else 0

    # Treat clock as local mean time ≈ longitude/15h offset from UTC.
    offset_hours = profile.longitude / 15.0
    local_as_utc = datetime(y, m, d, hour, minute, 0, tzinfo=timezone.utc)
    # Subtract offset: east longitude → local ahead of UTC → UTC = local - offset
    utc_seconds = local_as_utc.timestamp() - offset_hours * 3600.0
    return datetime.fromtimestamp(utc_seconds, tz=timezone.utc)


def _ecliptic_longitude(eph, body_name: str, t) -> float:
    earth = eph["earth"]
    body = eph[body_name]
    astrometric = earth.at(t).observe(body)
    # Apparent place (light-time + deflection approx via apparent())
    apparent = astrometric.apparent()
    lat, lon, _ = apparent.frame_latlon(ecliptic_frame)
    return normalize_longitude(lon.degrees)


def _obliquity_degrees(jd_tt: float) -> float:
    # IAU 2000 approx; T in Julian centuries from J2000.0
    T = (jd_tt - 2451545.0) / 36525.0
    return 23.439291 - 0.0130042 * T


def _gmst_degrees(t) -> float:
    # Skyfield: gast is apparent sidereal time in hours; use GMST via gmst
    # t.gmst is in hours
    return normalize_longitude(t.gmst * 15.0)


def _calculate_ascendant(ramc_deg: float, latitude_deg: float, eps_deg: float) -> float:
    ramc = math.radians(ramc_deg)
    lat = math.radians(latitude_deg)
    eps = math.radians(eps_deg)
    y = -math.cos(ramc)
    x = math.sin(ramc) * math.cos(eps) + math.tan(lat) * math.sin(eps)
    asc = math.degrees(math.atan2(y, x))
    return normalize_longitude(asc)


def _equal_houses(ascendant_lon: float) -> list[HouseCusp]:
    houses: list[HouseCusp] = []
    for i in range(12):
        lon = normalize_longitude(ascendant_lon + i * 30.0)
        sign = longitude_to_sign(lon)
        houses.append(
            HouseCusp(
                number=i + 1,
                longitude=lon,
                sign=sign.id,
                sign_el=sign.name_el,
                degree_in_sign=degree_in_sign(lon),
                formatted=f"{sign.symbol} {sign.name_el} {format_degree(lon)}",
            )
        )
    return houses


def compute_natal_chart(profile: BirthProfile) -> NatalChart:
    ts, eph = _load_ephemeris()
    utc_dt = _parse_profile_datetime(profile)
    t = ts.from_datetime(utc_dt)
    approximate = profile.time_unknown or not profile.birth_time
    notes: list[str] = []

    planets: list[PlanetPosition] = []
    for pid, name_el, name_en, body_name in PLANET_DEFS:
        lon = _ecliptic_longitude(eph, body_name, t)
        planets.append(_to_planet_position(pid, name_el, name_en, lon))

    ascendant: Optional[PlanetPosition] = None
    houses: Optional[list[HouseCusp]] = None

    if not approximate:
        gmst = _gmst_degrees(t)
        lst = normalize_longitude(gmst + profile.longitude)
        eps = _obliquity_degrees(t.tt)
        asc_lon = _calculate_ascendant(lst, profile.latitude, eps)
        ascendant = _to_planet_position("asc", "Ωροσκόπος", "Ascendant", asc_lon)
        houses = _equal_houses(asc_lon)
    else:
        notes.append(
            "Ώρα γέννησης άγνωστη ή προσεγγιστική (μεσημέρι) — "
            "χωρίς Ωροσκόπο / οίκους. Οι θέσεις πλανητών είναι κατά προσέγγιση."
        )

    notes.append(
        "Εφήμεριδα: Skyfield + JPL DE421 · τροπικό ζώδιο · Equal House · "
        "ώρα ≈ τοπική μέσω γεωγρ. μήκους (χωρίς IANA TZ)."
    )

    return NatalChart(
        planets=planets,
        ascendant=ascendant,
        houses=houses,
        approximate=approximate,
        julian_day=float(t.tt),
        notes=notes,
    )


def get_sun_sign_from_profile(profile: BirthProfile) -> ZodiacInfo:
    y, m, d = (int(x) for x in profile.date_of_birth.split("-"))
    return sun_sign_from_date(y, m, d)


def ensure_ephemeris_ready() -> str:
    """Trigger download/load; return status string for UI."""
    _load_ephemeris()
    path = _DATA_DIR / "de421.bsp"
    return f"DE421 έτοιμο ({path})" if path.exists() else "Ephemeris loaded"
