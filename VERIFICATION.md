# Verification notes and failure log

## One run, one set of checks

`run_all.py` is the only entry point. The Colab notebook calls the same file. Every run executes the same 39 checks and the same reference comparison; nothing is optional, skipped or environment-dependent. (In A3 the GeoPandas cross-check ran only where GeoPandas was installed, so the recorded run said "skipped" while the report said "runs in Colab". A4 removes that split; see F2.)

| Group | Checks | How the expected value was set |
|---|---|---|
| A3 structure and known cases | 25 (`n` = 1–25) | Written by hand before running: scenario count, six seat areas, six fit checks, seven hand-calculated band shares / overlaps, three range checks, sweep range, S1 width range |
| Independent re-measurement | 1 (`G`) | All 36 scenarios re-measured by counting 1 cm grid cells (numpy) instead of interval arithmetic. Expected: identical, and S2 / east / w = 1.50 m = 0.30 m² |
| A4 window-size test | 13 (`W1`–`W13`) | Written by hand before running: row count; W = 6.0 m reproduces A3 exactly under both rules; four 5 × 5 m cases; offset rule at every size; north-edge symmetry; two north-edge limit cases; perpendicular seat never passes all widths |
| Reproduction | 2 tables | `outputs/a3_scenarios.csv` (36 rows) and `outputs/a4_window_size.csv` (504 rows) compared with `reference/`, tolerance 0.01 |

## Recorded runs

| Date | Where | Steps followed | Result |
|---|---|---|---|
| 26 Nov 2026 | Linux, Python 3.13.18, numpy 2.5.3, matplotlib 3.11.2 | `python run_all.py` in the repository | 39 of 39 PASS · REPRODUCED |
| 26 Nov 2026 | Fresh clone into an empty folder, `outputs/` deleted first | README Option B only | 39 of 39 PASS · REPRODUCED; `fig_window_size.png` byte-identical to the committed one (MD5 ef66b125…) |
| 26 Nov 2026 | Notebook cells executed in an empty folder (embedded-file path, as in Colab without the repository) | Notebook top to bottom | 39 of 39 PASS · REPRODUCED; key figure byte-identical |
| To do | Google Colab (author's account) | README Option A | Paste the RESULT line and the section 1 versions here |
| To do | Week 11 capsule swap: peer's own machine | README only | Peer name, date, RESULT line, or the exact step that failed |

## Failure log

| # | What failed | Where | Repair | Status |
|---|---|---|---|---|
| F1 | A draft claimed an EPSG:2326 conversion and a verified 46.06 m OSM edge; no coordinates had been loaded | A3 draft | Claim withdrawn; OSM way ID kept as provenance only | Closed (A3) |
| F2 | "Skipped in the recorded run" and "runs in Colab" described the same check; a reader could not tell which run to trust | A3 report, slides 2, 3, 7, 8 | Replaced the GeoPandas check with the grid re-measurement, which needs no extra library; single entry point `run_all.py`; README states one expected RESULT line | Closed (A4) |
| F3 | First A4 run: check "offset rule not turned, north proxy: 0 of 3 at every window size" FAILED (observed 2 of 3 at 4.0 m, 1 of 3 at 4.5–5.5 m) | `a3src/a4_window_size.py` | The expectation was reasoned from the 6 m window only. In smaller windows the seat sits nearer the north edge and partly enters the north band. Recalculated two cases by hand (W = 6.0 m: 0 of 3; W = 5.0 m: 1 of 3) and replaced the check; the code was not changed | Closed; the Object Card limit row shows 0–2 of 3 |
| F4 | Key-figure title ran off the page | `a3src/figures.py` | Shortened | Closed |
| F5 | The A3 report said S1 fails "if c₂ ≤ 1.30 m or c₁ ≥ 0.90 m" (w = 1.00 m). Rechecked: at exactly c₂ = 1.30 m or c₁ = 0.90 m, S1 scores 60 % and passes | A3 report, slide 6 | Corrected to "c₂ < 1.30 m or c₁ > 0.90 m" in the A4 Research Brief | Closed |

## What these checks do not establish

They show the code computes the stated geometry correctly and reproducibly. They do not show where people walk at Window C, how wide the movement corridor is, whether people stay at this seat, or whether c₁ = 0.30 m, c₂ = 1.50 m and s = 60 % are the right values.
