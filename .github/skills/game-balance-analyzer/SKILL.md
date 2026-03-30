---
name: game-balance-analyzer
description: Reviews and adjusts game balance in robot-pokemon — wild encounter rates, trainer difficulty, prize money scaling, and item shop prices. Use when wild Pokemon feel too rare/common, trainers are too easy/hard, or the economy is broken.
---

# game-balance-analyzer

Analyses and tunes game balance: encounter rates, trainer levels, prize money, shop prices, and catch rates.

## Associated Agent
`game-logic.agent.md`

## Instructions

### 1. Input
- **What feels wrong** — "Trainers on Route 3 are too easy", "Zubat encounters too frequent", "money runs out fast"
- **Player's badge count / location** — context for expected difficulty
- **Specific metrics** — levels, HP numbers, prices if known

### 2. Trainer Difficulty Guidelines

| Badge count | Expected trainer level range | Boss (gym leader) level range |
|---|---|---|
| 0 (Route 1-2) | 3–10 | 12–14 (Brock) |
| 1 (Route 3-4, Mt. Moon) | 10–16 | 18–21 (Misty) |
| 2 (Routes 5-6, S.S. Anne) | 16–22 | 24–28 (Lt. Surge) |

Trainer prize money formula: `level * trainer_class_multiplier * 4`
- Youngster/Lass multiplier: ~8
- Hiker/Bug Catcher: ~8
- Gym Leader: ~40

```python
# trainer_data.py — prize_money should scale with highest Pokemon level
prize_money = highest_level * 8   # for route trainers
```

### 3. Wild Encounter Rate

Wild Pokemon are defined per-location as a list. All species in the list have **equal** encounter weight by default. To make a species rarer, add fewer entries (or weight by duplicating common ones):

```python
wild_pokemon=[
    {"species": "ZUBAT",    "min_level": 8, "max_level": 12},  # common
    {"species": "ZUBAT",    "min_level": 8, "max_level": 12},  # common (duplicate = ~2x weight)
    {"species": "GEODUDE",  "min_level": 8, "max_level": 12},  # common
    {"species": "CLEFAIRY", "min_level": 9, "max_level": 11},  # rare (single entry)
],
```

### 4. Shop Prices

Standard price reference (Gen 1 canonical):
```
Potion:        ₽300    Great Ball:    ₽600
Super Potion:  ₽700    Ultra Ball:    ₽1200
Antidote:      ₽100    Revive:        ₽1500
Pokeball:      ₽200    Repel:         ₽350
```

Sell price is always 50% of buy price. Nuggets sell at full ₽5000.

### 5. Catch Rate Guide

Higher catch_rate = easier to catch (0–255):
- Legendary: 3
- Pseudo-legendary (Dragonite line): 45
- Starter: 45
- Rare (Lapras, Chansey): 30–45
- Common (Rattata, Pidgey): 180–255
- Clefairy (rare in-game but catchable): 150

### 6. Output
- Specific numeric changes with before/after comparison
- Reasoning tied to badge progression or economy impact

## Examples

**Input:** "Route 3 trainers are too weak — player wins every battle without strategy."

**Analysis:** Trainers are level 8-10 but player arrives post-Brock at level ~16.

**Fix:**
```python
# Raise Route 3 trainer levels to 12-15
Trainer(id="youngster_ben", ..., pokemon=[TrainerPokemon("SPEAROW", 13)], prize_money=104)
Trainer(id="lass_dana",     ..., pokemon=[TrainerPokemon("JIGGLYPUFF", 13)], prize_money=104)
```

## Dependencies
- `pytemon/data/trainer_data.py` — trainer levels and prize money
- `pytemon/locations.py` — wild encounter tables
- `pytemon/data/pokemon_data.py` — base catch rates
- `pytemon/buildings.py` — `SHOP_CATALOG_BASIC` / `SHOP_CATALOG_ADVANCED` prices

## Error Handling
- **Prize money feels random**: recalculate as `highest_level * class_multiplier * 4`
- **Wild battles feel too frequent**: reduce list length or run `explore_area` encounter probability check in `exploration.py`
- **Gym leader too easy**: ensure leader's ace is 2–3 levels above the highest route trainer in the area
