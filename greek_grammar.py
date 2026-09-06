"""Greek zodiac grammar helpers (cases for readable narrative)."""
from __future__ import annotations

from zodiac import ZodiacSignId, get_zodiac_by_id

# nominative already in zodiac.name_el
# accusative after στον/στην/στους
ACCUSATIVE: dict[ZodiacSignId, str] = {
    "aries": "Κριό",
    "taurus": "Ταύρο",
    "gemini": "Διδύμους",
    "cancer": "Καρκίνο",
    "leo": "Λέοντα",
    "virgo": "Παρθένο",
    "libra": "Ζυγό",
    "scorpio": "Σκορπιό",
    "sagittarius": "Τοξότη",
    "capricorn": "Αιγόκερω",
    "aquarius": "Υδροχόο",
    "pisces": "Ιχθύες",
}

# genitive: του/της/των X
GENITIVE: dict[ZodiacSignId, str] = {
    "aries": "του Κριού",
    "taurus": "του Ταύρου",
    "gemini": "των Διδύμων",
    "cancer": "του Καρκίνου",
    "leo": "του Λέοντα",
    "virgo": "της Παρθένου",
    "libra": "του Ζυγού",
    "scorpio": "του Σκορπιού",
    "sagittarius": "του Τοξότη",
    "capricorn": "του Αιγόκερω",
    "aquarius": "του Υδροχόου",
    "pisces": "των Ιχθύων",
}

PLURAL = {"gemini", "pisces"}
FEMININE = {"virgo"}


def sun_in_sign(sign_id: ZodiacSignId) -> str:
    """e.g. 'Ήλιος στους Ιχθύες' / 'Ήλιος στον Υδροχόο'."""
    z = get_zodiac_by_id(sign_id)
    acc = ACCUSATIVE[sign_id]
    if sign_id in PLURAL:
        return f"Ήλιος στους **{acc}**"
    if sign_id in FEMININE:
        return f"Ήλιος στην **{acc}**"
    return f"Ήλιος στον **{acc}**"


def moon_in_sign(sign_id: ZodiacSignId) -> str:
    acc = ACCUSATIVE[sign_id]
    if sign_id in PLURAL:
        return f"Σελήνη στους **{acc}**"
    if sign_id in FEMININE:
        return f"Σελήνη στην **{acc}**"
    return f"Σελήνη στον **{acc}**"


def asc_in_sign(sign_id: ZodiacSignId) -> str:
    acc = ACCUSATIVE[sign_id]
    if sign_id in PLURAL:
        return f"Ωροσκόπος στους **{acc}**"
    if sign_id in FEMININE:
        return f"Ωροσκόπος στην **{acc}**"
    return f"Ωροσκόπος στον **{acc}**"


def the_sign_inside(sign_id: ZodiacSignId) -> str:
    """For 'τι θα έκανε ο/η X μέσα μου'."""
    z = get_zodiac_by_id(sign_id)
    if sign_id in PLURAL:
        return f"οι **{z.name_el}** μέσα μου"
    if sign_id in FEMININE:
        return f"η **{z.name_el}** μέσα μου"
    return f"ο **{z.name_el}** μέσα μου"


def my_sign_needs(sign_id: ZodiacSignId) -> str:
    z = get_zodiac_by_id(sign_id)
    if sign_id in PLURAL:
        return f"οι **{z.name_el}** μου"
    if sign_id in FEMININE:
        return f"η **{z.name_el}** μου"
    return f"ο **{z.name_el}** μου"
