---
name: mock-data-creator
description: Creates test fixtures, MockRichLog instances, and synthetic GameState setups for robot-pokemon tests. Use when a test needs a pre-configured party, specific bag contents, active battle state, or a location with story flags already set.
---

# mock-data-creator

Builds reusable test fixtures and mock objects for the robot-pokemon test suite.

## Associated Agent
`test-writer.agent.md`

## Instructions

### 1. Standard Fixtures (already in `tests/conftest.py` — use these first)

```python
@pytest.fixture
def gs():
    """Fresh GameState with start_new_game() called."""
    state = GameState()
    state.start_new_game()
    return state

@pytest.fixture
def output():
    """MockRichLog that records all writes."""
    return MockRichLog()
```

### 2. MockRichLog

```python
class MockRichLog:
    def __init__(self):
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return "\n".join(str(l) for l in self.lines)
```

**Assertions on output:**
```python
assert any("Badge" in str(l) for l in output.lines)
assert output.combined.count("HP") >= 1
```

### 3. Custom GameState Configurations

**Set player location:**
```python
def gs_in_cerulean(gs):
    gs.game_data["location"] = "Cerulean City"
    gs.current_location = "Cerulean City"
    return gs
```

**Add a party Pokemon:**
```python
def add_pokemon_to_party(gs, species="PIKACHU", level=20, hp=None):
    from pytemon.data import get_pokemon
    base = get_pokemon(species)
    max_hp = base["base_stats"]["hp"] + level * 2
    pkmn = {
        "species": species,
        "name": species.capitalize(),
        "level": level,
        "hp": hp if hp is not None else max_hp,
        "max_hp": max_hp,
        "moves": list(base["base_moves"]),
        "status": None,
        "exp": 0,
    }
    gs.game_data["party"].append(pkmn)
    return pkmn
```

**Set badges:**
```python
gs.game_data["badges"].append("boulder")
gs.game_data["badges"].append("cascade")
```

**Set story flags:**
```python
gs.game_data["story_flags"]["received_bicycle"] = True
gs.game_data["story_flags"]["rival_cerulean_beaten"] = True
```

**Set bag contents:**
```python
gs.game_data["bag"]["Potion"] = 5
gs.game_data["bag"]["Pokeball"] = 10
gs.game_data["bag"]["Moon Stone"] = 1
```

**Set money:**
```python
gs.game_data["money"] = 5000
```

### 4. Battle State Mock

```python
def setup_wild_battle(gs, species="PIDGEY", level=10):
    """Start a wild battle; returns BattleState."""
    from pytemon.engine.battle_engine import BattleState
    return BattleState(gs, species, level, is_wild=True)
```

### 5. Pytest Fixtures from Custom Configs

Register composite fixtures in `conftest.py` for reuse:
```python
@pytest.fixture
def gs_with_pikachu(gs):
    add_pokemon_to_party(gs, "PIKACHU", level=25)
    return gs

@pytest.fixture
def gs_post_brock(gs):
    gs.game_data["badges"].append("boulder")
    gs.game_data["location"] = "Route 3"
    gs.current_location = "Route 3"
    return gs
```

## Examples

**Input:** "I need a GameState with two party Pokemon and Cascade Badge for a Route 24 test."

**Output:**
```python
@pytest.fixture
def gs_cerulean_ready(gs):
    add_pokemon_to_party(gs, "PIKACHU", level=22)
    add_pokemon_to_party(gs, "BULBASAUR", level=20)
    gs.game_data["badges"].extend(["boulder", "cascade"])
    gs.game_data["location"] = "Cerulean City"
    gs.current_location = "Cerulean City"
    return gs
```

## Dependencies
- `tests/conftest.py` — standard fixtures
- `pytemon/game_state.py` — `GameState`, `start_new_game`
- `pytemon/data/__init__.py` — `get_pokemon`
- `pytemon/engine/battle_engine.py` — `BattleState`

## Error Handling
- **`KeyError` on `game_data`**: always call `start_new_game()` before customising state; it initialises all keys
- **Fixture scope issues**: default fixture scope is `function` (fresh per test) — don't use `session` scope for mutable GameState
