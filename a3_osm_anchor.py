"""A3 Window C: run the whole workflow.

Usage:  python a3_osm_anchor.py
Writes outputs/ (CSV tables, figures, check log, versions). Edit inputs/config.json to test other assumptions.
The file name is kept from the first draft; this version loads no OpenStreetMap coordinates
(the OSM way ID in config.json is provenance only).
"""
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from a3src import a3_workflow as wf  # noqa: E402

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)
cfg, variants = wf.load_inputs(ROOT)
V = {v["variant"]: v for v in variants}

# 1. scenarios, summaries, sweep
rows = wf.run_scenarios(cfg, variants)
wf.write_csv(OUT / "a3_scenarios.csv", rows)
summary = wf.variant_summary(rows, cfg)
wf.write_csv(OUT / "a3_variant_summary.csv", summary)
sweep = wf.position_sweep(cfg)
wf.write_csv(OUT / "a3_position_sweep.csv", sweep)
curves = {vid: wf.width_curve(V[vid], cfg) for vid in ("S1", "S2")}
wf.write_csv(OUT / "a3_width_sensitivity.csv", curves["S1"] + curves["S2"])

# 2. checks
checks = wf.internal_checks(cfg, variants, rows)
cross = wf.geopandas_cross_check(cfg, variants, rows)
log = checks + [{"n": "GP", "check": "GeoPandas overlay cross-check (east proxy)", "expected": "S2 / w=1.50 m = 0.30 m2; no difference from core",
                 "observed": cross["detail"], "status": cross["status"]}]
wf.write_csv(OUT / "a3_checks.csv", log)
n_pass = sum(c["status"] == "PASS" for c in checks)

# 3. versions
vers = ["python " + platform.python_version(), "matplotlib " + matplotlib.__version__]
for mod in ("geopandas", "shapely", "pandas", "pyproj"):
    try:
        vers.append(f"{mod} {__import__(mod).__version__}")
    except ImportError:
        vers.append(f"{mod} not installed")
(OUT / "versions.txt").write_text("\n".join(vers) + "\n", encoding="utf8")

# 4. figures
GREEN, TEAL, TAN, ORANGE, RULE = "#1f5a4e", "#9fbfb0", "#dcc3a5", "#c8623f", "#d9532b"
W, BW, C1, C2, S = cfg["window_m"], cfg["base_width_m"], cfg["c1_m"], cfg["c2_m"], cfg["s_pct"]
get = lambda vid, edge, w: next(r for r in rows if r["variant"] == vid and r["edge_proxy"] == edge and abs(r["w_m"] - w) < 1e-9)

fig, axes = plt.subplots(2, 3, figsize=(13.6, 9.4))
for ax, v in zip(axes.flat, variants):
    r = get(v["variant"], "east", BW)
    x0, x1, y0, y1 = wf.seat_rect(v, cfg)
    ax.add_patch(Rectangle((-W, -W), W, W, fill=False, ec="#4b6b62", ls="--", lw=1))
    ax.add_patch(Rectangle((-BW, -W), BW, W, fc=TAN, ec="none", alpha=0.65))
    ax.add_patch(Rectangle((-(BW + C2), -W), C2 - C1, W, fc=TEAL, ec="none", alpha=0.5))
    ax.plot([0, 0], [0, -W], color=GREEN, lw=3)
    conflict = r["corridor_overlap_m2"] > 0
    ax.add_patch(Rectangle((-x1, -y1), x1 - x0, y1 - y0, fc=ORANGE, ec="#8f1d1d" if conflict else ORANGE, lw=2.5 if conflict else 1.5, alpha=0.7))
    ax.set_title(f'{v["variant"]} · {v["position"].lower()} / {v["orientation"]}\n'
                 f'Band share {r["band_share_pct"]:.0f}% · overlap {r["corridor_overlap_m2"]:.2f} m²', fontsize=11, color="#1f3b34")
    ax.set_xlim(-W - 0.5, 0.45); ax.set_ylim(-W - 0.5, 0.4); ax.set_aspect("equal")
    ax.set_xlabel("Local x (m) · east edge at x=0", fontsize=8.5); ax.set_ylabel("Local y (m) · north edge at y=0", fontsize=8.5)
    ax.grid(alpha=0.12)
fig.suptitle(f"Window C / six ALTERNATIVE placements of ONE 2 × 1 m seat\nAssumed 6 × 6 m geometry; east edge proxy, w = {BW:.1f} m",
             fontsize=15, fontweight="bold", color=GREEN)
fig.text(0.5, 0.015, "Schematic geometry only • green = proposed flow-adjacent band • tan = assumed corridor • orange = seat",
         ha="center", fontsize=9.5, color="#5f786f")
