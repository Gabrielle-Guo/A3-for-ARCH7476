# A3 — Window C, Harbour Road Garden: OSM-anchored prototype

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Starive/A3-for-ARCH7476/blob/main/a3_seat_C.ipynb)

**Run it now:** click the badge, then choose Runtime → Run all. Colab asks you to sign in with a Google account; nothing needs to be installed or uploaded. Section 4 should print `REPRODUCED`.

**Status: executable exploratory geometric prototype.** The test is located using verified OpenStreetMap garden-boundary nodes. The proposed Window C extent, assumed local flow edges, seat positions and comfort thresholds remain researcher-defined. No measured pedestrian routes, pedestrian volumes, short-stay durations, or direct comfort observations were available for this run.

## Quick start (anyone can re-run this)

**Option A: Google Colab, nothing to install**
1. Open https://colab.research.google.com/github/Starive/A3-for-ARCH7476/blob/main/a3_seat_C.ipynb (or click the badge above).
2. Runtime → Run all. If Colab warns that the notebook was not authored by Google, choose "Run anyway".
3. Section 4 should print `REPRODUCED: all 36 scenarios match the reference`.

The notebook is self-contained: it carries its own copy of the code and reference results, and it downloads no data.

**Option B: your own computer (Python 3.10 or newer)**
```bash
pip install -r requirements.txt
python code/a3_osm_anchor.py
python code/make_variant_panels.py
python code/make_figures.py
python code/check_reproduction.py
```
The last command should print `REPRODUCED`. Run the commands from this folder.

**What you get:** `outputs/a3_results_osm_anchored.csv` (36 scenarios), four figures, a verification log and `outputs/versions.txt`.

**To test another assumption:** edit the `CONFIG` block at the top of `code/a3_osm_anchor.py` and run again. The reproduction check will then list the differences, which is expected.

### Troubleshooting
| Symptom | Cause | Fix |
|---|---|---|
| `ModuleNotFoundError: geopandas` | Packages not installed | `pip install -r requirements.txt` |
| `pip` cannot find the pinned versions | Older Python | Remove the `==` version pins in `requirements.txt` |
| `AssertionError` in `a3_osm_anchor.py` | `CONFIG` was changed, so the known case (S1 = 80%) no longer applies | Restore the default `CONFIG`, or remove that assertion for your own test |
| `NOT REPRODUCED` | `CONFIG` changed, or a library computes differently | Restore `CONFIG`; compare `outputs/versions.txt` with the versions listed in `requirements.txt` |
| Figure text looks different | DejaVu font missing | Harmless; the numbers are unaffected |

## Verified OSM data

