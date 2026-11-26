"""Compare a fresh run with the reference results.

Called at the end of run_all.py; can also be run on its own after run_all.py:
    python check_reproduction.py
"""
import csv
import sys
from pathlib import Path

TOL = 0.01
TABLES = [
    ("a3_scenarios.csv", ("variant", "edge_proxy", "w_m")),
    ("a4_window_size.csv", ("rule", "window_m", "variant", "edge_proxy", "w_m")),
]


def _key(r, cols):
    return tuple(f"{float(r[c]):.2f}" if c in ("w_m", "window_m") else r[c] for c in cols)


def _load(path, cols):
    with open(path, encoding="utf8", newline="") as f:
        return {_key(r, cols): r for r in csv.DictReader(f)}


def _num(x):
    return None if x in ("", None) else float(x)


def compare(root):
    root = Path(root)
    msgs, ok = [], True
    for name, cols in TABLES:
        new = _load(root / "outputs" / name, cols)
        ref = _load(root / "reference" / name.replace(".csv", "_reference.csv"), cols)
        problems = [] if set(new) == set(ref) else [f"{name}: scenario keys differ ({len(new)} new vs {len(ref)} reference)"]
        for key in sorted(set(new) & set(ref)):
            for col in ("corridor_overlap_m2", "band_share_pct"):
                a, b = _num(new[key][col]), _num(ref[key][col])
                if (a is None) != (b is None) or (a is not None and abs(a - b) > TOL):
                    problems.append(f"{name} {key} {col}: got {new[key][col]}, reference {ref[key][col]}")
            if new[key]["passes_rule"].strip().lower() != ref[key]["passes_rule"].strip().lower():
                problems.append(f"{name} {key} passes_rule differs")
        if problems:
            ok = False
            msgs += problems
        else:
            msgs.append(f"{name}: all {len(ref)} rows match within {TOL}")
    return ok, msgs


if __name__ == "__main__":
    ok, msgs = compare(Path(__file__).resolve().parent)
    print(("REPRODUCED" if ok else "NOT REPRODUCED (expected if inputs/ were edited)") + ":")
    for m in msgs:
        print("  -", m)
    sys.exit(0 if ok else 1)
