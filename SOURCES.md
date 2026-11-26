# Data and source list

Retrieval / reading date for every entry below: 26 Nov 2026, unless stated.
Status labels follow the Week 11 evidence trace: Supported as stated · Needs narrowing · Contradicted · Not yet established.

## 1. Inputs used by the code

| Input | Where | What it is | Status |
|---|---|---|---|
| Window C, 6.0 × 6.0 m (A3); 4.0–7.0 m (A4 test) | `inputs/config.json` | Researcher assumption, estimated from the map; not surveyed | Not yet established |
| Seat 2.0 × 1.0 m, six placements S1–S6 | `inputs/config.json`, `inputs/variants.csv` | Design input (A3, Week 7 clinic: start with six alternatives) | Design choice |
| Edge proxies: east (base case), north | `inputs/config.json` | Researcher assumption about which edge carries movement | Not yet established |
| Corridor half-width w = 0.75 / 1.00 / 1.50 m | `inputs/config.json` | Researcher assumption (A2 range) | Not yet established |
| c₁ = 0.30 m, c₂ = 1.50 m, s = 60 % | `inputs/config.json` | Researcher assumptions; the sources in section 2 support the direction (stay at the edge, near activity), not these distances | Not yet established |

No map coordinates are loaded. The site is located by OpenStreetMap way 27059126, Harbour Road Garden, Wan Chai (https://www.openstreetmap.org/way/27059126, © OpenStreetMap contributors, ODbL); the ID is cited for location only. The A3 site drawing used Hong Kong Lands Department iB1000 and the 3D Pedestrian Network for context; their download date was not recorded in A3 (recorded here as a gap).

## 2. Literature behind "short stay" (instructor feedback on A3)

"Short stay" in this project means a **stationary activity at the seat**: a person sitting or standing in one place, as opposed to walking through. The term is anchored to the three sources below. None of them gives the distances c₁, c₂ or the share s.

| # | Source | Locator | What it establishes, and under what conditions | How this project differs | Claim as used here | Status |
|---|---|---|---|---|---|---|
| G | Gehl, J. (2011) *Life Between Buildings: Using Public Space*, trans. J. Koch. Washington DC: Island Press. ISBN 978-1-59726-827-1 | pp. 9–12 (three types of outdoor activity; sitting as an optional activity, p. 11); p. 27 (Tivoli Garden: most-used benches line the main path; benches facing activity are used); pp. 147–150 ("Standing", "Zones for staying – the edge effect"); pp. 155–159 ("Sitting": most popular sitting places at the edges of spaces, back protected, view of activity) | Staying concentrates at the edges of spaces, where people can see activity; seats with a view of the main path are used most. Observational, mainly Scandinavian and European squares and streets | Hong Kong pocket garden, subtropical climate; one seat, not a whole space | A seat at the edge of the garden, in view of the movement edge, is where staying is most likely | Needs narrowing: supports direction (edge + view of movement), not the band distances |
| W | Whyte, W. H. (1980) *The Social Life of Small Urban Spaces*. Washington DC: The Conservation Foundation. ISBN 0-89164-057-6 | p. 19 ("What attracts people most … is other people"); pp. 20–21 (people stop and sit in the main pedestrian flow, "People also sit in the mainstream"); p. 28 ("Sitting Space": people sit most where there are places to sit) | Sitting follows the supply of sittable places; people sit and talk in or beside the main flow. Time-lapse observation of New York plazas, 1970s | Garden edge, not a plaza; no counts at Window C | Providing the seat is the precondition for staying; being next to the flow is not a deterrent | Contradicted: the A3 reading that comfort requires distance from the flow does not hold. Kept the corridor as a **clearance** rule for walkers, not as a comfort claim |
| M | Mehta, V. (2006) *Lively Streets: Exploring the Relationship Between Built Environment and Social Behavior*. PhD dissertation, University of Maryland. http://hdl.handle.net/1903/4165 | p. 32, notes 1–3 (definitions of stationary, lingering and social activity) | Operational definition: a stationary activity is a person standing, sitting or lying in one place outdoors for more than 15 seconds. Neighbourhood commercial streets, Boston area | Garden, not a commercial street | Used only to define what to count in the next site observation | Supported as stated (as a definition) |

OpenAlex IDs: not retrieved. The OpenAlex API was not reachable from the workspace used on 26 Nov 2026, and G and W are books without DOIs. To add: search `https://api.openalex.org/works?search=<title>`, check author and year, and paste the W-ID here.

## 3. Figures

| Figure | Made by | Data |
|---|---|---|
| `outputs/fig_window_size.png` (key figure, Object Card) | `a3src/figures.py: window_size_figure` | `outputs/a4_window_size_summary.csv`, `outputs/a4_offset_rule.csv` |
| `outputs/fig_window_plans.png` | `a3src/figures.py: window_plans_figure` | computed from `inputs/` with `a3_workflow.evaluate` |
| `outputs/fig_six_placements.png`, `fig_base_comparison_east.png`, `fig_base_comparison_north.png`, `fig_width_sensitivity.png` | `a3src/figures.py: a3_figures` | `outputs/a3_scenarios.csv`, `outputs/a3_width_sensitivity.csv` |

Re-running `python run_all.py` (or the Colab notebook) redraws every figure from these tables.
