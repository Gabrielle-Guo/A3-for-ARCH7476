"""A3 Window C workflow core.

Local-metre schematic frame: x = distance inward from the east edge proxy (0..window),
y = distance south from the north edge proxy (0..window). No map coordinates are loaded.
One 2 x 1 m seat is tested at six alternative placements. Each seat keeps the same position
in space under both edge proxies; only the edge used as the movement proxy changes.

The core uses exact interval arithmetic (Python standard library). `grid_cross_check` re-measures
all 36 scenarios by counting 1 cm grid cells with numpy, as an independent check. No GIS library is
needed, so the same checks run on a local machine and in Colab.
"""
import csv
import json
from pathlib import Path

EPS = 1e-9


def load_inputs(root):
    root = Path(root)
    cfg = json.loads((root / "inputs" / "config.json").read_text(encoding="utf8"))
    with open(root / "inputs" / "variants.csv", encoding="utf8", newline="") as f:
        variants = [dict(r, centre_from_east_m=float(r["centre_from_east_m"])) for r in csv.DictReader(f)]
    return cfg, variants


def seat_rect(variant, cfg, centre_from_east=None):
    """Seat rectangle (x0, x1, y0, y1). 'parallel' = long side N-S, along the east edge."""
    xc = variant["centre_from_east_m"] if centre_from_east is None else centre_from_east
    yc = cfg["seat_centre_from_north_m"]
    if variant["orientation"] == "parallel":
        hx, hy = cfg["seat_short_m"] / 2, cfg["seat_long_m"] / 2
    else:
        hx, hy = cfg["seat_long_m"] / 2, cfg["seat_short_m"] / 2
    return (xc - hx, xc + hx, yc - hy, yc + hy)


def _overlap(a0, a1, b0, b1):
    return max(0.0, min(a1, b1) - max(a0, b0))


def evaluate(rect, edge, w, cfg, c1=None, c2=None):
    """Corridor overlap (m2) and proposed band share (%) of one seat for one edge proxy and width."""
    c1 = cfg["c1_m"] if c1 is None else c1
    c2 = cfg["c2_m"] if c2 is None else c2
    x0, x1, y0, y1 = rect
    d0, d1, along = (x0, x1, y1 - y0) if edge == "east" else (y0, y1, x1 - x0)
    W = cfg["window_m"]
    area = (x1 - x0) * (y1 - y0)
    overlap = _overlap(d0, d1, 0.0, w) * along
    band = _overlap(d0, d1, min(w + c1, W), min(w + c2, W)) * along
    return overlap, 100.0 * band / area


def passes(overlap, share, cfg, s=None):
    s = cfg["s_pct"] if s is None else s
    return overlap <= EPS and share >= s - EPS


def run_scenarios(cfg, variants):
    rows = []
    for edge in cfg["edge_proxies"]:
        for w in cfg["widths_m"]:
            for v in variants:
                rect = seat_rect(v, cfg)
                overlap, share = evaluate(rect, edge, w, cfg)
                x0, x1, y0, y1 = rect
                rows.append({
                    "variant": v["variant"], "position": v["position"], "orientation": v["orientation"],
                    "edge_proxy": edge, "w_m": w,
                    "corridor_overlap_m2": round(overlap, 4), "band_share_pct": round(share, 2),
                    "seat_area_m2": round((x1 - x0) * (y1 - y0), 4),
                    "inside_window": x0 >= -EPS and y0 >= -EPS and x1 <= cfg["window_m"] + EPS and y1 <= cfg["window_m"] + EPS,
                    "geometry": "conflict" if overlap > EPS else "clear",
                    "passes_rule": passes(overlap, share, cfg),
                })
    return rows


