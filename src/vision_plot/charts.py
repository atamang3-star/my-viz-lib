"""The chart functions — the public API of vision_plot.

Design rules (straight from the build-a-library slides):
  * One job per function.
  * Small signatures: pass a pandas DataFrame, get a Matplotlib Figure back.
  * Never mutate the caller's DataFrame; never print — always return.

Every function returns a ``matplotlib.figure.Figure`` so you can show it,
save it, or drop it into a report.
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .theme import (
    ACCENT, HIGHLIGHT, INK, PALETTE, apply_theme, style_axes, titled,
)

# Numeric columns worth correlating (Person ID is just a row label).
_NUMERIC = [
    "Age", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
    "Stress Level", "Heart Rate", "Daily Steps",
]


def _require(df: pd.DataFrame, cols: list[str]) -> None:
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise KeyError(f"DataFrame is missing expected column(s): {missing}")


def quality_by_occupation(df: pd.DataFrame) -> plt.Figure:
    """Ranked horizontal bars: mean sleep quality per occupation.

    Aesthetic: a single accent hue for context, with the top-scoring occupation
    picked out in a warm highlight so the winner reads instantly. Bars are sorted
    so the ordering comes for free, and each bar is direct-labelled so the x-axis
    can disappear entirely.
    """
    _require(df, ["Occupation", "Quality of Sleep"])
    apply_theme()
    means = (df.groupby("Occupation")["Quality of Sleep"]
               .mean().sort_values())

    # Everything sits in the calm accent; the highest bar gets a warm highlight
    # so the reader's eye lands on the best-sleeping job first.
    top = len(means) - 1
    colors = [ACCENT] * len(means)
    colors[top] = HIGHLIGHT

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.barh(means.index, means.values, color=colors,
                   height=0.68, zorder=3)
    for bar, val in zip(bars, means.values):
        ax.text(val - 0.12, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", ha="right",
                color=INK["surface"], fontweight="bold", fontsize=10)

    # A real x-axis: ticks, marks, a baseline and a faint vertical grid so the
    # chart reads as a measured graph, not just labelled blocks.
    style_axes(ax, grid_axis="x")
    ax.set_xlim(0, 10)
    ax.set_xticks(range(0, 11, 2))
    ax.tick_params(axis="x", length=5, color=INK["baseline"])
    ax.set_xlabel("Mean quality of sleep (1–10)")
    # Bold only the winning occupation's label so its name reads as emphatically
    # as its bar — the reader's eye ties the two together.
    ax.get_yticklabels()[top].set_fontweight("bold")
    titled(ax, "Which jobs sleep best?",
           "Average sleep quality by occupation",
           title_color=ACCENT)
    fig.tight_layout()
    return fig


def sleep_duration_distribution(df: pd.DataFrame) -> plt.Figure:
    """Histogram of sleep duration with a mean reference line.

    Aesthetic: half-hour bins keep the shape readable (narrower bins split the
    round-number clustering into a noisy comb), each bar carries its count so
    the exact numbers are never in doubt, and a single labelled line marks the
    mean.
    """
    _require(df, ["Sleep Duration"])
    apply_theme()
    hours = df["Sleep Duration"]

    fig, ax = plt.subplots(figsize=(8, 5))
    counts, edges, _ = ax.hist(hours, bins=np.arange(5.5, 8.51, 0.5),
                               color=ACCENT, edgecolor=INK["surface"],
                               linewidth=1.5, zorder=3)
    top = counts.max() * 1.15
    ax.set_ylim(0, top)
    for c, e in zip(counts, edges[:-1]):
        if c:
            ax.text(e + 0.25, c + top * 0.015, f"{int(c)}", ha="center",
                    va="bottom", color=INK["secondary"], fontweight="bold",
                    fontsize=10)

    mean = hours.mean()
    ax.axvline(mean, color=PALETTE[1], linewidth=2, zorder=4)
    ax.text(mean + 0.06, top * 0.9, f"mean {mean:.1f} h",
            color=PALETTE[1], fontweight="bold", fontsize=10)

    style_axes(ax, grid_axis="y")
    ax.set_xlabel("Sleep duration (hours)")
    ax.set_ylabel("People")
    titled(ax, "How long do people actually sleep?",
           "Distribution of nightly sleep duration")
    fig.tight_layout()
    return fig


def quality_by_stress(df: pd.DataFrame) -> plt.Figure:
    """Bars: average sleep quality at each stress level.

    Aesthetic: aggregating one bar per stress level (instead of a cloud of
    overlapping dots) turns the relationship into a single clear message — the
    bars step down as stress climbs. A single accent hue keeps the focus on the
    trend, and each bar is topped with its value.
    """
    _require(df, ["Stress Level", "Quality of Sleep"])
    apply_theme()
    means = df.groupby("Stress Level")["Quality of Sleep"].mean()

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.bar(means.index, means.values, color=ACCENT, width=0.7, zorder=3)
    for bar, val in zip(bars, means.values):
        ax.text(bar.get_x() + bar.get_width() / 2, val + 0.12, f"{val:.1f}",
                ha="center", va="bottom", color=INK["secondary"],
                fontweight="bold", fontsize=9)

    style_axes(ax, grid_axis="y")
    ax.set_ylim(0, 10)
    ax.set_xticks(means.index)
    ax.tick_params(axis="x", length=5, color=INK["baseline"])
    ax.set_xlabel("Stress level (1–10)")
    ax.set_ylabel("Mean sleep quality (1–10)")
    titled(ax, "Higher stress, worse sleep",
           "Average sleep quality at each stress level", title_color=ACCENT)
    fig.tight_layout()
    return fig


def quality_correlations(df: pd.DataFrame) -> plt.Figure:
    """Diverging bars: how strongly each factor is linked to sleep quality.

    Aesthetic: correlation is *signed*, so bars grow left/right from a zero
    baseline — factors that track higher sleep quality run right in the accent
    blue, factors that track lower quality run left in the warm highlight.
    Plain-language cues above each side ("linked to better / worse sleep") tell a
    non-technical reader what the direction means, while the coefficient label on
    every bar keeps it precise for a technical one. Sorting turns it into a
    ranked answer.
    """
    cols = [c for c in _NUMERIC if c in df.columns]
    _require(df, cols)
    apply_theme()
    target = "Quality of Sleep"
    corr = df[cols].corr()[target].drop(target).sort_values()
    colors = [HIGHLIGHT if v < 0 else ACCENT for v in corr.values]

    fig, ax = plt.subplots(figsize=(8, 5.4))
    bars = ax.barh(corr.index, corr.values, color=colors, height=0.66, zorder=3)
    ax.axvline(0, color=INK["baseline"], linewidth=1.4, zorder=4)
    for bar, v in zip(bars, corr.values):
        ha = "left" if v >= 0 else "right"
        ax.text(v + (0.03 if v >= 0 else -0.03),
                bar.get_y() + bar.get_height() / 2, f"{v:+.2f}",
                va="center", ha=ha, color=INK["secondary"],
                fontweight="bold", fontsize=9)

    # Plain-language direction cues, color-matched to the bars, so the meaning of
    # left vs. right (and blue vs. orange) is stated rather than assumed.
    top = len(corr) - 1
    ax.set_ylim(-0.7, top + 1.0)
    ax.text(0.5, top + 0.55, "Linked to better sleep →", ha="center",
            va="center", color=ACCENT, fontweight="bold", fontsize=10.5)
    ax.text(-0.5, top + 0.55, "← Linked to worse sleep", ha="center",
            va="center", color=HIGHLIGHT, fontweight="bold", fontsize=10.5)

    style_axes(ax, grid_axis="x")
    ax.set_xlim(-1.18, 1.18)  # headroom so outer value labels clear the axis
    ax.set_xticks([-1, -0.5, 0, 0.5, 1])
    ax.tick_params(axis="x", length=5, color=INK["baseline"])
    ax.set_xlabel("Correlation with sleep quality (−1 to 1)")
    titled(ax, "What's linked to sleep quality?",
           "Correlation of each factor with sleep quality", title_color=ACCENT)
    fig.tight_layout()
    return fig
