# A3 — Window C seat placement: re-runnable prototype

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Starive/A3-for-ARCH7476/blob/main/a3_seat_C.ipynb)

ARCH7476 Evidence-Based Generative Design, Assignment 3 (Guo Xinghe).

**Decision supported:** which of six 2.0 × 1.0 m seat placements in Window C best supports short stays in the garden while keeping pedestrian clearance?

**Status:** exploratory geometric prototype. It works in a local-metre schematic of an assumed 6 × 6 m window. No map coordinates are loaded: the OpenStreetMap way ID (27059126, Harbour Road Garden) is cited for location only. The window, the two edge proxies, the corridor widths and the thresholds are researcher assumptions, so the results screen geometry; they are not evidence of pedestrian flow, short-stay behaviour or comfort.

## Run it

**Google Colab (nothing to install).** Click the badge, sign in with a Google account, then Runtime → Run all. If Colab warns that the notebook was not authored by Google, choose "Run anyway". The notebook is self-contained and downloads no data. It should end with `25 of 25 PASS`, a GeoPandas cross-check `PASS`, and `REPRODUCED`.

**Your own computer (Python 3.10 or newer).**
```bash
pip install -r requirements.txt
python a3_osm_anchor.py
python check_reproduction.py
```

## What it does

| Step | Detail |
|---|---|
| Input | `inputs/config.json` (window, seat, widths, c₁, c₂, s) and `inputs/variants.csv` (S1–S6) |
| Operation | Builds six alternative placements of one seat; buffers each edge proxy (east, north) by the corridor half-width w; derives the proposed band from w + c₁ to w + c₂; intersects both with the seat |
| Output | `outputs/a3_scenarios.csv`: 6 variants × 3 widths × 2 edge proxies = 36 rows with corridor overlap (m²) and band share (%) |
| Rule (stated in advance) | Conflict if overlap > 0 m². Otherwise the placement passes the proxy rule if band share ≥ s (60 %, a researcher assumption, not a comfort standard) |
| Quality check | 25 internal checks against hand-calculated values, plus an independent `geopandas.overlay` cross-check, plus a comparison with `reference/a3_scenarios_reference.csv` |

Each seat keeps the same position in space under both edge proxies; only the edge treated as the movement proxy changes.

## Files

| File | Role |
|---|---|
| `a3_seat_C.ipynb` | Self-contained Colab notebook (carries its own copy of the code and inputs) |
| `a3_osm_anchor.py` | Runs the whole workflow and writes `outputs/` |
| `a3src/a3_workflow.py` | Geometry core, rule, sweep, 25 checks, GeoPandas cross-check |
| `inputs/config.json`, `inputs/variants.csv` | Every assumption, in one place |
| `outputs/a3_scenarios.csv` | The 36 scenarios |
| `outputs/a3_variant_summary.csv` | Per variant: share range, overlap and pass status for each proxy |
| `outputs/a3_position_sweep.csv` | Exploratory 0.05 m sweep of a parallel seat along the east proxy |
| `outputs/a3_width_sensitivity.csv` | S1 and S2 band share for w from 0.5 to 2.1 m |
| `outputs/a3_checks.csv` | The 25 checks and the cross-check, expected vs observed |
| `outputs/fig_*.png` | Six-placement plan, base-case charts (east and north), width-sensitivity chart |
| `outputs/versions.txt` | Versions of the run that wrote the outputs |
| `check_reproduction.py`, `reference/` | Confirms a fresh run matches the reference results |

## Results under the default assumptions

- East proxy, w = 1.00 m: S1 80 %, S2 60 %, S4 15 %, S3/S5/S6 0 %; no corridor overlap.
- S1 is width-sensitive: 55 % at w = 0.75 m, and it clears s = 60 % only for w from 0.80 to 1.70 m.
- S2 overlaps the corridor by 0.30 m² at w = 1.50 m.
- North proxy, w = 1.00 m: S1 reaches 25 %; no variant reaches 60 %.
- No original variant passes all 36 conditions.
- Sweep: a parallel seat centred 2.00–2.15 m from the east proxy passes all three east-proxy widths (minimum share 60–70 %, no overlap).

## Change an assumption

Edit `inputs/config.json` or `inputs/variants.csv` and run again. The hand-calculated checks and the reference comparison assume the default inputs, so they will then report differences; that is expected.

## Limits and what remains unverified

The real pedestrian path and flow at Window C, the measured extent of Window C, and c₁, c₂ and s as short-stay criteria. Neither edge proxy is a verified pedestrian route. An earlier draft of this package claimed an EPSG:2326 conversion and a verified 46.06 m OSM edge; that claim was withdrawn and the code now loads no coordinates.

## AI-assisted disclosure

AI assisted with the re-runnable tooling: workflow code, this Colab notebook, the checks and the figures (ChatGPT, 13 Nov 2026; Claude, 15–17 Nov 2026). The design assumptions, thresholds and placement judgment are the author's. See the AI-Assisted Fact-Checking Card in the submitted A3 report.

Location reference © OpenStreetMap contributors (ODbL).