def variant_summary(rows, cfg):
    out = []
    for vid in sorted({r["variant"] for r in rows}):
        mine = [r for r in rows if r["variant"] == vid]
        rec = {"variant": vid}
        for edge in cfg["edge_proxies"]:
            e = [r for r in mine if r["edge_proxy"] == edge]
            rec[f"{edge}_share_min_pct"] = min(r["band_share_pct"] for r in e)
            rec[f"{edge}_share_max_pct"] = max(r["band_share_pct"] for r in e)
            rec[f"{edge}_max_overlap_m2"] = max(r["corridor_overlap_m2"] for r in e)
            rec[f"{edge}_passes_all_widths"] = all(r["passes_rule"] for r in e)
        rec["passes_all_36_conditions"] = all(r["passes_rule"] for r in mine)
        out.append(rec)
    return out


def position_sweep(cfg, orientation="parallel", edge="east", start=1.5, stop=4.5):
    """Move one seat in steps along x and test every tested width (exploratory)."""
    step = cfg["sweep_step_m"]
    out, n = [], int(round((stop - start) / step))
    for k in range(n + 1):
        xc = round(start + k * step, 4)
        rect = seat_rect({"orientation": orientation, "centre_from_east_m": xc}, cfg)
        res = [evaluate(rect, edge, w, cfg) for w in cfg["widths_m"]]
        out.append({"orientation": orientation, "edge_proxy": edge, "centre_from_east_m": xc,
                    "share_min_pct": round(min(s for _, s in res), 2),
                    "max_overlap_m2": round(max(o for o, _ in res), 4),
                    "passes_all_widths": all(passes(o, s, cfg) for o, s in res)})
    return out


def width_curve(variant, cfg, edge="east", lo=0.5, hi=2.1, step=0.01):
    out, n = [], int(round((hi - lo) / step))
    rect = seat_rect(variant, cfg)
    for k in range(n + 1):
        w = round(lo + k * step, 4)
        overlap, share = evaluate(rect, edge, w, cfg)
        out.append({"variant": variant["variant"], "edge_proxy": edge, "w_m": w,
                    "band_share_pct": round(share, 3), "corridor_overlap_m2": round(overlap, 4),
                    "passes_rule": passes(overlap, share, cfg)})
    return out


def pass_range(curve):
    ws = [r["w_m"] for r in curve if r["passes_rule"]]
    return (min(ws), max(ws)) if ws else (None, None)


def internal_checks(cfg, variants, rows):
    """25 checks. Expected values were written by hand before the code was run."""
    V = {v["variant"]: v for v in variants}
    get = lambda vid, edge, w: next(r for r in rows if r["variant"] == vid and r["edge_proxy"] == edge and abs(r["w_m"] - w) < EPS)
    checks = []

    def add(name, expected, observed, ok):
        checks.append({"n": len(checks) + 1, "check": name, "expected": expected, "observed": observed,
                       "status": "PASS" if ok else "FAIL"})

    add("Scenario count", "6 x 3 x 2 = 36", len(rows), len(rows) == 36)
    for vid in sorted(V):
        a = get(vid, "east", 1.0)["seat_area_m2"]
        add(f"{vid} seat area", "2.00 m2", f"{a:.2f} m2", abs(a - 2.0) < 1e-6)
    for vid in sorted(V):
        ins = get(vid, "east", 1.0)["inside_window"]
        add(f"{vid} inside Window C", "True", str(ins), ins)
    known = [("S1", "east", 1.0, "band_share_pct", 80.0, "seat x 1.7-2.7 in band 1.3-2.5: 0.8 of 1.0"),
             ("S2", "east", 1.0, "band_share_pct", 60.0, "seat x 1.2-3.2 in band 1.3-2.5: 1.2 of 2.0"),
             ("S1", "east", 0.75, "band_share_pct", 55.0, "band 1.05-2.25: 0.55 of 1.0"),
             ("S1", "east", 1.5, "band_share_pct", 90.0, "band 1.8-3.0: 0.9 of 1.0"),
             ("S2", "east", 1.5, "corridor_overlap_m2", 0.30, "seat x 1.2-1.5 inside corridor: 0.3 m x 1.0 m"),
             ("S1", "north", 1.0, "band_share_pct", 25.0, "seat y 2.0-4.0 in band 1.3-2.5: 0.5 of 2.0"),
             ("S4", "east", 1.0, "band_share_pct", 15.0, "seat x 2.2-4.2 in band 1.3-2.5: 0.3 of 2.0")]
    for vid, edge, w, col, exp, why in known:
        obs = get(vid, edge, w)[col]
        add(f"Known case {vid} / {edge} / w={w:.2f}: {col}", f"{exp} ({why})", obs, abs(obs - exp) < 1e-6)
    shares = [r["band_share_pct"] for r in rows]
    add("All band shares within 0-100 %", "True", f"{min(shares)} to {max(shares)}", min(shares) >= 0 and max(shares) <= 100)
    ovs = [r["corridor_overlap_m2"] for r in rows]
    add("All overlaps within 0-2.00 m2", "True", f"{min(ovs)} to {max(ovs)}", min(ovs) >= 0 and max(ovs) <= 2.0)
    none075 = all(r["corridor_overlap_m2"] == 0 for r in rows if r["edge_proxy"] == "east" and abs(r["w_m"] - 0.75) < EPS)
    add("No east-proxy overlap at w = 0.75 m", "True", str(none075), none075)
    sweep_pass = [r["centre_from_east_m"] for r in position_sweep(cfg) if r["passes_all_widths"]]
    add("Position sweep (parallel, east): passing centres", "2.00 to 2.15 m",
        f"{min(sweep_pass):.2f} to {max(sweep_pass):.2f} m" if sweep_pass else "none",
        bool(sweep_pass) and abs(min(sweep_pass) - 2.0) < 1e-6 and abs(max(sweep_pass) - 2.15) < 1e-6)
    lo, hi = pass_range(width_curve(V["S1"], cfg))
    add("S1 east-proxy pass range of w", "0.80 to 1.70 m", f"{lo:.2f} to {hi:.2f} m",
        lo is not None and abs(lo - 0.80) < 1e-6 and abs(hi - 1.70) < 1e-6)
    return checks