- Garden: [Harbour Road Garden, OSM way 27059126](https://www.openstreetmap.org/way/27059126), tagged `leisure=garden`.
- NE corner: [node 296894103](https://www.openstreetmap.org/node/296894103), WGS84 `22.2806549, 114.1759247`.
- SE corner: [node 296894102](https://www.openstreetmap.org/node/296894102), WGS84 `22.2802402, 114.1759591`.
- Other confirmed garden nodes: [8308187127](https://www.openstreetmap.org/node/8308187127), [296894101](https://www.openstreetmap.org/node/296894101), [12270766150](https://www.openstreetmap.org/node/12270766150).
- Verified boundary east side from NE to SE projects to **46.06 m** under EPSG:2326. This is a garden-boundary length, not a pedestrian-route width.
- OSM also associates footways `893892257` and `893892261` with nodes on the western/southern garden perimeter. **They do not establish a flow line at Window C on the northeast corner.** The northeast garden edge itself is tagged as a garden boundary, not as `highway=footway`.
- Access/transcription date: 13 Nov 2026. Source licence: © OpenStreetMap contributors (ODbL). The northwestern boundary node could not be independently retrieved in this environment; the GIS test uses the fully confirmed east boundary only.

## Researcher-defined, not site-verified inputs

- Window C: a **provisional 6 × 6 m** polygon aligned with the garden east boundary, starting 5 m along that boundary from the OSM NE corner. The exact 6×6 m dimension and chosen 5m offset are not recorded in OSM.
- Seat: 2 × 1 m, with 3 positions × 2 orientations (S1–S6); positions 2.2/3.2/4.3m measured inwards from the assumed flow-edge proxy.
- Main flow proxy 1: the east **garden boundary**. This is a known geographic edge but **not verified pedestrian flow**.
- Main flow proxy 2: north boundary of the constructed Window C; this edge is **fully assumed**.
- Corridor half-width w = 0.75, 1.0, 1.5 m (A2 screening assumptions).
- Flow-adjacent comfort band: c1 = 0.30m to c2 = 1.50m **outside the assumed corridor** (exploratory spatial hypothesis).
- Band-share threshold s = 60% (exploratory decision line). Neither c1/c2/s nor claimed comfort or stopping behaviour have been validated.
- A map-offset tolerance δ has not been measured and is deliberately excluded from this site-based computation.

## Re-run steps

See **Quick start** above. Required packages are pinned in `requirements.txt`; the versions of the reference run are recorded in `outputs/versions.txt`.

## Inputs and outputs

- `inputs/osm_garden_nodes_verified.geojson`: five confirmed OSM nodes with links and WGS84 coordinates; geometry in EPSG:2326.
- `inputs/osm_provenance.json`: source IDs/links and access status.
- `inputs/window_C_osm_anchored_ASSUMED.geojson`: *assumed* Window C, metrically anchored to the east garden boundary.
- `inputs/flow_edge_proxies_NOT_PATHS.geojson`: two candidate proxy edges; explicitly **not** measured pedestrian routes.
- `inputs/variants.csv`: the six controlled 2×1m variants.
- `outputs/a3_results_osm_anchored.csv`: 36 scenario rows with overlap and band-share metrics.
- `outputs/a3_base_comparison.csv`: the base-case result for w=1m and the east garden-edge proxy.
- `outputs/fig_six_placements.png`, `fig_base_comparison.png`, `fig_width_sensitivity.png`: report figures drawn by `code/make_figures.py`.
- `outputs/osm_context.png`, `a3_six_variant_plans.png`, `a3_threshold_chart.png`, `a3_flip_chart.png`: figures from the original run.
- `outputs/a3_verification_log.csv`: computed checks and explicitly pending checks.
- `reference/a3_results_reference.csv`: results of the reference run, used by `code/check_reproduction.py`.
- `requirements.txt`: package versions of the reference run.

## Results and valid interpretation

At the **assumed** base case (east-garden-edge as flow proxy, w=1.0 m, c1=0.30 m, c2=1.50 m, s=60%), S1 has 80% band share and S2 60%. Geometry assertions confirm 36 rows, seats of 2.00 m² after rotation and known-case S1 arithmetic `2×0.80/2.00=80%`. Changing w can move S1 across the assumed 60% line. These outcomes validate an exploratory computational procedure. They **cannot establish a pedestrian path location, real comfort, or the best pavilion seat on the site**.

## Next verification steps

1. Open the live OSM/official Hong Kong GIS layer in QGIS and identify a **ground-level path near C**, including its date, level, and measured or defensibly estimated width.
2. Verify/digitise the site-appropriate extent of Window C. Record the actual candidate geometry, its survey method and position uncertainty δ.
3. Justify c1, c2 and s from observations, precedents or a declared test protocol; test sensitivity before design recommendation.
4. Have a person independently rerun one overlap and one band-share calculation in QGIS and record the outcome/date.
5. In A4, compare the spatial hypothesis with collected short-stay observations.

## AI-assisted disclosure

ChatGPT (GPT-6) helped prepare the OSM-linked input geometry, GeoPandas/Shapely Python script, figure layouts and PowerPoint. Numeric assertions were executed and saved. The final independent GIS/field checks, threshold justification and final design recommendation are still pending. See `AI_Fact_Checking_Card.md`.

## Data and reuse

Node coordinates: © OpenStreetMap contributors, Open Database Licence (ODbL), https://www.openstreetmap.org/copyright. Code and figures: coursework for ARCH7476; reuse with attribution to the author.
