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
    "quality_correlations": vp.quality_correlations,
}

for name, fn in charts.items():
    fig = fn(df)
    fig.savefig(OUT / f"{name}.png", dpi=150, bbox_inches="tight")
    print("wrote", OUT / f"{name}.png")
