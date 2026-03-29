"""
Comprehensive tests for PokemonLibrary/cheat_commands.py

Covers: check_secret_phrase, process_cheat_command, show_cheat_help,
list_pokemon, list_trainers, list_locations, warp_to_location, give_item,
add_money, trigger_cheat_battle, trigger_cheat_trainer_battle,
add_pokemon_to_party, remove_pokemon_from_party, level_up_pokemon,
evolve_pokemon.
"""

import pytest

from pytemon.cheat_commands import (
    SECRET_PHRASE_DISABLE,
    SECRET_PHRASE_ENABLE,
    add_money,
    add_pokemon_to_party,
    check_secret_phrase,
    evolve_pokemon,
    faint_pokemon,
    give_item,
    level_up_pokemon,
    list_locations,
    list_pokemon,
    list_trainers,
    process_cheat_command,
    remove_pokemon_from_party,
    show_cheat_help,
    teach_move_cheat,
    warp_to_location,
)
from pytemon.game_state import GameState


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def noop(*_a, **_kw):
    pass


def make_party_pokemon(gs, name="PIKACHU", level=10):
    from pytemon.engine import BattleState

    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


# ===========================================================================
# check_secret_phrase
# ===========================================================================


class TestCheckSecretPhrase:
    def test_enable_phrase_activates_cheat_mode(self, gs, output):
        gs.cheat_mode = False
        result = check_secret_phrase(SECRET_PHRASE_ENABLE, gs, output)
        assert result is True
        assert gs.cheat_mode is True

    def test_enable_phrase_case_insensitive(self, gs, output):
        gs.cheat_mode = False
        result = check_secret_phrase(SECRET_PHRASE_ENABLE.upper(), gs, output)
        assert result is True
        assert gs.cheat_mode is True

    def test_enable_when_already_enabled_shows_warning(self, gs, output):
        gs.cheat_mode = True
        result = check_secret_phrase(SECRET_PHRASE_ENABLE, gs, output)
        assert result is True
        assert "already enabled" in output.combined.lower()

    def test_disable_phrase_deactivates_cheat_mode(self, gs, output):
        gs.cheat_mode = True
        result = check_secret_phrase(SECRET_PHRASE_DISABLE, gs, output)
        assert result is True
        assert gs.cheat_mode is False

    def test_disable_when_already_disabled_shows_warning(self, gs, output):
        gs.cheat_mode = False
        result = check_secret_phrase(SECRET_PHRASE_DISABLE, gs, output)
        assert result is True
        assert "already disabled" in output.combined.lower()

    def test_random_command_returns_false(self, gs, output):
        result = check_secret_phrase("hello world", gs, output)
        assert result is False

    def test_empty_command_returns_false(self, gs, output):
        result = check_secret_phrase("", gs, output)
        assert result is False


# ===========================================================================
# process_cheat_command
# ===========================================================================


