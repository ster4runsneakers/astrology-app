"""
Αστρολογικός χάρτης — Streamlit MVP
Main entry for Streamlit Community Cloud (Main file path: streamlit_app.py)
"""
from __future__ import annotations

from datetime import date, time

import pandas as pd
import streamlit as st

from chart_viz import build_chart_figure, chart_table_rows, houses_table_rows
from ai_enrich import enrich_monthly_outlook, enrich_personality, keys_status
from chinese_zodiac import get_chinese_zodiac
from horoscope import get_daily_horoscope
from monthly_outlook import build_monthly_outlook
from natal import (
    BirthProfile,
    compute_natal_chart,
    ensure_ephemeris_ready,
    get_sun_sign_from_profile,
)
from personality import analyze_personality
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
  /* Layout */
  .block-container {
    padding-top: 1.25rem;
    padding-bottom: 2.5rem;
    max-width: 760px;
  }
  footer { visibility: hidden; }
  header[data-testid="stHeader"] { background: transparent; }

  /* Typography */
  h1, h2, h3 { letter-spacing: -0.01em; }
  .stMarkdown p { line-height: 1.55; }

  /* App header */
  .app-header {
    text-align: center;
    margin-bottom: 0.25rem;
  }
  .app-kicker {
    letter-spacing: 0.28em;
    text-transform: uppercase;
    color: #9b87d8;
    font-size: 0.72rem;
    margin: 0;
    font-weight: 600;
  }
  .app-title {
    margin: 0.4rem 0 0.35rem 0;
    color: #f8f7fc;
    font-size: clamp(1.55rem, 4.5vw, 2rem);
    font-weight: 700;
    line-height: 1.2;
  }
  .app-sub {
    color: #a8a3b8;
    font-size: 0.92rem;
    margin: 0 auto;
    max-width: 30rem;
    line-height: 1.5;
  }

  /* Cards */
  .ui-card {
    background: linear-gradient(160deg, rgba(28, 22, 48, 0.95) 0%, rgba(18, 16, 32, 0.98) 100%);
    border: 1px solid rgba(167, 139, 250, 0.22);
    border-radius: 1rem;
    padding: 1.1rem 1.15rem 1.15rem;
    margin: 0.65rem 0 1rem 0;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.28);
  }
  .ui-card-title {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #b8a5e8;
    margin: 0 0 0.75rem 0;
  }

  /* Sun hero */
  .sun-hero {
    text-align: center;
    padding: 1.5rem 1.1rem 1.35rem;
    border-radius: 1.15rem;
    background:
      radial-gradient(ellipse at 50% 0%, rgba(167, 139, 250, 0.28) 0%, transparent 55%),
      linear-gradient(145deg, #1c1535 0%, #2a1f4e 50%, #15182a 100%);
    border: 1px solid rgba(196, 181, 253, 0.35);
    margin: 0.35rem 0 1.1rem 0;
    box-shadow: 0 10px 36px rgba(88, 60, 160, 0.22);
  }
  .sun-hero .sym {
    font-size: clamp(2.6rem, 8vw, 3.4rem);
    line-height: 1;
    filter: drop-shadow(0 0 12px rgba(240, 199, 94, 0.35));
  }
  .sun-hero .name {
    font-size: clamp(1.45rem, 5vw, 1.85rem);
    font-weight: 700;
    color: #f5f0ff;
    margin-top: 0.35rem;
  }
  .sun-hero .meta {
    color: #c4b5fd;
    font-size: 0.95rem;
    margin-top: 0.15rem;
  }
  .sun-hero .label {
    color: #8b8699;
    font-size: 0.8rem;
    margin-top: 0.55rem;
    letter-spacing: 0.06em;
  }

  /* Angle chips (Asc / MC) */
  .angle-row {
    display: flex;
    gap: 0.65rem;
    flex-wrap: wrap;
    margin: 0.35rem 0 0.85rem 0;
  }
  .angle-chip {
    flex: 1 1 140px;
    min-width: 140px;
    background: rgba(167, 139, 250, 0.1);
    border: 1px solid rgba(196, 181, 253, 0.35);
    border-radius: 0.85rem;
    padding: 0.85rem 0.95rem;
    text-align: center;
  }
  .angle-chip .k {
    font-size: 0.7rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #b8a5e8;
    font-weight: 700;
    margin: 0;
  }
  .angle-chip .v {
    font-size: 1.05rem;
    font-weight: 700;
    color: #f0e9ff;
    margin: 0.25rem 0 0 0;
  }
  .angle-chip .d {
    font-size: 0.8rem;
    color: #a8a3b8;
    margin: 0.15rem 0 0 0;
  }

  /* Personality section blocks */
  .pers-block {
    background: rgba(22, 18, 42, 0.7);
    border: 1px solid rgba(167, 139, 250, 0.18);
    border-radius: 0.85rem;
    padding: 0.9rem 1rem;
    margin: 0.55rem 0;
  }
  .pers-block h4 {
    margin: 0 0 0.4rem 0;
    font-size: 0.95rem;
    color: #e4dcff;
  }
  .tag-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.4rem;
    margin: 0.35rem 0 0.2rem 0;
  }
  .tag {
    background: rgba(167, 139, 250, 0.14);
    border: 1px solid rgba(196, 181, 253, 0.28);
    color: #e8e0ff;
    border-radius: 999px;
    padding: 0.28rem 0.7rem;
    font-size: 0.82rem;
  }
  .tag.challenge {
    background: rgba(251, 146, 60, 0.1);
    border-color: rgba(251, 146, 60, 0.3);
    color: #fdd5b0;
  }

  /* Disclaimer */
  .disclaimer {
    font-size: 0.78rem;
    color: #9b97b0;
    border-left: 3px solid #a78bfa;
    padding: 0.55rem 0.75rem;
    margin-top: 0.85rem;
    background: rgba(167, 139, 250, 0.06);
    border-radius: 0 0.5rem 0.5rem 0;
    line-height: 1.45;
  }

  /* Form polish */
  div[data-testid="stForm"] {
    background: linear-gradient(160deg, rgba(28, 22, 48, 0.85) 0%, rgba(18, 16, 32, 0.92) 100%);
    border: 1px solid rgba(167, 139, 250, 0.22);
    border-radius: 1rem;
    padding: 1rem 1rem 0.85rem;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.22);
  }
  div[data-testid="stForm"] .stButton > button {
    margin-top: 0.35rem;
    font-weight: 650;
    border-radius: 0.65rem;
    min-height: 2.75rem;
  }

  /* Tabs */
  .stTabs [data-baseweb="tab-list"] {
    gap: 0.35rem;
    background: rgba(22, 18, 42, 0.65);
    border-radius: 0.75rem;
    padding: 0.3rem;
    border: 1px solid rgba(167, 139, 250, 0.18);
  }
  .stTabs [data-baseweb="tab"] {
    border-radius: 0.55rem;
    padding: 0.55rem 0.9rem;
    color: #a8a3b8;
  }
  .stTabs [aria-selected="true"] {
    background: rgba(167, 139, 250, 0.2) !important;
    color: #f1eef8 !important;
  }

  /* Mobile */
  @media (max-width: 640px) {
    .block-container {
      padding-left: 0.85rem;
      padding-right: 0.85rem;
      padding-top: 0.85rem;
    }
    .ui-card, div[data-testid="stForm"] {
      padding: 0.9rem 0.8rem;
      border-radius: 0.85rem;
    }
    .angle-chip { min-width: 100%; }
    .sun-hero { padding: 1.25rem 0.85rem 1.15rem; }
  }
