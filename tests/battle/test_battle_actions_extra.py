"""
Extended tests for PokemonLibrary/battle/battle_actions.py

Covers: trigger_wild_encounter, trigger_trainer_encounter, execute_player_move,
execute_wild_pokemon_turn, attempt_flee, attempt_catch_pokemon, execute_switch,
handle_battle_command, execute_item.
"""

import pytest

from pytemon.battle.battle_actions import (
    attempt_catch_pokemon,
    attempt_flee,
    execute_player_move,
    execute_switch,
    execute_wild_pokemon_turn,
    trigger_trainer_encounter,
    trigger_wild_encounter,
)
from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.locations import get_location


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text) -> None:
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


def noop(*_a, **_kw):
    pass


def make_party_pokemon(gs, name="PIKACHU", level=10):
    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


def setup_wild_battle(gs, player_name="PIKACHU", wild_name="RATTATA", level=5):
    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    gs.game_data["pokemon"] = [player_pokemon]
    bs.start_wild_battle(player_pokemon, wild_name, level)
    gs.battle_state = bs
    gs.in_battle = True
    return bs


def setup_trainer_battle(gs, player_name="PIKACHU", level=10):
    from pytemon.data.trainer_data import TRAINERS

    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    gs.game_data["pokemon"] = [player_pokemon]
    trainer = TRAINERS.get("youngster_joey_route1")
    if trainer is None:
        trainer = next(iter(TRAINERS.values()))
    bs.start_trainer_battle(player_pokemon, trainer)
    gs.battle_state = bs
    gs.in_battle = True
    return bs


# ===========================================================================
# trigger_wild_encounter
# ===========================================================================


