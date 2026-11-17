"""Compare a fresh run against the reference results shipped with the package.
Usage: python code/check_reproduction.py   (run after code/a3_osm_anchor.py)
Uses only the Python standard library."""
import csv, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
TOL = 0.01  # m2 and percentage points

def load(path):
    with open(path, encoding="utf8", newline="") as f:
        return {(r["variant"], r["flow_proxy"], f'{float(r["w_m"]):.2f}'): r for r in csv.DictReader(f)}

def main(new_path=None, ref_path=None):
    new = load(new_path or ROOT / "outputs" / "a3_results_osm_anchored.csv")
    ref = load(ref_path or ROOT / "reference" / "a3_results_reference.csv")
    problems = []
    if set(new) != set(ref):
        problems.append(f"scenario keys differ: {len(new)} new vs {len(ref)} reference")
    for key in sorted(set(new) & set(ref)):
        for col in ("corridor_overlap_m2", "comfort_band_share_pct"):
            a, b = float(new[key][col]), float(ref[key][col])
            if abs(a - b) > TOL:
                problems.append(f"{key} {col}: got {a}, reference {b}")
        if new[key]["band_threshold_pass"].strip().lower() != ref[key]["band_threshold_pass"].strip().lower():
            problems.append(f"{key} band_threshold_pass differs")
    if problems:
        print("NOT REPRODUCED:")
        for p in problems:
            print("  -", p)
        return 1
    print(f"REPRODUCED: all {len(ref)} scenarios match the reference within {TOL}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
