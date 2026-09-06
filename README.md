# Αστρολογικός χάρτης / Astrology MVP (Streamlit)

Εφαρμογή Streamlit (MVP) με UI στα **Ελληνικά**: φόρμα γέννησης, ζώδιο ηλίου, ημερήσια πρόβλεψη και βασικός γενέθλιος χάρτης.

A Streamlit Community Cloud–ready MVP: birth form, sun sign, deterministic Greek daily horoscope, and a natal chart powered by **Skyfield + JPL DE421** (no paid APIs).

**Flat layout** — όλα τα `.py` στο root του repo (εύκολο upload από το GitHub web UI).

---

## Streamlit Community Cloud

| Setting | Value |
|--------|--------|
| Repository | `https://github.com/ster4runsneakers/astrology-app` |
| Branch | `main` (or your default) |
| **Main file path** | **`streamlit_app.py`** |
| Python | 3.10+ |

### Deploy steps

1. Upload files to the GitHub repo root (see `UPLOAD_GREEK.txt`). Keep `.py` extensions.
2. Open [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select the repo / branch.
4. Set **Main file path** to: `streamlit_app.py`
5. Deploy. First boot downloads JPL DE421 (~17 MB) into `data/` (ephemeral on Cloud).

No API keys or secrets required.

---

## Τοπικό τρέξιμο / Local run

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

---

## Ephemeris: Skyfield + JPL DE421

- Geocentric apparent ecliptic longitudes (tropical zodiac).
- Ascendant via GMST + latitude/obliquity; **Equal House** when birth time + place are known.
- Without time: noon + approximate flag (no Asc/houses).
- Time zone: local mean time approximated as `UTC ≈ local − longitude/15h` (no IANA TZ database).

---

## Scope / Λειτουργίες

1. Birth form (optional name, required DOB, optional time default noon, place + lat/lng with Greek presets).
2. Sun sign (**ζώδιο**) prominent.
3. Daily Greek horoscope bank keyed by sign + date (illustrative MVP).
4. Natal: Sun, Moon, Asc (if time), Mercury, Venus, Mars, Jupiter, Saturn — wheel + table.
5. Profile kept in `st.session_state` (Cloud is ephemeral — no durable persistence).

---

## Limitations / Περιορισμοί

- No IANA time zones — longitude-based offset only.
- Equal houses only (not Placidus).
- No aspects, progressions, or synastry.
- Daily horoscope is generated demo text, not professional advice.
- No external geocoding; use presets or enter lat/lng manually.
- Streamlit Cloud filesystem is ephemeral; DE421 may re-download after restarts.

---

## Δομή / Layout (flat)

```
streamlit_app.py      # MAIN ENTRY (Streamlit Cloud)
natal.py
zodiac.py
horoscope.py
places.py
chart_viz.py
requirements.txt
README.md
.gitignore
.streamlit/config.toml
data/                 # DE421 download cache (gitignored *.bsp)
```

## GitHub

https://github.com/ster4runsneakers/astrology-app