fig.tight_layout(rect=(0, 0.03, 1, 0.93), h_pad=2.2)
fig.savefig(OUT / "fig_six_placements.png", dpi=160); plt.close(fig)

ids = [v["variant"] for v in variants]
for edge in cfg["edge_proxies"]:
    base = [get(v, edge, BW) for v in ids]
    shares = [r["band_share_pct"] for r in base]
    lead = ids[max(range(len(ids)), key=lambda i: shares[i])]
    fig, ax = plt.subplots(figsize=(10, 4.9))
    ax.bar(ids, shares, color=[GREEN if r["passes_rule"] else "#5f7d73" for r in base], width=0.66)
    for i, s in enumerate(shares):
        ax.text(i, s + 1.5, f"{s:.0f}%", ha="center", fontsize=10, color="#2a3d38")
    ax.axhline(S, color=RULE, lw=2, ls="--", label=f"Assumed research threshold s = {S:.0f}%")
    ax.set_ylim(0, 105); ax.set_ylabel("Proposed flow-adjacent band share (%)")
    title = (f"Base-case {lead} leads; proxy threshold is NOT a comfort standard" if max(shares) >= S
             else f"No variant reaches s = {S:.0f}% under the {edge} proxy")
    ax.set_title(title, fontweight="bold", color=GREEN)
    ax.legend(frameon=False, loc="upper right", fontsize=9); ax.spines[["top", "right"]].set_visible(False)
    fig.text(0.5, 0.02, f"{edge.capitalize()} edge proxy · corridor half-width w = {BW:.2f} m · c₁={C1:.2f}m, c₂={C2:.2f}m", ha="center", fontsize=9, color="#5f786f")
    fig.tight_layout(rect=(0, 0.05, 1, 1))
    fig.savefig(OUT / f"fig_base_comparison_{edge}.png", dpi=160); plt.close(fig)

lo, hi = wf.pass_range(curves["S1"])
fig, ax = plt.subplots(figsize=(10, 5.2))
if lo is not None:
    ax.axvspan(lo, hi, color="#e7efea", zorder=0)
    ax.axvline(lo, color="#b08a3c", lw=1, ls=":"); ax.axvline(hi, color="#b08a3c", lw=1, ls=":")
    ax.text(lo + 0.02, 6, "S1 conditional pass range\n(excluding geometric overlaps)", fontsize=8.5, color=GREEN)
for vid, col in (("S1", GREEN), ("S2", ORANGE)):
    ax.plot([r["w_m"] for r in curves[vid]], [r["band_share_pct"] for r in curves[vid]], color=col, lw=2.2, label=f"{vid} band share")
    for w in cfg["widths_m"]:
        ax.plot(w, get(vid, "east", w)["band_share_pct"], "o", color=col, ms=6)
ax.axhline(S, color="#a8522f", lw=1.6, ls="--", label=f"Assumed s = {S:.0f}%")
ax.set_xlim(0.5, 2.1); ax.set_ylim(0, 108)
ax.set_xlabel("Assumed corridor half-width w (m)"); ax.set_ylabel("Proposed band share (%)")
ax.set_title(f"Sensitivity: S1 clears s only for {lo:.2f} ≤ w ≤ {hi:.2f} m (east proxy)" if lo is not None else "Sensitivity: S1 never clears s (east proxy)",
             fontweight="bold", color=GREEN)
ax.legend(frameon=False, loc="upper left", fontsize=9); ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout(); fig.savefig(OUT / "fig_width_sensitivity.png", dpi=160); plt.close(fig)

# 5. report
print(f"Scenarios: {len(rows)} rows -> outputs/a3_scenarios.csv")
print(f"Internal checks: {n_pass} of {len(checks)} PASS")
for c in checks:
    if c["status"] != "PASS":
        print("  FAIL:", c["check"], "| expected", c["expected"], "| observed", c["observed"])
print(f"GeoPandas cross-check: {cross['status']} - {cross['detail']}")
passing = [r["centre_from_east_m"] for r in sweep if r["passes_all_widths"]]
print("Variants passing all 36 conditions:", [s["variant"] for s in summary if s["passes_all_36_conditions"]] or "none")
print("Position sweep (parallel seat, east proxy) passes all three widths at centres:",
      f"{min(passing):.2f}-{max(passing):.2f} m" if passing else "none")
print("These are geometric screening results under assumed inputs, not evidence of pedestrian flow or comfort.")
if n_pass != len(checks) or cross["status"] in ("FAIL", "ERROR"):
    sys.exit(1)
