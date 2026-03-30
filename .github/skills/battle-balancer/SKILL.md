---
name: battle-balancer
description: Tunes battle balance in robot-pokemon — catch rates, flee probabilities, wild Pokemon encounter levels, and status condition durations. Use when catching feels too easy or hard, fleeing never works, or status effects are too powerful/weak.
---

# battle-balancer

Adjusts battle balance parameters: catch rates, flee odds, encounter levels, and status durations.

## Associated Agent
`battle-system.agent.md`

## Instructions

### 1. Catch Rate Formula (Gen 1 approximation)

```python
# battle/battle_actions.py — attempt_catch()
def attempt_catch(pokemon: dict, ball: str, gs: GameState) -> tuple[bool, int, list[str]]:
    catch_rate = POKEMON[pokemon["species"]]["catch_rate"]  # 0-255
    hp_ratio = pokemon["hp"] / pokemon["max_hp"]

    # Ball multiplier
    ball_multipliers = {
        "Pokeball": 1, "Great Ball": 1.5, "Ultra Ball": 2, "Master Ball": 255
    }
    ball_mult = ball_multipliers.get(ball, 1)

    # Status bonus
    status_bonus = 1.5 if pokemon.get("status") in ("sleep", "freeze") else (
                   1.2 if pokemon.get("status") in ("paralysis", "poison", "burn") else 1.0)

    # Catch value (higher = easier)
    catch_value = (catch_rate * ball_mult * status_bonus) / (3 * hp_ratio)
    catch_value = min(catch_value, 255)

    # 3 shake checks (must pass all 3)
    shakes = 0
    caught = True
    for _ in range(3):
        if random.randint(0, 255) < catch_value:
            shakes += 1
        else:
            caught = False
            break

    return caught, shakes, []
```

### 2. Tuning Catch Difficulty

| Desired feel | Adjustment |
|---|---|
| Too hard | Increase `catch_rate` on species, or reduce required shakes to 2 |
| Too easy | Decrease `catch_rate`, or require 3 successful shake checks |
| Ball feels useless | Increase its multiplier in `ball_multipliers` |
| Status bonus too mild | Increase status bonus values |

**Canonical catch_rate values for reference:**
- Easy (Magikarp, Rattata): 255
- Medium (Pikachu, starter post-game): 45-190
- Hard (Lapras, Chansey): 30-45
- Legendary: 3

### 3. Flee Probability

```python
# battle/battle_actions.py — attempt_flee()
def attempt_flee(player_pokemon: dict, wild_pokemon: dict) -> bool:
    player_speed = player_pokemon.get("speed", 50)
    wild_speed = wild_pokemon.get("speed", 50)

    if player_speed > wild_speed:
        return True   # always flee if faster

    # Otherwise: 50% base + speed advantage
    odds = 50 + (player_speed - wild_speed) * 2
    odds = max(10, min(90, odds))   # clamp 10-90%
    return random.randint(1, 100) <= odds
```

Tuning: increase base odds (50) if fleeing feels too hard; decrease if it feels trivial.

### 4. Status Condition Durations

```python
# engine/battle_engine.py — check_status_at_turn_start()
if status == "sleep":
    turns_asleep = pokemon.get("sleep_turns", 0) + 1
    if turns_asleep >= random.randint(1, 7):   # wake up after 1-7 turns
        pokemon["status"] = None
        pokemon.pop("sleep_turns", None)
    else:
        pokemon["sleep_turns"] = turns_asleep
        cannot_act = True
```

| Status | Duration / Damage | Tuning hint |
|---|---|---|
| Sleep | 1-7 turns (random each) | Reduce max turns if OP |
| Poison | 1/16 max HP per turn | Increase to 1/8 for more pressure |
| Burn | 1/8 max HP per turn | Already higher than poison |
| Paralysis | 25% chance to lose turn | Increase % if it feels ignorable |
| Freeze | Until thawed (random 20%/turn) | Increase thaw% if frustrating |

### 5. Output
- Changed constants/formulas with before/after comparison
- Explanation of expected player experience impact

## Dependencies
- `pytemon/battle/battle_actions.py` — `attempt_catch`, `attempt_flee`
- `pytemon/engine/battle_engine.py` — status duration and end-of-turn damage
- `pytemon/data/pokemon_data.py` — `catch_rate` per species

## Error Handling
- **Master Ball catching wrong**: ensure its multiplier is 255+ (bypasses all shake checks)
- **Flee never succeeds**: check speed is being read from `pokemon["speed"]`, not `base_stats["speed"]` (they may differ if not computed)
- **Status damage kills in one turn**: add `max(0, hp - damage)` flooring at 0
