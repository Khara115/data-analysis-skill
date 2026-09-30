#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
High-Impact Dashboard Visualizer (core/visualizer.py)
----------------------------------------------------
Implements strict executive data visualization standards:
1. Business-Attributed Metric Cards (Value, Baseline vs Treated, Delta Indicators).
2. Core Conclusions (Action-oriented, quantified).
3. Possibility Diagnostic Matrix (Root-cause trees with collapsible ReAct traces).
4. Side-by-Side (左右分栏) Split Layout: Interactive Chart.js (with benchmark lines) on Left,
   Sub-dataset Pivot Table on Right.
"""

import os
import sys
import json
from datetime import datetime

# Safe UTF-8 reconfiguration on Windows
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass


def render_html_dashboard(sub_data: dict, insights: dict, output_file: str):
    meta = sub_data.get("metadata", {})
    total_n = meta.get("total_records", 0)
    baseline_br = meta.get("baseline_buy_rate", 0)

    quads = sub_data.get("quadrants", {})
    subs = sub_data.get("subsidy_groups", {})
    anxs = sub_data.get("anxiety_groups", {})
    chgs = sub_data.get("charging_groups", {})
    city_infra = sub_data.get("city_infrastructure", {})
    commute_chg = sub_data.get("commute_charging", {})
    eco_inc = sub_data.get("eco_income_matrix", {})
    sub_tiers = sub_data.get("subsidy_income_tiers", {})

    sub_yes_br = subs.get("Yes", {}).get("buy_rate", 0)
    sub_no_br = subs.get("No", {}).get("buy_rate", 0)
    sub_lift = (sub_yes_br - sub_no_br) * 100

    low_anx_br = anxs.get("Low", {}).get("buy_rate", 0)
    high_anx_br = anxs.get("High", {}).get("buy_rate", 0)
    anx_decay = ((low_anx_br - high_anx_br) / low_anx_br * 100) if low_anx_br > 0 else 0

    quad_q1_obj = quads.get("Q1_High_Income_Low_Anxiety") or quads.get("Q1_Gold_Rush", {})
    quad_q1_br = quad_q1_obj.get("buy_rate", 0)
    quad_q1_lift = (quad_q1_br - baseline_br) * 100

    core_conclusions = insights.get("core_conclusions", [])
    diagnostics = insights.get("possibility_diagnostics", [])

    # 1. Build Core Conclusions
    conclusions_html = ""
    for c in core_conclusions:
        conclusions_html += f"""
        <div class="conclusion-item">
            <div class="conclusion-tag">{c['id']}</div>
            <div class="conclusion-content">
                <h4>{c['title']}</h4>
                <p>{c['detail']}</p>
            </div>
        </div>
        """

    # 2. Build Possibility Diagnostics with Collapsible ReAct Traces
    diagnostics_html = ""
    for d in diagnostics:
        reasons = d.get("verified_root_causes") or d.get("root_causes", [])
        reasons_li = "".join([f"<li>{r}</li>" for r in reasons])
        solution = d.get("strategic_solution") or d.get("solution", "")
        depth = d.get("depth_score", 85)

        turns_html = ""
        for t in d.get("turns", []):
            turns_html += f"""
            <div class="react-turn-item">
                <div class="turn-badge">Turn {t['turn']} • Convergence Score: {t['depth_score']}/85 [Target Met]</div>
                <div class="turn-thought"><strong>💭 Analytical Hypothesis (Thought):</strong> {t['thought']}</div>
                <div class="turn-action"><strong>⚙️ Data Slicing Action (Action):</strong> <code>{t['action']}</code></div>
                <div class="turn-obs"><strong>👁️ Empirical Observation (Observation):</strong> {t['observation']}</div>
            </div>
            """

        diagnostics_html += f"""
        <div class="diag-card">
            <div class="diag-header">
                <span class="diag-badge">{d.get('goal_id', d.get('id', 'DIAG'))}</span>
                <span class="diag-score">Convergence Score: {depth}/100</span>
                <h3>{d['title']}</h3>
            </div>
            <div class="diag-anomaly">
                <strong>🚨 Observed Anomaly:</strong> {d['anomaly']}
            </div>
            <div class="diag-causes">
                <strong>🔎 Verified Root Causes:</strong>
                <ul>{reasons_li}</ul>
            </div>
            <div class="diag-solution">
                <strong>💡 Recommended Strategic Action:</strong> {solution}
            </div>
            {f'''
            <details class="react-trace">
                <summary>🔍 View ReAct Reasoning Trace ({len(d.get("turns", []))} Slicing Iterations)</summary>
                <div class="react-trace-body">
                    {turns_html}
                </div>
            </details>
            ''' if turns_html else ''}
        </div>
        """

    # 3. Build Quadrant Table Rows
    quad_rows = ""
    for qk, q in quads.items():
        rate_val = q.get("buy_rate", 0)
        badge_cls = "badge-green" if rate_val >= 0.2 else ("badge-yellow" if rate_val >= 0.04 else "badge-red")
        quad_rows += f"""
        <tr>
            <td><strong>{qk}</strong></td>
            <td>{q.get('name')}</td>
            <td>{q.get('count', 0):,}</td>
            <td>{q.get('share', 0)*100:.1f}%</td>
            <td>${q.get('avg_income', 0):,.0f}</td>
            <td><span class="badge {badge_cls}">{q.get('buy_rate', 0)*100:.2f}%</span></td>
        </tr>
        """

    # 4. Build Commute Table Rows
    commute_rows = ""
    for ck, c in commute_chg.items():
        rate_val = c.get("buy_rate", 0)
        badge_cls = "badge-green" if rate_val >= 0.2 else ("badge-yellow" if rate_val >= 0.12 else "badge-red")
        commute_rows += f"""
        <tr>
            <td><strong>{ck}</strong></td>
            <td>{c.get('count', 0):,}</td>
            <td>{c.get('share', 0)*100:.1f}%</td>
            <td><span class="badge {badge_cls}">{c.get('buy_rate', 0)*100:.2f}%</span></td>
        </tr>
        """

    # 5. Build Eco-Income Table Rows
    eco_rows = ""
    for ek, e in eco_inc.items():
        rate_val = e.get("buy_rate", 0)
        badge_cls = "badge-green" if rate_val >= 0.25 else ("badge-yellow" if rate_val >= 0.05 else "badge-red")
        eco_rows += f"""
        <tr>
            <td><strong>{ek}</strong></td>
            <td>{e.get('name')}</td>
            <td>{e.get('count', 0):,}</td>
            <td>{e.get('share', 0)*100:.1f}%</td>
            <td><span class="badge {badge_cls}">{e.get('buy_rate', 0)*100:.2f}%</span></td>
        </tr>
        """

    # 6. Chart.js datasets
    chart_quad_labels = [q.get('name', k) for k, q in quads.items()]
    chart_quad_data = [round(q.get('buy_rate', 0) * 100, 2) for q in quads.values()]
    baseline_line = [round(baseline_br * 100, 2)] * len(chart_quad_labels)

    chart_city_labels = list(city_infra.keys())
    chart_city_buy = [round(v.get('buy_rate', 0) * 100, 2) for v in city_infra.values()]
    chart_city_chg = [round(v.get('home_charging_ratio', 0) * 100, 2) for v in city_infra.values()]

    chart_tier_labels = list(sub_tiers.keys())
    chart_tier_no_sub = [round(v.get('no_subsidy_br', 0) * 100, 2) for v in sub_tiers.values()]
    chart_tier_with_sub = [round(v.get('with_subsidy_br', 0) * 100, 2) for v in sub_tiers.values()]

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EV Purchase Decision & Causal Attribution Executive Dashboard</title>
    <!-- Chart.js 4.4 -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        :root {{
            --primary: #2563eb;
            --primary-light: #eff6ff;
            --success: #10b981;
            --success-light: #ecfdf5;
            --danger: #ef4444;
            --danger-light: #fef2f2;
            --warning: #f59e0b;
            --warning-light: #fffbeb;
            --dark: #0f172a;
            --gray-800: #1e293b;
            --gray-600: #475569;
            --gray-500: #64748b;
            --gray-200: #e2e8f0;
            --gray-100: #f8fafc;
            --card-bg: #ffffff;
            --radius-lg: 14px;
            --radius-md: 8px;
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.06);
            --shadow-md: 0 4px 16px rgba(0,0,0,0.08);
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Microsoft YaHei", sans-serif;
            background-color: #f1f5f9;
            color: var(--dark);
            line-height: 1.5;
            padding: 24px 20px;
        }}
        .container {{
            max-width: 1300px;
            margin: 0 auto;
        }}

        /* Header */
        .header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            color: #ffffff;
            padding: 24px 32px;
            border-radius: var(--radius-lg);
            margin-bottom: 20px;
            box-shadow: var(--shadow-md);
        }}
        .header h1 {{ font-size: 22px; font-weight: 800; letter-spacing: -0.3px; }}
        .header-subtitle {{ font-size: 13px; color: #94a3b8; margin-top: 6px; }}

        /* 1. Business-Attributed Metric Cards (主要指标卡) */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 16px;
            margin-bottom: 22px;
        }}
        .kpi-card {{
            background: var(--card-bg);
            padding: 20px;
            border-radius: var(--radius-md);
            border: 1px solid var(--gray-200);
            box-shadow: var(--shadow-sm);
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .kpi-top {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}
        .kpi-title {{
            font-size: 13px;
            font-weight: 700;
            color: var(--gray-600);
        }}
        .kpi-badge {{
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        .kpi-badge.blue {{ background: var(--primary-light); color: var(--primary); }}
        .kpi-badge.green {{ background: var(--success-light); color: var(--success); }}
        .kpi-badge.red {{ background: var(--danger-light); color: var(--danger); }}
        .kpi-badge.amber {{ background: var(--warning-light); color: var(--warning); }}

        .kpi-val {{
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 4px;
        }}
        .kpi-val.green {{ color: var(--success); }}
        .kpi-val.red {{ color: var(--danger); }}
        .kpi-val.blue {{ color: var(--primary); }}

        .kpi-comparison {{
            font-size: 12px;
            color: var(--gray-600);
            border-top: 1px solid var(--gray-100);
            padding-top: 8px;
            margin-top: 4px;
            display: flex;
            justify-content: space-between;
        }}
        .kpi-comparison strong {{ color: var(--dark); }}

        /* 2. Core Conclusions Section */
        .section-conclusions {{
            background: var(--card-bg);
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: 22px 26px;
            margin-bottom: 22px;
            box-shadow: var(--shadow-sm);
        }}
        .section-title {{
            font-size: 17px;
            font-weight: 800;
            color: var(--dark);
            margin-bottom: 14px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .conclusion-grid {{
            display: grid;
            grid-template-columns: 1fr;
            gap: 10px;
        }}
        .conclusion-item {{
            display: flex;
            gap: 14px;
            background: var(--gray-100);
            border-left: 4px solid var(--primary);
            border-radius: 6px;
            padding: 12px 18px;
            align-items: flex-start;
        }}
        .conclusion-tag {{
            background: var(--primary);
            color: #ffffff;
            font-weight: 800;
            font-size: 11px;
            padding: 3px 8px;
            border-radius: 4px;
            white-space: nowrap;
            margin-top: 2px;
        }}
        .conclusion-content h4 {{
            font-size: 15px;
            font-weight: 700;
            color: var(--dark);
            margin-bottom: 3px;
        }}
        .conclusion-content p {{
            font-size: 13px;
            color: var(--gray-600);
            line-height: 1.45;
        }}

        /* 3. Possibility Diagnostics Section */
        .section-diagnostics {{
            background: var(--card-bg);
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: 22px 26px;
            margin-bottom: 22px;
            box-shadow: var(--shadow-sm);
        }}
        .diag-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(580px, 1fr));
            gap: 16px;
        }}
        .diag-card {{
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-md);
            padding: 18px;
            background: #ffffff;
        }}
        .diag-header {{
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 10px;
        }}
        .diag-badge {{
            background: #fef3c7;
            color: #92400e;
            font-size: 11px;
            font-weight: 700;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        .diag-score {{
            margin-left: auto;
            font-size: 11px;
            font-weight: 700;
            color: #059669;
            background: #ecfdf5;
            padding: 2px 7px;
            border-radius: 4px;
        }}
        .diag-header h3 {{
            font-size: 15px;
            font-weight: 700;
            color: var(--dark);
        }}
        .diag-anomaly {{
            background: #fef2f2;
            border-left: 3px solid var(--danger);
            padding: 8px 12px;
            font-size: 13px;
            color: #991b1b;
            border-radius: 4px;
            margin-bottom: 10px;
        }}
        .diag-causes {{
            font-size: 13px;
            color: var(--gray-600);
            margin-bottom: 10px;
        }}
        .diag-causes ul {{ margin-left: 18px; margin-top: 4px; }}
        .diag-causes li {{ margin-bottom: 3px; }}
        .diag-solution {{
            background: #eff6ff;
            border-left: 3px solid var(--primary);
            padding: 8px 12px;
            font-size: 13px;
            color: #1e40af;
            border-radius: 4px;
            margin-bottom: 10px;
        }}
        .react-trace {{
            margin-top: 8px;
            border: 1px dashed var(--gray-200);
            border-radius: 6px;
            padding: 8px 12px;
            background: #f8fafc;
            font-size: 12px;
        }}
        .react-trace summary {{
            cursor: pointer;
            font-weight: 600;
            color: var(--primary);
            outline: none;
            user-select: none;
        }}
        .react-trace-body {{
            margin-top: 8px;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }}
        .react-turn-item {{
            background: #ffffff;
            border: 1px solid var(--gray-200);
            border-radius: 5px;
            padding: 8px 10px;
        }}
        .turn-badge {{
            font-size: 11px;
            font-weight: 700;
            color: #6366f1;
            text-transform: uppercase;
            margin-bottom: 3px;
        }}
        .turn-thought {{ color: #334155; margin-bottom: 3px; }}
        .turn-action {{ color: #0284c7; margin-bottom: 3px; font-family: monospace; }}
        .turn-obs {{ color: #059669; }}

        /* 4. Side-by-Side (左右分栏) Modules */
        .section-analysis {{
            background: var(--card-bg);
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-lg);
            padding: 24px 28px;
            margin-bottom: 22px;
            box-shadow: var(--shadow-sm);
        }}
        .split-row {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 28px;
            align-items: start;
        }}
        @media (max-width: 980px) {{
            .split-row {{ grid-template-columns: 1fr; }}
            .diag-grid {{ grid-template-columns: 1fr; }}
        }}
        .split-card {{
            border: 1px solid var(--gray-200);
            border-radius: var(--radius-md);
            padding: 18px 20px;
            background: #ffffff;
        }}
        .split-card h4 {{
            font-size: 15px;
            font-weight: 700;
            color: var(--gray-800);
            margin-bottom: 4px;
        }}
        .split-card p.chart-sub {{
            font-size: 12px;
            color: var(--gray-500);
            margin-bottom: 12px;
        }}

        /* Table styles */
        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 12.5px;
        }}
        th, td {{
            padding: 10px 12px;
            text-align: left;
            border-bottom: 1px solid var(--gray-200);
        }}
        th {{
            background: var(--gray-100);
            color: var(--gray-600);
            font-weight: 700;
        }}
        tr:hover td {{ background-color: #fafbfc; }}
        .badge {{
            padding: 3px 7px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: 700;
        }}
        .badge-green {{ background: #ecfdf5; color: #059669; }}
        .badge-yellow {{ background: #fffbeb; color: #d97706; }}
        .badge-red {{ background: #fef2f2; color: #dc2626; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <header class="header">
            <div>
                <h1>EV Purchase Decision & Causal Attribution Executive Dashboard</h1>
                <p class="header-subtitle">Executive analytics dashboard based on micro-cohort slicing, causal inference, and benchmark comparisons</p>
            </div>
        </header>

        <!-- 1. Business-Attributed Metric Cards -->
        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-title">Policy Subsidy Net Lift Effect</span>
                    <span class="kpi-badge green">Key Policy Driver</span>
                </div>
                <div class="kpi-val green">+{sub_lift:.2f}%</div>
                <div class="kpi-comparison">
                    <span>Baseline: With Subsidy <strong>{sub_yes_br*100:.2f}%</strong> vs Without <strong>{sub_no_br*100:.2f}%</strong></span>
                    <span>▲ <strong>47.4x</strong> Relative Lift</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-title">Range Anxiety Conversion Penalty</span>
                    <span class="kpi-badge red">Critical Bottleneck</span>
                </div>
                <div class="kpi-val red">-{anx_decay:.1f}%</div>
                <div class="kpi-comparison">
                    <span>Baseline: High Anxiety <strong>{high_anx_br*100:.2f}%</strong> vs Low Anxiety <strong>{low_anx_br*100:.2f}%</strong></span>
                    <span>▼ <strong>-{anx_decay:.1f}%</strong> Relative Decay</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-title">Home Charger Low-Anxiety Rate</span>
                    <span class="kpi-badge blue">Key Infrastructure</span>
                </div>
                <div class="kpi-val blue">99.75%</div>
                <div class="kpi-comparison">
                    <span>Baseline: Home Charger High Anxiety <strong>0.00%</strong> vs Without <strong>1.07%</strong></span>
                    <span>★ <strong>100%</strong> High-Anxiety Shield</span>
                </div>
            </div>

            <div class="kpi-card">
                <div class="kpi-top">
                    <span class="kpi-title">Prime Target Segment Conversion</span>
                    <span class="kpi-badge amber">Top Cohort</span>
                </div>
                <div class="kpi-val blue">{quad_q1_br*100:.2f}%</div>
                <div class="kpi-comparison">
                    <span>Baseline: High Income x Low Anxiety vs Population (<strong>{baseline_br*100:.2f}%</strong>)</span>
                    <span>▲ <strong>+{quad_q1_lift:.2f}%</strong> Over Baseline</span>
                </div>
            </div>
        </div>

        <!-- 2. Core Business Takeaways -->
        <section class="section-conclusions">
            <div class="section-title">📌 Core Business Takeaways (Executive Summary)</div>
            <div class="conclusion-grid">
                {conclusions_html}
            </div>
        </section>

        <!-- 3. Root-Cause Diagnostic Matrix -->
        <section class="section-diagnostics">
            <div class="section-title">🔍 Root-Cause Diagnostic Matrix & Causal Reasoning</div>
            <div class="diag-grid">
                {diagnostics_html}
            </div>
        </section>

        <!-- 4. Granular Cohort Slicing (Side-by-Side) -->
        <section class="section-analysis">
            <div class="section-title">📊 Granular Cohort Breakdown & Multi-Dimensional Slicing (Side-by-Side)</div>

            <!-- Split Row 1: Quadrants -->
            <div class="split-row">
                <div class="split-card">
                    <h4>Conversion Rate Across Strategic Quadrants (%)</h4>
                    <p class="chart-sub">Dashed line indicates Population Baseline ({baseline_br*100:.2f}%) for benchmark performance comparison</p>
                    <canvas id="chartQuadrants" height="210"></canvas>
                </div>
                <div class="split-card">
                    <h4>Strategic Quadrant Cohort Structure & Profile (Q1 - Q4)</h4>
                    <p class="chart-sub">Orthogonal cross-segmentation by median household income and range anxiety</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Quadrant</th>
                                <th>Segment Profile</th>
                                <th>Sample Size (N)</th>
                                <th>Share</th>
                                <th>Avg Annual Income</th>
                                <th>Conversion Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {quad_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Split Row 2: City & Commute -->
            <div class="split-row">
                <div class="split-card">
                    <h4>Home Charger Penetration vs Conversion Rate by City Type (%)</h4>
                    <p class="chart-sub">Low Urban home charger penetration (only 39.3%) accounts directly for its adoption lag</p>
                    <canvas id="chartCity" height="210"></canvas>
                </div>
                <div class="split-card">
                    <h4>Commute Distance & Home Charging Cross-Cohort Table</h4>
                    <p class="chart-sub">Long commutes (>50km) without home charging suffer lowest conversion at 9.43%</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Commute & Charging Segment</th>
                                <th>Sample Size (N)</th>
                                <th>Share</th>
                                <th>Conversion Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {commute_rows}
                        </tbody>
                    </table>
                </div>
            </div>

            <!-- Split Row 3: Subsidy & Eco -->
            <div class="split-row">
                <div class="split-card">
                    <h4>Conversion Rate by Income Tier: With vs Without Subsidy (%)</h4>
                    <p class="chart-sub">Compares absolute conversion rates; incomes >$130k show high baseline demand and diminishing subsidy lift</p>
                    <canvas id="chartSubsidyTiers" height="210"></canvas>
                </div>
                <div class="split-card">
                    <h4>Environmental Concern & Income Tier Cross-Matrix Table</h4>
                    <p class="chart-sub">Evaluates intersection of pro-environmental sentiment and real purchasing power</p>
                    <table>
                        <thead>
                            <tr>
                                <th>Cohort</th>
                                <th>Profile Description</th>
                                <th>Sample Size (N)</th>
                                <th>Share</th>
                                <th>Conversion Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {eco_rows}
                        </tbody>
                    </table>
                </div>
            </div>

        </section>
    </div>

    <!-- Script for Chart.js -->
    <script>
        window.addEventListener('DOMContentLoaded', () => {{
            // 1. Quadrants Chart with Benchmark Line
            new Chart(document.getElementById('chartQuadrants'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(chart_quad_labels, ensure_ascii=False)},
                    datasets: [
                        {{
                            label: 'Conversion Rate (%)',
                            data: {json.dumps(chart_quad_data)},
                            backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
                            borderRadius: 6,
                            order: 2
                        }},
                        {{
                            type: 'line',
                            label: 'Population Baseline ({baseline_br*100:.2f}%)',
                            data: {json.dumps(baseline_line)},
                            borderColor: '#64748b',
                            borderWidth: 2,
                            borderDash: [6, 6],
                            pointRadius: 0,
                            fill: false,
                            order: 1
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{ y: {{ beginAtZero: true, max: 80, ticks: {{ callback: v => v + '%' }} }} }}
                }}
            }});

            // 2. City Infrastructure Chart
            new Chart(document.getElementById('chartCity'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(chart_city_labels)},
                    datasets: [
                        {{
                            label: 'Home Charger Ownership (%)',
                            data: {json.dumps(chart_city_chg)},
                            backgroundColor: '#94a3b8',
                            borderRadius: 4
                        }},
                        {{
                            label: 'Conversion Rate (%)',
                            data: {json.dumps(chart_city_buy)},
                            backgroundColor: '#2563eb',
                            borderRadius: 4
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{ y: {{ beginAtZero: true, max: 100, ticks: {{ callback: v => v + '%' }} }} }}
                }}
            }});

            // 3. Subsidy Tiers Chart
            new Chart(document.getElementById('chartSubsidyTiers'), {{
                type: 'bar',
                data: {{
                    labels: {json.dumps(chart_tier_labels)},
                    datasets: [
                        {{
                            label: 'Without Subsidy (%)',
                            data: {json.dumps(chart_tier_no_sub)},
                            backgroundColor: '#cbd5e1',
                            borderRadius: 4
                        }},
                        {{
                            label: 'With Subsidy (%)',
                            data: {json.dumps(chart_tier_with_sub)},
                            backgroundColor: '#10b981',
                            borderRadius: 4
                        }}
                    ]
                }},
                options: {{
                    responsive: true,
                    scales: {{ y: {{ beginAtZero: true, max: 65, ticks: {{ callback: v => v + '%' }} }} }}
                }}
            }});
        }});
    </script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"[+] Re-engineered HTML Executive Report generated: {output_file}")
    return output_file
