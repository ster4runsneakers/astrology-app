"""Next N months outlook — varied Greek templates (media-astrology voice)."""
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

# (theme_label, focus_hint)
THEMES: Sequence[Tuple[str, str]] = (
    ("καρδιά & σχέσεις", "τι νιώθεις πραγματικά και τι λες δυνατά"),
    ("δουλειά & κατεύθυνση", "έναν στόχο που αξίζει τον κόπο σου"),
    ("σώμα & ρυθμός", "ύπνο, κίνηση και όρια χωρίς ενοχές"),
    ("χρήμα & ασφάλεια", "μικρές σταθερές αποφάσεις, όχι πανικό"),
    ("δημιουργία & έμπνευση", "ιδέες που ζητούν να πάρουν μορφή"),
    ("εσωτερική φωνή", "ησυχία αρκετή για να ακούσεις τον εαυτό σου"),
    ("κοινωνία & εικόνα", "πώς σε βλέπουν και τι θέλεις να δείξεις"),
    ("οικογένεια & ρίζες", "δεσμούς που χρειάζονται φροντίδα ή χώρο"),
)

# Distinct openers / middles / closers — rotated so months never read identical
OPENERS = (
    "Άκου λίγο προσεκτικά αυτόν τον μήνα,",
    "Μην το πάρεις αψήφιστα:",
    "Έρχεται μια φάση που ζητάει καθαρότητα,",
    "Κράτα το ημερολόγιό σου ανοιχτό —",
    "Αν κάτι «τραβάει» την προσοχή σου τώρα,",
    "Υπάρχει μια υπόγεια αλλαγή στον αέρα,",
    "Μην βιάζεσαι να κλείσεις κύκλους·",
    "Αυτός ο μήνας έχει χαρακτήρα,",
)

MIDDLES = (
    "οι συναντήσεις μετράνε περισσότερο από τις μεγάλες θεωρίες",
    "ένα θέμα που ανέβαλλες ζητάει απόφαση με ψυχραιμία",
    "η υπομονή σου θα φανεί πιο δυνατή από την πίεση γύρω σου",
    "μια λεπτομέρεια στην επικοινωνία αλλάζει όλο το κλίμα",
    "η ενέργειά σου ανεβοκατεβαίνει — όρισε προτεραιότητες",
    "κάποιος κοντά σου μπορεί να γίνει καθρέφτης, όχι εχθρός",
    "οι ευκαιρίες δεν φωνάζουν· χρειάζονται μάτι και θάρρος",
    "το σώμα σου λέει την αλήθεια πριν το μυαλό προλάβει",
)

CLOSERS = (
    "Προτίμησε την αλήθεια από την ωραιοποίηση.",
    "Κάνε ένα βήμα· όχι δέκα μεμιάς.",
    "Ό,τι φυλάς μέσα σου, αξίζει μια ήρεμη κουβέντα.",
    "Μην αφήσεις τον φόβο να διαλέξει για σένα.",
    "Η σταθερότητα τώρα χτίζει το επόμενο κεφάλαιο.",
    "Κράτα αξιοπρέπεια· τα υπόλοιπα τακτοποιούνται.",
    "Δώσε χρόνο — και μην ξεχάσεις να δώσεις και σε σένα.",
    "Το σύμπαν εδώ δεν «τιμωρεί»· καλεί σε συνείδηση.",
)

SIGN_FLAVOR = {
    "aries": "Με τη φωτιά του Κριού,",
    "taurus": "Με τη γη του Ταύρου κάτω από τα πόδια σου,",
    "gemini": "Με το μυαλό των Διδύμων σε εγρήγορση,",
    "cancer": "Με την ευαισθησία του Καρκίνου ενεργή,",
    "leo": "Με τη λάμψη του Λέοντα στο στήθος,",
    "virgo": "Με το κριτικό μάτι της Παρθένου,",
    "libra": "Με την ανάγκη της Ζυγού για ισορροπία,",
    "scorpio": "Με το βάθος του Σκορπιού,",
    "sagittarius": "Με την ορμή του Τοξότη μπροστά,",
    "capricorn": "Με την πειθαρχία του Αιγόκερω,",
    "aquarius": "Με το διαφορετικό βλέμμα του Υδροχόου,",
    "pisces": "Με τη διαίσθηση των Ιχθύων ανοιχτή,",
}

