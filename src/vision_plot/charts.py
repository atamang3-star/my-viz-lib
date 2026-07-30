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
from matplotlib.colors import LinearSegmentedColormap

from .theme import (
    ACCENT, DIVERGING, HIGHLIGHT, INK, PALETTE, apply_theme, style_axes, titled,
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
    for i, (bar, val) in enumerate(zip(bars, means.values)):
        label = f"Mean {val:.1f}" if i == top else f"{val:.1f}"
        ax.text(val - 0.12, bar.get_y() + bar.get_height() / 2,
                label, va="center", ha="right",
                color=INK["surface"], fontweight="bold", fontsize=10)

    style_axes(ax, grid_axis=None)
    ax.set_xlim(0, 10)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    # Bold only the winning occupation's label so its name reads as emphatically
    # as its bar — the reader's eye ties the two together.
    ax.get_yticklabels()[top].set_fontweight("bold")
    titled(ax, "Which jobs sleep best?",
           "Mean quality-of-sleep score (1–10) by occupation",
           title_color=ACCENT)
    fig.tight_layout()
    return fig


def sleep_duration_distribution(df: pd.DataFrame) -> plt.Figure:
    """Histogram of sleep duration with a mean reference line.

    Aesthetic: soft filled bars with a thin surface gap between them, and a
    single labelled marker for the mean so the summary rides on the shape.
    """
    _require(df, ["Sleep Duration"])
    apply_theme()
    hours = df["Sleep Duration"]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(hours, bins=np.arange(5.5, 8.6, 0.25), color=ACCENT,
            edgecolor=INK["surface"], linewidth=1.5, zorder=3)
    mean = hours.mean()
    ax.axvline(mean, color=PALETTE[1], linewidth=2, zorder=4)
    ax.text(mean + 0.05, ax.get_ylim()[1] * 0.94, f"mean {mean:.1f} h",
            color=PALETTE[1], fontweight="bold", fontsize=10)

    style_axes(ax, grid_axis="y")
    ax.set_xlabel("Sleep duration (hours)")
    ax.set_ylabel("People")
    titled(ax, "How long do people actually sleep?",
           "Distribution of nightly sleep duration")
    fig.tight_layout()
    return fig


def stress_vs_quality(df: pd.DataFrame) -> plt.Figure:
    """Scatter of stress level against sleep quality, split by gender.

    Aesthetic: two categorical hues (identity, not magnitude) with a thin
    surface ring on each marker so overlapping points stay legible, plus a
    legend because there is more than one series.
    """
    _require(df, ["Stress Level", "Quality of Sleep", "Gender"])
    apply_theme()

    fig, ax = plt.subplots(figsize=(8, 5.5))
    for hue, (name, grp) in zip(PALETTE, df.groupby("Gender")):
        jitter = np.random.default_rng(0).normal(0, 0.06, len(grp))
        ax.scatter(grp["Stress Level"] + jitter, grp["Quality of Sleep"],
                   s=70, color=hue, edgecolor=INK["surface"], linewidth=1.2,
                   alpha=0.85, label=name, zorder=3)

    style_axes(ax, grid_axis="y")
    ax.set_xlabel("Stress level (1–10)")
    ax.set_ylabel("Sleep quality (1–10)")
    ax.legend(frameon=False, loc="lower left", title="Gender")
    titled(ax, "Stress versus sleep quality",
           "Each dot is one person; higher stress tracks lower quality")
    fig.tight_layout()
    return fig


def disorder_breakdown(df: pd.DataFrame) -> plt.Figure:
    """Donut of sleep-disorder prevalence (missing values read as 'None').

    Aesthetic: a donut (not a pie) so a center label can carry the headline,
    fixed categorical hues, and a 2px surface gap between wedges.
    """
    _require(df, ["Sleep Disorder"])
    apply_theme()
    counts = df["Sleep Disorder"].fillna("None").value_counts()
    order = ["None", "Sleep Apnea", "Insomnia"]
    counts = counts.reindex([o for o in order if o in counts.index])

    fig, ax = plt.subplots(figsize=(6.5, 6))
    wedges, _ = ax.pie(
        counts.values, colors=PALETTE[:len(counts)], startangle=90,
        counterclock=False, wedgeprops=dict(width=0.42, edgecolor=INK["surface"],
                                            linewidth=2))
    ax.legend(wedges, [f"{n}  ·  {v}" for n, v in counts.items()],
              frameon=False, loc="center left", bbox_to_anchor=(0.98, 0.5))
    healthy = counts.get("None", 0) / counts.sum() * 100
    ax.text(0, 0.08, f"{healthy:.0f}%", ha="center", fontsize=26,
            fontweight="bold", color=INK["primary"])
    ax.text(0, -0.14, "no disorder", ha="center", fontsize=11,
            color=INK["secondary"])
    titled(ax, "Sleep disorders in the cohort")
    fig.tight_layout()
    return fig


def correlation_heatmap(df: pd.DataFrame) -> plt.Figure:
    """Diverging heatmap of correlations between the numeric health metrics.

    Aesthetic: correlations are *signed*, so this uses a diverging blue-gray-red
    ramp (cool = negative, warm = positive) with a neutral midpoint at zero —
    never a rainbow. Cells are annotated so the exact value never depends on
    color perception alone.
    """
    cols = [c for c in _NUMERIC if c in df.columns]
    _require(df, cols)
    apply_theme()
    corr = df[cols].corr()
    cmap = LinearSegmentedColormap.from_list("vision_plot_div", DIVERGING)

    fig, ax = plt.subplots(figsize=(7.5, 6.5))
    im = ax.imshow(corr.values, cmap=cmap, vmin=-1, vmax=1)
    ax.set_xticks(range(len(cols)), labels=cols, rotation=40, ha="right",
                  fontsize=9)
    ax.set_yticks(range(len(cols)), labels=cols, fontsize=9)
    for i in range(len(cols)):
        for j in range(len(cols)):
            v = corr.values[i, j]
            ax.text(j, i, f"{v:.2f}", ha="center", va="center", fontsize=8,
                    color=INK["surface"] if abs(v) > 0.55 else INK["primary"])
    for side in ax.spines.values():
        side.set_visible(False)
    ax.tick_params(length=0)
    cbar = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.outline.set_visible(False)
    cbar.ax.tick_params(length=0, colors=INK["muted"])
    titled(ax, "What moves together?",
           "Pairwise correlation of the numeric health metrics")
    fig.tight_layout()
    return fig
