"""Western + Chinese synastry (compatibility) — Greek original copy."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple

from chinese_zodiac import ChineseZodiac, get_chinese_zodiac
from natal import BirthProfile, NatalChart, compute_natal_chart, get_sun_sign_from_profile
from zodiac import ZodiacSignId, get_zodiac_by_id

TRIADS = (
    frozenset({"rat", "dragon", "monkey"}),
    frozenset({"ox", "snake", "rooster"}),
    frozenset({"tiger", "horse", "dog"}),
    frozenset({"rabbit", "goat", "pig"}),
)

HARMONIES = {
    frozenset({"rat", "ox"}),
    frozenset({"tiger", "pig"}),
    frozenset({"rabbit", "dog"}),
    frozenset({"dragon", "rooster"}),
    frozenset({"snake", "monkey"}),
    frozenset({"horse", "goat"}),
}

CLASH = {
    frozenset({"rat", "horse"}),
    frozenset({"ox", "goat"}),
    frozenset({"tiger", "monkey"}),
    frozenset({"rabbit", "rooster"}),
    frozenset({"dragon", "dog"}),
    frozenset({"snake", "pig"}),
}

ELEMENT_OF: dict[ZodiacSignId, str] = {
    "aries": "fire", "leo": "fire", "sagittarius": "fire",
    "taurus": "earth", "virgo": "earth", "capricorn": "earth",
    "gemini": "air", "libra": "air", "aquarius": "air",
    "cancer": "water", "scorpio": "water", "pisces": "water",
}

ELEMENT_SCORE = {
    ("fire", "fire"): 4, ("fire", "air"): 5, ("fire", "earth"): 2, ("fire", "water"): 2,
    ("air", "air"): 4, ("air", "fire"): 5, ("air", "earth"): 2, ("air", "water"): 3,
    ("earth", "earth"): 4, ("earth", "water"): 5, ("earth", "fire"): 2, ("earth", "air"): 2,
    ("water", "water"): 4, ("water", "earth"): 5, ("water", "fire"): 2, ("water", "air"): 3,
}


@dataclass
class SynastryReport:
    title_el: str
    score: int
    western_el: str
    chinese_el: str
    tips: List[str]
    sun_a: str
    sun_b: str
    animal_a: str
    animal_b: str


def _planet_sign(chart: NatalChart, pid: str) -> Optional[ZodiacSignId]:
    for p in chart.planets:
        if p.id == pid:
            return p.sign  # type: ignore[return-value]
    return None


def _chinese_pair(a: ChineseZodiac, b: ChineseZodiac) -> Tuple[str, int]:
    pair = frozenset({a.animal_id, b.animal_id})
    if a.animal_id == b.animal_id:
        text = (
            f"Ίδιο κινεζικό ζώδιο (**{a.animal_el}**): δυνατή αναγνώριση και καθρέφτης. "
            f"Υπέροχα για κατανόηση· πρόσεξε τον ανταγωνισμό."
        )
        return text, 7
    if any(pair <= t for t in TRIADS):
        text = (
            f"**Τρίγωνο αρμονίας**: {a.animal_el} + {b.animal_el}. "
            f"Στηρίζεστε φυσικά· συχνά νιώθετε ότι ανήκετε στην ίδια ομάδα."
        )
        return text, 9
    if pair in HARMONIES:
        text = (
            f"**Μυστική αρμονία**: {a.animal_el} + {b.animal_el}. "
            f"Έλξη και συμπλήρωμα — ο ένας μαλακώνει ό,τι λείπει στον άλλον."
        )
        return text, 9
    if pair in CLASH:
        text = (
            f"**Αντίθεση / ένταση**: {a.animal_el} απέναντι από {b.animal_el}. "
            f"Δεν σημαίνει καταστροφή — σημαίνει σπίθα και ανάγκη για όρια. "
            f"Με σεβασμό γίνεται ανάπτυξη."
        )
        return text, 4
    if a.element_el == b.element_el:
        text = (
            f"Διαφορετικά ζώδια αλλά **ίδιο στοιχείο** ({a.element_el}): "
            f"μιλάτε παρόμοια γλώσσα ενέργειας."
        )
        return text, 6
    text = (
        f"{a.animal_el} ({a.element_el}) με {b.animal_el} ({b.element_el}): "
        f"σχέση που χτίζεται με συνειδητή προσπάθεια."
    )
    return text, 5


def _western_pair(
    chart_a: NatalChart, chart_b: NatalChart, name_a: str, name_b: str
) -> Tuple[str, int]:
    sun_a = _planet_sign(chart_a, "sun")
    sun_b = _planet_sign(chart_b, "sun")
    moon_a = _planet_sign(chart_a, "moon")
    moon_b = _planet_sign(chart_b, "moon")
    if not sun_a or not sun_b:
        return "Δεν υπολογίστηκαν Ήλιοι.", 5

    za, zb = get_zodiac_by_id(sun_a), get_zodiac_by_id(sun_b)
    ea, eb = ELEMENT_OF[sun_a], ELEMENT_OF[sun_b]
    sun_score = ELEMENT_SCORE.get((ea, eb), 3)
    na = name_a or "Α"
    nb = name_b or "Β"
    parts = [
        f"**Ήλιος** {za.name_el} ({na}) με **Ήλιος** {zb.name_el} ({nb}): "
        f"στοιχεία {za.element_el}–{zb.element_el}."
    ]
    score = sun_score

    if moon_a and moon_b:
        ma, mb = get_zodiac_by_id(moon_a), get_zodiac_by_id(moon_b)
        mea, meb = ELEMENT_OF[moon_a], ELEMENT_OF[moon_b]
        moon_score = ELEMENT_SCORE.get((mea, meb), 3)
        score = round((sun_score + moon_score) / 2)
        parts.append(
            f"**Σελήνη** {ma.name_el} με **Σελήνη** {mb.name_el}: "
            f"εκεί παίζεται η καθημερινή συναισθηματική συμβίωση."
        )
        if moon_a == sun_b or moon_b == sun_a:
            parts.append("Υπάρχει δεσμός Σελήνης–Ήλιου: συχνά «σε νιώθω σαν σπίτι».")
            score = min(10, score + 1)

    asc_a = chart_a.ascendant.sign if chart_a.ascendant and not chart_a.approximate else None
    asc_b = chart_b.ascendant.sign if chart_b.ascendant and not chart_b.approximate else None
    if asc_a and asc_b:
        aa = get_zodiac_by_id(asc_a)  # type: ignore[arg-type]
        ab = get_zodiac_by_id(asc_b)  # type: ignore[arg-type]
        parts.append(
            f"**Ωροσκόποι** {aa.name_el} / {ab.name_el}: η πρώτη χημεία ως ζευγάρι."
        )

    if sun_score >= 5:
        parts.append("Στον πυρήνα υπάρχει καλή ροή — αν δουλέψετε την επικοινωνία, πάτε μακριά.")
    elif sun_score <= 2:
        parts.append("Οι πυρήνες διαφέρουν πολύ· χρειάζεται περιέργεια, όχι προσπάθεια αλλαγής του άλλου.")
    else:
        parts.append("Υπάρχει δυναμική που θέλει συνειδητή φροντίδα.")

    return "\n\n".join(parts), max(1, min(10, score))


def build_synastry(
    profile_a: BirthProfile,
    profile_b: BirthProfile,
    chart_a: Optional[NatalChart] = None,
    chart_b: Optional[NatalChart] = None,
) -> SynastryReport:
    chart_a = chart_a or compute_natal_chart(profile_a)
    chart_b = chart_b or compute_natal_chart(profile_b)
    cz_a = get_chinese_zodiac(date.fromisoformat(profile_a.date_of_birth))
    cz_b = get_chinese_zodiac(date.fromisoformat(profile_b.date_of_birth))
    western, wscore = _western_pair(chart_a, chart_b, profile_a.name, profile_b.name)
    chinese, cscore = _chinese_pair(cz_a, cz_b)
    score = max(1, min(10, round((wscore * 0.55) + (cscore * 0.45))))
    na = profile_a.name or "Άτομο Α"
    nb = profile_b.name or "Άτομο Β"
    tips = [
        "Μιλήστε ανοιχτά για ανάγκες ασφάλειας (Σελήνη) πριν για στόχους (Ήλιος).",
        "Στην ένταση: όρια πρώτα, εξηγήσεις μετά.",
        f"Κινεζικά: τιμήστε τη διαφορά {cz_a.animal_el} / {cz_b.animal_el}.",
    ]
    return SynastryReport(
        title_el=f"Συναστρία: {na} × {nb}",
        score=score,
        western_el=western,
        chinese_el=chinese,
        tips=tips,
        sun_a=get_sun_sign_from_profile(profile_a).name_el,
        sun_b=get_sun_sign_from_profile(profile_b).name_el,
        animal_a=f"{cz_a.symbol} {cz_a.animal_el}",
        animal_b=f"{cz_b.symbol} {cz_b.animal_el}",
    )

