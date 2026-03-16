"""
Unit tests for PokemonLibrary/stats.py.
"""

from types import SimpleNamespace

from pytemon import stats
from pytemon.game_state import GameState


class StubOutput:
    """Collect output.write() calls for assertions."""

    def __init__(self):
        self.lines = []

    def write(self, text):
        self.lines.append(text)


def test_record_wild_encounter_and_explore_initialize_stats():
    gs = GameState()
    gs.start_new_game()
    gs.get_active_pokemon = lambda: {"name": "PIKACHU"}  # type: ignore[method-assign]

    stats.record_wild_encounter(gs, "Route 1")
    stats.record_explore(gs, "Route 1")

    st = gs.game_data["stats"]
    assert st["wild_encounters"] == 1
    assert st["total_explores"] == 1
    assert st["explores_by_location"]["Route 1"] == 1
    assert st["pokemon_stats"]["PIKACHU"]["battles"] == 1


def test_record_helpers_increment_expected_counters():
    gs = GameState()
    gs.start_new_game()
    gs.get_active_pokemon = lambda: {"name": "CHARMANDER"}  # type: ignore[method-assign]

    stats.record_trainer_encounter(gs)
    stats.record_ko_dealt(gs, "CHARMANDER")
    stats.record_wild_battle_won(gs)
    stats.record_trainer_battle_won(gs)
    stats.record_fled(gs)
    stats.record_catch(gs, "PIDGEY")
    stats.record_faint(gs, "CHARMANDER")

    st = gs.game_data["stats"]
    assert st["trainer_battles"] == 1
    assert st["wild_victories"] == 1
    assert st["trainer_victories"] == 1
    assert st["wild_fled"] == 1
    assert st["catches"] == 1
    assert st["pokemon_stats"]["CHARMANDER"]["kos_dealt"] == 1
    assert st["pokemon_stats"]["CHARMANDER"]["faints"] == 1


def test_record_faint_in_trainer_battle_increments_trainer_losses():
    gs = GameState()
    gs.start_new_game()
    gs.battle_state = SimpleNamespace(is_trainer_battle=True)

    stats.record_faint(gs, "PIKACHU")

    assert gs.game_data["stats"]["trainer_losses"] == 1


def test_show_stats_no_battle_data_message():
    gs = GameState()
    gs.start_new_game()
    output = StubOutput()

    stats.show_stats(gs, output)  # type: ignore[arg-type]

    rendered = "\n".join(str(line) for line in output.lines)
    assert "Adventure Statistics" in rendered
    assert "No battle stats yet. Go find some Pokemon!" in rendered


def test_show_stats_with_populated_data_renders_sections_and_mvp():
    gs = GameState()
    gs.start_new_game()
    gs.game_data["stats"] = {
        "total_explores": 3,
        "explores_by_location": {"Route 1": 2, "Pallet Town": 1},
        "wild_encounters": 4,
        "wild_victories": 3,
        "wild_fled": 1,
        "trainer_battles": 2,
        "trainer_victories": 1,
        "trainer_losses": 1,
        "catches": 2,
        "pokemon_stats": {
            "PIKACHU": {"battles": 3, "kos_dealt": 2, "faints": 1},
            "BULBASAUR": {"battles": 1, "kos_dealt": 0, "faints": 0},
        },
    }
    output = StubOutput()

    stats.show_stats(gs, output)  # type: ignore[arg-type]

    rendered = "\n".join(str(line) for line in output.lines)
    assert "Favourite location" in rendered
    assert "Wild victories" in rendered
    assert "Trainer losses" in rendered
    assert "Per-Pokémon" in rendered
    assert "MVP:" in rendered
