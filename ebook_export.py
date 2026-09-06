"""Export astrology reading as PDF / EPUB e-book."""
from __future__ import annotations

import html
import io
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from natal import BirthProfile

_FONT_CANDIDATES = [
    Path(__file__).resolve().parent / "fonts" / "DejaVuSans.ttf",
    Path(__file__).resolve().parent / "fonts" / "DejaVuSans-Bold.ttf",
    Path("fonts/DejaVuSans.ttf"),
    Path("fonts/DejaVuSans-Bold.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
    Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
]


def _find_fonts() -> Tuple[Optional[Path], Optional[Path]]:
    regular = next((p for p in _FONT_CANDIDATES if p.is_file() and "Bold" not in p.name), None)
    bold = next((p for p in _FONT_CANDIDATES if p.is_file() and "Bold" in p.name), None)
    if regular is None:
        for p in _FONT_CANDIDATES:
            if p.is_file():
                regular = p
                break
    return regular, bold


def _strip_md(text: str) -> str:
    t = text or ""
    t = re.sub(r"\*\*(.+?)\*\*", r"\1", t)
    t = re.sub(r"\*(.+?)\*", r"\1", t)
    t = t.replace("`", "")
    return t.strip()


def _sections_from_payload(payload: Dict[str, Any]) -> List[Tuple[str, str]]:
    profile = payload.get("profile") or {}
    sections: List[Tuple[str, str]] = []

    who = profile.get("name") or "Αναγνώστης"
    meta_lines = [
        f"Όνομα: {who}",
        f"Γέννηση: {profile.get('date_of_birth', '—')} · ώρα {profile.get('birth_time', '—')}",
        f"Τόπος: {profile.get('place_name', '—')}",
        f"Ζώνη: {profile.get('timezone', '—')}",
        f"Ήλιος: {payload.get('sun_el') or '—'}",
        f"Αποθήκευση: {payload.get('saved_at') or datetime.now().isoformat(timespec='seconds')}",
    ]
    sections.append(("Στοιχεία γέννησης", "\n".join(meta_lines)))

    cn = payload.get("chinese") or {}
    if cn:
        sections.append(
            (
                "Κινεζικό ωροσκόπιο",
                cn.get("summary_el")
                or (
                    f"{cn.get('animal_el', '')} · {cn.get('element_el', '')} "
                    f"({cn.get('polarity', '')}) · {cn.get('lunar_year', '')}"
                ),
            )
        )

    ca = payload.get("chinese_analysis") or {}
    if ca.get("body_el"):
        sections.append(("Κινεζική ανάλυση", str(ca.get("body_el"))))
        if ca.get("love_el"):
            sections.append(("Κινεζικά · Αγάπη", str(ca["love_el"])))
        if ca.get("work_el"):
            sections.append(("Κινεζικά · Δουλειά", str(ca["work_el"])))
        if ca.get("gift_el"):
            sections.append(("Κινεζικά · Δώρο", str(ca["gift_el"])))
        if ca.get("shadow_el"):
            sections.append(("Κινεζικά · Σκιά", str(ca["shadow_el"])))

    if payload.get("personality_summary"):
        sections.append(("Ανάλυση προσωπικότητας", str(payload["personality_summary"])))

    ai = payload.get("ai_personality") or {}
    if isinstance(ai, dict) and ai.get("text"):
        sections.append((f"AI ανάλυση ({ai.get('source', 'AI')})", str(ai["text"])))

    outlook = payload.get("outlook") or {}
    if outlook.get("chinese_note_el"):
        sections.append(("Κινεζική νότα μηνών", str(outlook["chinese_note_el"])))
    for m in outlook.get("months") or []:
        if not isinstance(m, dict):
            continue
        title = f"{m.get('label_el', 'Μήνας')} · {m.get('theme_el', '')}".strip(" ·")
        sections.append((title, str(m.get("text_el") or "")))

    sections.append(
        (
            "Σημείωση",
            "Ψυχαγωγικό αστρολογικό e-book (MVP). Δεν αποτελεί επιστημονική, "
            "ιατρική, νομική ή οικονομική συμβουλή.",
        )
    )
    return [(t, _strip_md(b)) for t, b in sections if b and str(b).strip()]


def build_pdf_bytes(payload: Dict[str, Any], title: str = "Αστρολογικό πορτρέτο") -> bytes:
    from fpdf import FPDF

    regular, bold = _find_fonts()
    if regular is None:
        raise RuntimeError(
            "Λείπει γραμματοσειρά με ελληνικά (DejaVuSans). "
            "Τοπικά βάλε fonts/DejaVuSans.ttf ή εγκατέστησε fonts-dejavu."
        )

    pdf = FPDF(format="A5", unit="mm")
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()
    pdf.add_font("DejaVu", "", str(regular))
    has_bold = bool(bold and bold.is_file())
    if has_bold:
        pdf.add_font("DejaVu", "B", str(bold))

    def heading(text: str) -> None:
        pdf.ln(4)
        pdf.set_font("DejaVu", "B" if has_bold else "", 13)
        pdf.set_text_color(6, 78, 59)
        pdf.multi_cell(0, 7, text)
        pdf.set_text_color(20, 30, 28)
        pdf.ln(1)

    def body(text: str) -> None:
        pdf.set_font("DejaVu", "", 10)
        pdf.multi_cell(0, 5.5, text)
        pdf.ln(2)

    pdf.set_font("DejaVu", "B" if has_bold else "", 20)
    pdf.set_text_color(16, 185, 129)
    pdf.ln(20)
    pdf.multi_cell(0, 10, title, align="C")
    pdf.set_font("DejaVu", "", 11)
    pdf.set_text_color(80, 100, 90)
    who = (payload.get("profile") or {}).get("name") or ""
    subtitle = who if who else "Προσωπική αστρολογική ανάγνωση"
    pdf.ln(4)
    pdf.multi_cell(0, 6, subtitle, align="C")
    pdf.ln(2)
    pdf.multi_cell(0, 5, "Electric Midnight · Astrology MVP", align="C")
    pdf.ln(8)

    for sec_title, sec_body in _sections_from_payload(payload):
        if pdf.get_y() > 170:
            pdf.add_page()
        heading(sec_title)
        body(sec_body)

    out = io.BytesIO()
    pdf.output(out)
    return out.getvalue()


def build_epub_bytes(payload: Dict[str, Any], title: str = "Αστρολογικό πορτρέτο") -> bytes:
    from ebooklib import epub

    book = epub.EpubBook()
    who = (payload.get("profile") or {}).get("name") or "Αναγνώστης"
    book.set_identifier(f"astro-mvp-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    book.set_title(f"{title} — {who}")
    book.set_language("el")
    book.add_author("Astrology MVP")

    spine = ["nav"]
    toc = []

    for i, (sec_title, sec_body) in enumerate(_sections_from_payload(payload)):
        file_name = f"chap_{i+1}.xhtml"
        chap = epub.EpubHtml(title=sec_title, file_name=file_name, lang="el")
        paras = "".join(
            f"<p>{html.escape(line)}</p>" if line.strip() else "<p><br/></p>"
            for line in sec_body.split("\n")
        )
        chap.content = (
            f"<html><head></head><body>"
            f"<h1>{html.escape(sec_title)}</h1>{paras}"
            f"</body></html>"
        )
        book.add_item(chap)
        toc.append(chap)
        spine.append(chap)

    book.toc = tuple(toc)
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    book.spine = spine

    buf = io.BytesIO()
    epub.write_epub(buf, book)
    return buf.getvalue()


def default_ebook_basename(profile: BirthProfile) -> str:
    raw = (profile.name or "astro").strip() or "astro"
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in raw)[:40]
    return f"{safe}_astrology_ebook"
