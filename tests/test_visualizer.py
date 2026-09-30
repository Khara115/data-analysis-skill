# -*- coding: utf-8 -*-
"""
Unit tests for core/visualizer.py: Side-by-side layout, HTML rendering, metric delta badges, and chart baseline.
"""

import os
import tempfile
import pytest
from core.engine import slice_sub_datasets, synthesize_conclusions_and_diagnostics
from core.visualizer import render_html_dashboard


def test_render_html_dashboard(synthetic_ev_df):
    sub_data = slice_sub_datasets(synthetic_ev_df)
    insights = synthesize_conclusions_and_diagnostics(sub_data, synthetic_ev_df)

    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as tmp:
        out_html = tmp.name

    try:
        render_html_dashboard(sub_data, insights, out_html)
        assert os.path.exists(out_html)
        assert os.path.getsize(out_html) > 5000

        with open(out_html, "r", encoding="utf-8") as f:
            html = f.read()

        # Check key components
        assert "EV Purchase Decision & Causal Attribution Executive Dashboard" in html
        assert "grid-template-columns: 1fr 1fr" in html
        assert "kpi-grid" in html
        assert "kpi-badge" in html
        assert "View ReAct Reasoning Trace" in html
    finally:
        if os.path.exists(out_html):
            os.remove(out_html)
