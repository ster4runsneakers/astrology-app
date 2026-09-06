"""Chinese zodiac (animal + element) from Gregorian birth date — Greek copy."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Tuple

# Approximate Chinese New Year (Gregorian) for common years; fallback Jan 31.
# For MVP we use a compact table 1924–2031; outside → approx Feb 4.
_CNY: dict[int, Tuple[int, int]] = {
    1924: (2, 5), 1925: (1, 24), 1926: (2, 13), 1927: (2, 2), 1928: (1, 23),
    1929: (2, 10), 1930: (1, 30), 1931: (2, 17), 1932: (2, 6), 1933: (1, 26),
    1934: (2, 14), 1935: (2, 4), 1936: (1, 24), 1937: (2, 11), 1938: (1, 31),
    1939: (2, 19), 1940: (2, 8), 1941: (1, 27), 1942: (2, 15), 1943: (2, 5),
    1944: (1, 25), 1945: (2, 13), 1946: (2, 2), 1947: (1, 22), 1948: (2, 10),
    1949: (1, 29), 1950: (2, 17), 1951: (2, 6), 1952: (1, 27), 1953: (2, 14),
    1954: (2, 3), 1955: (1, 24), 1956: (2, 12), 1957: (1, 31), 1958: (2, 18),
    1959: (2, 8), 1960: (1, 28), 1961: (2, 15), 1962: (2, 5), 1963: (1, 25),
    1964: (2, 13), 1965: (2, 2), 1966: (1, 21), 1967: (2, 9), 1968: (1, 30),
    1969: (2, 17), 1970: (2, 6), 1971: (1, 27), 1972: (2, 15), 1973: (2, 3),
    1974: (1, 23), 1975: (2, 11), 1976: (1, 31), 1977: (2, 18), 1978: (2, 7),
    1979: (1, 28), 1980: (2, 16), 1981: (2, 5), 1982: (1, 25), 1983: (2, 13),
    1984: (2, 2), 1985: (2, 20), 1986: (2, 9), 1987: (1, 29), 1988: (2, 17),
    1989: (2, 6), 1990: (1, 27), 1991: (2, 15), 1992: (2, 4), 1993: (1, 23),
    1994: (2, 10), 1995: (1, 31), 1996: (2, 19), 1997: (2, 7), 1998: (1, 28),
    1999: (2, 16), 2000: (2, 5), 2001: (1, 24), 2002: (2, 12), 2003: (2, 1),
    2004: (1, 22), 2005: (2, 9), 2006: (1, 29), 2007: (2, 18), 2008: (2, 7),
    2009: (1, 26), 2010: (2, 14), 2011: (2, 3), 2012: (1, 23), 2013: (2, 10),
    2014: (1, 31), 2015: (2, 19), 2016: (2, 8), 2017: (1, 28), 2018: (2, 16),
    2019: (2, 5), 2020: (1, 25), 2021: (2, 12), 2022: (2, 1), 2023: (1, 22),
    2024: (2, 10), 2025: (1, 29), 2026: (2, 17), 2027: (2, 6), 2028: (1, 26),
    2029: (2, 13), 2030: (2, 3), 2031: (1, 23),
}

ANIMALS_EL = (
    ("rat", "Αρουραίος", "🐭"),
    ("ox", "Βόδι", "🐂"),
    ("tiger", "Τίγρης", "🐅"),
    ("rabbit", "Κουνέλι", "🐇"),
    ("dragon", "Δράκος", "🐉"),
    ("snake", "Φίδι", "🐍"),
    ("horse", "Άλογο", "🐴"),
    ("goat", "Κατσίκα", "🐐"),
    ("monkey", "Πίθηκος", "🐒"),
    ("rooster", "Κόκορας", "🐓"),
    ("dog", "Σκύλος", "🐕"),
    ("pig", "Γουρούνι", "🐷"),
)

# Stem → element (Wood/Fire/Earth/Metal/Water), Yang/Yin
ELEMENTS_EL = {
    0: ("ξύλο", "Yang"),   # Jia
    1: ("ξύλο", "Yin"),    # Yi
    2: ("φωτιά", "Yang"),  # Bing
    3: ("φωτιά", "Yin"),   # Ding
    4: ("γη", "Yang"),     # Wu
    5: ("γη", "Yin"),      # Ji
    6: ("μέταλλο", "Yang"),# Geng
    7: ("μέταλλο", "Yin"), # Xin
    8: ("νερό", "Yang"),   # Ren
    9: ("νερό", "Yin"),    # Gui
}

TRAITS_EL = {
    "rat": "Έξυπνος, προσαρμοστικός, καλός με ευκαιρίες και λεπτομέρειες.",
    "ox": "Υπομονετικός, αξιόπιστος, χτίζει μεθοδικά και αντέχει στην πίεση.",
    "tiger": "Θαρραλέος, χαρισματικός, θέλει πρωτοβουλία και χώρο να κινηθεί.",
    "rabbit": "Διπλωματικός, ευαίσθητος, προτιμά αρμονία και κομψές λύσεις.",
    "dragon": "Οραματιστής, δυναμικός, εμπνέει και στοχεύει ψηλά.",
    "snake": "Διορατικός, ήρεμος στρατηγός, σκέφτεται πριν κινηθεί.",
    "horse": "Ελεύθερος, ενεργητικός, προχωρά με πάθος και ρυθμό.",
    "goat": "Καλλιτεχνικός, τρυφερός, χρειάζεται στήριξη και ομορφιά γύρω του.",
    "monkey": "Εφευρετικός, παιχνιδιάρης, λύνει προβλήματα με ευελιξία.",
    "rooster": "Οργανωτικός, περήφανος, εκτιμά την ακρίβεια και την εμφάνιση.",
    "dog": "Πιστός, δίκαιος, προστατεύει όσους αγαπά.",
    "pig": "Μεγαλόψυχος, απολαυστικός, φέρνει ζεστασιά και γενναιοδωρία.",
}


@dataclass(frozen=True)
class ChineseZodiac:
    animal_id: str
    animal_el: str
    symbol: str
    element_el: str
    polarity: str  # Yang / Yin
    lunar_year: int
    traits_el: str
    summary_el: str


def _cny_date(year: int) -> date:
    if year in _CNY:
        m, d = _CNY[year]
        return date(year, m, d)
    # crude fallback near early February
    return date(year, 2, 4)


def lunar_year_for(dob: date) -> int:
    """Chinese sexagenary year for a Gregorian birth date."""
    cny = _cny_date(dob.year)
    return dob.year if dob >= cny else dob.year - 1


def get_chinese_zodiac(dob: date) -> ChineseZodiac:
    ly = lunar_year_for(dob)
    # 1984 = Rat Wood Yang (Jia-Zi). Offset from 1984.
    animal = ANIMALS_EL[(ly - 1984) % 12]
    stem = (ly - 1984) % 10
    elem, pol = ELEMENTS_EL[stem]
    aid, name_el, sym = animal
    traits = TRAITS_EL[aid]
    summary = (
        f"Στο κινεζικό ωροσκόπιο ανήκεις στο ζώδιο του **{name_el}** "
        f"({sym}), στοιχείο **{elem}** ({pol}), σεληνιακό έτος **{ly}**. "
        f"{traits}"
    )
    return ChineseZodiac(
        animal_id=aid,
        animal_el=name_el,
        symbol=sym,
        element_el=elem,
        polarity=pol,
        lunar_year=ly,
        traits_el=traits,
        summary_el=summary,
    )