</style>
""",
    unsafe_allow_html=True,
)

# --- Header -------------------------------------------------------------------
st.markdown(
    """
<div class="app-header">
  <p class="app-kicker">Astrology · Ελληνικά</p>
  <h1 class="app-title">Αστρολογικός χάρτης</h1>
  <p class="app-sub">
    Ζώδιο, ημερήσια πρόβλεψη, γενέθλιος χάρτης και ανάλυση προσωπικότητας —
    χωρίς επί πληρωμή APIs.
  </p>
</div>
""",
    unsafe_allow_html=True,
)

st.markdown("")  # breathing room

# --- Birth form ---------------------------------------------------------------
st.markdown(
    '<p class="ui-card-title" style="margin-bottom:0.35rem">Στοιχεία γέννησης</p>',
    unsafe_allow_html=True,
)

profile: BirthProfile = st.session_state.profile

with st.form("birth_form", clear_on_submit=False):
    name = st.text_input(
        "Όνομα",
        value=profile.name,
        placeholder="π.χ. Μαρία (προαιρετικό)",
        help="Εμφανίζεται στην ανάλυση προσωπικότητας.",
    )

    # Stack date/time more clearly; still use 2 cols on wider screens via columns
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

    st.markdown("##### Τόπος & ζώνη ώρας")
    preset = st.selectbox(
        "Πόλη (προεπιλογή)",
        options=PRESET_NAMES,
        index=PRESET_NAMES.index(profile.place_name)
        if profile.place_name in PRESET_NAMES
        else 0,
        help="Επιλέξτε πόλη για γρήγορες συντεταγμένες.",
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
        "Ζώνη ώρας",
        options=tz_options,
        index=tz_index,
        help="Η ώρα γέννησης ερμηνεύεται σε αυτή τη ζώνη (με θερινή ώρα αν ισχύει).",
    )

    preset_obj = get_preset(preset) or PLACE_PRESETS[0]
    with st.expander("Συντεταγμένες (lat / lng)", expanded=False):
        c_lat, c_lng = st.columns(2)
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

    submitted = st.form_submit_button(
        "✨ Υπολογισμός χάρτη",
        type="primary",
        use_container_width=True,
    )

if submitted:
    if use_preset_coords and preset_obj:
        latitude = float(preset_obj["latitude"])
        longitude = float(preset_obj["longitude"])
        if place_custom.strip() == profile.place_name or not place_custom.strip():
            place_name = preset_obj["name"]
        else:
            place_name = place_custom.strip()
    else:
        place_name = place_custom.strip() or preset

    bt = "12:00" if time_unknown else birth_t.strftime("%H:%M")
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
    st.rerun()

# Sync lat/lng helper when preset changes outside computation
with st.expander("Γρήγορη εφαρμογή προεπιλογής τόπου"):
    psel = st.selectbox("Πόλη", PRESET_NAMES, key="quick_preset")
    if st.button("Εφαρμογή lat/lng", use_container_width=True):
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

# Sun sign hero
who = f" · {profile.name}" if profile.name else ""
st.markdown(
    f"""
