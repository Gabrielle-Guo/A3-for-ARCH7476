"""Compare a fresh run with the reference results. Usage: python check_reproduction.py (after a3_osm_anchor.py)."""
import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TOL = 0.01


def load(path):
    with open(path, encoding="utf8", newline="") as f:
        return {(r["variant"], r["edge_proxy"], f'{float(r["w_m"]):.2f}'): r for r in csv.DictReader(f)}


new = load(ROOT / "outputs" / "a3_scenarios.csv")
ref = load(ROOT / "reference" / "a3_scenarios_reference.csv")
problems = [] if set(new) == set(ref) else [f"scenario keys differ: {len(new)} new vs {len(ref)} reference"]
for key in sorted(set(new) & set(ref)):
    for col in ("corridor_overlap_m2", "band_share_pct"):
        if abs(float(new[key][col]) - float(ref[key][col])) > TOL:
            problems.append(f"{key} {col}: got {new[key][col]}, reference {ref[key][col]}")
    if new[key]["passes_rule"].strip().lower() != ref[key]["passes_rule"].strip().lower():
        problems.append(f"{key} passes_rule differs")
if problems:
    print("NOT REPRODUCED (expected if inputs/config.json or variants.csv was edited):")
    for p in problems:
        print("  -", p)
    sys.exit(1)
print(f"REPRODUCED: all {len(ref)} scenarios match the reference within {TOL}.")