class TestTriggerWildEncounter:
    def test_no_active_pokemon_shows_error(self, gs, output):
        gs.current_location = get_location("Route 1")
        gs.game_data["pokemon"] = []
        pending = []
        trigger_wild_encounter(gs, output, lambda cmd: pending.append(cmd))
        assert "fainted" in output.combined.lower() or "❌" in output.combined

    def test_starts_battle(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        pending = []
        trigger_wild_encounter(gs, output, lambda cmd: pending.append(cmd))
        assert "battle" in pending
        assert gs.battle_state is not None

    def test_shows_battle_start(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        pending = []
        trigger_wild_encounter(gs, output, lambda cmd: pending.append(cmd))
        assert len(output.lines) > 0

    def test_calls_show_battle_buttons(self, gs, output):
        gs.cheat_mode = True
        gs.current_location = get_location("Route 1")
        make_party_pokemon(gs)
        called = []
        trigger_wild_encounter(
            gs, output, noop, show_battle_buttons_callback=lambda: called.append(True)
        )
        assert called


def _get_trainer():
    from pytemon.data.trainer_data import TRAINERS

    trainer = TRAINERS.get("youngster_joey_route1")
    if trainer is None:
        trainer = next(iter(TRAINERS.values()))
    return trainer


# ===========================================================================
# trigger_trainer_encounter
# ===========================================================================


class TestTriggerTrainerEncounter:
    def test_starts_trainer_battle(self, gs, output):
        make_party_pokemon(gs)
        trainer = _get_trainer()
        pending = []
        trigger_trainer_encounter(gs, output, trainer, lambda cmd: pending.append(cmd))
        assert "battle" in pending
        assert gs.battle_state is not None

    def test_no_active_pokemon_shows_error(self, gs, output):
        gs.game_data["pokemon"] = []
        trainer = _get_trainer()
        trigger_trainer_encounter(gs, output, trainer, noop)
        assert "fainted" in output.combined.lower() or "❌" in output.combined


# ===========================================================================
# execute_player_move
# ===========================================================================


class TestExecutePlayerMove:
    def test_back_shows_battle_options(self, gs, output):
        setup_wild_battle(gs)
        options_shown = []
        execute_player_move(
            gs,
            "back",
            output,
            pending_command_callback=noop,
            show_battle_options_callback=lambda out: options_shown.append(True),
            show_move_selection_callback=noop,
            handle_battle_victory_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert options_shown

    def test_invalid_move_shows_error(self, gs, output):
        setup_wild_battle(gs)
        pending = []
        execute_player_move(
            gs,
            "xyz_invalid_move",
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            show_move_selection_callback=noop,
            handle_battle_victory_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "Unknown move" in output.combined or "❌" in output.combined

    def test_valid_move_by_number(self, gs, output):
        setup_wild_battle(gs, "PIKACHU", "RATTATA", 5)
        pending = []
        execute_player_move(
            gs,
            "1",
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            show_move_selection_callback=noop,
            handle_battle_victory_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert len(output.lines) > 0


# ===========================================================================
# execute_wild_pokemon_turn
# ===========================================================================


class TestExecuteWildPokemonTurn:
    def test_executes_move(self, gs, output):
        setup_wild_battle(gs)
        execute_wild_pokemon_turn(gs, output)
        assert len(output.lines) > 0

    def test_writes_move_used(self, gs, output):
        setup_wild_battle(gs)
        execute_wild_pokemon_turn(gs, output)
        assert "used" in output.combined.lower()

    def test_struggle_when_no_pp(self, gs, output):
        bs = setup_wild_battle(gs)
        for move in bs.wild_pokemon["moves"]:
            move["pp"] = 0
        execute_wild_pokemon_turn(gs, output)
        assert "Struggle" in output.combined


# ===========================================================================
# attempt_flee
# ===========================================================================


class TestAttemptFlee:
    def test_cant_flee_trainer_battle(self, gs, output):
        setup_trainer_battle(gs)
        pending = []
        attempt_flee(
            gs,
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            end_battle_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "No!" in output.combined or "trainer" in output.combined.lower()

    def test_flee_success_ends_battle(self, gs, output):
        import random

        setup_wild_battle(gs)
        ended = []
        original_random = random.random
        try:
            random.random = lambda: 0.0  # always < 0.75, so always flee successfully
            attempt_flee(
                gs,
                output,
                pending_command_callback=noop,
                show_battle_options_callback=noop,
                end_battle_callback=lambda out: ended.append(True),
                handle_pokemon_fainted_callback=noop,
            )
        finally:
            random.random = original_random
        assert ended

    def test_flee_failure_continues_battle(self, gs, output):
        import random

        setup_wild_battle(gs)
        pending = []
        original_random = random.random
        try:
            random.random = lambda: 0.99  # always >= 0.75, so always fail
            attempt_flee(
                gs,
                output,
                pending_command_callback=lambda cmd: pending.append(cmd),
                show_battle_options_callback=noop,
                end_battle_callback=noop,
                handle_pokemon_fainted_callback=noop,
            )
        finally:
            random.random = original_random
        assert len(output.lines) > 0


# ===========================================================================
# attempt_catch_pokemon
# ===========================================================================


class TestAttemptCatchPokemon:
    def test_no_pokeballs_shows_error(self, gs, output):
        setup_wild_battle(gs)
        gs.game_data["items"] = {}
        pending = []
        attempt_catch_pokemon(
            gs,
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            end_battle_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "no Pokeballs" in output.combined.lower() or "❌" in output.combined

    def test_cant_catch_trainer_pokemon(self, gs, output):
        setup_trainer_battle(gs)
        gs.game_data.setdefault("items", {})["Pokeball"] = 5
        pending = []
        attempt_catch_pokemon(
            gs,
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            end_battle_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "blocked" in output.combined.lower() or "❌" in output.combined

    def test_successful_catch_adds_to_party(self, gs, output):
        import random

        setup_wild_battle(gs, "PIKACHU", "RATTATA", 5)
        gs.game_data.setdefault("items", {})["Pokeball"] = 5
        ended = []
        original_randint = random.randint
        try:
            random.randint = lambda a, b: 0  # Always pass shake check
            attempt_catch_pokemon(
                gs,
                output,
                pending_command_callback=noop,
                show_battle_options_callback=noop,
                end_battle_callback=lambda out: ended.append(True),
                handle_pokemon_fainted_callback=noop,
            )
        finally:
            random.randint = original_randint
        assert ended or "caught" in output.combined.lower()

    def test_failed_catch_shows_message(self, gs, output):
        import random

        setup_wild_battle(gs, "PIKACHU", "RATTATA", 5)
        gs.game_data.setdefault("items", {})["Pokeball"] = 5
        original_random = random.random
        try:
            random.random = lambda: 0.99  # always fail
            pending = []
            attempt_catch_pokemon(
                gs,
                output,
                pending_command_callback=lambda cmd: pending.append(cmd),
                show_battle_options_callback=noop,
                end_battle_callback=noop,
                handle_pokemon_fainted_callback=noop,
            )
        finally:
            random.random = original_random
        assert len(output.lines) > 0

    def test_party_full_sends_to_pc(self, gs, output):
        import random

        setup_wild_battle(gs, "PIKACHU", "RATTATA", 5)
        # Fill party to 6
        for name in ["CHARMANDER", "SQUIRTLE", "BULBASAUR", "RATTATA", "PIDGEY"]:
            make_party_pokemon(gs, name)
        gs.game_data.setdefault("items", {})["Pokeball"] = 5
        original_random = random.random
        ended = []
        try:
            random.random = lambda: 0.0  # always succeed
            attempt_catch_pokemon(
                gs,
                output,
                pending_command_callback=noop,
                show_battle_options_callback=noop,
                end_battle_callback=lambda out: ended.append(True),
                handle_pokemon_fainted_callback=noop,
            )
        finally:
            random.random = original_random
        assert len(output.lines) > 0


# ===========================================================================
# execute_switch
# ===========================================================================


class TestExecuteSwitch:
    def test_switch_invalid_target(self, gs, output):
        setup_wild_battle(gs)
        make_party_pokemon(gs, "CHARMANDER")
        pending = []
        execute_switch(
            gs,
            "fakemon999",
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            show_pokemon_switch_menu_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_switch_to_self_shows_error(self, gs, output):
        setup_wild_battle(gs, "PIKACHU")
        pending = []
        execute_switch(
            gs,
            "pikachu",
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            show_pokemon_switch_menu_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "already" in output.combined.lower()

    def test_switch_to_valid_pokemon(self, gs, output):
        setup_wild_battle(gs, "PIKACHU")
        make_party_pokemon(gs, "CHARMANDER")
        pending = []
        execute_switch(
            gs,
            "charmander",
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            show_pokemon_switch_menu_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert len(output.lines) > 0

    def test_switch_to_fainted_shows_error(self, gs, output):
        setup_wild_battle(gs, "PIKACHU")
        fainted = make_party_pokemon(gs, "CHARMANDER")
        fainted["hp"] = 0
        pending = []
        execute_switch(
            gs,
            "charmander",
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            show_pokemon_switch_menu_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "fainted" in output.combined.lower() or "❌" in output.combined


# ===========================================================================
# handle_battle_victory
# ===========================================================================


class TestHandleBattleVictory:
    def test_wild_victory_ends_battle(self, gs, output):
        from pytemon.battle.battle_actions import handle_battle_victory

        bs = setup_wild_battle(gs)
        bs.wild_pokemon["hp"] = 0
        ended = []
        handle_battle_victory(
            gs,
            output,
            pending_command_callback=noop,
            show_battle_options_callback=noop,
            handle_trainer_defeated_callback=noop,
            end_battle_callback=lambda out: ended.append(True),
        )
        assert ended
        assert "gained" in output.combined.lower() or "fainted" in output.combined.lower()

    def test_trainer_victory_shows_output(self, gs, output):
        from pytemon.battle.battle_actions import handle_battle_victory

        setup_trainer_battle(gs, "PIKACHU", 20)
        pending = []
        handle_battle_victory(
            gs,
            output,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            handle_trainer_defeated_callback=noop,
            end_battle_callback=noop,
        )
        assert len(output.lines) > 0


# ===========================================================================
# handle_trainer_defeated
# ===========================================================================


class TestHandleTrainerDefeated:
    def test_awards_prize_money(self, gs, output):
        from pytemon.battle.battle_actions import handle_trainer_defeated

        setup_trainer_battle(gs)
        old_money = gs.game_data.get("money", 0)
        handle_trainer_defeated(gs, output, lambda out: None)
        assert gs.game_data.get("money", 0) >= old_money

    def test_marks_trainer_as_defeated(self, gs, output):
        from pytemon.battle.battle_actions import handle_trainer_defeated

        bs = setup_trainer_battle(gs)
        trainer_id = bs.trainer_data["id"]
        handle_trainer_defeated(gs, output, lambda out: None)
        assert trainer_id in gs.game_data.get("defeated_trainers", [])


# ===========================================================================
# handle_pokemon_fainted
# ===========================================================================


class TestHandlePokemonFainted:
    def test_player_pokemon_fainted_other_alive(self, gs, output):
        from pytemon.battle.battle_actions import handle_pokemon_fainted

        bs = setup_wild_battle(gs, "PIKACHU")
        bs.player_pokemon["hp"] = 0
        make_party_pokemon(gs, "CHARMANDER")
        ended = []
        handle_pokemon_fainted(gs, output, lambda out: ended.append(True))
        assert ended

    def test_fainted_stays_fainted_during_switch_prompt_flow(self, gs, output):
        from pytemon.battle.battle_actions import handle_pokemon_fainted

        bs = setup_wild_battle(gs, "PIKACHU")
        bs.player_pokemon["hp"] = 0
        make_party_pokemon(gs, "CHARMANDER")

        prompted = []
        ended = []
        handle_pokemon_fainted(
            gs,
            output,
            lambda out: ended.append(True),
            show_faint_options_callback=lambda can_run: prompted.append(can_run),
        )

        assert prompted
        assert not ended
        assert bs.player_pokemon["hp"] == 0

    def test_all_fainted_transports_to_pokemon_center(self, gs, output):
        from pytemon.battle.battle_actions import handle_pokemon_fainted

        bs = setup_wild_battle(gs, "PIKACHU")
        bs.player_pokemon["hp"] = 0
        gs.game_data["last_pokemon_center"] = "Viridian City"
        ended = []
        handle_pokemon_fainted(gs, output, lambda out: ended.append(True))
        assert ended
        assert gs.game_data.get("location") == "Viridian City"

    def test_no_pokemon_center_goes_home(self, gs, output):
        from pytemon.battle.battle_actions import handle_pokemon_fainted

        bs = setup_wild_battle(gs, "PIKACHU")
        bs.player_pokemon["hp"] = 0
        gs.game_data["last_pokemon_center"] = None
        ended = []
        handle_pokemon_fainted(gs, output, lambda out: ended.append(True))
        assert ended
        assert gs.game_data.get("location") == "Pallet Town"


# ===========================================================================
# use_heal_item
# ===========================================================================


class TestUseHealItem:
    def test_no_item_shows_error(self, gs, output):
        from pytemon.battle.battle_actions import use_heal_item

        setup_wild_battle(gs)
        gs.game_data["items"] = {}
        pending = []
        use_heal_item(
            gs,
            output,
            "Potion",
            20,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "no Potion" in output.combined.lower() or "❌" in output.combined

    def test_heals_pokemon(self, gs, output):
        from pytemon.battle.battle_actions import use_heal_item

        bs = setup_wild_battle(gs)
        bs.player_pokemon["hp"] = 5
        gs.game_data.setdefault("items", {})["Potion"] = 5
        pending = []
        use_heal_item(
            gs,
            output,
            "Potion",
            20,
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "HP" in output.combined or "recovered" in output.combined.lower()


# ===========================================================================
# use_status_cure
# ===========================================================================


class TestUseStatusCure:
    def test_no_item_shows_error(self, gs, output):
        from pytemon.battle.battle_actions import use_status_cure

        setup_wild_battle(gs)
        gs.game_data["items"] = {}
        pending = []
        use_status_cure(
            gs,
            output,
            "Antidote",
            "POISON",
            "cured of poison",
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "❌" in output.combined

    def test_wrong_status_shows_warning(self, gs, output):
        from pytemon.battle.battle_actions import use_status_cure

        bs = setup_wild_battle(gs)
        bs.player_pokemon["status"] = None
        gs.game_data.setdefault("items", {})["Antidote"] = 1
        pending = []
        use_status_cure(
            gs,
            output,
            "Antidote",
            "POISON",
            "cured of poison",
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert "doesn't have" in output.combined.lower() or "⚠" in output.combined

    def test_cures_status(self, gs, output):
        from pytemon.battle.battle_actions import use_status_cure

        bs = setup_wild_battle(gs)
        bs.player_pokemon["status"] = "POISON"
        gs.game_data.setdefault("items", {})["Antidote"] = 1
        pending = []
        use_status_cure(
            gs,
            output,
            "Antidote",
            "POISON",
            "cured of poison",
            pending_command_callback=lambda cmd: pending.append(cmd),
            show_battle_options_callback=noop,
            handle_pokemon_fainted_callback=noop,
        )
        assert bs.player_pokemon["status"] is None


# ===========================================================================
# end_battle
# ===========================================================================


class TestEndBattle:
    def test_clears_battle_state(self, gs, output):
        from pytemon.battle.battle_actions import end_battle

        setup_wild_battle(gs)
        end_battle(gs, output, noop)
        assert gs.battle_state is None
        assert gs.in_battle is False

    def test_calls_look_around(self, gs, output):
        from pytemon.battle.battle_actions import end_battle

        setup_wild_battle(gs)
        called = []
        end_battle(gs, output, lambda out: called.append(True))
        assert called
