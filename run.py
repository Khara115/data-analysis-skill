#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Main Entry Point with Human-in-the-Loop Review Gate (run.py)
-----------------------------------------------------------
Execution Flow:
  Phase 1: [Engine] Ingest Excel/CSV, Slice 6 Sub-datasets, Infer Conclusions & 4-Way Root Causes.
  Phase 1.5: [Human Review Gate] Present findings in terminal for user confirmation/adjustment.
  Phase 2: [Harness Gate] Deterministic verification & invariant validation (silent guardian).
  Phase 3: [Visualizer] Render executive-grade HTML dashboard (KPIs -> Conclusions -> Diagnostics -> Details).
"""

import os
import sys
import argparse

# Safe UTF-8 reconfiguration on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass

from core.engine import process_dataset
from core.visualizer import render_html_dashboard
from harness.test_harness import run_harness_audit


def parse_args():
    parser = argparse.ArgumentParser(description="EV Data Analysis Pipeline with Human Review Gate")
    parser.add_argument("--input", "-i", type=str, default="examples/sample_ev_data.xlsx",
                        help="Path to input Excel (.xlsx/.xls) or CSV file")
    parser.add_argument("--output-dir", "-o", type=str, default="outputs",
                        help="Directory to save output reports and artifacts")
    parser.add_argument("--yes", "-y", action="store_true", default=False,
                        help="Skip interactive confirmation prompt (auto-approve)")
    return parser.parse_args()


def display_human_review_summary(sub_data: dict, insights: dict):
    meta = sub_data.get("metadata", {})
    total_n = meta.get("total_records", 0)
    baseline_br = meta.get("baseline_buy_rate", 0)

    print("\n" + "=" * 75)
    print("📋 [Phase 1: Sub-dataset Slicing & Initial Diagnostic Review (Human Gate)]")
    print("=" * 75)
    print(f"[*] Sample Size: {total_n:,} records | Population Baseline Buy Rate: {baseline_br*100:.2f}%\n")

    print("📌 [Core Business Conclusions Draft]:")
    for c in insights.get("core_conclusions", []):
        print(f"  • {c['id']}: {c['title']}")
        print(f"    Detail: {c['detail']}\n")

    print("🔍 [Root-Cause Diagnostic Matrix & Causal Reasoning]:")
    for d in insights.get("possibility_diagnostics", []):
        print(f"  • [{d['id']}] {d['name']}")
        print(f"    - Observed Anomaly: {d['anomaly']}")
        for rc in d.get("root_causes", []):
            print(f"      * Verified Cause: {rc}")
        print(f"    - Recommended Action: {d['solution']}\n")
    print("=" * 75)


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)

    print("\n" + "=" * 75)
    print("🚀 DATA ANALYSIS SKILL: STARTING PIPELINE")
    print("   [Case Study: EV Purchase Decision & Causal Attribution Benchmark]")
    print(f"[*] Input File:  {args.input}")
    print(f"[*] Output Dir:  {args.output_dir}")
    print("=" * 75)

    # Phase 1: Ingestion, Sub-dataset Slicing, Causal Diagnostics
    sub_data, insights = process_dataset(args.input, args.output_dir)

    # Phase 1.5: Human-in-the-Loop Review Gate
    display_human_review_summary(sub_data, insights)

    if not args.yes:
        # Check if stdin is interactive
        if sys.stdin.isatty():
            choice = input("👉 Please review the findings above. Enter [Y/Enter] to generate HTML dashboard, or [N] to abort: ").strip().lower()
            if choice not in ["", "y", "yes"]:
                print("\n🛑 Pipeline aborted by user. Adjust hypotheses in core/engine.py or re-run.")
                sys.exit(0)
        else:
            print("ℹ️ Non-interactive terminal environment: auto-approving human review gate.")

    # Phase 2: Silent Harness Audit
    sub_path = os.path.join(args.output_dir, "sub_datasets.json")
    ins_path = os.path.join(args.output_dir, "insights.json")
    harness_ok = run_harness_audit(sub_path, ins_path)
    if not harness_ok:
        print("\n❌ CRITICAL: Harness gate caught invariant violation. Rendering aborted!")
        sys.exit(1)

    # Phase 3: Visualizer Rendering
    print("\n>>> [Phase 3: Visualizer] Rendering executive-grade HTML interactive dashboard...")
    output_html = os.path.join(args.output_dir, "report.html")
    render_html_dashboard(sub_data, insights, output_html)

    print("\n" + "=" * 75)
    print("✨ SUCCESS: Executive HTML dashboard generated successfully!")
    print(f"🔗 Dashboard URL: file:///{os.path.abspath(output_html).replace(os.sep, '/')}")
    print("=" * 75 + "\n")


if __name__ == "__main__":
    main()
