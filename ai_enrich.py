"""Optional Gemini / xAI enrichment for personality + monthly outlook (Greek)."""
from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

from chinese_zodiac import ChineseZodiac
from monthly_outlook import MonthCard, MonthlyOutlook, build_monthly_outlook
from natal import BirthProfile, NatalChart
from personality import PersonalityAnalysis
from zodiac import ZodiacSignId


def _secret(name: str) -> Optional[str]:
    for key in (name, name.lower(), name.upper()):
        try:
            val = st.secrets.get(key)  # type: ignore[attr-defined]
            if val:
                return str(val).strip()
        except Exception:
            pass
    env = os.environ.get(name) or os.environ.get(name.upper()) or os.environ.get(name.lower())
    return env.strip() if env else None


def get_gemini_api_key() -> Optional[str]:
    return _secret("GEMINI_API_KEY")


def get_xai_api_key() -> Optional[str]:
    return _secret("XAI_API_KEY") or _secret("GROK_API_KEY")


def keys_status() -> Dict[str, bool]:
    return {
        "gemini": bool(get_gemini_api_key()),
        "xai": bool(get_xai_api_key()),
    }


def _strip_fence(text: str) -> str:
    t = (text or "").strip()
    if t.startswith("```"):
        t = re.sub(r"^```(?:json|markdown|text)?\s*", "", t)
        t = re.sub(r"\s*```$", "", t)
    return t.strip()


def _chart_brief(chart: NatalChart, profile: BirthProfile) -> str:
    bits = [
        f"Όνομα: {profile.name or '—'}",
        f"Γέννηση: {profile.date_of_birth} {profile.birth_time} ({profile.timezone})",
        f"Τόπος: {profile.place_name} ({profile.latitude}, {profile.longitude})",
    ]
    for p in chart.planets:
        bits.append(f"{p.name_el}: {p.formatted}")
    if chart.ascendant and not chart.approximate:
        bits.append(f"Asc: {chart.ascendant.formatted}")
    if getattr(chart, "midheaven", None) and not chart.approximate:
        bits.append(f"MC: {chart.midheaven.formatted}")
    return "\n".join(bits)


def _call_gemini(prompt: str, system: str) -> Tuple[Optional[str], Optional[str]]:
    key = get_gemini_api_key()
    if not key:
        return None, "no_gemini_key"
    try:
        import google.generativeai as genai
    except ImportError:
        return None, "google-generativeai not installed"
    try:
        genai.configure(api_key=key)
        model_names = [
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-flash-latest",
        ]
        last_err = None
        for mid in model_names:
            try:
                model = genai.GenerativeModel(mid, system_instruction=system)
                resp = model.generate_content(prompt)
                text = (getattr(resp, "text", None) or "").strip()
                if text:
                    return text, None
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
                continue
        return None, last_err or "gemini_empty"
    except Exception as e:  # noqa: BLE001
        return None, str(e)


def _call_xai(prompt: str, system: str) -> Tuple[Optional[str], Optional[str]]:
    key = get_xai_api_key()
    if not key:
        return None, "no_xai_key"
    try:
        from openai import OpenAI
    except ImportError:
        return None, "openai package not installed"
    client = OpenAI(api_key=key, base_url="https://api.x.ai/v1")
    for mid in ("grok-4.6", "grok-4.5", "grok-4.3"):
        try:
            resp = client.chat.completions.create(
                model=mid,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
            )
            text = (resp.choices[0].message.content or "").strip()
            if text:
                return text, None
        except Exception as e:  # noqa: BLE001
            last = str(e)
            continue
    return None, locals().get("last", "xai_failed")


