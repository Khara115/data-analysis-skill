#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Harness Engineering Test Suite (harness/test_harness.py)
--------------------------------------------------------
Deterministic, programmatic test harness enforcing data invariants,
statistical boundaries, and structural validity on sub-datasets and insights.
"""

import os
import sys
import json
import argparse

# Safe UTF-8 reconfiguration on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def run_harness_audit(sub_datasets_path: str, insights_path: str) -> bool:
    if not os.path.exists(sub_datasets_path) or not os.path.exists(insights_path):
        return False

    with open(sub_datasets_path, "r", encoding="utf-8") as f:
        sub_data = json.load(f)

    with open(insights_path, "r", encoding="utf-8") as f:
        insights = json.load(f)

    failures = []

    # 1. Total N conservation
    total_n = sub_data.get("metadata", {}).get("total_records", 0)
    quads = sub_data.get("quadrants", {})
    quad_sum = sum(q.get("count", 0) for q in quads.values())
    if quad_sum != total_n:
        failures.append(f"Invariant Violation: Sum of quadrants ({quad_sum}) != total N ({total_n})")

    # 2. Probability Bounds
    for qk, q in quads.items():
        if not (0.0 <= q.get("buy_rate", 0) <= 1.0):
            failures.append(f"Bound Violation: {qk} buy_rate out of [0, 1]")

    # 3. Causal Consistency: Low Anxiety > High Anxiety
    anxs = sub_data.get("anxiety_groups", {})
    low_anx = anxs.get("Low", {}).get("buy_rate", 0)
    high_anx = anxs.get("High", {}).get("buy_rate", 1)
    if high_anx >= low_anx:
        failures.append("Causal Violation: High anxiety buy_rate is not strictly lower than Low anxiety")

    # 4. Schema Check for Diagnostics
    diags = insights.get("possibility_diagnostics", [])
    if len(diags) < 3:
        failures.append("Diagnostic Depth Violation: Fewer than 3 possibility diagnostic branches provided")

    for d in diags:
        if not d.get("root_causes") or len(d.get("root_causes")) < 2:
            failures.append(f"Diagnostic Root Cause Violation in {d.get('id')}: Needs at least 2 causal reasons")

    if failures:
        print("[HARNESS FAILED]:")
        for fail in failures:
            print(f"  ❌ {fail}")
        return False

    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sub-datasets", default="outputs/sub_datasets.json")
    parser.add_argument("--insights", default="outputs/insights.json")
    args = parser.parse_args()

    ok = run_harness_audit(args.sub_datasets, args.insights)
    sys.exit(0 if ok else 1)
