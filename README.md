# Window C seat placement — reproducibility capsule (ARCH7476 A3 → A4)

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Starive/A3-for-ARCH7476/blob/main/a3_seat_C.ipynb)

ARCH7476 Evidence-Based Generative Design · Guo Xinghe · Route B (live studio application).

**Decision:** where to place one 2.0 × 1.0 m seat in Window C of Harbour Road Garden (Wan Chai) so that it supports short stays (people sitting or standing in one place, see `SOURCES.md`) while keeping the assumed walking corridor clear.

**Key figure:** `outputs/fig_window_size.png`. Re-running the workflow redraws it from `outputs/a4_window_size_summary.csv` and `outputs/a4_offset_rule.csv`; a correct re-run ends with `RESULT: ALL CHECKS PASS · REPRODUCED`.

## Run it (about one minute)

**Option A: Google Colab, nothing to install**

1. Click the **Open in Colab** badge above.
2. Sign in with any Google account.
3. Choose **Runtime → Run all**. If Colab warns that the notebook was not written by Google, choose **Run anyway**.
4. Section 3 prints the run record. The last line must read `RESULT: ALL CHECKS PASS · REPRODUCED`.
5. Section 4 shows the key figure.

**Option B: your own computer (Python 3.10 or newer)**

```bash
git clone https://github.com/Starive/A3-for-ARCH7476.git
cd A3-for-ARCH7476
pip install -r requirements.txt
python run_all.py
```

The last line printed must read `RESULT: ALL CHECKS PASS · REPRODUCED`; the key figure is written to `outputs/fig_window_size.png`. Exit code 0 means every check passed.

Both options run the same file (`run_all.py`) and the same 39 checks. No step is optional or skipped, and no GIS library is needed.

## What the workflow does

| Step | Detail |
|---|---|
| Input | `inputs/config.json` (window, seat, w, c₁, c₂, s, window sizes) and `inputs/variants.csv` (S1–S6). All are assumptions; see `SOURCES.md` |
| A3 baseline | Six alternative placements of one seat × three corridor half-widths × two edge proxies = 36 scenarios; position sweep; width sensitivity |
| A4 window-size test | The 36 scenarios repeated for square windows of 4.0–7.0 m, with the six placements either scaled with the window (proportional) or kept at their distances in metres (fixed offset) = 504 scenarios; plus the offset rule (parallel seat, centre 2.00–2.15 m from the movement edge) at every size |
| Rule (set in A3, before running) | Pass if the seat has 0 m² inside the corridor (0 to w from the edge) **and** at least s = 60 % of its area inside the band (w + c₁ to w + c₂) |
| Checks | 25 hand-calculated A3 checks; a grid cross-check that re-measures all 36 scenarios on a 1 cm grid; 13 hand-calculated A4 checks; comparison of both scenario tables with `reference/` (tolerance 0.01) |
| Output | CSV tables, six figures, `outputs/a3_checks.csv`, `outputs/run_record.txt`, `outputs/versions.txt` |

## Files

| File | Role |
|---|---|
| `run_all.py` | Runs everything and prints the run record |
| `a3src/a3_workflow.py` | Geometry, rule, A3 scenarios, sweep, 25 checks, grid cross-check |
| `a3src/a4_window_size.py` | A4 window-size test, offset rule, 13 checks |
| `a3src/figures.py` | All figures, drawn from the computed tables |
| `check_reproduction.py`, `reference/` | Compares a fresh run with the reference tables |
| `a3_seat_C.ipynb` | Colab notebook; carries its own copy of the files above |
| `inputs/` | Every assumption, in one place |
| `outputs/` | Tables, figures, check log, run record of the last run |
| `DATA_DICTIONARY.md` | Every input field and output column, with units |
| `SOURCES.md` | Inputs, literature with page locators, figure sources |
| `VERIFICATION.md` | Checks, reruns and failure log |
| `AI_PROMPT_LOG.md` | What AI was asked to do and how each output was checked |
| `requirements.txt` | numpy, matplotlib |

`Window_C_Peer_Run.ipynb` and `Window_C_Peer_Run (1).ipynb` are the author's separate peer-review notebooks; they are not part of this capsule's run or checks.

## Environment of the recorded run

Python 3.13.18 · numpy 2.5.3 · matplotlib 3.11.2 · Linux x86_64, 26 Nov 2026 (`outputs/versions.txt`). Colab prints its own versions in section 1. Results are compared with a tolerance of 0.01, so other recent versions reproduce the same tables.

## Results under the default assumptions

- A3, 6 × 6 m, east edge, w = 1.00 m: S1 80 %, S2 60 %, S4 15 %, S3/S5/S6 0 %. No placement passes all 36 conditions.
- A3 sweep: a parallel seat whose centre is 2.00–2.15 m from the east edge passes all three widths.
- A4, 5 × 5 m with the geometry kept (proportional): S1 moves to 1.83 m from the edge and overlaps the w = 1.50 m corridor by 0.33 m², so it passes 2 of 3 widths. Across 4.0–7.0 m the label that passes changes (S3 at 4.0 m, S1 at 5.5 m, none at 4.5, 5.0, 6.0, 6.5 or 7.0 m).
- A4, fixed offsets: results are those of A3 wherever the seat fits; S4–S6 do not fit the smaller windows.
- A4, offset rule: a parallel seat with its centre 2.00–2.15 m from the movement edge passes all three widths at every window size from 4.0 to 7.0 m. If movement runs along the north edge, the same seat (not turned) passes 0–2 of 3.

## Change an assumption

Edit `inputs/config.json` or `inputs/variants.csv` and run again. The hand-calculated checks and the reference comparison describe the default inputs, so they will then report differences; that is expected and shows what changed.

## Limits

Schematic geometry in local metres; no map coordinates are loaded (OpenStreetMap way 27059126 is cited for location only). The movement edge, w, c₁, c₂, s and the window size are assumptions. The sources in `SOURCES.md` support placing a seat at the edge and in view of movement; they do not give these distances. Nothing here measures pedestrian flow, short stays or comfort.

## AI-assisted disclosure

AI assisted with the tooling: workflow code, the notebook, checks, figures and these documents (ChatGPT, 13 Nov 2026; Claude, 15–17 and 26 Nov 2026). The design assumptions, thresholds and placement judgment are the author's. See `AI_PROMPT_LOG.md`.

Location reference © OpenStreetMap contributors (ODbL).
