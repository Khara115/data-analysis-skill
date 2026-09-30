# -*- coding: utf-8 -*-
"""
Unit tests for core/reasoner.py: ReAct diagnostic loops, multi-turn reasoning, and depth thresholds.
"""

import pytest
from core.reasoner import ReActDataAnalyst


def test_react_data_analyst_execution(synthetic_ev_df):
    analyst = ReActDataAnalyst(synthetic_ev_df, depth_threshold=85, max_turns=3)
    results = analyst.run_multi_turn_reasoning()

    assert "synthesized_diagnostics" in results
    diags = results["synthesized_diagnostics"]
    assert len(diags) == 4

    for d in diags:
        assert "id" in d
        assert "anomaly" in d
        assert "root_causes" in d
        assert len(d["root_causes"]) >= 2
        assert d.get("depth_score", 0) >= 85

        # Check ReAct trace turns
        turns = d.get("turns", [])
        assert len(turns) >= 1
        for step in turns:
            assert "turn" in step
            assert "thought" in step
            assert "action" in step
            assert "observation" in step
