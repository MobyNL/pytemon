"""
Comprehensive tests for PokemonLibrary/battle/battle_ui.py

Covers: show_battle_start, show_trainer_battle_start, show_battle_options,
show_move_selection, show_pokemon_switch_menu, show_battle_help, show_bag_menu.
"""

import pytest

from pytemon.battle.battle_ui import (
    show_bag_menu,
    show_battle_help,
    show_battle_options,
    show_battle_start,
    show_move_selection,
    show_pokemon_switch_menu,
    show_trainer_battle_start,
)
from pytemon.engine import BattleState
from pytemon.game_state import GameState


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text) -> None:
        # write can receive Rich objects or strings
        self.lines.append(str(text))

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


def _setup_wild_battle(gs, player_name="PIKACHU", wild_name="RATTATA", level=5):
    """Helper: start a wild battle and return the battle state."""
    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    bs.start_wild_battle(player_pokemon, wild_name, level)
    gs.battle_state = bs
    gs.game_data["pokemon"] = [player_pokemon]
    return bs


def _setup_trainer_battle(gs, player_name="PIKACHU", level=5):
    """Helper: start a trainer battle and return the battle state."""
    from pytemon.data.trainer_data import TRAINERS

    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)

    # Use a real trainer
    trainer = TRAINERS.get("youngster_joey_route1") or next(iter(TRAINERS.values()))
    bs.start_trainer_battle(player_pokemon, trainer)
    gs.battle_state = bs
    gs.game_data["pokemon"] = [player_pokemon]
    return bs


# ===========================================================================
# show_battle_start
# ===========================================================================


class TestShowBattleStart:
    def test_writes_wild_encounter(self, gs, output):
        _setup_wild_battle(gs)
        show_battle_start(gs, output)
        assert "appeared" in output.combined.lower() or "wild" in output.combined.lower()

    def test_shows_player_pokemon_name(self, gs, output):
        _setup_wild_battle(gs, player_name="PIKACHU")
        show_battle_start(gs, output)
        assert "PIKACHU" in output.combined

    def test_shows_wild_pokemon_name(self, gs, output):
        _setup_wild_battle(gs, wild_name="RATTATA")
        show_battle_start(gs, output)
        assert "RATTATA" in output.combined


# ===========================================================================
# show_trainer_battle_start
# ===========================================================================


class TestShowTrainerBattleStart:
    def test_shows_trainer_battle_header(self, gs, output):
        _setup_trainer_battle(gs)
        show_trainer_battle_start(gs, output)
        assert "TRAINER BATTLE" in output.combined or "trainer" in output.combined.lower()

    def test_shows_trainer_name(self, gs, output):
        bs = _setup_trainer_battle(gs)
        trainer = bs.trainer_data
        show_trainer_battle_start(gs, output)
        assert trainer["name"] in output.combined

    def test_shows_player_pokemon(self, gs, output):
        _setup_trainer_battle(gs, player_name="SQUIRTLE")
        show_trainer_battle_start(gs, output)
        assert "SQUIRTLE" in output.combined


# ===========================================================================
# show_battle_options
# ===========================================================================


class TestShowBattleOptions:
    def test_no_battle_state_returns_early(self, gs, output):
        gs.battle_state = None
        show_battle_options(gs, output)
        assert len(output.lines) == 0

    def test_shows_what_will_you_do(self, gs, output):
        _setup_wild_battle(gs)
        show_battle_options(gs, output)
        assert "What will you do" in output.combined

    def test_wild_battle_shows_catch_option(self, gs, output):
        _setup_wild_battle(gs)
        gs.game_data.setdefault("items", {})["Pokeball"] = 5
        show_battle_options(gs, output)
        assert "Catch" in output.combined

    def test_wild_battle_no_pokeballs_shows_no_pokeballs(self, gs, output):
        _setup_wild_battle(gs)
        gs.game_data["items"] = {}
        show_battle_options(gs, output)
        assert "No Pokeballs" in output.combined or "no pokeball" in output.combined.lower()

    def test_trainer_battle_shows_no_flee(self, gs, output):
        _setup_trainer_battle(gs)
        show_battle_options(gs, output)
        assert "trainer battles" in output.combined.lower() or "Can't flee" in output.combined

    def test_shows_hp_bars(self, gs, output):
        _setup_wild_battle(gs)
        show_battle_options(gs, output)
        assert "HP" in output.combined


# ===========================================================================
# show_move_selection
# ===========================================================================


class TestShowMoveSelection:
    def test_no_battle_state_returns_early(self, gs, output):
        gs.battle_state = None
        show_move_selection(gs, output)
        assert len(output.lines) == 0

    def test_shows_moves(self, gs, output):
        _setup_wild_battle(gs)
        show_move_selection(gs, output)
        assert "Select a move" in output.combined

    def test_shows_pp_info(self, gs, output):
        _setup_wild_battle(gs)
        show_move_selection(gs, output)
        assert "PP" in output.combined

    def test_shows_back_hint(self, gs, output):
        _setup_wild_battle(gs)
        show_move_selection(gs, output)
        assert "Back" in output.combined


