"""Render every chart to examples/ so the README can show a gallery.

    python examples/generate_gallery.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import pandas as pd

import sleepviz as sv

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "examples"
df = pd.read_csv(ROOT / "data" / "Sleep_health.csv")

charts = {
    "quality_by_occupation": sv.quality_by_occupation,
    "sleep_duration_distribution": sv.sleep_duration_distribution,
    "stress_vs_quality": sv.stress_vs_quality,
    "disorder_breakdown": sv.disorder_breakdown,
    "correlation_heatmap": sv.correlation_heatmap,
}

for name, fn in charts.items():
    fig = fn(df)
    fig.savefig(OUT / f"{name}.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / f"{name}.png")
