"""Render every chart to examples/ so the README can show a gallery.

    python examples/generate_gallery.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import pandas as pd

import vision_plot as vp

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples"
df = pd.read_csv(ROOT / "data" / "Sleep_health.csv")

charts = {
    "quality_by_occupation": vp.quality_by_occupation,
    "sleep_duration_distribution": vp.sleep_duration_distribution,
    "stress_vs_quality": vp.stress_vs_quality,
    "disorder_breakdown": vp.disorder_breakdown,
    "correlation_heatmap": vp.correlation_heatmap,
}

for name, fn in charts.items():
    fig = fn(df)
    fig.savefig(OUT / f"{name}.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / f"{name}.png")
