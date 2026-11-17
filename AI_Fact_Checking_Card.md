# AI-Assisted Fact-Checking Card — A3 Window C

## Task and AI role
- Decision: compare six 2 × 1 m seat placements in an OSM-located Window C.
- AI task: retrieve available source context, draft GeoPandas geometry code, prepare scenario outputs and charts, structure A3 PPT.
- Tool/model/date: ChatGPT / GPT-6 / 2026-11-13. Mode setting unknown.
- Supplied inputs: A2 submitted PDF, A3_Outline.md, OSM way and individually retrieved OSM node pages, user conversation on the thresholds and assignment brief.
- Saved files: `code/a3_osm_anchor.py`, `inputs/`, `outputs/`, `A3_Window_C_OSM_Anchored.pptx`, this card.

## Output type
- Workflow/code component: **Yes**.
- Fact-based reiteration (OSM node positions, source): **Yes**; checked against cited OSM element pages.
- Relationship hypothesis: **Yes, explicitly pending** — flow-adjacent comfort band is a researcher hypothesis.
- Writing/structure support: **Yes**; wording checked against submitted outline and course rubric.

## Prompt log (summary)
1. User: build an A3 PPT following the supplied A3 Outline → eight-page A3 content scaffold.
2. User: retrieve actual geometry from OSM → identified garden way 27059126 and five source-linked OSM nodes.
3. AI workflow: project verified northeast/east garden-boundary coordinates into EPSG:2326; construct a labelled six-by-six-metre **assumed** Window C; generate 36 hypothetical placements/scenarios.

## Generated output and verification/final gate
| Check attempted | Expected result and basis | Observed result | Status |
|---|---|---|---|
| CRS + east OSM boundary | EPSG:2326, 40–55 m sanity range for segment from OSM NE to SE nodes | 46.06 m | Passed (source coordinates; independent field length unverified) |
| Variant output count | 6 × 3 × 2 = 36 rows | 36 rows | Passed |
| Seat area | 2.00 m² for each rotation | 2.00 m² | Passed |
| Known case S1 band share | Seat u [1.7,2.7] vs band u [1.3,2.5] gives 0.8×2 / 2 = 80% | 80.0% | Passed as bounded analytical check |
| QGIS manual independent check | One traced route and C extent checked in QGIS | Not run / no validated walking route at C | Pending |
| Behavioural comfort | Evidence that proposed c1/c2/s predicts observed stopping | No observation data | Pending |

## Judgment and design consequence
- **Accept** the exploratory code and labelled OSM geolocation as a draft/prototype.
- **Pending**: real walking route, C measured extent, map-offset tolerance δ, comfort-band thresholds, final choice of S1–S6.
- Conditional result: S1 has largest band share in one modelled base case. This is **not** a verified recommended placement.
- Next: identify a tagged ground-level pedestrian path beside C, validate width/level and rerun; evaluate short-stay observations during A4.

## Reproducibility / failure log
- Runnable Python script and notebook wrapper saved with GeoJSON, CSV, plots, versions and README.
- Failure/limitation: web session could not download full OSM Way XML/Overpass; five individual nodes were transcribed from OSM HTML. The northwestern node was not needed for the verified garden east segment.
- OSM shows a garden boundary; pedestrian flow at C is inferred in the prototype and requires field verification.
- Independent peer/QGIS rerun **still pending**. Chart/geometry conclusions are conditional on assumptions.

## Disclosure statement
AI assisted with OSM source lookup, a GeoPandas/Shapely workflow prototype, code and figure drafting, and PPT structure. The code was run and checked against known geometry/area values. OSM boundary geolocation was sourced from public nodes. I retain the spatial-comfort interpretation and final seat-placement choice as pending because pedestrian flow, real C dimensions, and comfort-band parameters remain unverified.