<div class="sun-hero">
  <div class="sym">{sun.symbol}</div>
  <div class="name">{sun.name_el}</div>
  <div class="meta">{sun.element_el} · {sun.modality_el}{who}</div>
  <div class="label">Ζώδιο ηλίου (τροπικό)</div>
</div>
""",
    unsafe_allow_html=True,
)

# API keys status (secrets)
_ks = keys_status()
with st.expander("🔑 AI κλειδιά (Gemini / xAI)", expanded=False):
    st.caption(
        "Πρόσθεσε στο Streamlit **Secrets** ή σε `.streamlit/secrets.toml`: "
        "`GEMINI_API_KEY` και/ή `XAI_API_KEY`. Χωρίς κλειδιά δουλεύει η τοπική ανάλυση."
    )
    c1, c2 = st.columns(2)
    c1.write("✅ Gemini" if _ks["gemini"] else "⬜ Gemini — λείπει")
    c2.write("✅ xAI / Grok" if _ks["xai"] else "⬜ xAI — λείπει")
    ai_provider = st.selectbox(
        "Πάροχος AI enrichment",
        ["auto", "gemini", "xai", "off"],
        format_func=lambda x: {
            "auto": "Αυτόματα (Gemini → xAI)",
            "gemini": "Μόνο Gemini",
            "xai": "Μόνο xAI Grok",
            "off": "Απενεργοποιημένο (μόνο τοπικά)",
        }[x],
        help="Το AI εμπλουτίζει προσωπικότητα + μηνιαίες προβλέψεις· δεν αλλάζει τον χάρτη.",
    )

# Chinese zodiac from DOB
try:
    _dob = date.fromisoformat(profile.date_of_birth)
except Exception:
    _dob = date.today()
chinese = get_chinese_zodiac(_dob)

# Tabs
tab_chart, tab_pers, tab_cn, tab_fore = st.tabs(
    ["Χάρτης", "Προσωπικότητα", "Κινεζικό", "Προβλέψεις"]
)

# ===== Χάρτης ================================================================
with tab_chart:
    st.markdown(
        '<p class="ui-card-title">Γενέθλιος χάρτης</p>',
        unsafe_allow_html=True,
    )
    if chart.approximate:
        st.info(
            "Ώρα προσεγγιστική (μεσημέρι) — εμφανίζονται πλανήτες χωρίς Ωροσκόπο / οίκους."
        )

    # Asc + MC chips
    asc = chart.ascendant if (chart.ascendant and not chart.approximate) else None
    mc = (
        chart.midheaven
        if (getattr(chart, "midheaven", None) and not chart.approximate)
        else None
    )
    if asc or mc:
        chips = ['<div class="angle-row">']
        if asc:
            chips.append(
                f'<div class="angle-chip">'
                f'<p class="k">Asc · Ωροσκόπος</p>'
                f'<p class="v">{asc.sign_el}</p>'
                f'<p class="d">{asc.formatted}</p>'
                f"</div>"
            )
        if mc:
            chips.append(
                f'<div class="angle-chip">'
                f'<p class="k">MC · Μεσουράνημα</p>'
                f'<p class="v">{mc.sign_el}</p>'
                f'<p class="d">{mc.formatted}</p>'
                f"</div>"
            )
        chips.append("</div>")
        st.markdown("".join(chips), unsafe_allow_html=True)
    elif chart.approximate:
        st.caption(
            "Asc / MC εμφανίζονται όταν δώσετε ακριβή ώρα γέννησης."
        )

    fig = build_chart_figure(chart)
    st.pyplot(fig, clear_figure=True, use_container_width=True)

    st.markdown("**Πλανήτες & γωνίες**")
    df = pd.DataFrame(chart_table_rows(chart))
    st.dataframe(df, use_container_width=True, hide_index=True)

    if chart.houses:
        with st.expander("Οίκοι (Equal House)", expanded=False):
            st.dataframe(
                pd.DataFrame(houses_table_rows(chart.houses)),
                use_container_width=True,
                hide_index=True,
            )

    for note in chart.notes:
        st.caption(f"ℹ️ {note}")

# ===== Προσωπικότητα ========================================================
with tab_pers:
    st.markdown(
        '<p class="ui-card-title">Ανάλυση προσωπικότητας</p>',
        unsafe_allow_html=True,
    )
    try:
        analysis = analyze_personality(chart, profile)

        st.markdown("#### Συνολική εικόνα")
        st.markdown(analysis.summary)

        for title, body in analysis.iter_sections():
            st.markdown(
                f'<div class="pers-block"><h4>{title}</h4></div>',
                unsafe_allow_html=True,
            )
            st.markdown(body)

        if analysis.strengths:
            st.markdown("#### Δυνάμεις")
            tags = "".join(f'<span class="tag">{s}</span>' for s in analysis.strengths)
            st.markdown(f'<div class="tag-list">{tags}</div>', unsafe_allow_html=True)

        if analysis.challenges:
            st.markdown("#### Προκλήσεις")
            tags = "".join(
                f'<span class="tag challenge">{c}</span>' for c in analysis.challenges
            )
            st.markdown(f'<div class="tag-list">{tags}</div>', unsafe_allow_html=True)

        st.markdown(
            f'<p class="disclaimer">{analysis.disclaimer_el}</p>',
            unsafe_allow_html=True,
        )

        if ai_provider != "off" and (_ks["gemini"] or _ks["xai"]):
            if st.button("✨ AI εμπλουτισμός προσωπικότητας", use_container_width=True):
                with st.spinner("AI ανάλυση…"):
                    text, src, err = enrich_personality(
                        analysis, chart, profile, provider=ai_provider
                    )
                    st.session_state["ai_personality"] = {
                        "text": text,
                        "source": src,
                        "error": err,
                    }
            if st.session_state.get("ai_personality"):
                ap = st.session_state["ai_personality"]
                st.markdown("#### AI ανάλυση")
                st.caption(f"Πηγή: `{ap['source']}`")
                st.markdown(ap["text"])
                if ap.get("error") and ap["source"] == "local":
                    st.warning(f"AI fallback: {ap['error']}")
        elif ai_provider != "off":
            st.info("Για AI enrichment πρόσθεσε `GEMINI_API_KEY` ή `XAI_API_KEY` στα Secrets.")
    except Exception as exc:  # noqa: BLE001
        st.warning(f"Δεν ήταν δυνατή η ανάλυση προσωπικότητας: {exc}")

# ===== Κινεζικό ==============================================================
with tab_cn:
    st.markdown(
        '<p class="ui-card-title">Κινεζικό ωροσκόπιο</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
<div class="sun-hero">
  <div class="sym">{chinese.symbol}</div>
  <div class="name">{chinese.animal_el}</div>
  <div class="meta">{chinese.element_el} · {chinese.polarity} · έτος {chinese.lunar_year}</div>
  <div class="label">Κινεζικό ζώδιο</div>
</div>
""",
        unsafe_allow_html=True,
    )
    st.markdown(chinese.summary_el)
    st.caption(
        "Υπολογισμός με βάση την κινεζική πρωτοχρονιά (πίνακας ετών). "
        "Ενδεικτικό / ψυχαγωγικό MVP."
    )

