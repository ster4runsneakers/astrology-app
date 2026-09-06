"""Simple natal chart wheel with matplotlib."""
from __future__ import annotations

import math
from typing import Optional

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.figure import Figure

from natal import HouseCusp, NatalChart, PlanetPosition
from zodiac import ZODIAC_SIGNS

# Soft cosmos palette
_BG = "#0c0a14"
_RING = "#2e2a48"
_TEXT = "#f1eef8"
_ACCENT = "#c4b5fd"
_GOLD = "#f5d76e"
_MUTED = "#9b97b0"

_PLANET_GLYPH = {
    "sun": "☉",
    "moon": "☽",
    "mercury": "☿",
    "venus": "♀",
    "mars": "♂",
    "jupiter": "♃",
    "saturn": "♄",
    "asc": "Asc",
    "mc": "MC",
}


def _lon_to_theta(lon: float) -> float:
    """Ecliptic longitude → polar theta (Aries at east / 0°, CCW like usual wheel)."""
    # Matplotlib polar: 0 at east, CCW. Astrology wheel often has Asc on left (west).
    # We put 0° Aries at left (π) so Asc near eastern horizon sits near right if Asc~0 —
    # Simpler: plot longitude as theta = radians(lon), with 0 at east CCW.
    return math.radians(lon)


def build_chart_figure(chart: NatalChart) -> Figure:
    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(7.2, 7.2))
    fig.patch.set_facecolor(_BG)
    ax.set_facecolor(_BG)
    ax.set_theta_zero_location("E")
    ax.set_theta_direction(1)  # CCW
    ax.set_ylim(0, 1.15)
    ax.set_yticklabels([])
    ax.grid(False)
    ax.spines["polar"].set_visible(False)

    # Zodiac ring wedges
    colors = [
        "#3d2a2a",
        "#2a3d2a",
        "#2a3d3d",
        "#2a2a3d",
        "#3d3d2a",
        "#3d2a3d",
    ]
    for i, z in enumerate(ZODIAC_SIGNS):
        theta1 = i * 30
        ax.bar(
            math.radians(theta1 + 15),
            0.18,
            width=math.radians(30),
            bottom=0.82,
            color=colors[i % len(colors)],
            edgecolor=_RING,
            linewidth=0.5,
            align="center",
            alpha=0.9,
        )
        ax.text(
            math.radians(theta1 + 15),
            0.93,
            z.symbol,
            ha="center",
            va="center",
            color=_TEXT,
            fontsize=11,
        )

    # Inner circle
    theta = np.linspace(0, 2 * math.pi, 200)
    ax.plot(theta, np.full_like(theta, 0.82), color=_RING, lw=1)
    ax.plot(theta, np.full_like(theta, 0.35), color=_RING, lw=0.8)

    # House lines if available
    if chart.houses:
        for h in chart.houses:
            th = _lon_to_theta(h.longitude)
            ax.plot([th, th], [0.35, 0.82], color=_MUTED, lw=0.6, alpha=0.7)
            mid_r = 0.58
            ax.text(
                th,
                mid_r,
                str(h.number),
                ha="center",
                va="center",
                color=_MUTED,
                fontsize=7,
            )

    # Planets
    bodies: list[PlanetPosition] = list(chart.planets)
    if chart.ascendant:
        bodies = bodies + [chart.ascendant]
    if getattr(chart, "midheaven", None):
        bodies = bodies + [chart.midheaven]

    # Slight radial stagger to reduce overlap
    for i, p in enumerate(bodies):
        th = _lon_to_theta(p.longitude)
        r = 0.55 + (i % 4) * 0.06
        glyph = _PLANET_GLYPH.get(p.id, p.name_en[:2])
        is_angle = p.id in ("asc", "mc")
        color = _GOLD if p.id in ("sun", "asc", "mc") else (_ACCENT if p.id == "moon" else _TEXT)
        ax.plot(th, r, "o", color=color, markersize=7 if is_angle else 6, zorder=5)
        ax.text(
            th,
            r + 0.09,
            glyph,
            ha="center",
            va="center",
            color=color,
            fontsize=9 if is_angle else 10,
            fontweight="bold",
            zorder=6,
            bbox=dict(
                boxstyle="round,pad=0.15",
                facecolor="#1a1530",
                edgecolor=color,
                linewidth=0.6,
                alpha=0.85,
            )
            if is_angle
            else None,
        )

    title = "Γενέθλιος χάρτης"
    if chart.approximate:
        title += " (προσέγγιση)"
    ax.set_title(title, color=_TEXT, pad=16, fontsize=14)

    # Hide degree tick labels; show sign markers only
    ax.set_xticks([])
    fig.tight_layout()
    return fig


def chart_table_rows(chart: NatalChart) -> list[dict]:
    rows = []
    bodies: list[PlanetPosition] = list(chart.planets)
    angles = []
    if chart.ascendant:
        angles.append(chart.ascendant)
    if getattr(chart, "midheaven", None):
        angles.append(chart.midheaven)
    if angles:
        bodies = angles + bodies
    for p in bodies:
        rows.append(
            {
                "Σώμα": p.name_el,
                "Ζώδιο": f"{p.sign_el}",
                "Μοίρα": f"{format_deg_local(p.degree_in_sign)}",
                "Μορφή": p.formatted,
            }
        )
    return rows


def format_deg_local(deg_in_sign: float) -> str:
    deg = int(deg_in_sign)
    minutes = int((deg_in_sign - deg) * 60)
    return f"{deg}°{minutes:02d}′"


def houses_table_rows(houses: list[HouseCusp]) -> list[dict]:
    return [
        {
            "Οίκος": h.number,
            "Ζώδιο": h.sign_el,
            "Μοίρα": format_deg_local(h.degree_in_sign),
            "Μορφή": h.formatted,
        }
        for h in houses
    ]
