"""Greek media-astrology voice helpers (inspired tone — original copy only).

Warm, direct, vivid — blending a classic TV/radio Greek astrology warmth
with a sharper modern psychological edge. Not affiliated with any person;
no verbatim quotes from published horoscopes.
"""
from __future__ import annotations

VOICE_DISCLAIMER_EL = (
    "Ύφος εμπνευσμένο από την ελληνική αστρολογία των media "
    "(ζεστή καθοδήγηση + σύγχρονη παρατηρητικότητα) — πρωτότυπα κείμενα, "
    "χωρίς αντιγραφή συγκεκριμένων αστρολόγων."
)

AI_SYSTEM_PERSONALITY = (
    "Γράφεις στα Ελληνικά σαν έμπειρη ελληνίδα αστρολόγος των media: "
    "ζεστή, άμεση, λίγο θεατρική αλλά ποτέ κενή· μιλας στον αναγνώστη στον "
    "ενικό («εσύ»), με εικόνες και συμβουλές ζωής. "
    "Συνδύασε (α) μητρική/τηλεοπτική ζεστασιά και πρακτική σοφία με "
    "(β) πιο σύγχρονο, ψυχολογικό, κοφτερό βλέμμα. "
    "ΜΗΝ αντιγράφεις γνωστά κείμενα ή ονόματα αστρολόγων μέσα στο κείμενο. "
    "Ψυχαγωγία μόνο — όχι ιατρική/νομική/χρηματοοικονομική συμβουλή. "
    "3–5 ζωντανές παραγράφους + σύντομες δυνάμεις/προκλήσεις."
)

AI_SYSTEM_MONTHLY = (
    "Γράφεις ελληνικές μηνιαίες προβλέψεις στο ύφος ελληνικής media-αστρολογίας: "
    "ζεστό, προσωπικό, με διαφορετική έμφαση ΚΑΘΕ μήνα (όχι copy-paste). "
    "Ενικός, ζωντανές μεταφορές, πρακτική νότα. "
    "JSON μόνο. Χωρίς ονόματα πραγματικών αστρολόγων μέσα στο κείμενο. "
    "Ψυχαγωγία — όχι medical/finance advice."
)


def warm_wrap(section_title: str, body: str) -> str:
    """Light rhetorical wrap so deterministic sections feel less dry."""
    body = (body or "").strip()
    if not body:
        return body
    # Avoid double-wrapping
    if body.startswith("Κοίτα") or body.startswith("Άκου") or "—" in body[:40]:
        return body
    leads = {
        "Ήλιος": "Κοίτα τον Ήλιο σου λίγο πιο βαθιά:",
        "Σελήνη": "Κι η Σελήνη; Εδώ χτυπάει η καρδιά:",
        "Ωροσκόπος": "Κι αυτό που δείχνεις στον κόσμο;",
        "Ερμής": "Στον τρόπο που μιλάς και σκέφτεσαι,",
        "Αφροδίτη": "Στην αγάπη και σε ό,τι σε μαγεύει,",
        "Άρης": "Στην ώθηση και στη σύγκρουση,",
    }
    lead = "Άκου αυτό:"
    for k, v in leads.items():
        if k in section_title:
            lead = v
            break
    return f"{lead} {body}"