# ===== Προβλέψεις ============================================================
with tab_fore:
    st.markdown(
        f'<p class="ui-card-title">Ημερήσια πρόβλεψη {horoscope.symbol}</p>',
        unsafe_allow_html=True,
    )
    st.caption(horoscope.date_label_el)
    st.write(horoscope.text)
    st.markdown(
        f'<p class="disclaimer">{horoscope.disclaimer_el}</p>',
        unsafe_allow_html=True,
    )

    st.divider()
    st.markdown(
        '<p class="ui-card-title">Επόμενοι μήνες</p>',
        unsafe_allow_html=True,
    )
    n_months = st.slider("Πόσοι μήνες", 3, 6, 6)
    outlook = build_monthly_outlook(sun.id, chinese, start=date.today(), months=n_months)

    if ai_provider != "off" and (_ks["gemini"] or _ks["xai"]):
        if st.button("✨ AI μηνιαίες προβλέψεις", use_container_width=True, key="ai_months_btn"):
            with st.spinner("AI μηνιαίο outlook…"):
                outlook2, err = enrich_monthly_outlook(
                    sun.id, chinese, outlook, profile, provider=ai_provider
                )
                st.session_state["ai_outlook"] = {"outlook": outlook2, "error": err}
        if st.session_state.get("ai_outlook"):
            outlook = st.session_state["ai_outlook"]["outlook"]
            if st.session_state["ai_outlook"].get("error") and outlook.source == "local":
                st.warning(f"AI fallback: {st.session_state['ai_outlook']['error']}")

    st.caption(f"Πηγή: `{outlook.source}`")
    if outlook.chinese_note_el:
        st.info(outlook.chinese_note_el)

    for card in outlook.months:
        with st.expander(f"{card.label_el} · {card.theme_el}", expanded=False):
            st.markdown(card.text_el)

    st.markdown(
        f'<p class="disclaimer">{outlook.disclaimer_el}</p>',
        unsafe_allow_html=True,
    )

st.divider()
st.caption(
    "Υπολογισμοί με Skyfield + JPL DE421 · προφίλ σε `st.session_state` "
    "(το Streamlit Cloud είναι εφήμερο — δεν υπάρχει μόνιμη αποθήκευση) · MVP επίδειξης"
)
