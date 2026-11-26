# Data dictionary

Units: metres (m), square metres (m²), percent (%). Frame: local-metre schematic, x = distance inward from the east edge, y = distance south from the north edge. No map coordinates.

## Inputs

### `inputs/config.json`

| Field | Value (default) | Meaning |
|---|---|---|
| `window_m` | 6.0 | Side of the square Window C used in A3 |
| `seat_long_m`, `seat_short_m` | 2.0, 1.0 | Seat footprint |
| `seat_centre_from_north_m` | 3.0 | Seat centre distance from the north edge (A3) |
| `widths_m` | 0.75, 1.0, 1.5 | Tested corridor half-widths w |
| `base_width_m` | 1.0 | w used for the base case |
| `c1_m`, `c2_m` | 0.30, 1.50 | Band starts at w + c₁ and ends at w + c₂ from the movement edge |
| `s_pct` | 60 | Minimum share of the seat inside the band to pass |
| `edge_proxies` | east, north | Edge treated as the movement edge |
| `sweep_step_m` | 0.05 | Step of the A3 position sweep |
| `window_sizes_m` | 4.0 … 7.0 (0.5 steps) | A4 window-size test |
| `window_rules` | proportional, fixed_offset | How the six placements follow the window size (see `a3src/a4_window_size.py`) |
| `offset_rule_centres_m` | 2.00, 2.05, 2.10, 2.15 | Seat-centre distances tested for the offset rule |

### `inputs/variants.csv`

| Column | Meaning |
|---|---|
| `variant` | S1–S6 |
| `position` | Near / Centre / Far |
| `orientation` | parallel (long side N–S, along the east edge) / perpendicular (long side E–W) |
| `long_axis` | N-S or E-W |
| `centre_from_east_m` | Seat centre distance from the east edge in the 6 × 6 m window: 2.2 / 3.2 / 4.3 |

## Outputs

| File | Rows | Columns |
|---|---|---|
| `a3_scenarios.csv` | 36 | variant, position, orientation, edge_proxy, w_m, corridor_overlap_m2 (seat area inside the corridor 0–w), band_share_pct (% of seat area inside the band w+c₁ to w+c₂), seat_area_m2, inside_window, geometry (clear / conflict), passes_rule |
| `a3_variant_summary.csv` | 6 | per variant and edge: min / max band share, max overlap, passes all widths; passes_all_36_conditions |
| `a3_position_sweep.csv` | 61 | parallel seat, east edge, centre 1.50–4.50 m in 0.05 m steps: share_min_pct, max_overlap_m2, passes_all_widths |
| `a3_width_sensitivity.csv` | 322 | S1 and S2, east edge, w from 0.50 to 2.10 m in 0.01 m steps |
| `a4_window_size.csv` | 504 | rule, window_m, variant, orientation, centre_from_east_m, centre_from_north_m, edge_proxy, w_m, fits_window, corridor_overlap_m2, band_share_pct (blank if the seat does not fit), passes_rule |
| `a4_window_size_summary.csv` | 84 | rule, window_m, variant, fits_window, east_base_share_pct, east_widths_passed_of_3, all_conditions_passed_of_6 |
| `a4_offset_rule.csv` | 84 | case (east / north_turned / north_unturned), window_m, centre_from_edge_m, edge_proxy, fits_window, share_min_pct, max_overlap_m2, widths_passed_of_3 |
| `a3_checks.csv` | 39 | n, check, expected (written by hand before running), observed, status |
| `run_record.txt` | – | date, environment, results, RESULT line |
| `versions.txt` | – | python, numpy, matplotlib, platform of the run that wrote `outputs/` |

## Rule (set in A3, before any run)

A scenario passes if `corridor_overlap_m2 = 0` **and** `band_share_pct ≥ s`. A seat that does not fit inside the window is reported as "does not fit" and does not pass.
