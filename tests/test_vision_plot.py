"""Small smoke tests: every chart returns a Figure and helpers return plain data."""

import matplotlib
matplotlib.use("Agg")  # headless backend for CI

import pandas as pd
import pytest
from matplotlib.figure import Figure

import vision_plot as vp


@pytest.fixture
def df():
    return pd.DataFrame({
        "Occupation": ["Nurse", "Doctor", "Nurse", "Lawyer"],
        "Quality of Sleep": [7, 6, 8, 5],
        "Sleep Duration": [6.5, 6.1, 7.2, 5.9],
        "Stress Level": [4, 6, 3, 7],
        "Gender": ["Female", "Male", "Female", "Male"],
        "Sleep Disorder": [None, "Insomnia", None, "Sleep Apnea"],
        "Age": [30, 45, 29, 52],
        "Physical Activity Level": [60, 40, 75, 30],
        "Heart Rate": [70, 78, 68, 82],
        "Daily Steps": [8000, 5000, 9000, 4000],
    })


def test_summarize(df):
    out = vp.summarize(df)
    assert out["rows"] == 4
    assert "Occupation" in out["names"]


def test_missing(df):
    counts = vp.missing(df)
    assert counts["Sleep Disorder"] == 2


@pytest.mark.parametrize("fn", [
    vp.quality_by_occupation,
    vp.sleep_duration_distribution,
    vp.stress_vs_quality,
    vp.disorder_breakdown,
    vp.quality_correlations,
])
def test_charts_return_figure(df, fn):
    fig = fn(df)
    assert isinstance(fig, Figure)


def test_missing_column_raises(df):
    with pytest.raises(KeyError):
        vp.quality_by_occupation(df.drop(columns=["Occupation"]))
