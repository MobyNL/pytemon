---
name: battle-flow-designer
description: Designs and implements battle flow sequences for robot-pokemon — wild encounters, trainer battles, gym battles, and post-battle events (evolution, EXP, catch). Use when adding a new battle entry point, a new battle phase, or a post-battle sequence.
---

# battle-flow-designer

Implements complete battle flows: encounter triggers, turn sequencing, victory/defeat handling, and post-battle events.

## Associated Agent
`battle-system.agent.md`

## Instructions

### 1. Battle Entry Points

| Battle type | Entry method | File |
|---|---|---|
| Wild encounter | `BattleMixin.start_wild_battle(species, level, output)` | `ui/battle_mixin.py` |
| Trainer battle | `BattleMixin.start_trainer_battle(trainer_id, output)` | `ui/battle_mixin.py` |
| Gym challenge | `BattleMixin.start_gym_battle(gym_leader_id, output)` | `ui/battle_mixin.py` |

All entry points:
1. Construct a `BattleState` in `engine/battle_engine.py`
2. Set `self.pending_command = "battle"`
3. Display the battle intro via `battle_ui.py`
4. Hand control to `handle_pending_command`

### 2. Turn Sequence

```
Player input → handle_pending_command("battle", ...) 
    → dispatch on sub-command: "attack", "catch", "flee", "switch", "item"
    → execute player action (battle_actions.py)
    → execute enemy AI move (battle_engine.py)
    → apply end-of-turn effects (status damage, weather)
    → check faint conditions
    → if battle continues → re-display battle UI and await next input
    → if battle over → go to post-battle flow
```

### 3. Post-Battle Flow

**Wild battle win (Pokemon fleeing or fainting):**
```python
from pytemon.texts.en import battle_ui as T
from pytemon.ui.formatters import write_lines_fmt

def handle_wild_battle_end(self, result: str, output: Any) -> None:
    write_lines_fmt(output, T.WILD_FAINTED, name=enemy_name)  # "Wild {name} fainted!"
    # EXP gain
    exp_gained = calculate_exp(enemy_level, enemy_base_exp)
    grant_exp(self.game_state, active_pokemon, exp_gained, output)
    # Check level-up and evolution
    self._check_level_up_and_evolution(active_pokemon, output)
    # Clear battle state
    self.game_state.battle_state = None
    self.pending_command = None
```

**Catch:**
```python
from pytemon.texts.en import battle_ui as T
from pytemon.ui.formatters import write_lines_fmt

def handle_catch_success(self, caught_pokemon: dict, output: Any) -> None:
    write_lines_fmt(output, T.POKEMON_CAUGHT, name=caught_pokemon["name"])  # "{name} was caught!"
    # Add to party (if room) or send to PC
    if len(party) < 6:
        party.append(caught_pokemon)
    else:
        pc_deposit(self.game_state, caught_pokemon)
        write_lines_fmt(output, T.POKEMON_SENT_TO_PC, name=caught_pokemon["name"])  # "{name} sent to Bill's PC."
    self.game_state.battle_state = None
    self.pending_command = None
```

**Trainer battle win:**
```python
from pytemon.gym_system import award_badge
from pytemon.texts.en import battle_ui as T
from pytemon.ui.formatters import write_lines_fmt

def handle_trainer_battle_win(self, trainer: Trainer, output: Any) -> None:
    prize = trainer.prize_money
    self.game_state.game_data["money"] += prize
    write_lines_fmt(output, T.PRIZE_MONEY_WON, prize=prize)  # "You won ₽{prize}!"
    if trainer.badge_reward:
        award_badge(self.game_state, trainer.badge_id, output)
    self.game_state.battle_state = None
    self.pending_command = None
```

### 4. Player Defeat Flow

```python
from pytemon.texts.en import battle_ui as T
from pytemon.ui.formatters import write_lines

def handle_player_defeat(self, output: Any) -> None:
    write_lines(output, T.PLAYER_DEFEAT)   # "All your Pokémon fainted!" / "You blacked out..."
    # Halve money
    self.game_state.game_data["money"] //= 2
    # Heal party and warp to last Pokemon Center
    heal_all_pokemon(self.game_state, output)
    self.game_state.current_location = self.game_state.game_data.get(
        "last_pokemon_center", "Pallet Town"
    )
    self.game_state.battle_state = None
    self.pending_command = None
```

### 5. Adding a New Battle Entry Point

1. Create the `BattleState` with the combatants
2. Set `self.pending_command = "battle"` and `self.pending_command_data = {"phase": "start"}`
3. Call `show_battle_intro(output)` from `battle_ui.py`
4. Add a handler branch in `BattleMixin.handle_battle_command` for any new sub-phase

## Dependencies
- `pytemon/ui/battle_mixin.py` — battle entry, sub-command dispatch
- `pytemon/engine/battle_engine.py` — `BattleState`, turn resolution
- `pytemon/battle/battle_actions.py` — individual action implementations
- `pytemon/battle/battle_ui.py` — display helpers
- `pytemon/ui/game_flow_mixin.py` — `handle_pending_command`

## Error Handling
- **Battle state not cleared**: always set `self.game_state.battle_state = None` and `self.pending_command = None` in every ending path (win, lose, flee, catch)
- **Double-battle-start**: check `if self.game_state.battle_state is not None: return` at each entry point
- **Evolution prompt mid-battle**: defer evolution check to the post-battle handler, never during a turn