class TestProcessCheatCommand:
    def test_returns_false_when_cheat_mode_off(self, gs, output):
        gs.cheat_mode = False
        result = process_cheat_command("cheat list pokemon", gs, output, noop, noop, noop)
        assert result is False

    def test_returns_false_for_non_cheat_command(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("look around", gs, output, noop, noop, noop)
        assert result is False

    def test_bare_cheat_without_space_returns_false(self, gs, output):
        # "cheat" with no trailing space is not a cheat command prefix
        gs.cheat_mode = True
        result = process_cheat_command("cheat", gs, output, noop, noop, noop)
        assert result is False

    def test_list_pokemon(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat list pokemon", gs, output, noop, noop, noop)
        assert result is True

    def test_list_trainers(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat list trainers", gs, output, noop, noop, noop)
        assert result is True

    def test_list_locations(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat list locations", gs, output, noop, noop, noop)
        assert result is True

    def test_list_unknown_type_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat list blargblarg", gs, output, noop, noop, noop)
        assert result is True
        assert "Unknown" in output.combined or "unknown" in output.combined

    def test_list_without_type_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat list", gs, output, noop, noop, noop)
        assert result is True

    def test_battle_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat battle", gs, output, noop, noop, noop)
        assert result is True

    def test_battle_with_pokemon_name(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs)
        pending = []
        result = process_cheat_command(
            "cheat battle pikachu 5", gs, output, noop, noop, lambda cmd: pending.append(cmd)
        )
        assert result is True

    def test_trainer_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat trainer", gs, output, noop, noop, noop)
        assert result is True

    def test_warp_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat warp", gs, output, noop, noop, noop)
        assert result is True

    def test_warp_valid_location(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat warp Viridian City", gs, output, noop, noop, noop)
        assert result is True

    def test_give_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat give", gs, output, noop, noop, noop)
        assert result is True

    def test_give_item(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat give Potion 3", gs, output, noop, noop, noop)
        assert result is True
        assert gs.game_data.get("items", {}).get("Potion", 0) == 3

    def test_money_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat money", gs, output, noop, noop, noop)
        assert result is True

    def test_money_adds_money(self, gs, output):
        gs.cheat_mode = True
        old_money = gs.game_data.get("money", 0)
        result = process_cheat_command("cheat money 1000", gs, output, noop, noop, noop)
        assert result is True
        assert gs.game_data["money"] == old_money + 1000

    def test_add_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat add", gs, output, noop, noop, noop)
        assert result is True

    def test_add_pokemon(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat add pikachu 5", gs, output, noop, noop, noop)
        assert result is True

    def test_remove_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat remove", gs, output, noop, noop, noop)
        assert result is True

    def test_level_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat level", gs, output, noop, noop, noop)
        assert result is True

    def test_level_sets_pokemon_level(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs, "PIKACHU", 10)
        result = process_cheat_command("cheat level pikachu 20", gs, output, noop, noop, noop)
        assert result is True

    def test_level_non_numeric_shows_error(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs, "PIKACHU", 10)
        result = process_cheat_command("cheat level pikachu abc", gs, output, noop, noop, noop)
        assert result is True

    def test_evolve_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat evolve", gs, output, noop, noop, noop)
        assert result is True

    def test_unknown_action_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat unknownaction", gs, output, noop, noop, noop)
        assert result is True
        assert "Unknown" in output.combined or "unknown" in output.combined


# ===========================================================================
# show_cheat_help
# ===========================================================================


class TestShowCheatHelp:
    def test_writes_help_text(self, output):
        show_cheat_help(output)
        assert len(output.lines) > 0

    def test_mentions_cheat_commands(self, output):
        show_cheat_help(output)
        assert "cheat" in output.combined.lower()


# ===========================================================================
# list_pokemon
# ===========================================================================


class TestListPokemon:
    def test_writes_output(self, output):
        list_pokemon(output)
        assert len(output.lines) > 0

    def test_includes_pikachu(self, output):
        list_pokemon(output)
        assert "PIKACHU" in output.combined


# ===========================================================================
# list_trainers
# ===========================================================================


class TestListTrainers:
    def test_writes_output(self, output):
        list_trainers(output)
        assert len(output.lines) > 0


# ===========================================================================
# list_locations
# ===========================================================================


class TestListLocations:
    def test_writes_output(self, gs, output):
        list_locations(gs, output)
        assert len(output.lines) > 0

    def test_includes_pallet_town(self, gs, output):
        list_locations(gs, output)
        assert "Pallet Town" in output.combined


# ===========================================================================
# warp_to_location
# ===========================================================================


class TestWarpToLocation:
    def test_warp_to_valid_location(self, gs, output):
        gs.cheat_mode = True
        warp_to_location(gs, "Viridian City", output)
        assert gs.current_location is not None

    def test_warp_to_invalid_location_shows_error(self, gs, output):
        warp_to_location(gs, "NonexistentPlace9999", output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_warp_changes_location(self, gs, output):
        gs.cheat_mode = True
        warp_to_location(gs, "Viridian City", output)
        assert gs.current_location.name == "Viridian City"


# ===========================================================================
# give_item
# ===========================================================================


class TestGiveItem:
    def test_give_adds_item_to_bag(self, gs, output):
        give_item(gs, "Potion", 5, output)
        assert gs.game_data.get("items", {}).get("Potion", 0) == 5

    def test_give_multiple_calls_stacks(self, gs, output):
        give_item(gs, "Pokeball", 3, output)
        give_item(gs, "Pokeball", 2, output)
        assert gs.game_data.get("items", {}).get("Pokeball", 0) == 5

    def test_give_writes_success_message(self, gs, output):
        give_item(gs, "Potion", 1, output)
        assert len(output.lines) > 0


# ===========================================================================
# add_money
# ===========================================================================


class TestAddMoney:
    def test_add_money_increases_balance(self, gs, output):
        gs.game_data["money"] = 100
        add_money(gs, 500, output)
        assert gs.game_data["money"] == 600

    def test_add_money_writes_message(self, gs, output):
        add_money(gs, 1000, output)
        assert "1000" in output.combined


# ===========================================================================
# add_pokemon_to_party
# ===========================================================================


class TestAddPokemonToParty:
    def test_add_valid_pokemon(self, gs, output):
        add_pokemon_to_party(gs, "pikachu", 10, output)
        assert len(gs.game_data.get("pokemon", [])) > 0

    def test_add_invalid_pokemon_shows_error(self, gs, output):
        add_pokemon_to_party(gs, "fakemon9999", 5, output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_add_to_full_party_shows_error(self, gs, output):
        for name in ["PIKACHU", "CHARMANDER", "SQUIRTLE", "BULBASAUR", "RATTATA", "PIDGEY"]:
            make_party_pokemon(gs, name)
        add_pokemon_to_party(gs, "mewtwo", 50, output)
        assert "full" in output.combined.lower() or "❌" in output.combined

    def test_add_with_partial_name(self, gs, output):
        add_pokemon_to_party(gs, "char", 5, output)
        # Should match charmander
        assert len(gs.game_data.get("pokemon", [])) > 0


# ===========================================================================
# remove_pokemon_from_party
# ===========================================================================


class TestRemovePokemonFromParty:
    def test_remove_valid_pokemon(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        make_party_pokemon(gs, "CHARMANDER")
        remove_pokemon_from_party(gs, "pikachu", output)
        names = [p.get("name") for p in gs.game_data.get("pokemon", [])]
        assert "PIKACHU" not in names

    def test_remove_empty_party_shows_error(self, gs, output):
        gs.game_data["pokemon"] = []
        remove_pokemon_from_party(gs, "pikachu", output)
        assert "empty" in output.combined.lower() or "❌" in output.combined

    def test_remove_last_pokemon_shows_error(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        remove_pokemon_from_party(gs, "pikachu", output)
        assert "last" in output.combined.lower() or "❌" in output.combined

    def test_remove_nonexistent_pokemon_shows_error(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        make_party_pokemon(gs, "CHARMANDER")
        remove_pokemon_from_party(gs, "fakemon99999", output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_remove_by_slot_number(self, gs, output):
        make_party_pokemon(gs, "PIKACHU")
        make_party_pokemon(gs, "CHARMANDER")
        remove_pokemon_from_party(gs, "1", output)
        assert len(gs.game_data.get("pokemon", [])) == 1


# ===========================================================================
# level_up_pokemon
# ===========================================================================


class TestLevelUpPokemon:
    def test_level_up_valid_pokemon(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        level_up_pokemon(gs, "pikachu", 20, output)
        p = gs.game_data["pokemon"][0]
        assert p.get("level") == 20

    def test_level_out_of_range_shows_error(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        level_up_pokemon(gs, "pikachu", 150, output)
        assert "❌" in output.combined or "between" in output.combined.lower()

    def test_level_too_low_shows_error(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        level_up_pokemon(gs, "pikachu", 0, output)
        assert "❌" in output.combined

    def test_level_nonexistent_pokemon_shows_error(self, gs, output):
        level_up_pokemon(gs, "fakemon999", 20, output)
        assert "not found" in output.combined.lower() or "❌" in output.combined


# ===========================================================================
# evolve_pokemon
# ===========================================================================


class TestEvolvePokemon:
    def test_evolve_valid_pokemon(self, gs, output):
        make_party_pokemon(gs, "CHARMANDER", 16)
        evolve_pokemon(gs, "charmander", output)
        # Charmeleon or error
        assert len(output.lines) > 0

    def test_evolve_nonexistent_pokemon_shows_error(self, gs, output):
        evolve_pokemon(gs, "fakemon999", output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_evolve_pokemon_that_doesnt_evolve(self, gs, output):
        make_party_pokemon(gs, "KANGASKHAN", 30)
        evolve_pokemon(gs, "kangaskhan", output)
        assert "doesn't evolve" in output.combined.lower()


# ===========================================================================
# cheat win / cheat lose  (battle commands)
# ===========================================================================


def _make_battle_state(gs, player_name="PIKACHU", enemy_name="RATTATA", level=5):
    """Put gs into an active battle and return the BattleState."""
    from pytemon.engine import BattleState

    make_party_pokemon(gs, player_name, level)
    bs = BattleState()
    player_pokemon = gs.game_data["pokemon"][0]
    bs.start_wild_battle(player_pokemon, enemy_name, level)
    gs.battle_state = bs
    gs.in_battle = True
    return bs


class TestCheatWin:
    def _run(self, gs, output, victory_cb=None):
        gs.cheat_mode = True
        return process_cheat_command(
            "cheat win", gs, output, noop, noop, noop,
            handle_battle_victory_callback=victory_cb,
        )

    def test_win_outside_battle_shows_error(self, gs, output):
        gs.in_battle = False
        result = self._run(gs, output)
        assert result is True
        assert "not in a battle" in output.combined.lower()

    def test_win_sets_enemy_hp_to_zero(self, gs, output):
        bs = _make_battle_state(gs)
        self._run(gs, output)
        assert bs.wild_pokemon["hp"] == 0

    def test_win_calls_victory_callback(self, gs, output):
        _make_battle_state(gs)
        called = []
        self._run(gs, output, victory_cb=lambda o: called.append(True))
        assert called

    def test_win_without_callback_does_not_raise(self, gs, output):
        _make_battle_state(gs)
        self._run(gs, output, victory_cb=None)  # should not raise

    def test_win_writes_output(self, gs, output):
        _make_battle_state(gs)
        self._run(gs, output)
        assert len(output.lines) > 0


class TestCheatLose:
    def _run(self, gs, output, fainted_cb=None):
        gs.cheat_mode = True
        return process_cheat_command(
            "cheat lose", gs, output, noop, noop, noop,
            handle_pokemon_fainted_callback=fainted_cb,
        )

    def test_lose_outside_battle_shows_error(self, gs, output):
        gs.in_battle = False
        result = self._run(gs, output)
        assert result is True
        assert "not in a battle" in output.combined.lower()

    def test_lose_sets_player_hp_to_zero(self, gs, output):
        bs = _make_battle_state(gs)
        self._run(gs, output)
        assert bs.player_pokemon["hp"] == 0

    def test_lose_calls_fainted_callback(self, gs, output):
        _make_battle_state(gs)
        called = []
        self._run(gs, output, fainted_cb=lambda o: called.append(True))
        assert called

    def test_lose_without_callback_does_not_raise(self, gs, output):
        _make_battle_state(gs)
        self._run(gs, output, fainted_cb=None)

    def test_lose_writes_output(self, gs, output):
        _make_battle_state(gs)
        self._run(gs, output)
        assert len(output.lines) > 0


# ===========================================================================
# faint_pokemon
# ===========================================================================


class TestFaintPokemon:
    def test_faint_reduces_hp_to_zero(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        make_party_pokemon(gs, "BULBASAUR", 10)  # need 2 so guard doesn't block
        faint_pokemon(gs, "pikachu", output)
        assert gs.game_data["pokemon"][0]["hp"] == 0

    def test_faint_nonexistent_shows_error(self, gs, output):
        faint_pokemon(gs, "fakemon999", output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_faint_already_fainted_shows_warning(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        make_party_pokemon(gs, "BULBASAUR", 10)
        gs.game_data["pokemon"][0]["hp"] = 0
        faint_pokemon(gs, "pikachu", output)
        assert "already" in output.combined.lower()

    def test_faint_last_healthy_shows_error(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        faint_pokemon(gs, "pikachu", output)
        assert "last" in output.combined.lower() or "can't" in output.combined.lower()

    def test_faint_via_process_cheat_command(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs, "PIKACHU", 10)
        make_party_pokemon(gs, "SQUIRTLE", 10)
        result = process_cheat_command("cheat faint pikachu", gs, output, noop, noop, noop)
        assert result is True
        assert gs.game_data["pokemon"][0]["hp"] == 0

    def test_faint_without_args_shows_error(self, gs, output):
        gs.cheat_mode = True
        result = process_cheat_command("cheat faint", gs, output, noop, noop, noop)
        assert result is True
        assert "usage" in output.combined.lower() or "❌" in output.combined


# ===========================================================================
# teach_move_cheat
# ===========================================================================


class TestTeachMoveCheat:
    def test_teach_valid_move(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        teach_move_cheat(gs, "pikachu", "SURF", output)
        moves = gs.game_data["pokemon"][0]["moves"]
        assert any(m["name"] == "SURF" for m in moves)

    def test_teach_invalid_move_shows_error(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        teach_move_cheat(gs, "pikachu", "NOTAMOVE99", output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_teach_to_nonexistent_pokemon_shows_error(self, gs, output):
        teach_move_cheat(gs, "fakemon999", "SURF", output)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_teach_partial_move_name(self, gs, output):
        make_party_pokemon(gs, "PIKACHU", 10)
        # "FLAM" should match "FLAMETHROWER"
        teach_move_cheat(gs, "pikachu", "FLAM", output)
        moves = gs.game_data["pokemon"][0]["moves"]
        names = [m["name"] for m in moves]
        assert any("FLAM" in n for n in names)

    def test_teach_via_process_cheat_command(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs, "PIKACHU", 10)
        result = process_cheat_command("cheat learn pikachu surf", gs, output, noop, noop, noop)
        assert result is True
        moves = gs.game_data["pokemon"][0]["moves"]
        assert any(m["name"] == "SURF" for m in moves)

    def test_learn_without_move_shows_error(self, gs, output):
        gs.cheat_mode = True
        make_party_pokemon(gs, "PIKACHU", 10)
        result = process_cheat_command("cheat learn pikachu", gs, output, noop, noop, noop)
        assert result is True
        assert "usage" in output.combined.lower() or "❌" in output.combined
