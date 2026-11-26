"""Window C seat placement: run the whole workflow (A3 baseline + A4 window-size test).

Usage:  python run_all.py
Writes outputs/ (CSV tables, figures, check log, run record) and compares the run with reference/.
Every run executes the same steps and the same checks, on a local machine or in Colab; nothing is
optional or skipped. Exit code 0 = all checks PASS and results REPRODUCED; 1 = something differs.
"""
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from a3src import a3_workflow as wf  # noqa: E402
from a3src import a4_window_size as ws  # noqa: E402
from a3src import figures  # noqa: E402
import check_reproduction  # noqa: E402

OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
cfg, variants = wf.load_inputs(ROOT)
V = {v["variant"]: v for v in variants}

# 1. A3 baseline: 6 placements x 3 widths x 2 edge proxies = 36 scenarios
rows = wf.run_scenarios(cfg, variants)
wf.write_csv(OUT / "a3_scenarios.csv", rows)
summary = wf.variant_summary(rows, cfg)
wf.write_csv(OUT / "a3_variant_summary.csv", summary)
sweep = wf.position_sweep(cfg)
wf.write_csv(OUT / "a3_position_sweep.csv", sweep)
curves = {vid: wf.width_curve(V[vid], cfg) for vid in ("S1", "S2")}
wf.write_csv(OUT / "a3_width_sensitivity.csv", curves["S1"] + curves["S2"])

# 2. A4 window-size test: 2 geometry rules x 7 window sizes x 36 = 504 scenarios, plus the offset rule
wrows = ws.run_window_sizes(cfg, variants)
wf.write_csv(OUT / "a4_window_size.csv", wrows)
wsum = ws.window_summary(wrows, cfg)
wf.write_csv(OUT / "a4_window_size_summary.csv", wsum)
offs = ws.offset_rule(cfg)
wf.write_csv(OUT / "a4_offset_rule.csv", offs)

# 3. checks: 25 A3 hand-calculated checks, grid cross-check of all 36 scenarios, A4 window checks
checks = wf.internal_checks(cfg, variants, rows)
grid = wf.grid_cross_check(cfg, variants, rows)
wchecks = ws.window_checks(cfg, variants, rows, wrows, offs)
log = checks + [{"n": "G", "check": "Grid cross-check (1 cm cells, numpy) of all 36 scenarios",
                 "expected": "same overlap and share as the core; S2 / east / w=1.50 m = 0.30 m2",
                 "observed": grid["detail"], "status": grid["status"]}] + wchecks
wf.write_csv(OUT / "a3_checks.csv", log)
n_pass = sum(c["status"] == "PASS" for c in log)

# 4. figures
figures.draw_all(OUT, cfg, variants, rows, curves, wsum, offs)

# 5. reproduction against reference/ (A3 36 scenarios + A4 504 scenarios)
repro_ok, repro_msgs = check_reproduction.compare(ROOT)

# 6. run record (versions + results)
import matplotlib  # noqa: E402
import numpy  # noqa: E402
stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
vers = [f"python {platform.python_version()}", f"numpy {numpy.__version__}", f"matplotlib {matplotlib.__version__}",
        f"platform {platform.system()} {platform.machine()}"]
(OUT / "versions.txt").write_text("\n".join(vers) + "\n", encoding="utf8")

passing = [r["centre_from_east_m"] for r in sweep if r["passes_all_widths"]]
five = [s for s in wsum if s["rule"] == "proportional" and abs(s["window_m"] - 5.0) < 1e-9]
lines = [
    f"Run: {stamp}",
    "Environment: " + " | ".join(vers),
    f"A3 scenarios: {len(rows)} rows -> outputs/a3_scenarios.csv",
    f"A4 window-size scenarios: {len(wrows)} rows -> outputs/a4_window_size.csv",
    f"Checks: {n_pass} of {len(log)} PASS (25 A3 hand-calculated + 1 grid cross-check + {len(wchecks)} A4 window-size)",
    f"Grid cross-check: {grid['status']} - {grid['detail']}",
    "Variants passing all 36 A3 conditions: " + (", ".join(s["variant"] for s in summary if s["passes_all_36_conditions"]) or "none"),
    "A3 sweep (parallel seat, east proxy) passes all three widths at centres: "
    + (f"{min(passing):.2f}-{max(passing):.2f} m" if passing else "none"),
    "5 x 5 m window, proportional geometry, east widths passed of 3: "
    + ", ".join(f"{s['variant']} {s['east_widths_passed_of_3']}" for s in five),
    "Offset rule (parallel to east edge, centre 2.00-2.15 m): passes 3 of 3 widths at window sizes "
    + ", ".join(f"{W:g}" for W in cfg["window_sizes_m"]
                if all(o["widths_passed_of_3"] == 3 for o in offs if o["case"] == "east" and o["window_m"] == W)) + " m",
    "Reproduction: " + ("REPRODUCED - " if repro_ok else "NOT REPRODUCED - ") + "; ".join(repro_msgs[:6]),
    "Key figure: outputs/fig_window_size.png (Object Card).",
    "These are geometric screening results under assumed inputs, not evidence of pedestrian flow or comfort.",
]
for c in log:
    if c["status"] != "PASS":
        lines.append(f"  FAIL {c['n']}: {c['check']} | expected {c['expected']} | observed {c['observed']}")
verdict = "ALL CHECKS PASS · REPRODUCED" if (n_pass == len(log) and repro_ok) else "CHECK FAILED - see lines above"
lines.append("RESULT: " + verdict)
(OUT / "run_record.txt").write_text("\n".join(lines) + "\n", encoding="utf8")
print("\n".join(lines))
if verdict != "ALL CHECKS PASS · REPRODUCED":
    sys.exit(1)
