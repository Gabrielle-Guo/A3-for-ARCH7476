"""Report-style figures drawn from the results table.
Usage: python code/make_figures.py   (run after code/a3_osm_anchor.py)
Needs only matplotlib. Reads outputs/a3_results_osm_anchored.csv and inputs/variants.csv.
Geometry is drawn in the local Window C frame: east edge at x = 0, north edge at y = 0, metres."""
import csv
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "outputs"
WINDOW, SEAT_L, SEAT_W = 6.0, 2.0, 1.0
C1, C2, S_LINE = 0.30, 1.50, 60.0          # must match CONFIG in a3_osm_anchor.py
EDGE, EDGE_LABEL = "east_garden_boundary", "east edge proxy"
GREEN, TEAL, TAN, ORANGE, RULE = "#1f5a4e", "#9fbfb0", "#dcc3a5", "#c8623f", "#d9532b"

def read(path):
    with open(path, encoding="utf8", newline="") as f:
        return list(csv.DictReader(f))

rows = [r for r in read(OUT / "a3_results_osm_anchored.csv") if r["flow_proxy"] == EDGE]
dist = {r["variant"]: float(r["distance_from_flow_edge_m"]) for r in read(ROOT / "inputs" / "variants.csv")}
widths = sorted({float(r["w_m"]) for r in rows})
ids = sorted({r["variant"] for r in rows})
get = lambda vid, w: next(r for r in rows if r["variant"] == vid and abs(float(r["w_m"]) - w) < 1e-9)
BASE_W = 1.0 if 1.0 in widths else widths[len(widths) // 2]

# Figure 1: six alternative placements of one seat
fig, axes = plt.subplots(2, 3, figsize=(13.6, 9.4))
for ax, vid in zip(axes.flat, ids):
    r = get(vid, BASE_W)
    parallel = r["orientation"] == "parallel"
    du, dv = (SEAT_W / 2, SEAT_L / 2) if parallel else (SEAT_L / 2, SEAT_W / 2)
    d = dist[vid]
    ax.add_patch(Rectangle((-WINDOW, -WINDOW), WINDOW, WINDOW, fill=False, ec="#4b6b62", ls="--", lw=1))
    ax.add_patch(Rectangle((-BASE_W, -WINDOW), BASE_W, WINDOW, fc=TAN, ec="none", alpha=0.65))
    ax.add_patch(Rectangle((-(BASE_W + C2), -WINDOW), C2 - C1, WINDOW, fc=TEAL, ec="none", alpha=0.5))
    ax.plot([0, 0], [0, -WINDOW], color=GREEN, lw=3)
    conflict = float(r["corridor_overlap_m2"]) > 1e-8
    ax.add_patch(Rectangle((-d - du, -WINDOW / 2 - dv), 2 * du, 2 * dv, fc=ORANGE, ec="#8f1d1d" if conflict else ORANGE,
                           lw=2.5 if conflict else 1.5, alpha=0.7))
    ax.set_title(f'{vid} · {r["position"].lower()} / {r["orientation"]}\n'
                 f'Band share {float(r["comfort_band_share_pct"]):.0f}% · overlap {float(r["corridor_overlap_m2"]):.2f} m²',
                 fontsize=11, color="#1f3b34")
    ax.set_xlim(-WINDOW - 0.5, 0.45); ax.set_ylim(-WINDOW - 0.5, 0.4); ax.set_aspect("equal")
    ax.set_xlabel("Local x (m) · east edge at x=0", fontsize=8.5)
    ax.set_ylabel("Local y (m) · north edge at y=0", fontsize=8.5)
    ax.grid(alpha=0.12)
fig.suptitle(f"Window C / six ALTERNATIVE placements of ONE 2 × 1 m seat\n"
             f"Assumed 6 × 6 m geometry; {EDGE_LABEL}, w = {BASE_W:.1f} m", fontsize=15, fontweight="bold", color=GREEN)
fig.text(0.5, 0.015, "Schematic geometry only • green = proposed flow-adjacent band • tan = assumed corridor • orange = seat",
         ha="center", fontsize=9.5, color="#5f786f")
fig.tight_layout(rect=(0, 0.03, 1, 0.93), h_pad=2.2)
fig.savefig(OUT / "fig_six_placements.png", dpi=160); plt.close(fig)

# Figure 2: base-case comparison with the threshold drawn in
base = [get(v, BASE_W) for v in ids]
shares = [float(r["comfort_band_share_pct"]) for r in base]
passed = [r["band_threshold_pass"].strip().lower() == "true" for r in base]
lead = ids[max(range(len(ids)), key=lambda i: shares[i])]
fig, ax = plt.subplots(figsize=(10, 4.9))
ax.bar(ids, shares, color=[GREEN if p else "#5f7d73" for p in passed], width=0.66)
for i, s in enumerate(shares):
    ax.text(i, s + 1.5, f"{s:.0f}%", ha="center", fontsize=10, color="#2a3d38")
ax.axhline(S_LINE, color=RULE, lw=2, ls="--", label=f"Assumed research threshold s = {S_LINE:.0f}%")
ax.set_ylim(0, 105); ax.set_ylabel("Proposed flow-adjacent band share (%)")
ax.set_title(f"Base-case {lead} leads; proxy threshold is NOT a comfort standard", fontweight="bold", color=GREEN)
ax.legend(frameon=False, loc="upper right", fontsize=9)
ax.spines[["top", "right"]].set_visible(False)
fig.text(0.5, 0.02, f"East boundary proxy · corridor half-width w = {BASE_W:.2f} m · c₁={C1:.2f}m, c₂={C2:.2f}m",
         ha="center", fontsize=9, color="#5f786f")
fig.tight_layout(rect=(0, 0.05, 1, 1))
fig.savefig(OUT / "fig_base_comparison.png", dpi=160); plt.close(fig)

# Figure 3: band share across corridor widths, with corridor conflicts marked
fig, ax = plt.subplots(figsize=(10, 4.9))
for vid in ids:
    pts = [get(vid, w) for w in widths]
    ys = [float(r["comfort_band_share_pct"]) for r in pts]
    is_lead = vid == lead
    ax.plot(widths, ys, marker="o", color=GREEN if is_lead else "#8aa59c", lw=2.8 if is_lead else 1.4, zorder=3 if is_lead else 2)
    for w, y, r in zip(widths, ys, pts):
        if float(r["corridor_overlap_m2"]) > 1e-8:
            ax.plot(w, y, marker="X", ms=11, color="#8f1d1d", zorder=4)
    ax.text(widths[-1] + 0.02, ys[-1], vid, va="center", fontsize=9.5, fontweight="bold" if is_lead else "normal", color="#2a3d38")
ax.axhline(S_LINE, color=RULE, lw=2, ls="--", label=f"Assumed research threshold s = {S_LINE:.0f}%")
ax.plot([], [], marker="X", ls="none", ms=10, color="#8f1d1d", label="Seat overlaps the corridor")
lead_vals = [float(get(lead, w)["comfort_band_share_pct"]) for w in widths]
verdict = "stays above the line at every tested width" if min(lead_vals) >= S_LINE else "drops below the line at one or more tested widths"
ax.set_title(f"{lead} {verdict} (min {min(lead_vals):.0f}%)", fontweight="bold", color=GREEN)
ax.set_xticks(widths); ax.set_xlim(widths[0] - 0.05, widths[-1] + 0.12); ax.set_ylim(-3, 105)
ax.set_xlabel("Corridor half-width w (m; assumed)"); ax.set_ylabel("Proposed flow-adjacent band share (%)")
ax.legend(frameon=False, fontsize=9, loc="upper left"); ax.grid(alpha=0.15)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "fig_width_sensitivity.png", dpi=160); plt.close(fig)
print("Figures written to", OUT)
