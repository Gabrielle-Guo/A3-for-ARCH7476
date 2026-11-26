# AI prompt log

Prompts are summarised, not verbatim. The design assumptions (Window C, edges, w, c₁, c₂, s), the six placements and the placement judgment are the author's and were not delegated.

| # | Date | Tool | Prompt summary | Output | Check | Decision |
|---|---|---|---|---|---|---|
| 1 | 13 Nov 2026 | ChatGPT | Draft Python for six seat layouts and 36 scenarios | First notebook and script | Run; seat areas and one band share by hand | Revised (see 2) |
| 2 | 15–17 Nov 2026 | Claude | Make the workflow re-runnable from one link; add a reproduction check; draw the figures | `a3src/a3_workflow.py`, Colab notebook, `check_reproduction.py`, figures | 25 checks with hand-written expected values; reference comparison | Accepted after running. An earlier claim of an EPSG:2326 conversion and a 46.06 m OSM edge was withdrawn |
| 3 | 26 Nov 2026 | Claude | Add the instructor's window-size question (5 × 5 m, geometry kept) to the workflow | `a3src/a4_window_size.py`, 504 scenarios, offset-rule test, key figure | 13 checks with hand-written expected values; W = 6.0 m must reproduce A3 exactly | Accepted. One expected value was wrong on the first run (see `VERIFICATION.md`, F3) |
| 4 | 26 Nov 2026 | Claude | Remove the conflict between "skipped in the recorded run" and "runs in Colab" | Grid cross-check (numpy) replaces the GeoPandas check; one entry point `run_all.py` | All 36 scenarios match the core exactly (difference 0); same checks run locally and in Colab | Accepted |
| 5 | 26 Nov 2026 | Claude | Find page locators in Gehl (2011) and Whyte (1980) for staying at edges and sitting; find an operational definition of a stationary activity | `SOURCES.md` table (Gehl pp. 9–12, 27, 147–159; Whyte pp. 19–21, 28; Mehta 2006 p. 32) | Pending: author to open each source at the cited page and confirm the wording | Pending |
| 6 | 26 Nov 2026 | Claude | Draft the A4 package pages from the A3 report and the A3 feedback | Practice Case, Research Brief, Object Card, Ledger, Reflection Note drafts | Author reads every number against `outputs/run_record.txt` and the CSVs | Author to revise |

Same prompt, same output? Not guaranteed. The stable record is the code, inputs, outputs and reference tables in this repository; trust the checked run, not the chat text.