def enrich_personality(
    base: PersonalityAnalysis,
    chart: NatalChart,
    profile: BirthProfile,
    provider: str = "auto",
) -> Tuple[str, str, Optional[str]]:
    """
    Return (enriched_markdown, source, error).
    source: local | gemini | xai
    """
    system = (
        "Είσαι έμπειρος αστρολόγος που γράφει στα Ελληνικά, ζεστά και καθαρά. "
        "Ψυχαγωγική ανάλυση μόνο — όχι ιατρικές/νομικές/χρηματοοικονομικές συμβουλές. "
        "Μην εφευρίσκεις ακριβή γεγονότα ζωής. Χωρίς celebrity ονόματα."
    )
    prompt = (
        "Βάλε σε πιο ζωντανή, συνεκτική ελληνική ανάλυση προσωπικότητας "
        "(3–5 σύντομες παραγράφους + λίστα δυνάμεων/προκλήσεων) με βάση:\n\n"
        f"ΧΑΡΤΗΣ:\n{_chart_brief(chart, profile)}\n\n"
        f"ΒΑΣΙΚΗ ΑΝΑΛΥΣΗ (MVP):\n{base.summary}\n"
    )
    order = []
    if provider == "gemini":
        order = ["gemini"]
    elif provider == "xai":
        order = ["xai"]
    else:
        order = ["gemini", "xai"] if get_gemini_api_key() else ["xai", "gemini"]

    errs: List[str] = []
    for src in order:
        fn = _call_gemini if src == "gemini" else _call_xai
        text, err = fn(prompt, system)
        if text:
            return _strip_fence(text), src, None
        if err:
            errs.append(f"{src}: {err}")
    return base.summary, "local", "; ".join(errs) if errs else None


def enrich_monthly_outlook(
    sun_id: ZodiacSignId,
    chinese: Optional[ChineseZodiac],
    base: MonthlyOutlook,
    profile: BirthProfile,
    provider: str = "auto",
) -> Tuple[MonthlyOutlook, Optional[str]]:
    """AI rewrite of monthly cards; falls back to base."""
    system = (
        "Γράφεις ελληνικές μηνιαίες αστρολογικές προβλέψεις (ψυχαγωγία). "
        "JSON μόνο. Χωρίς hard dates γεγονότων, χωρίς medical/finance advice."
    )
    months_payload = [
        {"label": c.label_el, "theme": c.theme_el, "year": c.year, "month": c.month}
        for c in base.months
    ]
    cn = ""
    if chinese:
        cn = f"Κινεζικό: {chinese.animal_el}, στοιχείο {chinese.element_el} ({chinese.polarity})"
    prompt = (
        f"Ήλιος: {sun_id}. Προφίλ: {profile.name or '—'}, γέννηση {profile.date_of_birth}. {cn}\n"
        f"Γράψε κείμενο για κάθε μήνα (2–3 προτάσεις EL).\n"
        f"Επίστεψε JSON: {{\"months\":[{{\"year\":2026,\"month\":9,\"theme\":\"...\",\"text\":\"...\"}}],"
        f"\"chinese_note\":\"...\"}}\n"
        f"Μήνες: {json.dumps(months_payload, ensure_ascii=False)}"
    )

    order = []
    if provider == "gemini":
        order = ["gemini"]
    elif provider == "xai":
        order = ["xai"]
    else:
        order = ["gemini", "xai"] if get_gemini_api_key() else ["xai", "gemini"]

    errs: List[str] = []
    for src in order:
        fn = _call_gemini if src == "gemini" else _call_xai
        text, err = fn(prompt, system)
        if not text:
            if err:
                errs.append(f"{src}: {err}")
            continue
        try:
            data = json.loads(_strip_fence(text))
            raw_months = data.get("months") or []
            cards: List[MonthCard] = []
            by_key = {(c.year, c.month): c for c in base.months}
            for item in raw_months:
                if not isinstance(item, dict):
                    continue
                y = int(item.get("year") or 0)
                m = int(item.get("month") or 0)
                base_c = by_key.get((y, m))
                label = base_c.label_el if base_c else f"{m}/{y}"
                theme = str(item.get("theme") or (base_c.theme_el if base_c else ""))
                body = str(item.get("text") or "").strip()
                if not body:
                    continue
                cards.append(
                    MonthCard(year=y, month=m, label_el=label, theme_el=theme, text_el=body)
                )
            if not cards:
                raise ValueError("empty months")
            # preserve order of base if possible
            ordered = []
            for bc in base.months:
                match = next((c for c in cards if c.year == bc.year and c.month == bc.month), None)
                ordered.append(match or bc)
            cn_note = str(data.get("chinese_note") or base.chinese_note_el)
            return (
                MonthlyOutlook(
                    months=ordered,
                    chinese_note_el=cn_note,
                    disclaimer_el=base.disclaimer_el,
                    source=src,
                ),
                None,
            )
        except Exception as e:  # noqa: BLE001
            errs.append(f"{src}_parse: {e}")
            continue
    return base, "; ".join(errs) if errs else None
