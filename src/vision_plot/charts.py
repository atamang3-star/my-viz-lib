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
import pandas as pd

from .theme import ACCENT, HIGHLIGHT, INK, apply_theme, style_axes, titled

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

    Aesthetic: the two extremes are the story, so only they carry saturated
    colour — cool blue for the best-sleeping job, warm orange for the two
    worst — while the middle recedes into neutral gray. Blue and orange are a
    validated colourblind-safe pair; the neutral middle keeps a third saturated
    hue (which could not stay colourblind-safe beside them) off the chart.
    Bars are sorted and each is direct-labelled so the x-axis is optional.
    """
    _require(df, ["Occupation", "Quality of Sleep"])
    apply_theme()
    means = (df.groupby("Occupation")["Quality of Sleep"]
               .mean().sort_values())

    # Sorted ascending: index 0-1 are the two lowest, the last is the highest.
    n = len(means)
    emphasized = {0, 1, n - 1}          # two worst + the best
    colors = [INK["baseline"]] * n      # neutral gray context
    colors[n - 1] = ACCENT              # best sleeper -> cool blue
    colors[0] = colors[1] = HIGHLIGHT   # two lowest -> warm orange

    fig, ax = plt.subplots(figsize=(8, 5.5))
    bars = ax.barh(means.index, means.values, color=colors,
                   height=0.68, zorder=3)
    for i, (bar, val) in enumerate(zip(bars, means.values)):
        # White reads on the saturated bars; dark ink on the light gray ones.
        label_color = INK["surface"] if i in emphasized else INK["secondary"]
        ax.text(val - 0.12, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", ha="right",
                color=label_color, fontweight="bold", fontsize=10)

    # A real x-axis: ticks, marks, a baseline and a faint vertical grid so the
    # chart reads as a measured graph, not just labelled blocks.
    style_axes(ax, grid_axis="x")
    ax.set_xlim(0, 10)
    ax.set_xticks(range(0, 11, 2))
    ax.tick_params(axis="x", length=5, color=INK["baseline"])
    ax.set_xlabel("Mean quality of sleep (1–10)")
    # Bold the emphasised occupations' names so they read as strongly as their
    # coloured bars — the reader's eye ties name and bar together.
    for i in emphasized:
        ax.get_yticklabels()[i].set_fontweight("bold")
    titled(ax, "Which jobs sleep best?",
           "Average sleep quality by occupation",
           title_color=ACCENT)
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
