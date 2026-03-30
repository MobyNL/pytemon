---
name: battle-ai-trainer
description: Improves the AI move selection logic for trainers and gym leaders in robot-pokemon. Use when trainer battles feel too random, when implementing type-aware gym leader AI, or adding smarter switching/stat-move logic.
---

# battle-ai-trainer

Upgrades trainer AI from random move selection to type-aware, strategic behaviour — especially for gym leaders.

## Associated Agent
`battle-system.agent.md`

## Instructions

### 1. Current AI (Random)

All trainers currently pick moves at random:
```python
# engine/battle_engine.py
chosen_move = random.choice(available_moves)
```

### 2. Type-Aware AI

Replace random selection with a scoring function:

```python
def ai_select_move(trainer_pokemon: dict, player_pokemon: dict, available_moves: list) -> dict:
    """Select the best move based on type effectiveness."""
    from pytemon.data.type_chart import TYPE_CHART

    def move_score(move: dict) -> float:
        if move.get("power", 0) == 0:
            return 0.5   # status moves are lower priority
        score = move["power"]
        for def_type in player_pokemon.get("types", []):
            score *= TYPE_CHART.get(move["type"], {}).get(def_type, 1.0)
        # STAB bonus
        if move["type"] in trainer_pokemon.get("types", []):
            score *= 1.5
        return score

    return max(available_moves, key=move_score)
```

### 3. Gym Leader Profiles

Gym leaders should always prefer their specialty type:

```python
GYM_LEADER_AI = {
    "brock":  {"prefer_types": ["Rock", "Ground"], "strategy": "tank"},
    "misty":  {"prefer_types": ["Water"],           "strategy": "special"},
    "surge":  {"prefer_types": ["Electric"],        "strategy": "speed"},
}

def gym_leader_select_move(leader_id: str, trainer_pokemon: dict, player_pokemon: dict,
                            available_moves: list) -> dict:
    profile = GYM_LEADER_AI.get(leader_id, {})
    preferred = [m for m in available_moves if m["type"] in profile.get("prefer_types", [])]
    candidates = preferred if preferred else available_moves
    return ai_select_move(trainer_pokemon, player_pokemon, candidates)
```

### 4. When to Apply Each AI Level

| Trainer class | AI level |
|---|---|
| Youngster, Lass, Bug Catcher | Random (current) |
| Hiker, Swimmer, Sailor | Type-aware (`ai_select_move`) |
| Gym Trainer | Type-aware, prefer gym type |
| Gym Leader | `gym_leader_select_move` |
| Rival | Type-aware + prefers coverage moves |

### 5. Wiring Into Battle Engine

```python
# engine/battle_engine.py — in resolve_trainer_turn()
if self.trainer.trainer_class == "Gym Leader":
    chosen_move = gym_leader_select_move(
        self.trainer.id, self.trainer_pokemon, self.player_pokemon, available_moves
    )
elif self.trainer.trainer_class in ("Youngster", "Lass", "Bug Catcher"):
    chosen_move = random.choice(available_moves)
else:
    chosen_move = ai_select_move(self.trainer_pokemon, self.player_pokemon, available_moves)
```

### 6. Output
- `ai_select_move` function in `engine/battle_engine.py`
- `gym_leader_select_move` function with profiles
- Updated `resolve_trainer_turn` dispatch

## Dependencies
- `pytemon/engine/battle_engine.py` — `BattleState`, turn resolution
- `pytemon/data/type_chart.py` — `TYPE_CHART`
- `pytemon/data/trainer_data.py` — `Trainer.trainer_class`

## Error Handling
- **All scores equal**: AI falls back to `random.choice` when all moves score the same — this is correct
- **No available moves**: if all PP are zero, use Struggle (power 50, Normal type, no effect)
- **AI too predictable**: add a 20% chance to deviate from optimal for non-leader trainers
