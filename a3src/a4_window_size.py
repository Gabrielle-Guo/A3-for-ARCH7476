"""A4 window-size test (instructor feedback on A3, Nov 2026).

Question: is the A3 result driven by the assumed 6 x 6 m Window C? For example, what if the
window is 5 x 5 m and the overall geometry is kept?

Two ways of "keeping the geometry" are tested, because they answer different questions:
  proportional : near / centre / far stay at the same fraction of the window
                 (2.2/6, 3.2/6, 4.3/6 of W from the east edge; seat centred W/2 from the north edge).
  fixed_offset : the seat keeps its distance in metres from the edges (2.2 / 3.2 / 4.3 m from east,
                 3.0 m from north); a seat that no longer fits inside the window is reported, not scored.

Then the A3 sweep result is re-expressed as an offset rule: a seat parallel to the movement edge with
its centre 2.00-2.15 m from that edge. It is tested for every window size, and also under the north
proxy while still parallel to the east edge (the limit shown on the Object Card).

Uses the same evaluate() and rule as A3; no new thresholds.
"""
import copy

from . import a3_workflow as wf

EPS = wf.EPS
A3_WINDOW = 6.0


def window_cfg(cfg, W, rule):
    c = copy.deepcopy(cfg)
    c["window_m"] = W
    c["seat_centre_from_north_m"] = W / 2 if rule == "proportional" else cfg["seat_centre_from_north_m"]
    return c


def window_variants(variants, W, rule):
    out = []
    for v in variants:
        v2 = dict(v)
        if rule == "proportional":
            v2["centre_from_east_m"] = v["centre_from_east_m"] * W / A3_WINDOW
        out.append(v2)
    return out


def fits(rect, W):
    x0, x1, y0, y1 = rect
    return x0 >= -EPS and y0 >= -EPS and x1 <= W + EPS and y1 <= W + EPS


def run_window_sizes(cfg, variants):
    rows = []
    for rule in cfg["window_rules"]:
        for W in cfg["window_sizes_m"]:
            c = window_cfg(cfg, W, rule)
            for v in window_variants(variants, W, rule):
                rect = wf.seat_rect(v, c)
                inside = fits(rect, W)
                for edge in cfg["edge_proxies"]:
                    for w in cfg["widths_m"]:
                        ov, sh = wf.evaluate(rect, edge, w, c)
                        rows.append({
                            "rule": rule, "window_m": W, "variant": v["variant"], "orientation": v["orientation"],
                            "centre_from_east_m": round(v["centre_from_east_m"], 4),
                            "centre_from_north_m": round(c["seat_centre_from_north_m"], 4),
                            "edge_proxy": edge, "w_m": w, "fits_window": inside,
                            "corridor_overlap_m2": round(ov, 4) if inside else "",
                            "band_share_pct": round(sh, 2) if inside else "",
                            "passes_rule": bool(inside and wf.passes(ov, sh, c)),
                        })
    return rows


def window_summary(rows, cfg):
    """Per rule x window x variant: how many of the 3 east-proxy widths pass, and of all 6 conditions."""
    out = []
    keys = sorted({(r["rule"], r["window_m"], r["variant"]) for r in rows},
                  key=lambda k: (cfg["window_rules"].index(k[0]), k[1], k[2]))
    for rule, W, vid in keys:
        mine = [r for r in rows if r["rule"] == rule and r["window_m"] == W and r["variant"] == vid]
        east = [r for r in mine if r["edge_proxy"] == "east"]
        base = next(r for r in east if abs(r["w_m"] - cfg["base_width_m"]) < EPS)
        out.append({
            "rule": rule, "window_m": W, "variant": vid, "fits_window": mine[0]["fits_window"],
            "east_base_share_pct": base["band_share_pct"],
            "east_widths_passed_of_3": sum(r["passes_rule"] for r in east),
            "all_conditions_passed_of_6": sum(r["passes_rule"] for r in mine),
        })
    return out


def offset_rule(cfg):
    """Seat parallel to a given edge, centre d from it, tested for every window size.

    'east'           : seat parallel to the east edge (long side N-S), scored with the east proxy.
    'north_turned'   : seat turned parallel to the north edge (long side E-W), scored with the north proxy.
    'north_unturned' : seat still parallel to the east edge, scored with the north proxy (the limit).
    """
    rows = []
    for W in cfg["window_sizes_m"]:
        c = window_cfg(cfg, W, "proportional")
        for d in cfg["offset_rule_centres_m"]:
            cases = {
                "east": ("east", (d - 0.5, d + 0.5, W / 2 - 1.0, W / 2 + 1.0)),
                "north_turned": ("north", (W / 2 - 1.0, W / 2 + 1.0, d - 0.5, d + 0.5)),
                "north_unturned": ("north", (d - 0.5, d + 0.5, W / 2 - 1.0, W / 2 + 1.0)),
            }
            for case, (edge, rect) in cases.items():
                res = [wf.evaluate(rect, edge, w, c) for w in cfg["widths_m"]]
                ok = fits(rect, W)
                rows.append({
                    "case": case, "window_m": W, "centre_from_edge_m": d, "edge_proxy": edge, "fits_window": ok,
                    "share_min_pct": round(min(s for _, s in res), 2),
                    "max_overlap_m2": round(max(o for o, _ in res), 4),
                    "widths_passed_of_3": sum(ok and wf.passes(o, s, c) for o, s in res),
                })
    return rows


