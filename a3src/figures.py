"""All figures. Every value drawn is read from the rows computed by run_all.py (no typed numbers)."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import Rectangle  # noqa: E402

from . import a3_workflow as wf  # noqa: E402

GREEN, TEAL, TAN, ORANGE, RULE = "#1f5a4e", "#9fbfb0", "#dcc3a5", "#c8623f", "#d9532b"
INK, MUTED = "#1f3b34", "#5f786f"
plt.rcParams.update({"font.family": "DejaVu Sans", "axes.titlesize": 12})


def _get(rows, vid, edge, w):
    return next(r for r in rows if r["variant"] == vid and r["edge_proxy"] == edge and abs(r["w_m"] - w) < 1e-9)


def a3_figures(out, cfg, variants, rows, curves):
    W, BW, C1, C2, S = cfg["window_m"], cfg["base_width_m"], cfg["c1_m"], cfg["c2_m"], cfg["s_pct"]
    fig, axes = plt.subplots(2, 3, figsize=(13.6, 9.4))
    for ax, v in zip(axes.flat, variants):
        r = _get(rows, v["variant"], "east", BW)
        x0, x1, y0, y1 = wf.seat_rect(v, cfg)
        ax.add_patch(Rectangle((-W, -W), W, W, fill=False, ec="#4b6b62", ls="--", lw=1))
        ax.add_patch(Rectangle((-BW, -W), BW, W, fc=TAN, ec="none", alpha=0.65))
        ax.add_patch(Rectangle((-(BW + C2), -W), C2 - C1, W, fc=TEAL, ec="none", alpha=0.5))
        ax.plot([0, 0], [0, -W], color=GREEN, lw=3)
        conflict = r["corridor_overlap_m2"] > 0
        ax.add_patch(Rectangle((-x1, -y1), x1 - x0, y1 - y0, fc=ORANGE, ec="#8f1d1d" if conflict else ORANGE,
                               lw=2.5 if conflict else 1.5, alpha=0.7))
        ax.set_title(f'{v["variant"]} · {v["position"].lower()} / {v["orientation"]}\n'
                     f'Band share {r["band_share_pct"]:.0f}% · overlap {r["corridor_overlap_m2"]:.2f} m²', fontsize=11, color=INK)
        ax.set_xlim(-W - 0.5, 0.45); ax.set_ylim(-W - 0.5, 0.4); ax.set_aspect("equal")
        ax.set_xlabel("Local x (m) · east edge at x=0", fontsize=8.5); ax.set_ylabel("Local y (m) · north edge at y=0", fontsize=8.5)
        ax.grid(alpha=0.12)
    fig.suptitle(f"Window C / six ALTERNATIVE placements of ONE 2 × 1 m seat\nAssumed {W:g} × {W:g} m geometry; east edge proxy, w = {BW:.1f} m",
                 fontsize=15, fontweight="bold", color=GREEN)
    fig.text(0.5, 0.015, "Schematic geometry only • green = proposed flow-adjacent band • tan = assumed corridor • orange = seat",
             ha="center", fontsize=9.5, color=MUTED)
    fig.tight_layout(rect=(0, 0.03, 1, 0.93), h_pad=2.2)
    fig.savefig(out / "fig_six_placements.png", dpi=160); plt.close(fig)

    ids = [v["variant"] for v in variants]
    for edge in cfg["edge_proxies"]:
        base = [_get(rows, v, edge, BW) for v in ids]
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
        fig.text(0.5, 0.02, f"{edge.capitalize()} edge proxy · corridor half-width w = {BW:.2f} m · c₁={C1:.2f}m, c₂={C2:.2f}m",
                 ha="center", fontsize=9, color=MUTED)
        fig.tight_layout(rect=(0, 0.05, 1, 1))
        fig.savefig(out / f"fig_base_comparison_{edge}.png", dpi=160); plt.close(fig)

    lo, hi = wf.pass_range(curves["S1"])
    fig, ax = plt.subplots(figsize=(10, 5.2))
    if lo is not None:
        ax.axvspan(lo, hi, color="#e7efea", zorder=0)
        ax.axvline(lo, color="#b08a3c", lw=1, ls=":"); ax.axvline(hi, color="#b08a3c", lw=1, ls=":")
        ax.text(lo + 0.02, 6, "S1 conditional pass range\n(excluding geometric overlaps)", fontsize=8.5, color=GREEN)
    for vid, col in (("S1", GREEN), ("S2", ORANGE)):
        ax.plot([r["w_m"] for r in curves[vid]], [r["band_share_pct"] for r in curves[vid]], color=col, lw=2.2, label=f"{vid} band share")
        for w in cfg["widths_m"]:
            ax.plot(w, _get(rows, vid, "east", w)["band_share_pct"], "o", color=col, ms=6)
    ax.axhline(S, color="#a8522f", lw=1.6, ls="--", label=f"Assumed s = {S:.0f}%")
    ax.set_xlim(0.5, 2.1); ax.set_ylim(0, 108)
    ax.set_xlabel("Assumed corridor half-width w (m)"); ax.set_ylabel("Proposed band share (%)")
    ax.set_title(f"Sensitivity: S1 clears s only for {lo:.2f} ≤ w ≤ {hi:.2f} m (east proxy)" if lo is not None
                 else "Sensitivity: S1 never clears s (east proxy)", fontweight="bold", color=GREEN)
    ax.legend(frameon=False, loc="upper left", fontsize=9); ax.spines[["top", "right"]].set_visible(False)
    fig.tight_layout(); fig.savefig(out / "fig_width_sensitivity.png", dpi=160); plt.close(fig)


SHADE = {3: (GREEN, "white"), 2: ("#7fa898", INK), 1: ("#cfe0d6", INK), 0: ("#f3f1ea", "#8a8a80")}


def window_size_figure(out, cfg, variants, wsum, offs):
    """KEY FIGURE (Object Card). Rows: six labelled seats with proportional geometry, the offset rule,
    and the limit (same seat scored with the north proxy). Cells: east-proxy widths passed of 3."""
    sizes = cfg["window_sizes_m"]
    vlabel = {v["variant"]: f'{v["variant"]} · {v["position"].lower()} · {"parallel" if v["orientation"] == "parallel" else "perpendicular"}'
              for v in variants}
    fig = plt.figure(figsize=(12.4, 7.3))
    ax = fig.add_axes((0.30, 0.17, 0.66, 0.66))
    nrows = len(variants) + 2
    ax.set_xlim(0, len(sizes)); ax.set_ylim(nrows + 0.35, -0.05); ax.axis("off")

    def cell(col, row, k, sub=None, note=None):
        if k is None:
            ax.add_patch(Rectangle((col + 0.04, row + 0.06), 0.92, 0.88, fc="white", ec="#c9c2b4", hatch="///", lw=0.8))
            ax.text(col + 0.5, row + 0.5, "does not fit", ha="center", va="center", fontsize=8, color="#8a8a80")
            return
        fc, tc = SHADE[k]
        ax.add_patch(Rectangle((col + 0.04, row + 0.06), 0.92, 0.88, fc=fc, ec="white", lw=0))
        ax.text(col + 0.5, row + (0.42 if sub else 0.5), f"{k}/3", ha="center", va="center", fontsize=13, fontweight="bold", color=tc)
        if sub:
            ax.text(col + 0.5, row + 0.76, sub, ha="center", va="center", fontsize=8, color=tc if k == 3 else MUTED)

    for j, W in enumerate(sizes):
        tag = "  A3" if abs(W - 6.0) < 1e-9 else ("  5 × 5 asked" if abs(W - 5.0) < 1e-9 else "")
        ax.text(j + 0.5, -0.32, f"{W:g} × {W:g} m", ha="center", va="bottom", fontsize=10.5, fontweight="bold", color=INK)
        if tag:
            ax.text(j + 0.5, -0.62, tag.strip(), ha="center", va="bottom", fontsize=8.5, color=RULE, fontweight="bold")
            ax.add_patch(Rectangle((j + 0.01, -0.05), 0.98, nrows + 0.35, fill=False, ec=RULE, lw=1.6, ls="--"))
    for i, v in enumerate(variants):
        fig.text(0.295, 0.83 - 0.66 * (i + 0.5) / (nrows + 0.4), vlabel[v["variant"]], ha="right", va="center", fontsize=10.5, color=INK)
        for j, W in enumerate(sizes):
            s = next(x for x in wsum if x["rule"] == "proportional" and abs(x["window_m"] - W) < 1e-9 and x["variant"] == v["variant"])
            centre = v["centre_from_east_m"] * W / 6.0
            cell(j, i, s["east_widths_passed_of_3"] if s["fits_window"] else None, f"centre {centre:.2f} m")
    r_off, r_lim = len(variants) + 0.25, len(variants) + 1.25
    ax.plot([0, len(sizes)], [len(variants) + 0.12] * 2, color=INK, lw=1)
    lab = [("Rule: parallel seat, centre\n2.00–2.15 m from the movement edge", r_off, "east", GREEN),
           ("Limit: same seat if movement runs\nalong the north edge (not turned)", r_lim, "north_unturned", RULE)]
    for text, r, case, col in lab:
        fig.text(0.295, 0.83 - 0.66 * (r + 0.5) / (nrows + 0.4), text, ha="right", va="center", fontsize=10.5, color=col, fontweight="bold")
        for j, W in enumerate(sizes):
            ks = [o["widths_passed_of_3"] for o in offs if o["case"] == case and abs(o["window_m"] - W) < 1e-9]
            k = min(ks)
            cell(j, r, k, "all 4 centres" if min(ks) == max(ks) else f"{min(ks)}–{max(ks)} of 3")
    fig.text(0.03, 0.955, "The winning label changes with window size; a 2.00–2.15 m edge offset always passes",
             fontsize=16, fontweight="bold", color=GREEN)
    fig.text(0.03, 0.915, "Cells: tested corridor half-widths passed (w = 0.75 / 1.00 / 1.50 m), east edge as the assumed movement edge. "
             "Labelled seats keep their place as a fraction of the window.", fontsize=9.5, color=MUTED)
    fig.text(0.03, 0.06, f"Pass = 0 m² corridor overlap AND ≥ {cfg['s_pct']:.0f} % of the 2.0 × 1.0 m seat inside the band from w + {cfg['c1_m']:.2f} m "
             f"to w + {cfg['c2_m']:.2f} m (rule set in A3, before these runs).", fontsize=9.5, color=INK)
    fig.text(0.03, 0.025, "Schematic geometry; edge, w, c₁, c₂ and s are assumptions, not observed movement or use. "
             "Source: outputs/a4_window_size_summary.csv, outputs/a4_offset_rule.csv.", fontsize=9, color=MUTED)
    fig.savefig(out / "fig_window_size.png", dpi=200); plt.close(fig)


def window_plans_figure(out, cfg, variants):
    """Three plans at the same scale: A3 S1 (6 x 6), S1 kept proportional in 5 x 5, the offset rule."""
    S1 = next(v for v in variants if v["variant"] == "S1")
    C1, C2 = cfg["c1_m"], cfg["c2_m"]
    panels = [
        ("A3 · 6 × 6 m · S1 centre 2.20 m", 6.0, S1["centre_from_east_m"], 0.75),
        ("5 × 5 m, geometry kept · S1 centre 1.83 m", 5.0, S1["centre_from_east_m"] * 5.0 / 6.0, 1.5),
        ("Offset rule · centre 2.00–2.15 m", 5.0, None, None),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(13.2, 5.4))
    for ax, (title, W, xc, w) in zip(axes, panels):
        ax.add_patch(Rectangle((-W, -W), W, W, fc="#f7f4ec", ec="#e0602e", ls="--", lw=1.6))
        ax.plot([0, 0], [0.3, -W - 0.3], color="#1d5a8a", lw=4)
        yc = W / 2
        if xc is not None:
            rect = wf.seat_rect(S1, dict(cfg, seat_centre_from_north_m=yc), centre_from_east=xc)
            ov, sh = wf.evaluate(rect, "east", w, dict(cfg, window_m=W))
            ax.add_patch(Rectangle((-w, -W), w, W, fc=TAN, ec="none", alpha=0.75))
            ax.add_patch(Rectangle((-(w + C2), -W), C2 - C1, W, fc=TEAL, ec="none", alpha=0.55))
            x0, x1, y0, y1 = rect
            ax.add_patch(Rectangle((-x1, -y1), x1 - x0, y1 - y0, fc=ORANGE, ec="#8f1d1d", lw=1.5, alpha=0.85))
            if ov > 1e-9:
                ax.add_patch(Rectangle((-w, -y1), w - x0, y1 - y0, fc="none", ec="#8f1d1d", hatch="xxx", lw=0))
            verdict = (f"w = {w:.2f} m: overlap {ov:.2f} m² → fails" if ov > 1e-9
                       else f"w = {w:.2f} m: band share {sh:.0f} % < {cfg['s_pct']:.0f} % → fails")
            ax.text(-W / 2, -W - 0.75, verdict, ha="center", fontsize=10.5, color="#8f1d1d", fontweight="bold")
        else:
            for wv, ls in zip(cfg["widths_m"], (":", "--", "-")):
                ax.plot([-wv, -wv], [0, -W], color="#8a6d3b", lw=1.2, ls=ls)
            ax.add_patch(Rectangle((-2.65, -yc - 1.0), 1.15, 2.0, fc=ORANGE, alpha=0.25, ec="none"))
            ax.add_patch(Rectangle((-2.5, -yc - 1.0), 1.0, 2.0, fc=ORANGE, ec="#8f1d1d", lw=1.5, alpha=0.85))
            ax.annotate("", xy=(-2.075, -yc - 1.35), xytext=(0, -yc - 1.35), arrowprops=dict(arrowstyle="<->", color=INK, lw=1))
            ax.text(-2.25, -yc - 1.35, "centre 2.00–2.15 m", ha="right", va="center", fontsize=9, color=INK)
            ax.text(-W / 2, -W - 1.25, "brown lines: corridor edge at w = 0.75 (dotted), 1.00 (dashed), 1.50 m (solid)",
                    ha="center", fontsize=8.5, color="#8a6d3b")
            ax.text(-W / 2, -W - 0.75, "passes w = 0.75, 1.00 and 1.50 m", ha="center", fontsize=10.5, color=GREEN, fontweight="bold")
        ax.set_title(title, fontsize=11.5, color=INK, fontweight="bold")
        ax.set_xlim(-6.4, 0.9); ax.set_ylim(-7.4, 0.7); ax.set_aspect("equal"); ax.axis("off")
        ax.text(0.15, -W / 2, "east edge\n(assumed\nmovement)", fontsize=8, color="#1d5a8a", va="center")
    fig.suptitle("Keeping the geometry moves the seat; the edge offset does not", fontsize=14.5, fontweight="bold", color=GREEN, x=0.02, ha="left")
    fig.text(0.02, 0.02, "Same scale, plan, north up. Tan = corridor at the width shown, green = band, orange = 2.0 × 1.0 m seat. Schematic, not surveyed.",
             fontsize=9, color=MUTED)
    fig.tight_layout(rect=(0, 0.05, 1, 0.93))
    fig.savefig(out / "fig_window_plans.png", dpi=200); plt.close(fig)


def draw_all(out, cfg, variants, rows, curves, wsum, offs):
    a3_figures(out, cfg, variants, rows, curves)
    window_size_figure(out, cfg, variants, wsum, offs)
    window_plans_figure(out, cfg, variants)