# ===========================================================================
# show_pokemon_switch_menu
# ===========================================================================


class TestShowPokemonSwitchMenu:
    def test_shows_pokemon_list(self, gs, output):
        _setup_wild_battle(gs)
        # Add a second pokemon
        from pytemon.engine import BattleState

        second = BattleState().generate_wild_pokemon("CHARMANDER", 5)
        gs.game_data["pokemon"].append(second)
        show_pokemon_switch_menu(gs, output)
        assert "PIKACHU" in output.combined or "CHARMANDER" in output.combined

    def test_shows_active_pokemon_marker(self, gs, output):
        _setup_wild_battle(gs)
        from pytemon.engine import BattleState

        second = BattleState().generate_wild_pokemon("CHARMANDER", 5)
        gs.game_data["pokemon"].append(second)
        show_pokemon_switch_menu(gs, output)
        assert "Active" in output.combined

    def test_fainted_pokemon_shown_fainted(self, gs, output):
        _setup_wild_battle(gs)
        from pytemon.engine import BattleState

        second = BattleState().generate_wild_pokemon("CHARMANDER", 5)
        second["hp"] = 0
        gs.game_data["pokemon"].append(second)
        show_pokemon_switch_menu(gs, output)
        assert "Fainted" in output.combined


# ===========================================================================
# show_battle_help
# ===========================================================================


class TestShowBattleHelp:
    def test_writes_output(self, output):
        show_battle_help(output)
        assert len(output.lines) > 0

    def test_mentions_fight(self, output):
        show_battle_help(output)
        assert "Fight" in output.combined

    def test_mentions_flee(self, output):
        show_battle_help(output)
        assert "Flee" in output.combined

    def test_mentions_items(self, output):
        show_battle_help(output)
        assert "Item" in output.combined


# ===========================================================================
# show_bag_menu
# ===========================================================================


class TestShowBagMenu:
    def test_empty_bag_shows_no_items(self, gs, output):
        _setup_wild_battle(gs)
        gs.game_data["items"] = {}
        show_bag_menu(gs, output)
        assert "no usable items" in output.combined.lower()

    def test_shows_pokeballs(self, gs, output):
        _setup_wild_battle(gs)
        gs.game_data.setdefault("items", {})["Pokeball"] = 3
        show_bag_menu(gs, output)
        assert "Pokeball" in output.combined

    def test_shows_potions(self, gs, output):
        _setup_wild_battle(gs)
        gs.game_data.setdefault("items", {})["Potion"] = 2
        show_bag_menu(gs, output)
        assert "Potion" in output.combined

    def test_shows_super_potions(self, gs, output):
        _setup_wild_battle(gs)
        gs.game_data.setdefault("items", {})["Super Potion"] = 1
        show_bag_menu(gs, output)
        assert "Super Potion" in output.combined

    def test_antidote_shown_when_poisoned(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "POISON"
        gs.game_data.setdefault("items", {})["Antidote"] = 1
        show_bag_menu(gs, output)
        assert "Antidote" in output.combined

    def test_antidote_hidden_when_not_poisoned(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = None
        gs.game_data.setdefault("items", {})["Antidote"] = 1
        show_bag_menu(gs, output)
        # Antidote should not appear (only shows for poisoned pokemon)
        assert "Antidote" not in output.combined

    def test_paralyze_heal_shown_when_paralyzed(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "PARALYSIS"
        gs.game_data.setdefault("items", {})["Paralyze Heal"] = 1
        show_bag_menu(gs, output)
        assert "Paralyze Heal" in output.combined

    def test_awakening_shown_when_sleeping(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "SLEEP"
        gs.game_data.setdefault("items", {})["Awakening"] = 1
        show_bag_menu(gs, output)
        assert "Awakening" in output.combined


# ===========================================================================
# Status condition icons in show_battle_options HUD
# ===========================================================================


class TestShowBattleOptionsStatusIcons:
    def test_burn_status_shown_for_player(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "BURN"
        show_battle_options(gs, output)
        assert "BRN" in output.combined

    def test_poison_status_shown_for_player(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "POISON"
        show_battle_options(gs, output)
        assert "PSN" in output.combined

    def test_paralysis_status_shown_for_player(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "PARALYSIS"
        show_battle_options(gs, output)
        assert "PAR" in output.combined

    def test_sleep_status_shown_for_player(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = "SLEEP"
        show_battle_options(gs, output)
        assert "SLP" in output.combined

    def test_burn_status_shown_for_wild(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.wild_pokemon["status"] = "BURN"
        show_battle_options(gs, output)
        assert "BRN" in output.combined

    def test_no_status_icon_when_none(self, gs, output):
        bs = _setup_wild_battle(gs)
        bs.player_pokemon["status"] = None
        bs.wild_pokemon["status"] = None
        show_battle_options(gs, output)
        assert "BRN" not in output.combined
        assert "PSN" not in output.combined
        assert "PAR" not in output.combined
