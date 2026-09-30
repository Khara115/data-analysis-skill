# -*- coding: utf-8 -*-
"""
Pytest wrapper for harness/test_harness.py.
"""

import os
import tempfile
import json
import pytest
from core.engine import slice_sub_datasets, synthesize_conclusions_and_diagnostics
from harness.test_harness import run_harness_audit


def test_harness_audit_passes(synthetic_ev_df):
    sub_data = slice_sub_datasets(synthetic_ev_df)
    insights = synthesize_conclusions_and_diagnostics(sub_data, synthetic_ev_df)

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_sub, \
         tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f_ins:
        sub_path = f_sub.name
        ins_path = f_ins.name

    try:
        with open(sub_path, "w", encoding="utf-8") as f:
            json.dump(sub_data, f)
        with open(ins_path, "w", encoding="utf-8") as f:
            json.dump(insights, f)

        ok = run_harness_audit(sub_path, ins_path)
        assert ok is True
    finally:
        if os.path.exists(sub_path):
            os.remove(sub_path)
        if os.path.exists(ins_path):
            os.remove(ins_path)
