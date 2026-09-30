# Changelog

All notable changes to the **EV Data Analysis Skill** (`ev-data-analysis`) will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-10-01

### Added
- **GitHub Repository Standards Alignment**: Re-architected project repository layout following industry-standard agentic skill best practices.
- **Side-by-Side (50/50) Ergonomic Layout**: Integrated split-screen visualization pairing responsive interactive Chart.js modules (featuring $17.46\%$ baseline reference lines) with structured sub-dataset pivot tables.
- **Automated Pytest Suite**: Created 6 deterministic unit and integration tests under `tests/` (`test_engine.py`, `test_reasoner.py`, `test_visualizer.py`, `test_harness.py`, and `conftest.py`).
- **Multi-Platform CI**: Added `.github/workflows/ci.yml` supporting Ubuntu and Windows on Python 3.10, 3.12, and 3.13.
- **Complete Internationalization**: Fully translated all dashboard components, reasoner outputs, prompts, reference protocols, and documentation into professional, objective English.

### Changed
- **Executive Dashboard Polish**: Removed cluttered raw metadata blocks and informal tags from dashboard header; replaced with clean title, subtitle, and 4 KPI cards.
- **Professional Objective Tone**: Purged informal hyperbole ("死亡衰减", "一票否决硬壁垒") across all engine code, replacing with empirical econometric nomenclature.
- **ReAct Threshold Mechanism**: Standardized convergence threshold scoring ($\ge 85/100$) across all 4 diagnostic goals.

---

## [2.0.0] - 2026-09-30

### Added
- **Two-Core Engine Architecture**: Decoupled data ingestion and sub-dataset slicing (`core/engine.py`) from dashboard rendering (`core/visualizer.py`).
- **Deterministic Harness Audit**: Built `harness/test_harness.py` to enforce record conservation ($\sum N_i = N$), boundary constraints $[0.0, 1.0]$, and cross-reconciliation.
- **Interactive Human-in-the-Loop Gate**: Added CLI review pause with `--yes` flag for automated non-interactive runs.
- **ReAct Multi-Turn Causal Engine**: Implemented `ReActDataAnalyst` executing iterative `Thought -> Action -> Observation` loops.

---

## [1.0.0] - 2026-09-25

### Initial Release
- Initial baseline script for EV dataset exploration and summary statistics.
- Basic HTML report output with preliminary demographic breakdowns.
