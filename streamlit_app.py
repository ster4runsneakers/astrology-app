"""
Αστρολογικός χάρτης — Streamlit MVP
Main entry for Streamlit Community Cloud (Main file path: streamlit_app.py)
"""
from __future__ import annotations

from datetime import date, datetime, time

import pandas as pd
import streamlit as st

from chart_viz import build_chart_figure, chart_table_rows, houses_table_rows
from horoscope import get_daily_horoscope
from natal import (
    DEFAULT_PROFILE,
    BirthProfile,
    compute_natal_chart,
    ensure_ephemeris_ready,
    get_sun_sign_from_profile,
)
from places import PLACE_PRESETS, PRESET_NAMES, TIMEZONE_OPTIONS, get_preset

st.set_page_config(
    page_title="Αστρολογικός χάρτης",
    page_icon="♈",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# --- Session defaults ---------------------------------------------------------
if "profile" not in st.session_state:
    st.session_state.profile = BirthProfile()
if "computed" not in st.session_state:
    st.session_state.computed = False
if "ephemeris_ok" not in st.session_state:
    st.session_state.ephemeris_ok = False


def _apply_preset(name: str) -> None:
    preset = get_preset(name)
    if preset:
        p = st.session_state.profile
        p.place_name = preset["name"]
        p.latitude = preset["latitude"]
        p.longitude = preset["longitude"]
        p.timezone = preset.get("timezone", p.timezone)


# --- Styles -------------------------------------------------------------------
st.markdown(
    """
<style>
  .block-container { padding-top: 1.5rem; max-width: 720px; }
  .sun-hero {
    text-align: center;
    padding: 1.25rem 1rem;
    border-radius: 1rem;
    background: linear-gradient(145deg, #1a1530 0%, #2a1f4a 55%, #1e293b 100%);
    border: 1px solid #3b3358;
    margin: 0.5rem 0 1rem 0;
  }
  .sun-hero .sym { font-size: 3rem; line-height: 1; }
  .sun-hero .name { font-size: 1.75rem; font-weight: 700; color: #f0e9ff; margin-top: 0.25rem; }
  .sun-hero .meta { color: #a78bfa; font-size: 0.95rem; }
  .disclaimer {
    font-size: 0.8rem; color: #94a3b8; border-left: 3px solid #a78bfa;
    padding-left: 0.75rem; margin-top: 0.75rem;
  }
  footer { visibility: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# --- Header -------------------------------------------------------------------
st.markdown(
    """
<div style="text-align:center">
  <p style="letter-spacing:0.25em;text-transform:uppercase;color:#7c6bb5;font-size:0.8rem;margin:0">
    Astrology MVP
  </p>
  <h1 style="margin:0.35rem 0 0.25rem 0;color:#f8f7fc">Αστρολογικός χάρτης</h1>
  <p style="color:#94a3b8;font-size:0.95rem;margin:0 auto;max-width:28rem">
    Ζώδιο, ημερήσια πρόβλεψη και βασικός γενέθλιος χάρτης — χωρίς επί πληρωμή APIs.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

st.divider()

# --- Birth form ---------------------------------------------------------------
st.subheader("Στοιχεία γέννησης")

profile: BirthProfile = st.session_state.profile

with st.form("birth_form", clear_on_submit=False):
    name = st.text_input(
        "Όνομα (προαιρετικό)",
        value=profile.name,
        placeholder="π.χ. Μαρία",
    )

    col1, col2 = st.columns(2)
    with col1:
        try:
            default_dob = date.fromisoformat(profile.date_of_birth)
        except ValueError:
            default_dob = date(1990, 6, 15)
        dob = st.date_input(
            "Ημερομηνία γέννησης *",
            value=default_dob,
            min_value=date(1900, 1, 1),
            max_value=date.today(),
            format="DD/MM/YYYY",
        )
    with col2:
        try:
            hh, mm = (int(x) for x in (profile.birth_time or "12:00").split(":")[:2])
            default_t = time(hh, mm)
        except ValueError:
            default_t = time(12, 0)
        # Always enabled: forms don't rerun on checkbox change, so disabled= locks UX.
        birth_t = st.time_input(
            "Ώρα γέννησης",
            value=default_t,
            help="Για Ωροσκόπο και οίκους χρειάζεται ακριβής ώρα.",
        )
        time_unknown = st.checkbox(
            "Ώρα άγνωστη / προσεγγιστική",
            value=profile.time_unknown,
            help="Αν ενεργό, αγνοείται η ώρα και χρησιμοποιείται μεσημέρι (12:00) χωρίς Ωροσκόπο/οίκους.",
        )

    if time_unknown:
        st.caption(
            "📌 Με άγνωστη ώρα: υπολογισμός στις **12:00**. "
            "Ξετσεκάρετε για να χρησιμοποιηθεί η ώρα που βάλατε."
        )

    preset = st.selectbox(
        "Τόπος (προεπιλογές)",
        options=PRESET_NAMES,
        index=PRESET_NAMES.index(profile.place_name)
        if profile.place_name in PRESET_NAMES
        else 0,
    )
    place_custom = st.text_input(
        "Όνομα τόπου",
        value=profile.place_name,
        help="Μπορείτε να αλλάξετε το όνομα· lat/lng από προεπιλογή ή χειροκίνητα παρακάτω.",
    )

    preset_tz = (get_preset(preset) or {}).get("timezone", profile.timezone)
    tz_options = list(dict.fromkeys([preset_tz, profile.timezone, *TIMEZONE_OPTIONS]))
    tz_index = tz_options.index(profile.timezone) if profile.timezone in tz_options else 0
    timezone_name = st.selectbox(
        "Ζώνη ώρας (για σωστό Ωροσκόπο)",
        options=tz_options,
        index=tz_index,
        help="Η ώρα γέννησης ερμηνεύεται σε αυτή τη ζώνη (με θερινή ώρα αν ισχύει).",
    )

    c_lat, c_lng = st.columns(2)
    preset_obj = get_preset(preset) or PLACE_PRESETS[0]
    # When user picks a new preset in the form, seed lat/lng from it if place matches
    with c_lat:
        latitude = st.number_input(
            "Γεωγραφικό πλάτος (lat)",
            value=float(profile.latitude),
            min_value=-90.0,
            max_value=90.0,
            format="%.4f",
        )
    with c_lng:
        longitude = st.number_input(
            "Γεωγραφικό μήκος (lng)",
            value=float(profile.longitude),
            min_value=-180.0,
            max_value=180.0,
            format="%.4f",
        )

    use_preset_coords = st.checkbox(
        "Χρήση συντεταγμένων από την επιλεγμένη προεπιλογή",
        value=True,
        help="Αν ενεργό, lat/lng παίρνουν τις τιμές της πόλης που επιλέξατε πάνω.",
    )

    submitted = st.form_submit_button("Υπολογισμός χάρτη", type="primary", use_container_width=True)

if submitted:
    if use_preset_coords and preset_obj:
        latitude = float(preset_obj["latitude"])
        longitude = float(preset_obj["longitude"])
        place_name = preset_obj["name"] if not place_custom.strip() else place_custom.strip()
        if place_custom.strip() == profile.place_name or not place_custom.strip():
            place_name = preset_obj["name"]
        else:
            place_name = place_custom.strip()
    else:
        place_name = place_custom.strip() or preset

    bt = "12:00" if time_unknown else birth_t.strftime("%H:%M")
    # Prefer selected timezone; if using preset coords, keep user's TZ choice
    # unless they just picked a city (preset_tz already in timezone_name list).
    st.session_state.profile = BirthProfile(
        name=name.strip(),
        date_of_birth=dob.isoformat(),
        birth_time=bt,
        time_unknown=time_unknown,
        place_name=place_name,
        latitude=float(latitude),
        longitude=float(longitude),
        timezone=timezone_name,
    )
    st.session_state.computed = True
    # Quick button outside form to sync preset coords when checkbox used
    st.rerun()

# Sync lat/lng helper when preset changes outside computation
with st.expander("Γρήγορη εφαρμογή προεπιλογής τόπου"):
    psel = st.selectbox("Πόλη", PRESET_NAMES, key="quick_preset")
    if st.button("Εφαρμογή lat/lng"):
        _apply_preset(psel)
        st.success(f"Εφαρμόστηκε: {psel}")
        st.rerun()

profile = st.session_state.profile

# Auto-compute on first load with defaults so UI isn't empty
if not st.session_state.computed:
    st.session_state.computed = True

# --- Load ephemeris (once) ----------------------------------------------------
if not st.session_state.ephemeris_ok:
    with st.spinner("Φόρτωση εφημερίδας JPL DE421 (μία φορά)…"):
        try:
            ensure_ephemeris_ready()
            st.session_state.ephemeris_ok = True
        except Exception as exc:  # noqa: BLE001
            st.error(f"Αποτυχία φόρτωσης εφημερίδας: {exc}")
            st.stop()

# --- Results ------------------------------------------------------------------
sun = get_sun_sign_from_profile(profile)
horoscope = get_daily_horoscope(sun.id, date.today())
chart = compute_natal_chart(profile)

# Sun sign
who = f" για {profile.name}" if profile.name else ""
st.markdown(
    f"""
<div class="sun-hero">
  <div class="sym">{sun.symbol}</div>
  <div class="name">{sun.name_el}</div>
  <div class="meta">{sun.element_el} · {sun.modality_el}{who}</div>
  <div style="color:#94a3b8;font-size:0.85rem;margin-top:0.5rem">Ζώδιο ηλίου (τροπικό)</div>
</div>
""",
    unsafe_allow_html=True,
)

# Daily horoscope
st.subheader(f"Ημερήσια πρόβλεψη {horoscope.symbol}")
st.caption(horoscope.date_label_el)
st.write(horoscope.text)
st.markdown(
    f'<p class="disclaimer">{horoscope.disclaimer_el}</p>',
    unsafe_allow_html=True,
)

# Natal chart
st.subheader("Γενέθλιος χάρτης")
if chart.approximate:
    st.info(
        "Ώρα προσεγγιστική (μεσημέρι) — εμφανίζονται πλανήτες χωρίς Ωροσκόπο / οίκους."
    )

fig = build_chart_figure(chart)
st.pyplot(fig, clear_figure=True, use_container_width=True)

df = pd.DataFrame(chart_table_rows(chart))
st.dataframe(df, use_container_width=True, hide_index=True)

if chart.houses:
    st.markdown("**Οίκοι (Equal House)**")
    st.dataframe(
        pd.DataFrame(houses_table_rows(chart.houses)),
        use_container_width=True,
        hide_index=True,
    )

for note in chart.notes:
    st.caption(f"ℹ️ {note}")

st.divider()
st.caption(
    "Υπολογισμοί με Skyfield + JPL DE421 · προφίλ σε `st.session_state` "
    "(το Streamlit Cloud είναι εφήμερο — δεν υπάρχει μόνιμη αποθήκευση) · MVP επίδειξης"
)
