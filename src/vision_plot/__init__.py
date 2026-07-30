"""vision_plot — a tiny, opinionated visualization library for sleep-health data.

    import pandas as pd
    import vision_plot as vp

    df = pd.read_csv("data/Sleep_health.csv")
    fig = vp.quality_by_occupation(df)
    fig.savefig("quality.png", dpi=150)

Every chart function takes a pandas DataFrame and returns a Matplotlib Figure.
The two small EDA helpers (``summarize``, ``missing``) mirror the ones from the
build-a-library slides, so you can peek at a dataset before plotting it.
"""

from __future__ import annotations

import pandas as pd

from .charts import (
    disorder_breakdown,
    quality_by_occupation,
    quality_by_stress,
    quality_correlations,
    sleep_duration_distribution,
)
from .theme import PALETTE, apply_theme

__version__ = "0.1.0"


def summarize(df: pd.DataFrame) -> dict:
    """Shape and column overview — returns a plain dict, not a custom class."""
    return {
        "rows": len(df),
        "columns": len(df.columns),
        "names": list(df.columns),
    }


def missing(df: pd.DataFrame) -> pd.Series:
    """Null counts per column, highest first."""
    return df.isna().sum().sort_values(ascending=False)


__all__ = [
    "__version__",
    "summarize",
    "missing",
    "apply_theme",
    "PALETTE",
    "quality_by_occupation",
    "sleep_duration_distribution",
    "quality_by_stress",
    "disorder_breakdown",
    "quality_correlations",
]
