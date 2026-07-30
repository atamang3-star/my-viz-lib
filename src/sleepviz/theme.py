"""Shared visual language for every sleepviz chart.

One palette, one set of axis rules. Keeping the styling here (instead of
repeating it inside each chart) is what makes the whole library look like a
single system rather than a pile of unrelated plots.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

# --- Palette -------------------------------------------------------------
# A validated, colorblind-aware categorical order (light-surface steps).
# Hues are assigned in this fixed order and never cycled past slot 8.
PALETTE = [
    "#2a78d6",  # 1 blue
    "#eb6834",  # 2 orange
    "#1baf7a",  # 3 aqua
    "#eda100",  # 4 yellow
    "#e87ba4",  # 5 magenta
    "#008300",  # 6 green
    "#4a3aa7",  # 7 violet
    "#e34948",  # 8 red
]

ACCENT = PALETTE[0]  # single-series charts use one confident hue

# Ink + chrome. Text always wears an ink token, never a series color.
INK = {
    "surface": "#fcfcfb",
    "primary": "#0b0b0b",   # titles, values
    "secondary": "#52514e",  # subtitles, axis titles
    "muted": "#898781",     # tick labels
    "grid": "#e1e0d9",      # hairline gridlines
    "baseline": "#c3c2b7",  # axis / baseline
}

# Diverging pair for signed magnitudes (e.g. correlations): warm/cool poles
# around a neutral gray midpoint. Never a rainbow.
DIVERGING = ("#184f95", "#f0efec", "#c0392b")  # cool -> neutral -> warm


def apply_theme() -> None:
    """Set global matplotlib defaults so every figure starts on-brand."""
    plt.rcParams.update({
        "figure.facecolor": INK["surface"],
        "axes.facecolor": INK["surface"],
        "savefig.facecolor": INK["surface"],
        "font.family": "sans-serif",
        "font.size": 11,
        "text.color": INK["primary"],
        "axes.edgecolor": INK["baseline"],
        "axes.labelcolor": INK["secondary"],
        "xtick.color": INK["muted"],
        "ytick.color": INK["muted"],
        "axes.grid": False,
    })


def style_axes(ax, *, grid_axis: str | None = "x") -> None:
    """Apply the recessive-chrome rules to a single Axes.

    Drops the top/right spines, mutes the remaining ones, and draws a single
    hairline grid on the value axis only. This is the aesthetic backbone: the
    data gets the ink, the frame gets out of the way.
    """
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(INK["baseline"])
    ax.tick_params(length=0)
    if grid_axis:
        ax.grid(axis=grid_axis, color=INK["grid"], linewidth=0.8, zorder=0)
        ax.set_axisbelow(True)


def titled(ax, title: str, subtitle: str | None = None) -> None:
    """Left-aligned title with an optional secondary-ink subtitle."""
    ax.set_title(title, loc="left", fontsize=14, fontweight="bold",
                 color=INK["primary"], pad=30 if subtitle else 10)
    if subtitle:
        ax.text(0.0, 1.015, subtitle, transform=ax.transAxes,
                fontsize=10.5, color=INK["secondary"], va="bottom")
