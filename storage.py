"""Save / load birth profile + analyses as JSON (download, disk, in-app library)."""
from __future__ import annotations

import json
from dataclasses import asdict, is_dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from natal import BirthProfile

PROFILES_DIR = Path("saved_profiles")


def _to_plain(obj: Any) -> Any:
    if is_dataclass(obj):
        return asdict(obj)
    if isinstance(obj, dict):
        return {k: _to_plain(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_plain(x) for x in obj]
    return obj


def build_save_payload(
    profile: BirthProfile,
    *,
    sun_el: str = "",
    chinese: Optional[Dict[str, Any]] = None,
    chinese_analysis: Optional[Dict[str, Any]] = None,
    personality_summary: str = "",
    ai_personality: Optional[Dict[str, Any]] = None,
    outlook: Optional[Dict[str, Any]] = None,
    notes: str = "",
    label: str = "",
) -> Dict[str, Any]:
    name = profile.name.strip() or "Χωρίς όνομα"
    return {
        "version": 2,
        "label": label or name,
        "saved_at": datetime.now().isoformat(timespec="seconds"),
        "profile": {
            "name": profile.name,
            "date_of_birth": profile.date_of_birth,
            "birth_time": profile.birth_time,
            "time_unknown": profile.time_unknown,
            "place_name": profile.place_name,
            "latitude": profile.latitude,
            "longitude": profile.longitude,
            "timezone": profile.timezone,
        },
        "sun_el": sun_el,
        "chinese": chinese or {},
        "chinese_analysis": chinese_analysis or {},
        "personality_summary": personality_summary,
        "ai_personality": ai_personality,
        "outlook": outlook,
        "notes": notes,
    }


def dumps_save(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def loads_save(raw: str | bytes) -> Dict[str, Any]:
    if isinstance(raw, bytes):
        raw = raw.decode("utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict) or "profile" not in data:
        raise ValueError("Μη έγκυρο αρχείο αποθήκευσης.")
    return data


def profile_from_save(data: Dict[str, Any]) -> BirthProfile:
    p = data["profile"]
    return BirthProfile(
        name=str(p.get("name") or ""),
        date_of_birth=str(p.get("date_of_birth") or "1990-06-15"),
        birth_time=str(p.get("birth_time") or "12:00"),
        time_unknown=bool(p.get("time_unknown", False)),
        place_name=str(p.get("place_name") or "Αθήνα"),
        latitude=float(p.get("latitude") or 37.9838),
        longitude=float(p.get("longitude") or 23.7275),
        timezone=str(p.get("timezone") or "Europe/Athens"),
    )


def payload_label(data: Dict[str, Any]) -> str:
    if data.get("label"):
        return str(data["label"])
    p = data.get("profile") or {}
    name = p.get("name") or "Χωρίς όνομα"
    dob = p.get("date_of_birth") or ""
    sun = data.get("sun_el") or ""
    bits = [name]
    if dob:
        bits.append(dob)
    if sun:
        bits.append(sun)
    return " · ".join(bits)


def library_key(data: Dict[str, Any]) -> str:
    p = data.get("profile") or {}
    return "|".join(
        [
            str(p.get("name") or "").strip().lower(),
            str(p.get("date_of_birth") or ""),
            str(p.get("birth_time") or ""),
            str(p.get("place_name") or ""),
        ]
    )


def save_to_disk(payload: Dict[str, Any], filename: Optional[str] = None) -> Path:
    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    name = (payload.get("profile") or {}).get("name") or "profile"
    safe = "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in name)[:40] or "profile"
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = PROFILES_DIR / (filename or f"{safe}_{stamp}.json")
    path.write_text(dumps_save(payload), encoding="utf-8")
    return path


def list_saved() -> List[Path]:
    if not PROFILES_DIR.is_dir():
        return []
    return sorted(PROFILES_DIR.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)


def load_all_disk_payloads() -> Dict[str, Dict[str, Any]]:
    out: Dict[str, Dict[str, Any]] = {}
    for path in list_saved():
        try:
            data = loads_save(path.read_text(encoding="utf-8"))
            data["_path"] = str(path.name)
            out[library_key(data)] = data
        except Exception:
            continue
    return out