def window_checks(cfg, variants, a3_rows, rows, offs):
    """Expected values written by hand before running (A4)."""
    checks = []

    def add(name, expected, observed, ok):
        checks.append({"n": f"W{len(checks) + 1}", "check": name, "expected": expected, "observed": observed,
                       "status": "PASS" if ok else "FAIL"})

    def get(rule, W, vid, edge, w):
        return next(r for r in rows if r["rule"] == rule and abs(r["window_m"] - W) < EPS and r["variant"] == vid
                    and r["edge_proxy"] == edge and abs(r["w_m"] - w) < EPS)

    n = len(cfg["window_rules"]) * len(cfg["window_sizes_m"]) * len(variants) * len(cfg["edge_proxies"]) * len(cfg["widths_m"])
    add("Window-size row count", f"2 rules x {len(cfg['window_sizes_m'])} sizes x 6 x 2 x 3 = {n}", len(rows), len(rows) == n)
    for rule in cfg["window_rules"]:
        diff = 0.0
        for a in a3_rows:
            r = get(rule, 6.0, a["variant"], a["edge_proxy"], a["w_m"])
            diff = max(diff, abs(r["band_share_pct"] - a["band_share_pct"]), abs(r["corridor_overlap_m2"] - a["corridor_overlap_m2"]))
        add(f"{rule} at W = 6.0 m reproduces the 36 A3 scenarios", "max difference 0", f"{diff:.4f}", diff < 1e-6)
    r = get("proportional", 5.0, "S1", "east", 1.5)
    add("5 x 5 proportional: S1 / east / w=1.50 overlap", "0.33 m2 (seat x 1.333-2.333 vs corridor 0-1.5: 0.167 x 2.0)",
        r["corridor_overlap_m2"], abs(r["corridor_overlap_m2"] - 0.3333) < 1e-3)
    r = get("proportional", 5.0, "S1", "east", 1.0)
    add("5 x 5 proportional: S1 / east / w=1.00 band share", "100 % (seat 1.333-2.333 inside band 1.3-2.5)",
        r["band_share_pct"], abs(r["band_share_pct"] - 100.0) < 1e-6)
    r = get("proportional", 5.0, "S1", "east", 0.75)
    add("5 x 5 proportional: S1 / east / w=0.75 band share", "91.67 % (band 1.05-2.25: 0.917 of 1.0)",
        r["band_share_pct"], abs(r["band_share_pct"] - 91.67) < 0.01)
    r = get("fixed_offset", 5.0, "S6", "east", 1.0)
    add("5 x 5 fixed offset: S6 fits the window", "False (seat x 3.3-5.3 > 5.0)", str(r["fits_window"]), r["fits_window"] is False)
    r = get("fixed_offset", 5.0, "S1", "east", 0.75)
    add("5 x 5 fixed offset: S1 / east / w=0.75 unchanged from A3", "55 %", r["band_share_pct"], abs(r["band_share_pct"] - 55.0) < 1e-6)
    east = [o for o in offs if o["case"] == "east"]
    add("Offset rule (east, centre 2.00-2.15 m): passes 3/3 widths at every window size",
        "True for all sizes", str(all(o["widths_passed_of_3"] == 3 for o in east)), all(o["widths_passed_of_3"] == 3 for o in east))
    turned = [o for o in offs if o["case"] == "north_turned"]
    same = all(abs(t["share_min_pct"] - e["share_min_pct"]) < 1e-6 and t["widths_passed_of_3"] == e["widths_passed_of_3"]
               for t, e in zip(turned, east))
    add("Offset rule turned to the north edge gives the same result (symmetry)", "True", str(same), same)
    # First run (26 Nov 2026) expected 0 of 3 at every size and FAILED: in windows <= 5.5 m the seat sits
    # closer to the north edge, so it partly enters the north band. Replaced by two hand-calculated cases.
    un = {round(o["window_m"], 2): o for o in offs if o["case"] == "north_unturned" and abs(o["centre_from_edge_m"] - 2.0) < EPS}
    add("Offset rule NOT turned, north proxy, W = 6.0 m (centre 2.00 m)", "0 of 3 (seat y 2.0-4.0: 12.5 % / 25 % / 50 % at w=0.75/1.00/1.50)",
        un[6.0]["widths_passed_of_3"], un[6.0]["widths_passed_of_3"] == 0)
    add("Offset rule NOT turned, north proxy, W = 5.0 m (centre 2.00 m)", "1 of 3 (seat y 1.5-3.5: 37.5 % / 50 % / 60 % at w=0.75/1.00/1.50)",
        un[5.0]["widths_passed_of_3"], un[5.0]["widths_passed_of_3"] == 1)
    perp = [r for r in wf.position_sweep(cfg, orientation="perpendicular", start=1.0, stop=5.0) if r["passes_all_widths"]]
    add("Perpendicular seat, east proxy, centre swept 1.00-5.00 m: positions passing all 3 widths",
        "none (band 1.2 m deep, seat 2.0 m: 60 % at w=0.75 needs the seat to start <= 1.05 m, inside the w=1.50 corridor)",
        len(perp), len(perp) == 0)
    return checks
