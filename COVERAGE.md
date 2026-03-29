# Unit Test Coverage Report

**Date:** 2026-03-29  
**Overall:** 85% (6,942 / 8,163 statements) — 1,951 tests passing

---

## Files in Good Shape (≥ 90%)

| File | Stmts | Miss | Cover |
|---|---|---|---|
| `pytemon/__init__.py` | 3 | 0 | 100% |
| `pytemon/battle/__init__.py` | 0 | 0 | 100% |
| `pytemon/data/__init__.py` | 5 | 0 | 100% |
| `pytemon/data/move_data.py` | 38 | 0 | 100% |
| `pytemon/data/trainer_data.py` | 46 | 0 | 100% |
| `pytemon/data/type_chart.py` | 8 | 0 | 100% |
| `pytemon/engine/__init__.py` | 2 | 0 | 100% |
| `pytemon/locations.py` | 31 | 0 | 100% |
| `pytemon/texts/__init__.py` | 0 | 0 | 100% |
| `pytemon/texts/en/__init__.py` | 0 | 0 | 100% |
| `pytemon/ui/__init__.py` | 0 | 0 | 100% |
| `pytemon/ui/game_flow_mixin.py` | 233 | 4 | 98% |
| `pytemon/stats.py` | 113 | 2 | 98% |
| `pytemon/data/pokemon_data.py` | 94 | 3 | 97% |
| `pytemon/gym_system.py` | 216 | 6 | 97% |
| `pytemon/hm_tm_system.py` | 220 | 6 | 97% |
| `pytemon/models.py` | 73 | 2 | 97% |
| `pytemon/evolution.py` | 78 | 3 | 96% |
| `pytemon/displays.py` | 528 | 24 | 95% |
| `pytemon/game_state.py` | 178 | 9 | 95% |
| `pytemon/pc_system.py` | 192 | 9 | 95% |
| `pytemon/pokedex.py` | 214 | 16 | 93% |
| `pytemon/cheat_commands.py` | 511 | 45 | 91% |
| `pytemon/battle/battle_engine.py` | 610 | 56 | 91% |
| `pytemon/battle/battle_ui.py` | 185 | 19 | 90% |
| `pytemon/fishing.py` | 77 | 8 | 90% |
| `pytemon/ui/formatters.py` | 42 | 4 | 90% |
| `pytemon/ui/menus.py` | 296 | 31 | 90% |

---

## Files Needing Attention (< 90%)

| File | Stmts | Miss | Cover | Missing Lines |
|---|---|---|---|---|
| `pytemon/ui/battle_mixin.py` | 542 | 65 | 88% | 145-150, 156, 159, 166, 171, 342, 347, 349, 371-373, 405-458, 470-471, 476, 478-479, 481, 483-484, 508, 808-810, 812-814, 858-859 |
| `pytemon/items.py` | 334 | 48 | 86% | 381, 410-414, 429-430, 436-437, 460, 467-468, 485-489, 511, 530, 644-645, 652-666, 677, 680, 685-686, 692-693, 717-720, 761-762, 777-778 |
| `pytemon/ui/building_mixin.py` | 407 | 56 | 86% | 168, 185-188, 271-340 |
| `pytemon/battle/battle_actions.py` | 657 | 155 | 76% | 109-110, 122, 315-316, 333-334, 341, 343-344, 348, 350-351, 391, 467, 518-519, 587-588, 645, 677-803, 882, 945-975, 987-989, 995-998, 1002-1003, 1009-1017, 1219-1220, 1283-1284 |
| `pytemon/buildings.py` | 959 | 217 | 77% | 134-145, 166-173, 187, 190-214, 366, 553-570, 994-1010, 1022-1025, 1029-1032, 1138, 1177, 1270-1273, 1413-1423, 1447-1448, 1459-1464, 1523-1530, 1543-1574, 1585-1615, 1628-1657, 1670-1707, 1722-1776 |
| `pytemon/exploration.py` | 532 | 128 | 76% | 116-117, 128-129, 175, 283, 287-288, 310-312, 377, 388, 392-393, 411, 566, 568, 570, 572, 574, 580, 612-614, 634, 647-649, 653-655, 663, 681, 686-710, 761-835, 838-890, 919, 927, 936-958 |
| `pytemon/ui/panel_mixin.py` | 612 | 178 | 71% | 26-66, 71-89, 115-116, 120-123, 129-130, 138-149, 163-164, 191-192, 258-259, 305-306, 338-339, 352-353, 357-361, 365-445, 465-466, 490-491, 502-503, 534-535, 558-559, 588, 599-600, 617-618, 623-624, 628-629, 633-634, 659-664, 679-680, 686-687, 698-699, 703-704, 715-716, 721-722, 783-784, 799-800, 820-821, 824-825, 843-844, 864-865, 880-881, 910-911, 914-915, 919-920, 925-926, 941-947 |

---

## Text Constants (0% — Intentionally Untested)

These modules contain only string constants used for terminal output. They have no logic to test.

| File | Stmts |
|---|---|
| `pytemon/texts/en/battle_ui.py` | 12 |
| `pytemon/texts/en/buildings.py` | 23 |
| `pytemon/texts/en/cheat_commands.py` | 15 |
| `pytemon/texts/en/displays.py` | 7 |
| `pytemon/texts/en/evolution.py` | 2 |
| `pytemon/texts/en/exploration.py` | 17 |
| `pytemon/texts/en/fishing.py` | 6 |
| `pytemon/texts/en/gym_system.py` | 11 |
| `pytemon/texts/en/items.py` | 11 |
| `pytemon/texts/en/menus.py` | 9 |
| `pytemon/texts/en/pc_system.py` | 7 |
| `pytemon/texts/en/pokedex.py` | 7 |

---

## Notes

- **`ui/panel_mixin.py` (71%)** — Gap is expected. This module is pure Textual widget manipulation that requires a running app to exercise fully.
- **`battle_actions.py` (76%)** — Lines 677–803 are a large uncovered block. Worth targeting with new tests.
- **`buildings.py` (77%)** — Mostly complex building-entry flows (lines 1523–1776). Good candidate for new tests.
- **`exploration.py` (76%)** — Lines 761–890 (a large uncovered section) are the main gap.
- **Text constants (0%)** — These are intentionally excluded from coverage goals; they contain no logic.
