# -*- coding: utf-8 -*-
"""
Unit tests for core/engine.py: Data slicing, sub-dataset creation, and metric derivations.
"""

import os
import tempfile
import pytest
import pandas as pd
from core.engine import load_and_standardize, slice_sub_datasets, synthesize_conclusions_and_diagnostics


def test_slice_sub_datasets(synthetic_ev_df):
    sub_data = slice_sub_datasets(synthetic_ev_df)

    assert "metadata" in sub_data
    assert sub_data["metadata"]["total_records"] == len(synthetic_ev_df)

    # 1. Total records conservation across quadrants
    quads = sub_data.get("quadrants", {})
    quad_sum = sum(q["count"] for q in quads.values())
    assert quad_sum == len(synthetic_ev_df)

    # 2. Probability bounds
    for k, q in quads.items():
        assert 0.0 <= q["buy_rate"] <= 1.0

    # 3. Commute groups present
    commute_groups = sub_data.get("commute_charging", {})
    assert len(commute_groups) >= 3

    # 4. Eco groups present
    eco_groups = sub_data.get("eco_income_matrix", {})
    assert len(eco_groups) >= 3


def test_synthesize_conclusions_and_diagnostics(synthetic_ev_df):
    sub_data = slice_sub_datasets(synthetic_ev_df)
    insights = synthesize_conclusions_and_diagnostics(sub_data, synthetic_ev_df)

    assert "core_conclusions" in insights
    assert len(insights["core_conclusions"]) == 3

    assert "possibility_diagnostics" in insights
    assert len(insights["possibility_diagnostics"]) >= 3


def test_load_and_standardize_csv(synthetic_ev_df):
    with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as tmp:
        synthetic_ev_df.to_csv(tmp.name, index=False)
        tmp_path = tmp.name

    try:
        df = load_and_standardize(tmp_path)
        assert len(df) == len(synthetic_ev_df)
        assert "target" in df.columns
        assert set(df["target"].unique()).issubset({0, 1})
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