SEASON_HINT = {
    1: "αρχή χρόνου, καθαρό χαρτί",
    2: "χειμωνιάτικη εσωστρέφεια που ωριμάζει",
    3: "άνοιξη που σπρώχνει προς τα έξω",
    4: "αναγέννηση και καινούργια σχέδια",
    5: "ζωντάνια και εξωστρέφεια",
    6: "θερινό φως και επιλογές",
    7: "καλοκαιρινή ένταση / ανάγκη για ανάσα",
    8: "καρποί και απολογισμοί",
    9: "επιστροφή σε ρυθμό και στόχους",
    10: "σοβαρότητα και διευθετήσεις",
    11: "κλίμα σχέσεων και συλλογικότητας",
    12: "κλείσιμο κύκλων και εσωτερική σιγή",
}

DISCLAIMER_EL = (
    "Οι μηνιαίες προβλέψεις είναι ενδεικτικές / ψυχαγωγικές — "
    "ύφος εμπνευσμένο από την ελληνική αστρολογική παράδοση των media, "
    "χωρίς αντιγραφή συγκεκριμένων κειμένων. Δεν αποτελούν επαγγελματική συμβουλή."
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


def _pick(seq: Sequence[str], *keys: object) -> str:
    """Stable pick (not Python's randomized hash)."""
    n = 0
    for k in keys:
        n = (n * 131 + sum(ord(c) for c in str(k))) % 10_000_019
    return seq[n % len(seq)]


def build_monthly_outlook(
    sun_id: ZodiacSignId,
    chinese: Optional[ChineseZodiac] = None,
    start: Optional[date] = None,
    months: int = 6,
) -> MonthlyOutlook:
    """Deterministic but clearly distinct cards per calendar month."""
    start = start or date.today()
    months = max(3, min(6, int(months)))
    z = get_zodiac_by_id(sun_id)
    flavor = SIGN_FLAVOR.get(sun_id, "Με τον Ήλιο σου ενεργό,")
    cards: List[MonthCard] = []

    sun_off = sum(ord(c) for c in sun_id) % len(THEMES)
    for i, (y, m) in enumerate(_next_months(start, months)):
        theme, focus = THEMES[(i + sun_off) % len(THEMES)]
        opener = OPENERS[(i + sun_off) % len(OPENERS)]
        middle = MIDDLES[(i * 2 + sun_off + m) % len(MIDDLES)]
        closer = CLOSERS[(i * 3 + m) % len(CLOSERS)]
        season = SEASON_HINT.get(m, "μεταβατική ενέργεια")

        cn_bit = ""
        if chinese:
            cn_bit = (
                f" Ως **{chinese.animal_el}** του στοιχείου **{chinese.element_el}**, "
                f"δυνάμωσε ό,τι ταιριάζει στη φύση σου — {chinese.traits_el.rstrip('.')}."
            )

        life_bits = (
            "στις σχέσεις",
            "στη δουλειά",
            "στα οικονομικά μικροπράγματα",
            "στο σώμα και τον ύπνο",
            "στις οικογενειακές εκκρεμότητες",
            "στην εικόνα σου προς τα έξω",
        )
        life = life_bits[(i + sun_off + m) % len(life_bits)]
        text = (
            f"{opener} **{z.name_el}**.\n\n"
            f"{flavor} ο **{MONTHS_EL[m]} {y}** έχει αέρα «{season}» και κύριο θέμα "
            f"**{theme}**. Μην περιμένεις ουδέτερη περίοδο — κάτι θέλει την προσοχή σου "
            f"{life}.\n\n"
            f"Πρακτικά: {middle}. Στάσου λίγο σε {focus}. "
            f"Αν πιεστείς, μην αντιδράς στην πρώτη παρόρμηση· δώσε 48 ώρες πριν τις μεγάλες αποφάσεις.\n\n"
            f"**Συμβουλή μήνα:** {closer}{cn_bit}"
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
            f"**Κινεζική γραμμή:** {chinese.animal_el} {chinese.symbol} · "
            f"{chinese.element_el} ({chinese.polarity}) · σεληνιακό {chinese.lunar_year}. "
            f"{chinese.traits_el} Στους επόμενους μήνες, μην πας κόντρα στο στοιχείο σου — "
            f"χρησιμοποίησέ το."
        )
    else:
        cn_note = ""

    return MonthlyOutlook(
        months=cards,
        chinese_note_el=cn_note,
        disclaimer_el=DISCLAIMER_EL,
        source="local",
    )
