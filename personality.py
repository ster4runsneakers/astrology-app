"""Deterministic Greek personality analysis from natal chart placements."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from natal import BirthProfile, NatalChart, PlanetPosition
from narrative_el import build_rich_summary
from voice_el import VOICE_DISCLAIMER_EL, warm_wrap
from greek_grammar import ACCUSATIVE, PLURAL, FEMININE
from zodiac import ZodiacSignId, get_zodiac_by_id

DISCLAIMER_EL = (
    "Η ανάλυση είναι ενδεικτική / ψυχαγωγική — βασίζεται σε αστρολογικά μοτίβα "
    "Δεν αποτελεί ψυχολογική, "
    "ιατρική ή επαγγελματική συμβουλή. " + VOICE_DISCLAIMER_EL
)

# ---------------------------------------------------------------------------
# Sign trait banks (keyed by zodiac.py ids)
# ---------------------------------------------------------------------------

CORE_IDENTITY: dict[ZodiacSignId, str] = {
    "aries": "Θέλεις να ξεκινάς πρώτος και να βλέπεις αποτέλεσμα γρήγορα. Αν σε καθυστερούν, θυμώνεις.",
    "taurus": "Θέλεις σταθερότητα και ποιότητα. Δεν βιάζεσαι — αλλά όταν αποφασίσεις, δεν αλλάζεις εύκολα.",
    "gemini": "Θέλεις κουβέντα, ιδέες και αλλαγή. Η μονοτονία σε κουράζει γρήγορα.",
    "cancer": "Θέλεις ασφάλεια και δικούς σου ανθρώπους. Προστατεύεις ό,τι αγαπάς.",
    "leo": "Θέλεις να σε βλέπουν και να μετράς. Η αναγνώριση σε γεμίζει· η αδιαφορία σε πληγώνει.",
    "virgo": "Θέλεις τα πράγματα να δουλεύουν σωστά. Βλέπεις τα λάθη και θες να τα φτιάξεις.",
    "libra": "Θέλεις ηρεμία στις σχέσεις και δίκαιες αποφάσεις. Δυσκολεύεσαι όταν πρέπει να διαλέξεις πλευρά.",
    "scorpio": "Θέλεις αλήθεια και βάθος. Δεν αντέχεις τα ψέματα και τις επιφάνειες.",
    "sagittarius": "Θέλεις νόημα και ελευθερία. Αν νιώθεις παγιδευμένος, ψάχνεις έξοδο.",
    "capricorn": "Θέλεις αποτέλεσμα και σεβασμό. Χτίζεις αργά και μετράς με έργα, όχι με λόγια.",
    "aquarius": "Θέλεις χώρο να σκέφτεσαι διαφορετικά. Δεν σου αρέσει η πίεση να «ταιριάξεις».",
    "pisces": "Θέλεις σύνδεση και να νιώσεις χωρίς φίλτρο. Παίρνεις εύκολα τα συναισθήματα των άλλων.",
}

MOON_EMOTIONS: dict[ZodiacSignId, str] = {
    "aries": "Όταν στρεσάρεσαι, θέλεις κίνηση. Αν κάτσεις ακίνητος, το άγχος μεγαλώνει.",
    "taurus": "Όταν στρεσάρεσαι, θέλεις ηρεμία: φαγητό, σώμα, σταθερή ρουτίνα.",
    "gemini": "Όταν στρεσάρεσαι, χρειάζεσαι να το πεις ή να το γράψεις για να καταλάβεις τι νιώθεις.",
    "cancer": "Όταν στρεσάρεσαι, θέλεις σπίτι και οικείους. Κλείνεσαι αν δεν νιώθεις ασφαλής.",
    "leo": "Όταν στρεσάρεσαι, θέλεις ζεστασιά και να σου πουν ότι μετράς.",
    "virgo": "Όταν στρεσάρεσαι, βάζεις τάξη ή επικρίνεις. Ηρεμείς όταν νιώθεις χρήσιμος.",
    "libra": "Όταν στρεσάρεσαι, οι καβγάδες σε αδειάζουν. Θέλεις ήρεμο κλίμα.",
    "scorpio": "Όταν στρεσάρεσαι, κλείνεσαι. Ανοίγεις μόνο σε όποιον εμπιστεύεσαι απόλυτα.",
    "sagittarius": "Όταν στρεσάρεσαι, θέλεις να φύγεις — σώμα ή μυαλό σε «ταξίδι».",
    "capricorn": "Όταν στρεσάρεσαι, δουλεύεις περισσότερο. Δείχνεις έλεγχο ενώ μέσα σου βαραίνεις.",
    "aquarius": "Όταν στρεσάρεσαι, αποστασιοποιείσαι για να σκεφτείς. Δεν σημαίνει ότι δεν νοιάζεσαι.",
    "pisces": "Όταν στρεσάρεσαι, μπερδεύεις τα δικά σου συναισθήματα με των άλλων. Χρειάζεσαι σιωπή.",
}

ASC_OUTWARD: dict[ZodiacSignId, str] = {
    "aries": "Οι άλλοι σε βλέπουν δυναμικό και αποφασιστικό — αυτόν που παίρνει πρωτοβουλία.",
    "taurus": "Οι άλλοι σε βλέπουν σταθερό και αξιόπιστο από την πρώτη ματιά.",
    "gemini": "Οι άλλοι σε βλέπουν ευκολομίλητο και ζωηρό.",
    "cancer": "Οι άλλοι σε βλέπουν ζεστό και προστατευτικό.",
    "leo": "Οι άλλοι σε προσέχουν· αφήνεις έντονη πρώτη εντύπωση.",
    "virgo": "Οι άλλοι σε βλέπουν μαζεμένο, προσεκτικό, πρακτικό.",
    "libra": "Οι άλλοι σε βλέπουν ευγενικό και διπλωματικό.",
    "scorpio": "Οι άλλοι σε βλέπουν έντονο και δύσκολο στο «διάβασμα».",
    "sagittarius": "Οι άλλοι σε βλέπουν ανοιχτό και αισιόδοξο.",
    "capricorn": "Οι άλλοι σε βλέπουν σοβαρό και υπεύθυνο πριν καν μιλήσεις πολύ.",
    "aquarius": "Οι άλλοι σε βλέπουν ιδιαίτερο και ανεξάρτητο.",
    "pisces": "Οι άλλοι σε βλέπουν μαλακό και εύκολα προσιτό.",
}

MERCURY_STYLE: dict[ZodiacSignId, str] = {
    "aries": "Σκέφτεσαι και μιλάς άμεσα· προτιμάς συμπεράσματα χωρίς περιττές περιστροφές.",
    "taurus": "Η σκέψη σου είναι πρακτική και αργή αλλά σταθερή· πείθεσαι με γεγονότα, όχι με φανφάρες.",
    "gemini": "Το μυαλό σου είναι γρήγορο, ευέλικτο και πολυθεματικό· συνδέεις ιδέες με ευκολία.",
    "cancer": "Επικοινωνείς με συναίσθημα και μνήμη· οι λέξεις σου συχνά κουβαλούν ιστορία.",
    "leo": "Εκφράζεσαι θεατρικά και πειστικά· θέλεις οι ιδέες σου να ακουστούν.",
    "virgo": "Αναλύεις με ακρίβεια· βελτιώνεις κείμενα, σχέδια και επιχειρήματα μέχρι να «κάτσουν».",
    "libra": "Ζυγίζεις απόψεις και αναζητάς δίκαιη διατύπωση· η διπλωματία είναι φυσική σου γλώσσα.",
    "scorpio": "Διαβάζεις κάτω από τις λέξεις· ρωτάς το ουσιώδες και δεν συμβιβάζεσαι με επιφανειακές απαντήσεις.",
    "sagittarius": "Σκέφτεσαι σε μεγάλη κλίμακα· γενικεύεις, φιλοσοφείς και εμπνέεις με οράματα.",
    "capricorn": "Η επικοινωνία σου είναι δομημένη και υπεύθυνη· μετράς τις λέξεις σου με στόχο.",
    "aquarius": "Οι ιδέες σου είναι πρωτότυπες και συχνά μπροστά από την εποχή· σκέφτεσαι συστημικά.",
    "pisces": "Η σκέψη σου είναι εικονική και διαισθητική· εκφράζεσαι καλύτερα με μεταφορές και τέχνη.",
}

VENUS_STYLE: dict[ZodiacSignId, str] = {
    "aries": "Στην αγάπη θέλεις πάθος και πρωτοβουλία· βαριέσαι την αδράνεια στις σχέσεις.",
    "taurus": "Αγαπάς με σταθερότητα, αφή και αισθητική απόλαυση· η πίστη μετράει πολύ.",
    "gemini": "Φλερτάρεις με το μυαλό· χρειάζεσαι διάλογο και ποικιλία για να μείνεις δεσμευμένος.",
    "cancer": "Δείχνεις αγάπη μέσα από φροντίδα και συναισθηματική παρουσία· το σπίτι είναι ιερό.",
    "leo": "Αγαπάς μεγαλόψυχα και θερμά· θέλεις να νιώθεις ξεχωριστός και να το δείχνεις.",
    "virgo": "Η αγάπη σου φαίνεται σε μικρές, πρακτικές πράξεις· η κριτική μπορεί να μπερδευτεί με ενδιαφέρον.",
    "libra": "Αναζητάς ισορροπία, ομορφιά και δίκαιη ανταλλαγή· η σχέση είναι τέχνη για σένα.",
    "scorpio": "Αγαπάς με ένταση και αποκλειστικότητα· η επιφανειακή οικειότητα δεν σε ικανοποιεί.",
    "sagittarius": "Θέλεις ελευθερία και κοινές περιπέτειες· η αγάπη μεγαλώνει με νόημα και γέλιο.",
    "capricorn": "Δεσμεύεσαι σοβαρά και μακροπρόθεσμα· η αγάπη περνά από σεβασμό και αξιοπιστία.",
    "aquarius": "Χρειάζεσαι φιλία και χώρο μέσα στην αγάπη· η ισότητα είναι μη διαπραγματεύσιμη.",
    "pisces": "Αγαπάς ιδεαλιστικά και συμπονετικά· τα όρια στις σχέσεις θέλουν συνειδητή φροντίδα.",
}

MARS_STYLE: dict[ZodiacSignId, str] = {
    "aries": "Δρας άμεσα και ανταγωνιστικά· η ενέργειά σου θέλει κανάλι εξόδου.",
    "taurus": "Επιμένεις με σταθερότητα· θυμώνεις αργά αλλά βαθιά όταν παραβιάζονται όρια.",
    "gemini": "Η δράση σου περνά από λόγια και ιδέες· πολεμάς με επιχειρήματα και ευελιξία.",
    "cancer": "Υπερασπίζεσαι ό,τι θεωρείς «δικό σου»· ο θυμός συχνά είναι προστατευτικός.",
    "leo": "Δρας με περηφάνια και θεατρικότητα· θέλεις η προσπάθειά σου να φανεί.",
    "virgo": "Κατευθύνεις την ενέργεια σε βελτίωση και ακρίβεια· ο θυμός γίνεται κριτική ή υπερ-εργασία.",
    "libra": "Αποφεύγεις την ανοιχτή σύγκρουση· όταν θυμώνεις, ζητάς δικαιοσύνη και ισορροπία.",
    "scorpio": "Η θέλησή σου είναι εστιασμένη και επίμονη· δεν παρατάς εύκολα ό,τι έχει σημασία.",
    "sagittarius": "Δρας με ορμή προς ελευθερία και στόχους μεγάλης κλίμακας· βαριέσαι τους περιορισμούς.",
    "capricorn": "Η ενέργειά σου είναι πειθαρχημένη· χτίζεις, αντέχεις και μετράς τη νίκη μακροπρόθεσμα.",
    "aquarius": "Δρας για ιδέες και ανεξαρτησία· αντιστέκεσαι σε αυθαίρετη εξουσία.",
    "pisces": "Η δράση σου είναι έμμεση ή εμπνευσμένη· μερικές φορές αποφεύγεις τη σύγκρουση με απόσυρση.",
}

STRENGTHS: dict[ZodiacSignId, tuple[str, ...]] = {
    "aries": ("Πρωτοβουλία", "Θάρρος", "Αμεσότητα", "Ενέργεια εκκίνησης"),
    "taurus": ("Υπομονή", "Αισθητική κρίση", "Αξιοπιστία", "Πρακτική σοφία"),
    "gemini": ("Προσαρμοστικότητα", "Επικοινωνία", "Περιέργεια", "Νοητική ευελιξία"),
    "cancer": ("Ενσυναίσθηση", "Φροντίδα", "Διαίσθηση", "Συναισθηματική μνήμη"),
    "leo": ("Δημιουργικότητα", "Γενναιοδωρία", "Παρουσία", "Καρδιά που εμπνέει"),
    "virgo": ("Ακρίβεια", "Χρησιμότητα", "Ανάλυση", "Πρακτική βοήθεια"),
    "libra": ("Διπλωματία", "Αισθητική", "Δικαιοσύνη", "Ικανότητα γεφύρωσης"),
    "scorpio": ("Βάθος", "Αντοχή", "Διαίσθηση", "Ικανότητα μεταμόρφωσης"),
    "sagittarius": ("Αισιοδοξία", "Όραμα", "Ανοιχτό μυαλό", "Χιούμορ"),
    "capricorn": ("Πειθαρχία", "Υπευθυνότητα", "Στρατηγική", "Αντοχή στον χρόνο"),
    "aquarius": ("Πρωτοτυπία", "Ανεξαρτησία", "Κοινωνική συνείδηση", "Αποστασιοποιημένη διαύγεια"),
    "pisces": ("Συμπόνια", "Φαντασία", "Καλλιτεχνική ευαισθησία", "Πνευματική δεκτικότητα"),
}

CHALLENGES: dict[ZodiacSignId, tuple[str, ...]] = {
    "aries": ("Ανυπομονησία", "Παρορμητικότητα", "Δυσκολία με την αναμονή"),
    "taurus": ("Πείσμα", "Αντίσταση στην αλλαγή", "Υπερβολική προσκόλληση"),
    "gemini": ("Διάσπαση προσοχής", "Επιφανειακότητα όταν βιάζεσαι", "Αστάθεια δεσμεύσεων"),
    "cancer": ("Υπερευαισθησία", "Υπερπροστατευτικότητα", "Δυσκολία να αφήσεις το παρελθόν"),
    "leo": ("Ανάγκη επιβεβαίωσης", "Υπερηφάνεια που πληγώνεται", "Δράμα όταν νιώθεις αόρατος"),
    "virgo": ("Υπερκριτική", "Άγχος τελειότητας", "Δυσκολία να «αφήσεις»"),
    "libra": ("Αναβλητικότητα στις αποφάσεις", "Αποφυγή σύγκρουσης", "Υπερβολική εξάρτηση από γνώμη άλλων"),
    "scorpio": ("Ζήλια / έλεγχος", "Δυσκολία εμπιστοσύνης", "Ένταση που δεν εκτονώνεται"),
    "sagittarius": ("Υπερβολή", "Αποφυγή λεπτομερειών", "Υποσχέσεις μεγαλύτερες από τη δέσμευση"),
    "capricorn": ("Συναισθηματική συγκράτηση", "Υπερβολική πίεση στον εαυτό", "Κυνισμός όταν κουράζεσαι"),
    "aquarius": ("Συναισθηματική απόσταση", "Αποστασιοποίηση", "Πείσμα στις ιδέες"),
    "pisces": ("Θολά όρια", "Αποφυγή", "Τάση να χάνεσαι στις ανάγκες των άλλων"),
}

ELEMENT_OF: dict[ZodiacSignId, str] = {
    "aries": "fire",
    "leo": "fire",
    "sagittarius": "fire",
    "taurus": "earth",
    "virgo": "earth",
    "capricorn": "earth",
    "gemini": "air",
    "libra": "air",
    "aquarius": "air",
    "cancer": "water",
    "scorpio": "water",
    "pisces": "water",
}

ELEMENT_EL = {
    "fire": "Φωτιά",
    "earth": "Γη",
    "air": "Αέρας",
    "water": "Νερό",
}

def _sign_phrase(sign_id: ZodiacSignId) -> str:
    """Greek 'στον/στην/στους X' with correct accusative."""
    acc = ACCUSATIVE[sign_id]
    if sign_id in PLURAL:
        return f"στους **{acc}**"
    if sign_id in FEMININE:
        return f"στην **{acc}**"
    return f"στον **{acc}**"



# Pairwise sun–moon narrative seeds (element combos)
_ELEMENT_TENSION: dict[tuple[str, str], str] = {
    ("fire", "water"): (
        "Η φωτιά του Ήλιου θέλει δράση και έκφραση, ενώ το νερό της Σελήνης "
        "ζητά ασφάλεια και βάθος συναισθήματος. Αυτή η ένταση μπορεί να γίνει "
        "δημιουργική δύναμη όταν μάθεις να μην αγνοείς ούτε την ορμή ούτε την καρδιά."
    ),
    ("water", "fire"): (
        "Η συναισθηματική σου φύση (Σελήνη) συναντά έναν Ήλιο που ζητά πρωτοβουλία. "
        "Μερικές φορές νιώθεις πριν δράσεις· άλλες φορές δρας για να μην νιώσεις. "
        "Η ισορροπία έρχεται όταν η δράση υπηρετεί αυτό που πραγματικά νιώθεις."
    ),
    ("fire", "earth"): (
        "Ο Ήλιος σου φέρνει ορμή και όραμα· η Σελήνη γειώνει και ζητά αποτελέσματα. "
        "Όταν συνδυάζεις έμπνευση με πρακτικά βήματα, χτίζεις κάτι που αντέχει."
    ),
    ("earth", "fire"): (
        "Σταθερότητα έξω, φωτιά μέσα: η Σελήνη σου θέλει κίνηση ενώ ο Ήλιος "
        "χτίζει με υπομονή. Χρειάζεσαι τόσο δομή όσο και χώρο για αυθορμησία."
    ),
    ("fire", "air"): (
        "Φωτιά και αέρας τροφοδοτούνται αμοιβαία: ιδέες που γίνονται δράση, "
        "και δράση που γεννά νέες ιδέες. Πρόσεξε να μην ζεις μόνο στην ταχύτητα."
    ),
    ("air", "fire"): (
        "Το μυαλό σου (Σελήνη στον αέρα) συναντά έναν Ήλιο που θέλει να δράσει. "
        "Όταν οι ιδέες βρίσκουν κανάλι έκφρασης, είσαι ασταμάτητος· χωρίς εστίαση, σκορπίζεσαι."
    ),
    ("earth", "water"): (
        "Γη και νερό: η πρακτικότητα συναντά το συναίσθημα. Μπορείς να φροντίζεις "
        "με πράξεις και να χτίζεις ασφάλεια χωρίς να σκληραίνεις την καρδιά."
    ),
    ("water", "earth"): (
        "Η συναισθηματική σου φύση ζητά γείωση. Ο Ήλιος στη γη σου δίνει δομή· "
        "η Σελήνη στο νερό σου υπενθυμίζει ότι η ασφάλεια δεν είναι μόνο υλική."
    ),
    ("earth", "air"): (
        "Πρακτικότητα και ιδέες: ο Ήλιος θέλει απτά αποτελέσματα, η Σελήνη "
        "χρειάζεται νοητική ελευθερία. Όταν γειώνεις τις ιδέες σου, γίνεσαι πολύ αποτελεσματικός."
    ),
    ("air", "earth"): (
        "Σκέψη που θέλει γείωση: η Σελήνη στη γη ζητά σταθερότητα ενώ ο Ήλιος "
        "στον αέρα ανοίγει ορίζοντες. Μικρές ρουτίνες βοηθούν τις μεγάλες ιδέες να υλοποιηθούν."
    ),
    ("air", "water"): (
        "Αέρας και νερό: λογική και συναίσθημα σε διάλογο. Μερικές φορές "
        "αναλύεις αυτό που απλώς χρειάζεται να νιώσεις — και το αντίστροφο. "
        "Η τέχνη είναι να μην ακυρώνεις καμία πλευρά."
    ),
    ("water", "air"): (
        "Βαθιά συναισθήματα συναντούν ανάγκη για απόσταση και σαφήνεια. "
        "Η Σελήνη στον αέρα σε βοηθά να βάλεις λέξεις σε ό,τι νιώθεις ο Ήλιος σου."
    ),
    ("fire", "fire"): (
        "Διπλή φωτιά: έντονη ζωτικότητα, πάθος και ανάγκη για έκφραση. "
        "Η πρόκληση είναι να κατευθύνεις τη φλόγα χωρίς να καείς από ανυπομονησία."
    ),
    ("earth", "earth"): (
        "Διπλή γη: σταθερότητα, υπομονή και πρακτική σοφία. Πρόσεξε να μην "
        "γίνεσαι υπερβολικά άκαμπτος όταν η ζωή ζητά ευελιξία."
    ),
    ("air", "air"): (
        "Διπλός αέρας: ιδέες, διάλογος και νοητική ευελιξία. Χρειάζεσαι "
        "γειώσεις (σώμα, ρουτίνα, φύση) για να μην ζεις μόνο στο κεφάλι."
    ),
    ("water", "water"): (
        "Διπλό νερό: βαθιά ενσυναίσθηση και συναισθηματική διαίσθηση. "
        "Τα όρια και ο χρόνος μόνος είναι απαραίτητα για να μην απορροφάς τα πάντα."
    ),
}


@dataclass(frozen=True)
class PersonalityAnalysis:
    summary: str
    sun_section: str
    moon_section: str
    asc_section: str
    mercury_section: Optional[str] = None
    venus_section: Optional[str] = None
    mars_section: Optional[str] = None
    strengths: list[str] = field(default_factory=list)
    challenges: list[str] = field(default_factory=list)
    disclaimer_el: str = DISCLAIMER_EL

    def iter_sections(self) -> list[tuple[str, str]]:
        """Ordered (title, body) pairs for rich UI rendering."""
        sections: list[tuple[str, str]] = [
            ("☉ Ήλιος — πυρήνας ταυτότητας", self.sun_section),
            ("☽ Σελήνη — συναισθήματα", self.moon_section),
            ("↑ Ωροσκόπος — πώς σε βλέπουν", self.asc_section),
        ]
        if self.mercury_section:
            sections.append(("☿ Ερμής — σκέψη & επικοινωνία", self.mercury_section))
        if self.venus_section:
            sections.append(("♀ Αφροδίτη — αγάπη & αξίες", self.venus_section))
        if self.mars_section:
            sections.append(("♂ Άρης — δράση & επιθυμία", self.mars_section))
        return sections

    def to_markdown(self) -> str:
        parts: list[str] = []
        parts.append("### Συνολική εικόνα")
        parts.append(self.summary)
        parts.append("")
        parts.append("### Ήλιος — πυρήνας ταυτότητας")
        parts.append(self.sun_section)
        parts.append("")
        parts.append("### Σελήνη — συναισθήματα")
        parts.append(self.moon_section)
        parts.append("")
        parts.append("### Ωροσκόπος — πώς σε βλέπουν")
        parts.append(self.asc_section)
        if self.mercury_section:
            parts.append("")
            parts.append("### Ερμής — σκέψη & επικοινωνία")
            parts.append(self.mercury_section)
        if self.venus_section:
            parts.append("")
            parts.append("### Αφροδίτη — αγάπη & αξίες")
            parts.append(self.venus_section)
        if self.mars_section:
            parts.append("")
            parts.append("### Άρης — δράση & επιθυμία")
            parts.append(self.mars_section)
        if self.strengths:
            parts.append("")
            parts.append("### Δυνάμεις")
            parts.extend(f"- {s}" for s in self.strengths)
        if self.challenges:
            parts.append("")
            parts.append("### Προκλήσεις")
            parts.extend(f"- {c}" for c in self.challenges)
        parts.append("")
        parts.append(f"*{self.disclaimer_el}*")
        return "\n".join(parts)


def _planet_by_id(chart: NatalChart, pid: str) -> Optional[PlanetPosition]:
    for p in chart.planets:
        if p.id == pid:
            return p
    return None


def _unique_preserve(items: list[str], limit: int = 8) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for x in items:
        if x not in seen:
            seen.add(x)
            out.append(x)
        if len(out) >= limit:
            break
    return out


def _blend_summary(
    sun_id: ZodiacSignId,
    moon_id: ZodiacSignId,
    asc_id: Optional[ZodiacSignId],
    name: str,
) -> str:
    return build_rich_summary(sun_id, moon_id, asc_id, name)



def analyze_personality(
    chart: NatalChart,
    profile: BirthProfile | None = None,
) -> PersonalityAnalysis:
    """Build structured Greek personality text from natal placements (deterministic)."""
    name = (profile.name.strip() if profile and profile.name else "") or ""

    sun = _planet_by_id(chart, "sun")
    moon = _planet_by_id(chart, "moon")
    if sun is None or moon is None:
        raise ValueError("Ο χάρτης χρειάζεται τουλάχιστον Ήλιο και Σελήνη.")

    sun_id: ZodiacSignId = sun.sign  # type: ignore[assignment]
    moon_id: ZodiacSignId = moon.sign  # type: ignore[assignment]

    asc_id: Optional[ZodiacSignId] = None
    if chart.ascendant is not None and not chart.approximate:
        asc_id = chart.ascendant.sign  # type: ignore[assignment]

    sun_z = get_zodiac_by_id(sun_id)
    moon_z = get_zodiac_by_id(moon_id)

    sun_section = warm_wrap(
        "Ήλιος",
        f"**{sun.formatted}** — {CORE_IDENTITY[sun_id]}",
    )
    moon_section = warm_wrap(
        "Σελήνη",
        f"**{moon.formatted}** — {MOON_EMOTIONS[moon_id]}",
    )

    if asc_id and chart.ascendant is not None:
        asc_z = get_zodiac_by_id(asc_id)
        asc_section = warm_wrap(
            "Ωροσκόπος",
            f"**{chart.ascendant.formatted}** — {ASC_OUTWARD[asc_id]}",
        )
    else:
        asc_section = (
            "Χωρίς ακριβή ώρα, δεν «ανοίγει» ο Ωροσκόπος — και κρίμα, γιατί εκεί "
            "φαίνεται το πρώτο σου χαμόγελο στον κόσμο. Βάλε ώρα και τόπο όταν μπορείς· "
            "θα σε διαβάσουμε πιο καθαρά."
        )

    mercury = _planet_by_id(chart, "mercury")
    venus = _planet_by_id(chart, "venus")
    mars = _planet_by_id(chart, "mars")

    mercury_section = None
    if mercury is not None:
        mid: ZodiacSignId = mercury.sign  # type: ignore[assignment]
        mercury_section = warm_wrap("Ερμής", f"**{mercury.formatted}** — {MERCURY_STYLE[mid]}")

    venus_section = None
    if venus is not None:
        vid: ZodiacSignId = venus.sign  # type: ignore[assignment]
        venus_section = warm_wrap("Αφροδίτη", f"**{venus.formatted}** — {VENUS_STYLE[vid]}")

    mars_section = None
    if mars is not None:
        maid: ZodiacSignId = mars.sign  # type: ignore[assignment]
        mars_section = warm_wrap("Άρης", f"**{mars.formatted}** — {MARS_STYLE[maid]}")

    strength_pool: list[str] = []
    challenge_pool: list[str] = []
    for sid in (sun_id, moon_id, *( [asc_id] if asc_id else [] )):
        strength_pool.extend(STRENGTHS[sid])
        challenge_pool.extend(CHALLENGES[sid])

    # Prefer sun then moon then asc ordering already in pool; dedupe
    strengths = _unique_preserve(strength_pool, limit=7)
    challenges = _unique_preserve(challenge_pool, limit=6)

    summary = _blend_summary(sun_id, moon_id, asc_id, name)

    return PersonalityAnalysis(
        summary=summary,
        sun_section=sun_section,
        moon_section=moon_section,
        asc_section=asc_section,
        mercury_section=mercury_section,
        venus_section=venus_section,
        mars_section=mars_section,
        strengths=strengths,
        challenges=challenges,
        disclaimer_el=DISCLAIMER_EL,
    )
