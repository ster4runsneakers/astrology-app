"""Next N months outlook — deterministic Greek templates (+ optional AI later)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Sequence, Tuple

from chinese_zodiac import ChineseZodiac
from zodiac import ZodiacSignId, get_zodiac_by_id

MONTHS_EL = (
    "",
    "Ιανουάριος",
    "Φεβρουάριος",
    "Μάρτιος",
    "Απρίλιος",
    "Μάιος",
    "Ιούνιος",
    "Ιούλιος",
    "Αύγουστος",
    "Σεπτέμβριος",
    "Οκτώβριος",
    "Νοέμβριος",
    "Δεκέμβριος",
)

THEMES: Sequence[Tuple[str, str]] = (
    ("σχέσεις & σύνδεση", "επικοινωνία με αγαπημένα πρόσωπα"),
    ("εργασία & στόχοι", "σαφή βήματα και προτεραιότητες"),
    ("υγεία & ρυθμός", "ύπνος, κίνηση και υγιή όρια"),
    ("οικονομικά", "πλάνο και μικρές σταθερές αποφάσεις"),
    ("δημιουργικότητα", "ιδέες που ζητούν μορφή"),
    ("εσωτερική γαλήνη", "χώρος για ανάσα και επαναφορά"),
)

DISCLAIMER_EL = (
    "Οι μηνιαίες προβλέψεις είναι ενδεικτικές / ψυχαγωγικές (MVP) — "
    "δεν αποτελούν αστρολογική συμβουλή επί πληρωμή ούτε πρόβλεψη γεγονότων."
)


@dataclass
class MonthCard:
    year: int
    month: int
    label_el: str
    theme_el: str
    text_el: str


@dataclass
class MonthlyOutlook:
    months: List[MonthCard]
    chinese_note_el: str
    disclaimer_el: str
    source: str  # local | gemini | xai


def _next_months(start: date, count: int) -> List[Tuple[int, int]]:
    y, m = start.year, start.month
    out: List[Tuple[int, int]] = []
    for _ in range(count):
        out.append((y, m))
        m += 1
        if m > 12:
            m = 1
            y += 1
    return out


def build_monthly_outlook(
    sun_id: ZodiacSignId,
    chinese: Optional[ChineseZodiac] = None,
    start: Optional[date] = None,
    months: int = 6,
) -> MonthlyOutlook:
    """Deterministic 3–6 month cards keyed by sun sign + calendar."""
    start = start or date.today()
    months = max(3, min(6, int(months)))
    z = get_zodiac_by_id(sun_id)
    cards: List[MonthCard] = []

    for i, (y, m) in enumerate(_next_months(start, months)):
        theme, focus = THEMES[(hash((sun_id, y, m)) & 0xFFFF) % len(THEMES)]
        # mild variation by month index
        energy = ("ήπια", "ζωηρή", "στοχαστική", "πρακτική", "δημιουργική", "σταθεροποιητική")[i % 6]
        text = (
            f"Για τον **{z.name_el}**, ο {MONTHS_EL[m]} {y} φέρνει **{energy}** έμφαση σε "
            f"**{theme}**. Καλό είναι να δώσεις χώρο σε {focus}. "
            f"Μικρά, συνεπή βήματα ταιριάζουν περισσότερο από βεβιασμένες αποφάσεις."
        )
        cards.append(
            MonthCard(
                year=y,
                month=m,
                label_el=f"{MONTHS_EL[m]} {y}",
                theme_el=theme,
                text_el=text,
            )
        )

    if chinese:
        cn_note = (
            f"Κινεζική νότα: ως **{chinese.animal_el}** ({chinese.element_el}, {chinese.polarity}) "
            f"οι επόμενοι μήνες ευνοούν ό,τι ταιριάζει στο στοιχείο σου — "
            f"{chinese.traits_el}"
        )
    else:
        cn_note = ""

    return MonthlyOutlook(
        months=cards,
        chinese_note_el=cn_note,
        disclaimer_el=DISCLAIMER_EL,
        source="local",
    )