def grid_cross_check(cfg, variants, rows, cell=0.01):
    """Independent area check that needs no GIS library.

    Re-measures every one of the 36 scenarios by counting 1 cm grid cells (numpy), instead of the
    interval arithmetic used by evaluate(). All A3 boundaries lie on multiples of 0.05 m, so the
    count should match exactly. Runs identically on a local machine and in Colab.
    """
    import numpy as np
    W = cfg["window_m"]
    n = int(round(W / cell))
    centres = (np.arange(n) + 0.5) * cell
    X, Y = np.meshgrid(centres, centres)          # X = distance from east edge, Y = from north edge
    cell_area = cell * cell
    worst_ov, worst_sh, s2 = 0.0, 0.0, None
    for r in rows:
        v = next(v for v in variants if v["variant"] == r["variant"])
        x0, x1, y0, y1 = seat_rect(v, cfg)
        seat = (X > x0) & (X < x1) & (Y > y0) & (Y < y1)
        d = X if r["edge_proxy"] == "east" else Y
        w = r["w_m"]
        ov = float((seat & (d < w)).sum() * cell_area)
        band = (seat & (d > min(w + cfg["c1_m"], W)) & (d < min(w + cfg["c2_m"], W))).sum()
        sh = float(100.0 * band / seat.sum())
        worst_ov = max(worst_ov, abs(ov - r["corridor_overlap_m2"]))
        worst_sh = max(worst_sh, abs(sh - r["band_share_pct"]))
        if r["variant"] == "S2" and r["edge_proxy"] == "east" and abs(w - 1.5) < EPS:
            s2 = ov
    ok = worst_ov < 1e-6 and worst_sh < 1e-6 and s2 is not None and abs(s2 - 0.30) < 1e-6
    return {"status": "PASS" if ok else "FAIL",
            "detail": f"all 36 scenarios re-measured on a 1 cm grid; S2 / east / w=1.50 m overlap = {s2:.2f} m2; "
                      f"max difference: overlap {worst_ov:.1e} m2, share {worst_sh:.1e} %"}


def write_csv(path, rows):
    with open(path, "w", encoding="utf8", newline="") as f:
        wr = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        wr.writeheader()
        wr.writerows(rows)
