"""Tropical zodiac helpers and Greek labels."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

ZodiacSignId = Literal[
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittarius",
    "capricorn",
    "aquarius",
    "pisces",
]


@dataclass(frozen=True)
class ZodiacInfo:
    id: ZodiacSignId
    name_el: str
    name_en: str
    symbol: str
    element_el: str
    modality_el: str
    start_degree: float


ZODIAC_SIGNS: list[ZodiacInfo] = [
    ZodiacInfo("aries", "Κριός", "Aries", "♈", "Φωτιά", "Παρορμητικό", 0),
    ZodiacInfo("taurus", "Ταύρος", "Taurus", "♉", "Γη", "Σταθερό", 30),
    ZodiacInfo("gemini", "Δίδυμοι", "Gemini", "♊", "Αέρας", "Μεταβλητό", 60),
    ZodiacInfo("cancer", "Καρκίνος", "Cancer", "♋", "Νερό", "Παρορμητικό", 90),
    ZodiacInfo("leo", "Λέων", "Leo", "♌", "Φωτιά", "Σταθερό", 120),
    ZodiacInfo("virgo", "Παρθένος", "Virgo", "♍", "Γη", "Μεταβλητό", 150),
    ZodiacInfo("libra", "Ζυγός", "Libra", "♎", "Αέρας", "Παρορμητικό", 180),
    ZodiacInfo("scorpio", "Σκορπιός", "Scorpio", "♏", "Νερό", "Σταθερό", 210),
    ZodiacInfo("sagittarius", "Τοξότης", "Sagittarius", "♐", "Φωτιά", "Μεταβλητό", 240),
    ZodiacInfo("capricorn", "Αιγόκερως", "Capricorn", "♑", "Γη", "Παρορμητικό", 270),
    ZodiacInfo("aquarius", "Υδροχόος", "Aquarius", "♒", "Αέρας", "Σταθερό", 300),
    ZodiacInfo("pisces", "Ιχθύες", "Pisces", "♓", "Νερό", "Μεταβλητό", 330),
]

_BY_ID = {z.id: z for z in ZODIAC_SIGNS}


def normalize_longitude(lon: float) -> float:
    x = lon % 360.0
    if x < 0:
        x += 360.0
    return x


def longitude_to_sign(longitude: float) -> ZodiacInfo:
    lon = normalize_longitude(longitude)
    index = int(lon // 30) % 12
    return ZODIAC_SIGNS[index]


def degree_in_sign(longitude: float) -> float:
    return normalize_longitude(longitude) % 30.0


def format_degree(longitude: float) -> str:
    d = degree_in_sign(longitude)
    deg = int(d)
    minutes = int((d - deg) * 60)
    return f"{deg}°{minutes:02d}′"


def sun_sign_from_date(year: int, month: int, day: int) -> ZodiacInfo:
    """Tropical sun sign from calendar date (common Western cusp table)."""
    del year  # year unused; cusps are month/day based
    md = month * 100 + day
    if 321 <= md <= 419:
        return ZODIAC_SIGNS[0]
    if 420 <= md <= 520:
        return ZODIAC_SIGNS[1]
    if 521 <= md <= 620:
        return ZODIAC_SIGNS[2]
    if 621 <= md <= 722:
        return ZODIAC_SIGNS[3]
    if 723 <= md <= 822:
        return ZODIAC_SIGNS[4]
    if 823 <= md <= 922:
        return ZODIAC_SIGNS[5]
    if 923 <= md <= 1022:
        return ZODIAC_SIGNS[6]
    if 1023 <= md <= 1121:
        return ZODIAC_SIGNS[7]
    if 1122 <= md <= 1221:
        return ZODIAC_SIGNS[8]
    if md >= 1222 or md <= 119:
        return ZODIAC_SIGNS[9]
    if 120 <= md <= 218:
        return ZODIAC_SIGNS[10]
    return ZODIAC_SIGNS[11]


def get_zodiac_by_id(sign_id: ZodiacSignId) -> ZodiacInfo:
    return _BY_ID.get(sign_id, ZODIAC_SIGNS[0])
