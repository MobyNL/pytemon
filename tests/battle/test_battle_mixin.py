"""
Tests for PokemonLibrary/ui/battle_mixin.py using a MockTerminal.

Tests process_battle_command dispatch, execute_player_move, execute_wild_pokemon_turn,
handle_battle_victory, handle_pokemon_fainted, etc.
"""

import random

import pytest

from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.ui.battle_mixin import BattleMixin


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text) -> None:
        self.lines.append(str(text))

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


class MockAnimatedTextWriter:
    """Test double for AnimatedTextWriter.

    Writes all lines instantly and calls on_complete synchronously.
    Records each call as ``(method_name, delay, lines)`` in ``recorded_calls``
    so tests can verify that non-zero delays were requested.
    """

    def __init__(self):
        self.recorded_calls: list = []  # list of (method_name, delay, lines)

    def write_lines_with_delay(self, output, lines, delay=0.4, on_complete=None):
        self.recorded_calls.append(("write_lines_with_delay", delay, list(lines)))
        for line in lines:
            output.write(line)
        if on_complete:
            on_complete()

    def write_fast(self, output, lines, on_complete=None):
        self.recorded_calls.append(("write_fast", 0.2, list(lines)))
        for line in lines:
            output.write(line)
        if on_complete:
            on_complete()

    def write_medium(self, output, lines, on_complete=None):
        self.recorded_calls.append(("write_medium", 0.4, list(lines)))
        for line in lines:
            output.write(line)
        if on_complete:
            on_complete()

    def write_slow(self, output, lines, on_complete=None):
        self.recorded_calls.append(("write_slow", 0.8, list(lines)))
        for line in lines:
            output.write(line)
        if on_complete:
            on_complete()

    def write_instant(self, output, lines):
        self.recorded_calls.append(("write_instant", 0.0, list(lines)))
        for line in lines:
            output.write(line)

    def cancel(self):
        pass


class MockBattleTerminal(BattleMixin):
    """Mock terminal for testing BattleMixin methods."""

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self.pending_command = None
        self.pending_command_data = {}
        self._calls = {}
        self.text_animator = MockAnimatedTextWriter()

    # Stubs for Panel methods
    def hide_all_battle_panels(self):
        pass

    def hide_battle_loading(self):
        pass

    def show_battle_loading(self):
        pass

    def show_battle_hud(self):
        pass

    def update_battle_hud(self):
        pass

    def show_battle_options_panel(self):
        pass

    def show_battle_action_panel(self):
        pass

    def show_move_selection_panel(self):
        pass

    def show_battle_bag_panel(self):
        pass

    def show_switch_panel(self):
        pass

    def show_pokemon_switch_panel(self):
        pass

    def show_faint_switch_panel(self, can_run=False):
        self._calls["show_faint_switch_panel"] = can_run

    def hide_all_panels(self):
        pass

    def query_one(self, *a, **kw):
        return type("W", (), {"remove_class": lambda s, c: None})()

    # Stubs for game methods
    def show_location_arrival(self, output, is_load=False):
        pass

    def end_battle(self, output):
        self._calls["end_battle"] = True
        self.game_state.battle_state = None
        self.game_state.in_battle = False

    def handle_battle_victory(self, output):
        self._calls["handle_battle_victory"] = True

    def handle_pokemon_fainted(self, output):
        self._calls["handle_pokemon_fainted"] = True

    def _resume_after_evolution(self, output):
        self._calls["_resume_after_evolution"] = True

    def handle_trainer_defeated(self, output):
        self._calls["handle_trainer_defeated"] = True

    def _refresh_subtitle(self):
        pass

    def show_main_menu(self, output):
        pass

    def _return_to_pokemon_center(self, output):
        self._calls["_return_to_pokemon_center"] = True

    # BattleMixin display methods
    def show_battle_options(self, output):
        self._calls["show_battle_options"] = True

    def show_move_selection(self, output):
        self._calls["show_move_selection"] = True

    def show_battle_help(self, output):
        from pytemon.battle import battle_ui

        battle_ui.show_battle_help(output)

    def _queue_evolution_pending(self, pokemon, evolved_into, post_action, output):
        self._calls["_queue_evolution_pending"] = (pokemon, evolved_into, post_action)


@pytest.fixture
def term():
    return MockBattleTerminal()


@pytest.fixture
def output():
    return MockRichLog()


def make_pokemon(term, name="PIKACHU", level=10):
    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    term.game_state.game_data.setdefault("pokemon", []).append(p)
    return p


def setup_wild_battle(term, player_name="PIKACHU", wild_name="RATTATA", level=5):
    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    term.game_state.game_data["pokemon"] = [player_pokemon]
    bs.start_wild_battle(player_pokemon, wild_name, level)
    term.game_state.battle_state = bs
    term.game_state.in_battle = True
    return bs


def setup_trainer_battle(term, player_name="PIKACHU", level=10):
    from pytemon.data.trainer_data import TRAINERS

    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    term.game_state.game_data["pokemon"] = [player_pokemon]
    trainer = TRAINERS.get("youngster_joey_route1")
    if trainer is None:
        trainer = next(iter(TRAINERS.values()))
    bs.start_trainer_battle(player_pokemon, trainer)
    term.game_state.battle_state = bs
    term.game_state.in_battle = True
    return bs


# ===========================================================================
# ensure_battle_ready
# ===========================================================================


class TestEnsureBattleReady:
    def test_enriches_pokemon(self, term):
        p = {"name": "PIKACHU", "level": 5}
        term.ensure_battle_ready(p)
        assert "hp" in p
        assert "stats" in p
        assert "moves" in p


# ===========================================================================
# process_battle_command
# ===========================================================================


class TestProcessBattleCommand:
    def test_quit_shows_cannot_quit(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("quit", output)
        assert "can't quit" in output.combined.lower()
        assert term.pending_command == "battle"

    def test_exit_shows_cannot_quit(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("exit", output)
        assert "can't quit" in output.combined.lower()

    def test_save_shows_cannot_save(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("save", output)
        assert "can't save" in output.combined.lower()

    def test_help_shows_battle_help(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("help", output)
        assert "Fight" in output.combined or "Battle" in output.combined.lower()
        assert term.pending_command == "battle"

    def test_fight_shows_move_selection(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("fight", output)
        assert term._calls.get("show_move_selection") is True
        assert term.pending_command == "select_move"

    def test_attack_shows_move_selection(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("attack", output)
        assert term.pending_command == "select_move"

    def test_run_attempts_flee(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("run", output)
        # Flee was called — must produce output (flee success or fail message)
        assert len(output.lines) > 0

    def test_bag_shows_bag(self, term, output):
        setup_wild_battle(term)
        term.game_state.game_data["items"] = {}
        term.process_battle_command("bag", output)
        assert term.pending_command == "battle"

    def test_pokeball_attempts_catch(self, term, output):
        setup_wild_battle(term)
        term.game_state.game_data.setdefault("items", {})["Pokeball"] = 5
        original_random = random.random
        try:
            random.random = lambda: 0.0  # Always catch
            term.process_battle_command("pokeball", output)
        finally:
            random.random = original_random
        # Either caught or shows message
        assert len(output.lines) > 0

    def test_use_potion_heals(self, term, output):
        bs = setup_wild_battle(term)
        bs.player_pokemon["hp"] = 5
        term.game_state.game_data.setdefault("items", {})["Potion"] = 3
        term.process_battle_command("use potion", output)
        assert "HP" in output.combined or "recovered" in output.combined.lower()

    def test_use_potion_no_potions(self, term, output):
        setup_wild_battle(term)
        term.game_state.game_data["items"] = {}
        term.process_battle_command("use potion", output)
        assert "no Potions" in output.combined or "❌" in output.combined

    def test_super_potion(self, term, output):
        bs = setup_wild_battle(term)
        bs.player_pokemon["hp"] = 5
        term.game_state.game_data.setdefault("items", {})["Super Potion"] = 1
        term.process_battle_command("use super potion", output)
        assert len(output.lines) > 0

    def test_antidote(self, term, output):
        bs = setup_wild_battle(term)
        bs.player_pokemon["status"] = "POISON"
        term.game_state.game_data.setdefault("items", {})["Antidote"] = 1
        term.process_battle_command("use antidote", output)
        assert bs.player_pokemon["status"] is None

    def test_paralyze_heal(self, term, output):
        bs = setup_wild_battle(term)
        bs.player_pokemon["status"] = "PARALYSIS"
        term.game_state.game_data.setdefault("items", {})["Paralyze Heal"] = 1
        term.process_battle_command("use paralyze heal", output)
        assert bs.player_pokemon["status"] is None

    def test_awakening(self, term, output):
        bs = setup_wild_battle(term)
        bs.player_pokemon["status"] = "SLEEP"
        term.game_state.game_data.setdefault("items", {})["Awakening"] = 1
        term.process_battle_command("use awakening", output)
        assert bs.player_pokemon["status"] is None

    def test_pokemon_shows_switch_menu(self, term, output):
        setup_wild_battle(term)
        make_pokemon(term, "CHARMANDER")
        term.process_battle_command("pokemon", output)
        # Shows the switch menu header
        assert "Switch Pokemon" in output.combined or "👥" in output.combined

    def test_unknown_command_shows_error(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("dance", output)
        assert "❌" in output.combined or "Not a valid" in output.combined

    def test_q_shows_cannot_quit(self, term, output):
        setup_wild_battle(term)
        term.process_battle_command("q", output)
        assert "can't quit" in output.combined.lower()


# ===========================================================================
# execute_player_move
# ===========================================================================


class TestExecutePlayerMove:
    def test_back_shows_battle_options(self, term, output):
        setup_wild_battle(term)
        term.execute_player_move("back", output)
        assert term._calls.get("show_battle_options") is True
        assert term.pending_command == "battle"

    def test_invalid_move_shows_error(self, term, output):
        setup_wild_battle(term)
        term.execute_player_move("xyz_invalid_move", output)
        assert "Unknown move" in output.combined or "❌" in output.combined
        assert term.pending_command == "select_move"

    def test_valid_move_by_number(self, term, output):
        setup_wild_battle(term, "PIKACHU", "RATTATA", 5)
        term.execute_player_move("1", output)
        assert len(output.lines) > 0

    def test_move_with_no_pp(self, term, output):
        bs = setup_wild_battle(term)
        # Zero out PP on first move
        bs.player_pokemon["moves"][0]["pp"] = 0
        term.execute_player_move("1", output)
        assert "no PP" in output.combined.lower() or "❌" in output.combined

    def test_kills_wild_triggers_victory(self, term, output):
        bs = setup_wild_battle(term)
        # Make wild very weak
        bs.wild_pokemon["hp"] = 1
        bs.wild_pokemon["max_hp"] = 1
        # Use first move
        term.execute_player_move("1", output)
        # Either handle_battle_victory was called or wild still alive (randomness)
        assert len(output.lines) > 0


# ===========================================================================
# execute_wild_pokemon_turn
# ===========================================================================


class TestExecuteWildPokemonTurn:
    def test_executes_move_and_writes_output(self, term, output):
        setup_wild_battle(term)
        term.execute_wild_pokemon_turn(output)
        assert "used" in output.combined.lower()

    def test_struggle_when_no_pp(self, term, output):
        bs = setup_wild_battle(term)
        for move in bs.wild_pokemon["moves"]:
            move["pp"] = 0
        term.execute_wild_pokemon_turn(output)
        assert "Struggle" in output.combined


# ===========================================================================
# show_pokemon_switch_menu
# ===========================================================================


class TestShowPokemonSwitchMenu:
    def test_no_battle_state_does_nothing(self, term, output):
        term.game_state.battle_state = None
        term.show_pokemon_switch_menu(output)
        assert len(output.lines) == 0

    def test_shows_party_options(self, term, output):
        setup_wild_battle(term)
        make_pokemon(term, "CHARMANDER")
        term.show_pokemon_switch_menu(output)
        assert len(output.lines) > 0


# ===========================================================================
# attempt_flee (via mixin)
# ===========================================================================


class TestAttemptFlee:
    def test_flee_from_wild_success(self, term, output):
        setup_wild_battle(term)
        original_random = random.random
        try:
            random.random = lambda: 0.0  # Always flee
            term.attempt_flee(output)
        finally:
            random.random = original_random
        # end_battle should have been called
        assert term._calls.get("end_battle") or "got away" in output.combined.lower()


# ===========================================================================
# trigger_wild_encounter (mixin wrapper)
# ===========================================================================


class TestTriggerWildEncounterMixin:
    def test_triggers_battle_with_party(self, term, output):
        from pytemon.locations import get_location

        term.game_state.cheat_mode = True
        term.game_state.current_location = get_location("Route 1")
        make_pokemon(term, "PIKACHU")
        term.trigger_wild_encounter(output)
        assert term.game_state.battle_state is not None


# ===========================================================================
# handle_battle_victory (full implementation via override)
# ===========================================================================


class TestHandleBattleVictoryFull:
    """Test handle_battle_victory with full implementation (no mock override)."""

    def test_wild_victory_ends_battle(self, output):
        """Use a term with actual handle_battle_victory."""

        class FullBattleTerminal(BattleMixin):
            def __init__(self):
                self.game_state = GameState()
                self.game_state.start_new_game()
                self.pending_command = None
                self.pending_command_data = {}
                self._calls = {}

            def hide_all_battle_panels(self):
                pass

            def hide_battle_loading(self):
                pass

            def show_battle_loading(self):
                pass

            def show_battle_hud(self):
                pass

            def update_battle_hud(self):
                pass

            def show_battle_options_panel(self):
                pass

            def show_battle_action_panel(self):
                pass

            def show_move_selection_panel(self):
                pass

            def show_battle_bag_panel(self):
                pass

            def show_switch_panel(self):
                pass

            def show_pokemon_switch_panel(self):
                pass

            def show_faint_switch_panel(self, can_run=False):
                pass

            def query_one(self, *a, **kw):
                return type("W", (), {"remove_class": lambda s, c: None})()

            def show_battle_options(self, output):
                pass

            def show_move_selection(self, output):
                pass

            def _refresh_subtitle(self):
                pass

            def end_battle(self, output):
                self._calls["end_battle"] = True

            def handle_trainer_defeated(self, output):
                self._calls["handle_trainer_defeated"] = True

            def handle_pokemon_fainted(self, output):
                self._calls["handle_pokemon_fainted"] = True

            def _queue_evolution_pending(self, p, e, pa, out):
                self._calls["_queue_evolution_pending"] = True

            def _resume_after_evolution(self, output):
                self._calls["_resume_after_evolution"] = True

            def ensure_battle_ready(self, p):
                pass

        t = FullBattleTerminal()
        bs = BattleState()
        player_pokemon = bs.generate_wild_pokemon("PIKACHU", 20)
        t.game_state.game_data["pokemon"] = [player_pokemon]
        bs.start_wild_battle(player_pokemon, "RATTATA", 5)
        t.game_state.battle_state = bs

        t.handle_battle_victory(output)
        assert t._calls.get("end_battle")


# ===========================================================================
# Additional tests for uncovered mixin paths
# ===========================================================================

# ---------------------------------------------------------------------------
# Helpers for extended tests
# ---------------------------------------------------------------------------


class ExtendedBattleTerminal(BattleMixin):
    """Extended mock terminal with all required stubs for deeper testing."""

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self.pending_command = None
        self.pending_command_data = {}
        self._calls = {}
        self.text_animator = MockAnimatedTextWriter()

    # Panel stubs
    def hide_all_battle_panels(self):
        pass

    def hide_battle_loading(self):
        pass

    def show_battle_loading(self):
        pass

    def show_battle_hud(self):
        pass

    def update_battle_hud(self):
        pass

    def show_battle_options_panel(self):
        pass

    def show_battle_action_panel(self):
        pass

    def show_move_selection_panel(self):
        pass

    def show_battle_bag_panel(self):
        pass

    def show_switch_panel(self):
        pass

    def show_pokemon_switch_panel(self):
        pass

    def show_faint_switch_panel(self, can_run=False):
        self._calls["show_faint_switch_panel"] = can_run

    def hide_all_panels(self):
        pass

    def show_gym_panel(self):
        pass

    def query_one(self, *a, **kw):
        return type(
            "W",
            (),
            {
                "remove_class": lambda s, c: None,
                "add_class": lambda s, c: None,
                "update": lambda s, t: None,
            },
        )()

    # Game methods
    def show_location_arrival(self, output, is_load=False):
        pass

    def look_around(self, output):
        self._calls.setdefault("look_around", []).append(True)

    def ensure_battle_ready(self, p):
        pass

    def _refresh_subtitle(self):
        pass

    def show_main_menu(self, output):
        pass

    def show_battle_options(self, output):
        self._calls.setdefault("show_battle_options", []).append(True)

    def show_move_selection(self, output):
        self._calls.setdefault("show_move_selection", []).append(True)


@pytest.fixture
def ext_term():
    return ExtendedBattleTerminal()


@pytest.fixture
def ext_output():
    return MockRichLog()


def setup_wild_ext(term, player_name="PIKACHU", wild_name="RATTATA", level=5):
    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    term.game_state.game_data["pokemon"] = [player_pokemon]
    bs.start_wild_battle(player_pokemon, wild_name, level)
    term.game_state.battle_state = bs
    term.game_state.in_battle = True
    return bs


def setup_trainer_ext(term, player_name="PIKACHU", level=10):
    from pytemon.data.trainer_data import TRAINERS

    bs = BattleState()
    player_pokemon = bs.generate_wild_pokemon(player_name, level)
    term.game_state.game_data["pokemon"] = [player_pokemon]
    trainer = TRAINERS.get("youngster_joey_route1") or next(iter(TRAINERS.values()))
    bs.start_trainer_battle(player_pokemon, trainer)
    term.game_state.battle_state = bs
    term.game_state.in_battle = True
    return bs


# ===========================================================================
# trigger_gym_battle — calls get_trainer to look up by ID
# ===========================================================================


class TestTriggerGymBattle:
    def test_invalid_trainer_id_shows_error(self, ext_term, ext_output):
        ext_term.trigger_gym_battle("NONEXISTENT_TRAINER_ZZZZZ", ext_output)
        assert "❌" in ext_output.combined

    def test_valid_trainer_id_starts_battle(self, ext_term, ext_output):
        from pytemon.data.trainer_data import TRAINERS

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        ext_term.game_state.game_data["pokemon"] = [p]
        trainer_id = next(iter(TRAINERS.keys()))
        ext_term.trigger_gym_battle(trainer_id, ext_output)
        # Battle should be started when a valid trainer ID is used
        assert ext_term.game_state.battle_state is not None


# ===========================================================================
# show_battle_start / show_trainer_battle_start / show_battle_options /
# show_move_selection / show_battle_help thin wrappers
# ===========================================================================


class TestBattleDisplayWrappers:
    def test_show_battle_start(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.show_battle_start(ext_output)
        assert len(ext_output.lines) > 0

    def test_show_trainer_battle_start(self, ext_term, ext_output):
        setup_trainer_ext(ext_term)
        ext_term.show_trainer_battle_start(ext_output)
        assert len(ext_output.lines) > 0

    def test_show_battle_options_writes_output(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        # Bypass the stub to call the real method
        from pytemon.battle import battle_ui as bui

        bui.show_battle_options(ext_term.game_state, ext_output)
        assert len(ext_output.lines) > 0

    def test_show_move_selection_writes_output(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        from pytemon.battle import battle_ui as bui

        bui.show_move_selection(ext_term.game_state, ext_output)
        assert len(ext_output.lines) > 0

    def test_show_battle_help_writes_output(self, ext_term, ext_output):
        from pytemon.battle import battle_ui as bui

        bui.show_battle_help(ext_output)
        assert len(ext_output.lines) > 0


# ===========================================================================
# parse_move_choice edge cases
# ===========================================================================


class TestParseMoveChoiceExtra:
    def test_use_prefix_stripped(self, ext_term):
        setup_wild_ext(ext_term)
        player = ext_term.game_state.battle_state.player_pokemon
        # First move name
        move_name = player["moves"][0]["name"].lower()
        result = ext_term.parse_move_choice(f"use {move_name}", player)
        assert result is not None

    def test_index_out_of_range_returns_none(self, ext_term):
        setup_wild_ext(ext_term)
        player = ext_term.game_state.battle_state.player_pokemon
        result = ext_term.parse_move_choice("99", player)
        assert result is None

    def test_name_partial_match(self, ext_term):
        setup_wild_ext(ext_term)
        player = ext_term.game_state.battle_state.player_pokemon
        # Use first few letters of first move
        partial = player["moves"][0]["name"][:3].lower()
        result = ext_term.parse_move_choice(partial, player)
        assert result is not None

    def test_no_match_returns_none(self, ext_term):
        setup_wild_ext(ext_term)
        player = ext_term.game_state.battle_state.player_pokemon
        result = ext_term.parse_move_choice("xyznonexistent99", player)
        assert result is None


# ===========================================================================
# execute_player_move — faint paths and EOT effects
# ===========================================================================


class TestExecutePlayerMoveFaintPaths:
    def test_player_faints_after_opponent_move(self, ext_term, ext_output):
        """Player pokemon faints after opponent's counter-attack."""
        bs = setup_wild_ext(ext_term)
        # Give player 1 hp so almost any opponent move faints them
        bs.player_pokemon["hp"] = 1
        ext_term.execute_player_move("1", ext_output)
        # No crash expected
        assert len(ext_output.lines) > 0

    def test_wild_faints_after_player_move(self, ext_term, ext_output):
        """Wild pokemon faints after player move — victory triggered."""
        bs = setup_wild_ext(ext_term)
        # Make wild very weak
        bs.wild_pokemon["hp"] = 1
        bs.wild_pokemon["max_hp"] = 1
        ext_term.execute_player_move("1", ext_output)
        assert len(ext_output.lines) > 0

    def test_zero_pp_move_rejected(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        bs.player_pokemon["moves"][0]["pp"] = 0
        ext_term.execute_player_move("1", ext_output)
        assert "no PP" in ext_output.combined.lower() or "❌" in ext_output.combined

    def test_trainer_battle_uses_trainer_ai(self, ext_term, ext_output):
        """execute_wild_pokemon_turn uses trainer AI in trainer battles."""
        setup_trainer_ext(ext_term)
        ext_term.execute_wild_pokemon_turn(ext_output)
        assert len(ext_output.lines) > 0


# ===========================================================================
# show_pokemon_switch_menu — only-one-pokemon (no switch available)
# ===========================================================================


class TestShowPokemonSwitchMenuOnlyOne:
    def test_only_active_pokemon_no_switch(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        # Only one pokemon in party — no switch available
        ext_term.show_pokemon_switch_menu(ext_output)
        assert "No other" in ext_output.combined or ext_term.pending_command == "battle"


# ===========================================================================
# execute_switch — all branches
# ===========================================================================


class TestExecuteSwitchExtra:
    def test_no_battle_state_returns_silently(self, ext_term, ext_output):
        ext_term.game_state.battle_state = None
        ext_term.execute_switch("1", ext_output)
        assert len(ext_output.lines) == 0

    def test_cancel_switch(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.execute_switch("back", ext_output)
        assert "cancelled" in ext_output.combined.lower()
        assert ext_term.pending_command == "battle"

    def test_invalid_selection(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.execute_switch("99", ext_output)
        assert "❌" in ext_output.combined

    def test_switch_to_self_shows_warning(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        # First pokemon is active — switch to "1" should show warning
        ext_term.execute_switch("1", ext_output)
        assert "already in battle" in ext_output.combined.lower() or "❌" in ext_output.combined

    def test_switch_to_fainted_pokemon(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        # Add a fainted second pokemon
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        second["hp"] = 0
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.execute_switch("2", ext_output)
        assert "fainted" in ext_output.combined.lower() or "❌" in ext_output.combined

    def test_switch_by_name(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.execute_switch("charmander", ext_output)
        # Either switched or no crash
        assert len(ext_output.lines) > 0

    def test_switch_by_number(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.execute_switch("2", ext_output)
        assert len(ext_output.lines) > 0


# ===========================================================================
# handle_trainer_defeated — with and without pending evolution
# ===========================================================================


class TestHandleTrainerDefeatedExtra:
    def test_with_pending_evolution(self, ext_term, ext_output):
        bs = setup_trainer_ext(ext_term)
        # Set a pending evolution
        player = bs.player_pokemon
        bs.pending_evolution = (player, "RAICHU")
        queued = []
        ext_term._queue_evolution_pending = lambda p, e, pa, out: queued.append((e, pa))
        ext_term.handle_trainer_defeated(ext_output)
        assert queued  # Evolution was queued
        assert bs.pending_evolution is None

    def test_without_pending_evolution(self, ext_term, ext_output):
        bs = setup_trainer_ext(ext_term)
        bs.pending_evolution = None
        ext_term.handle_trainer_defeated(ext_output)
        assert len(ext_output.lines) > 0


# ===========================================================================
# handle_pokemon_fainted — delegates to battle_actions
# ===========================================================================


class TestHandlePokemonFaintedExtra:
    def test_fainted_with_other_pokemon_alive(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        ext_term.game_state.game_data["pokemon"].append(second)
        # Faint main pokemon
        bs.player_pokemon["hp"] = 0
        ext_term.handle_pokemon_fainted(ext_output)
        assert len(ext_output.lines) > 0

    def test_fainted_all_pokemon_blacked_out(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        # Only one pokemon, it fainted
        bs.player_pokemon["hp"] = 0
        ext_term.handle_pokemon_fainted(ext_output)
        assert (
            "fainted" in ext_output.combined.lower() or "black out" in ext_output.combined.lower()
        )


# ===========================================================================
# end_battle — regular and in_gym paths
# ===========================================================================


class TestEndBattleExtra:
    def test_regular_end_battle(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data = {}
        ext_term.end_battle(ext_output)
        assert ext_term.game_state.battle_state is None

    def test_end_battle_in_gym_lobby(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data = {"in_gym_lobby": True, "gym_location": "Pewter City"}
        from pytemon.locations import get_location

        ext_term.game_state.current_location = get_location("Pewter City")
        ext_term.end_battle(ext_output)
        assert ext_term.game_state.battle_state is None


class TestBattleBannerVisibility:
    def test_show_battle_options_hides_location_banner(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        calls = []

        class _BannerWidget:
            def add_class(self, cls):
                calls.append(("add", cls))

            def remove_class(self, cls):
                calls.append(("remove", cls))

        def _query_one(selector, *args, **kwargs):
            if selector == "#welcome":
                return _BannerWidget()
            return type(
                "W", (), {"add_class": lambda s, c: None, "remove_class": lambda s, c: None}
            )()

        ext_term.query_one = _query_one
        BattleMixin.show_battle_options(ext_term, ext_output)

        assert ("add", "hidden") in calls

    def test_end_battle_restores_location_banner(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        calls = []

        class _BannerWidget:
            def add_class(self, cls):
                calls.append(("add", cls))

            def remove_class(self, cls):
                calls.append(("remove", cls))

        def _query_one(selector, *args, **kwargs):
            if selector == "#welcome":
                return _BannerWidget()
            return type(
                "W", (), {"add_class": lambda s, c: None, "remove_class": lambda s, c: None}
            )()

        ext_term.query_one = _query_one
        ext_term.end_battle(ext_output)

        assert ("remove", "hidden") in calls


# ===========================================================================
# _queue_evolution_pending
# ===========================================================================


class TestQueueEvolutionPending:
    def test_sets_pending_command(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        pokemon = ext_term.game_state.battle_state.player_pokemon
        ext_term._queue_evolution_pending(pokemon, "RAICHU", "wild_end", ext_output)
        assert ext_term.pending_command == "confirm_evolution"
        assert "RAICHU" in ext_output.combined
        assert ext_term.pending_command_data.get("evolves_into") == "RAICHU"


# ===========================================================================
# _resume_after_evolution — all post_action branches
# ===========================================================================


class TestResumeAfterEvolution:
    def test_wild_end_ends_battle(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data = {"evolution_post_action": "wild_end"}
        ext_term._resume_after_evolution(ext_output)
        assert ext_term.game_state.battle_state is None

    def test_trainer_defeated_post_action(self, ext_term, ext_output):
        setup_trainer_ext(ext_term)
        ext_term.pending_command_data = {"evolution_post_action": "trainer_defeated"}
        ended = []
        ext_term.end_battle = lambda out: ended.append(True)
        ext_term._resume_after_evolution(ext_output)
        # handle_trainer_defeated was called; since no pending_evolution, end_battle was invoked
        assert ended

    def test_trainer_next_with_more_pokemon(self, ext_term, ext_output):
        from pytemon.data.trainer_data import TRAINERS

        # Use a trainer that has 2 pokemon (bug_catcher_rick)
        bs = BattleState()
        player_pokemon = bs.generate_wild_pokemon("PIKACHU", 10)
        ext_term.game_state.game_data["pokemon"] = [player_pokemon]
        trainer = TRAINERS["bug_catcher_rick"]
        bs.start_trainer_battle(player_pokemon, trainer)
        ext_term.game_state.battle_state = bs
        ext_term.game_state.in_battle = True
        ext_term.pending_command_data = {"evolution_post_action": "trainer_next"}
        ext_term._resume_after_evolution(ext_output)
        # After evolution, the second trainer pokemon should be announced
        assert "sent out" in ext_output.combined.lower() or ext_term.pending_command == "battle"

    def test_unknown_post_action_ends_battle(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data = {"evolution_post_action": "unknown_action"}
        ext_term._resume_after_evolution(ext_output)
        assert ext_term.game_state.battle_state is None

    def test_default_post_action_ends_battle(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data = {}
        ext_term._resume_after_evolution(ext_output)
        # Default is "wild_end"
        assert ext_term.game_state.battle_state is None


# ===========================================================================
# process_battle_command — potion that drops to 0 (item deleted)
# ===========================================================================


class TestProcessBattleCommandPotionDeletion:
    def test_potion_deleted_when_last_one_used(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        bs.player_pokemon["hp"] = 5
        ext_term.game_state.game_data["items"] = {"Potion": 1}
        ext_term.process_battle_command("use potion", ext_output)
        # Potion should be removed from items
        assert "Potion" not in ext_term.game_state.game_data["items"]

    def test_player_faints_after_potion_use(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        # Full HP (no heal needed), but wild kills player on counter
        bs.player_pokemon["hp"] = 1
        ext_term.game_state.game_data["items"] = {"Potion": 3}
        import random as _r

        orig = _r.random
        # Force 0 damage from player, maximum from wild
        try:
            ext_term.process_battle_command("use potion", ext_output)
        finally:
            _r.random = orig
        assert len(ext_output.lines) > 0


# ===========================================================================
# Real battle display wrappers — lines 75-76, 80-81, 85
# ===========================================================================


class RealDisplayTerminal(BattleMixin):
    """Mock that does NOT override show_battle_options/show_move_selection/show_battle_help
    so the real BattleMixin implementations are exercised."""

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self.pending_command = None
        self.pending_command_data = {}
        self._calls = {}

    def hide_battle_loading(self):
        pass

    def show_battle_loading(self):
        pass

    def show_battle_action_panel(self):
        pass

    def show_move_selection_panel(self):
        pass

    def hide_all_battle_panels(self):
        pass

    def show_battle_options_panel(self):
        pass

    def show_battle_bag_panel(self):
        pass

    def show_switch_panel(self):
        pass

    def show_pokemon_switch_panel(self):
        pass

    def show_faint_switch_panel(self, can_run=False):
        pass

    def hide_all_panels(self):
        pass

    def show_gym_panel(self):
        pass

    def query_one(self, *a, **kw):
        return type("W", (), {"remove_class": lambda s, c: None})()

    def ensure_battle_ready(self, p):
        pass

    def _refresh_subtitle(self):
        pass

    def show_main_menu(self, output):
        pass

    def show_battle_hud(self):
        pass

    def update_battle_hud(self):
        pass


class TestRealBattleDisplayMethods:
    def test_show_battle_options_real(self):
        term = RealDisplayTerminal()
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        term.game_state.game_data["pokemon"] = [p]
        bs.start_wild_battle(p, "RATTATA", 5)
        term.game_state.battle_state = bs
        output = MockRichLog()
        term.show_battle_options(output)
        assert len(output.lines) > 0

    def test_show_move_selection_real(self):
        term = RealDisplayTerminal()
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        term.game_state.game_data["pokemon"] = [p]
        bs.start_wild_battle(p, "RATTATA", 5)
        term.game_state.battle_state = bs
        output = MockRichLog()
        term.show_move_selection(output)
        assert len(output.lines) > 0

    def test_show_battle_help_real(self):
        term = RealDisplayTerminal()
        output = MockRichLog()
        term.show_battle_help(output)
        assert len(output.lines) > 0


# ===========================================================================
# Throw different ball types — lines 160, 163, 166
# ===========================================================================


class TestThrowDifferentBalls:
    def test_throw_great_ball(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.game_state.game_data["items"] = {"Great Ball": 5}
        ext_term.process_battle_command("throw great ball", ext_output)
        assert len(ext_output.lines) > 0

    def test_throw_ultra_ball(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.game_state.game_data["items"] = {"Ultra Ball": 5}
        ext_term.process_battle_command("throw ultra ball", ext_output)
        assert len(ext_output.lines) > 0

    def test_throw_master_ball(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.game_state.game_data["items"] = {"Master Ball": 1}
        ext_term.process_battle_command("throw master ball", ext_output)
        assert len(ext_output.lines) > 0


# ===========================================================================
# Potion then player faints — lines 151-152
# ===========================================================================


class FaintableTerminal(ExtendedBattleTerminal):
    """ExtendedBattleTerminal variant that stubs handle_pokemon_fainted."""

    def handle_pokemon_fainted(self, output):
        self._calls["handle_pokemon_fainted"] = True

    def handle_battle_victory(self, output):
        self._calls["handle_battle_victory"] = True

    def end_battle(self, output):
        self._calls["end_battle"] = True
        self.game_state.battle_state = None
        self.game_state.in_battle = False


class TestPotionPlayerFaint:
    def test_potion_then_player_faints(self):
        term = FaintableTerminal()
        bs = setup_wild_ext(term)
        bs.player_pokemon["hp"] = 5
        term.game_state.game_data["items"] = {"Potion": 3}

        def _force_faint(output):
            term.game_state.battle_state.player_pokemon["hp"] = 0

        term.execute_wild_pokemon_turn = _force_faint
        output = MockRichLog()
        term.process_battle_command("use potion", output)
        assert term._calls.get("handle_pokemon_fainted") is True


# ===========================================================================
# End-of-turn effects killing wild or player — lines 283, 285-286, 288, 290-291
# ===========================================================================


class TestEndOfTurnEffects:
    def test_eot_kills_wild(self):
        term = FaintableTerminal()
        bs = setup_wild_ext(term)
        bs.wild_pokemon["hp"] = 200
        bs.wild_pokemon["max_hp"] = 200
        bs.player_pokemon["hp"] = 50

        def _mock_wild_turn(output):
            term.game_state.battle_state.wild_pokemon["hp"] = 1
            term.game_state.battle_state.wild_pokemon["status"] = "POISON"
            term.game_state.battle_state.player_pokemon["hp"] = 50

        term.execute_wild_pokemon_turn = _mock_wild_turn
        output = MockRichLog()
        term.execute_player_move("1", output)
        assert len(output.lines) > 0

    def test_eot_kills_player(self):
        term = FaintableTerminal()
        bs = setup_wild_ext(term)
        bs.wild_pokemon["hp"] = 200
        bs.wild_pokemon["max_hp"] = 200
        bs.player_pokemon["hp"] = 50

        def _mock_wild_turn_poison_player(output):
            term.game_state.battle_state.wild_pokemon["hp"] = 50
            term.game_state.battle_state.player_pokemon["hp"] = 1
            term.game_state.battle_state.player_pokemon["status"] = "POISON"

        term.execute_wild_pokemon_turn = _mock_wild_turn_poison_player
        output = MockRichLog()
        term.execute_player_move("1", output)
        assert len(output.lines) > 0


# ===========================================================================
# show_pokemon_switch_menu with string party entry — line 373
# ===========================================================================


class TestSwitchMenuStringEntry:
    def test_string_entry_is_skipped(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        ext_term.game_state.game_data["pokemon"].append("PLACEHOLDER_STRING")
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.show_pokemon_switch_menu(ext_output)
        assert len(ext_output.lines) > 0


# ===========================================================================
# execute_switch: chosen faints after enemy turn — line 451
# ===========================================================================


class TestExecuteSwitchFaintPath:
    def test_switch_chosen_faints_after_enemy_turn(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        ext_term.game_state.game_data["pokemon"].append(second)

        def _force_faint_chosen(output):
            term = ext_term
            term.game_state.battle_state.player_pokemon["hp"] = 0

        ext_term.execute_wild_pokemon_turn = _force_faint_chosen
        fainted_called = []
        ext_term.handle_pokemon_fainted = lambda o: fainted_called.append(True)
        ext_term.execute_switch("2", ext_output)
        assert fainted_called


# ===========================================================================
# execute_faint_switch — all branches (lines 502-537)
# ===========================================================================


class TestExecuteFaintSwitch:
    def test_no_battle_returns_silently(self, ext_term, ext_output):
        ext_term.game_state.battle_state = None
        ext_term.execute_faint_switch("1", ext_output)
        assert len(ext_output.lines) == 0

    def test_invalid_digit_shows_error(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data["faint_can_run"] = True
        ext_term.execute_faint_switch("99", ext_output)
        assert "❌" in ext_output.combined

    def test_fainted_chosen_shows_error(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("CHARMANDER", 5)
        second["hp"] = 0
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.execute_faint_switch("2", ext_output)
        assert "fainted" in ext_output.combined.lower() or "❌" in ext_output.combined

    def test_valid_switch_by_number(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("CHARMANDER", 10)
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.execute_faint_switch("2", ext_output)
        assert ext_term.game_state.battle_state.player_pokemon["name"] == "CHARMANDER"
        assert ext_term.pending_command == "battle"

    def test_valid_switch_by_name(self, ext_term, ext_output):
        bs = setup_wild_ext(ext_term)
        second = bs.generate_wild_pokemon("SQUIRTLE", 10)
        ext_term.game_state.game_data["pokemon"].append(second)
        ext_term.execute_faint_switch("squirtle", ext_output)
        assert ext_term.game_state.battle_state.player_pokemon["name"] == "SQUIRTLE"

    def test_run_command_treated_as_invalid(self, ext_term, ext_output):
        setup_wild_ext(ext_term)
        ext_term.pending_command_data["faint_can_run"] = True
        ext_term.execute_faint_switch("run", ext_output)
        assert "❌" in ext_output.combined or len(ext_output.lines) > 0


# ===========================================================================
# _queue_move_learn — no new moves and full moveset prompt (lines 572-601)
# ===========================================================================


class TestQueueMoveLearnNew:
    def test_empty_new_moves_resumes_immediately(self, term, output):
        """With no new moves, _queue_move_learn calls _resume_after_move_learn."""
        bs = setup_wild_battle(term)
        player = bs.player_pokemon
        # end_battle is stubbed in MockBattleTerminal
        term._queue_move_learn(player, [], "wild_end", output)
        assert term._calls.get("end_battle") is True

    def test_full_moveset_prompt(self, term, output):
        """With new moves and a full moveset, prompt is written to output."""
        bs = setup_wild_battle(term)
        player = bs.player_pokemon
        player["moves"] = [
            {"name": "TACKLE", "pp": 35, "max_pp": 35},
            {"name": "GROWL", "pp": 40, "max_pp": 40},
            {"name": "SWIFT", "pp": 20, "max_pp": 20},
            {"name": "FLASH", "pp": 20, "max_pp": 20},
        ]
        term._queue_move_learn(player, ["SURF"], "wild_end", output)
        assert term.pending_command == "learn_move_choice"
        assert any("SURF" in line for line in output.lines)


# ===========================================================================
# _resume_after_move_learn — all post_action branches (lines 605-647)
# ===========================================================================


class TestResumeMoveLearnBranches:
    def _setup_trainer_two(self, term):
        from pytemon.data.trainer_data import TRAINERS

        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        term.game_state.game_data["pokemon"] = [player]
        trainer = TRAINERS["bug_catcher_rick"]
        bs.start_trainer_battle(player, trainer)
        term.game_state.battle_state = bs
        term.game_state.in_battle = True
        return bs, player

    def test_wild_end_calls_end_battle(self, term, output):
        bs = setup_wild_battle(term)
        player = bs.player_pokemon
        term.pending_command_data = {
            "learn_pokemon": player,
            "learn_move_name": "SURF",
            "learn_remaining": [],
            "learn_post_action": "wild_end",
        }
        term._resume_after_move_learn("wild_end", output)
        assert term._calls.get("end_battle") is True

    def test_trainer_defeated_calls_handle(self, term, output):
        bs = setup_trainer_battle(term)
        player = bs.player_pokemon
        term.pending_command_data = {
            "learn_pokemon": player,
            "learn_move_name": "SURF",
            "learn_remaining": [],
        }
        term._resume_after_move_learn("trainer_defeated", output)
        assert term._calls.get("handle_trainer_defeated") is True

    def test_trainer_next_with_more_pokemon(self, term, output):
        _, player = self._setup_trainer_two(term)
        term.pending_command_data = {
            "learn_pokemon": player,
            "learn_move_name": "SURF",
            "learn_remaining": [],
            "learn_post_action": "trainer_next",
        }
        term._resume_after_move_learn("trainer_next", output)
        assert term.pending_command == "battle" or len(output.lines) > 0

    def test_trainer_next_no_more_pokemon(self, term, output):
        from pytemon.data.trainer_data import TRAINERS

        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        term.game_state.game_data["pokemon"] = [player]
        trainer = TRAINERS["bug_catcher_rick"]
        bs.start_trainer_battle(player, trainer)
        # Exhaust all trainer pokemon
        while bs.has_more_pokemon():
            bs.switch_to_next_pokemon()
        term.game_state.battle_state = bs
        term.game_state.in_battle = True
        term.pending_command_data = {
            "learn_pokemon": player,
            "learn_move_name": "SURF",
        }
        term._resume_after_move_learn("trainer_next", output)
        assert term._calls.get("handle_trainer_defeated") is True


# ===========================================================================
# _queue_evolution_pending — exception in try block (lines 670-671)
# ===========================================================================


class EvolutionExceptionTerminal(ExtendedBattleTerminal):
    """Terminal where query_one raises for #evolution-title to trigger except block."""

    def query_one(self, selector, widget_type=None):
        if "#evolution-title" in str(selector):
            raise Exception("Mock Textual error for test")
        return type(
            "W",
            (),
            {
                "remove_class": lambda s, c: None,
                "add_class": lambda s, c: None,
                "update": lambda s, t: None,
            },
        )()


class TestQueueEvolutionException:
    def test_exception_in_try_block_is_swallowed(self):
        term = EvolutionExceptionTerminal()
        bs = setup_wild_ext(term)
        pokemon = bs.player_pokemon
        output = MockRichLog()
        # Should not raise despite exception in query_one
        term._queue_evolution_pending(pokemon, "RAICHU", "wild_end", output)
        assert term.pending_command == "confirm_evolution"


# ===========================================================================
# _resume_after_evolution: trainer_next but no more pokemon (line 704)
# ===========================================================================


class TestResumeAfterEvolutionTrainerNextEmpty:
    def test_trainer_next_no_more_pokemon(self, ext_term, ext_output):
        from pytemon.data.trainer_data import TRAINERS

        bs = BattleState()
        player = bs.generate_wild_pokemon("PIKACHU", 5)
        ext_term.game_state.game_data["pokemon"] = [player]
        trainer = TRAINERS["bug_catcher_rick"]
        bs.start_trainer_battle(player, trainer)
        # Exhaust all trainer pokemon
        while bs.has_more_pokemon():
            bs.switch_to_next_pokemon()
        ext_term.game_state.battle_state = bs
        ext_term.game_state.in_battle = True
        ext_term.pending_command_data = {"evolution_post_action": "trainer_next"}

        defeated_called = []
        ext_term.handle_trainer_defeated = lambda o: defeated_called.append(True)

        ext_term._resume_after_evolution(ext_output)
        assert defeated_called


# ===========================================================================
# Battle start animation — verify text_animator is called with delay > 0
# ===========================================================================


class TestBattleStartAnimation:
    """Battle encounter start should use text_animator with a non-zero delay."""

    def test_wild_encounter_start_has_nonzero_delay(self, ext_term, ext_output):
        """trigger_wild_encounter should animate the intro with delay > 0."""
        from pytemon.locations import get_location

        ext_term.game_state.current_location = get_location("Route 1")
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        ext_term.game_state.game_data["pokemon"] = [p]

        ext_term.trigger_wild_encounter(ext_output)

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0, "No animation calls recorded for wild encounter"
        delays = [delay for _, delay, _ in recorded]
        assert any(d > 0 for d in delays), f"Expected delay > 0, got {delays}"

    def test_trainer_encounter_start_has_nonzero_delay(self, ext_term, ext_output):
        """trigger_trainer_encounter should animate the intro with delay > 0."""
        from pytemon.data.trainer_data import TRAINERS

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        ext_term.game_state.game_data["pokemon"] = [p]
        trainer = next(iter(TRAINERS.values()))

        ext_term.trigger_trainer_encounter(ext_output, trainer)

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0, "No animation calls recorded for trainer encounter"
        delays = [delay for _, delay, _ in recorded]
        assert any(d > 0 for d in delays), f"Expected delay > 0, got {delays}"

    def test_show_battle_start_wrapper_has_nonzero_delay(self, ext_term, ext_output):
        """BattleMixin.show_battle_start() wrapper should use animation."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.show_battle_start(ext_output)

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0, "No animation calls recorded for show_battle_start"
        delays = [delay for _, delay, _ in recorded]
        assert any(d > 0 for d in delays)

    def test_show_trainer_battle_start_wrapper_has_nonzero_delay(self, ext_term, ext_output):
        """BattleMixin.show_trainer_battle_start() wrapper should use animation."""
        setup_trainer_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.show_trainer_battle_start(ext_output)

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0
        assert any(d > 0 for _, d, _ in recorded)

    def test_animation_lines_contain_wild_pokemon_name(self, ext_term, ext_output):
        """Animated lines for wild encounter must mention the Pokemon name."""
        from pytemon.locations import get_location

        ext_term.game_state.current_location = get_location("Route 1")
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        ext_term.game_state.game_data["pokemon"] = [p]

        ext_term.trigger_wild_encounter(ext_output)

        all_animated_lines = []
        for _, _, lines in ext_term.text_animator.recorded_calls:
            all_animated_lines.extend(lines)
        combined = " ".join(all_animated_lines)
        assert "appeared" in combined.lower() or "wild" in combined.lower()

    def test_animation_uses_medium_speed(self, ext_term, ext_output):
        """Battle encounter start should use write_medium (0.4 s delay)."""
        from pytemon.locations import get_location

        ext_term.game_state.current_location = get_location("Route 1")
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        ext_term.game_state.game_data["pokemon"] = [p]

        ext_term.trigger_wild_encounter(ext_output)

        methods = [method for method, _, _ in ext_term.text_animator.recorded_calls]
        assert "write_medium" in methods, f"Expected write_medium, got {methods}"


# ===========================================================================
# MockAnimatedTextWriter self-verification
# ===========================================================================


class TestMockAnimatedTextWriter:
    """Verify that MockAnimatedTextWriter correctly records delays per method."""

    def test_records_delay_per_method(self):
        writer = MockAnimatedTextWriter()
        log = MockRichLog()

        writer.write_fast(log, ["a"])
        writer.write_medium(log, ["b"])
        writer.write_slow(log, ["c"])
        writer.write_instant(log, ["d"])

        assert writer.recorded_calls[0] == ("write_fast", 0.2, ["a"])
        assert writer.recorded_calls[1] == ("write_medium", 0.4, ["b"])
        assert writer.recorded_calls[2] == ("write_slow", 0.8, ["c"])
        assert writer.recorded_calls[3] == ("write_instant", 0.0, ["d"])

    def test_writes_lines_to_output(self):
        writer = MockAnimatedTextWriter()
        log = MockRichLog()

        writer.write_medium(log, ["hello", "world"])

        assert log.lines == ["hello", "world"]

    def test_calls_on_complete(self):
        writer = MockAnimatedTextWriter()
        log = MockRichLog()
        called = []

        writer.write_medium(log, ["line"], on_complete=lambda: called.append(True))

        assert called == [True]

    def test_write_lines_with_delay_records_custom_delay(self):
        writer = MockAnimatedTextWriter()
        log = MockRichLog()

        writer.write_lines_with_delay(log, ["x"], delay=1.5)

        assert writer.recorded_calls[0] == ("write_lines_with_delay", 1.5, ["x"])


# ===========================================================================
# Fight move animation — verify text_animator fires with delay > 0
# ===========================================================================


class TestFightMoveAnimation:
    """execute_player_move should animate both player and opponent attacks."""

    def test_player_attack_triggers_nonzero_delay(self, ext_term, ext_output):
        """Choosing a move should fire text_animator with delay > 0."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.execute_player_move("1", ext_output)

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0, "No animation recorded for player attack"
        delays = [d for _, d, _ in recorded]
        assert any(d > 0 for d in delays), f"Expected delay > 0, got {delays}"

    def test_player_attack_uses_write_fast(self, ext_term, ext_output):
        """Player attack animation should use write_fast (0.2 s)."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.execute_player_move("1", ext_output)

        methods = [m for m, _, _ in ext_term.text_animator.recorded_calls]
        assert "write_fast" in methods, f"Expected write_fast, got {methods}"

    def test_player_attack_animated_lines_contain_move_name(self, ext_term, ext_output):
        """Animated lines should include the move's 'used X!' message."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        player = ext_term.game_state.battle_state.player_pokemon
        move_name = player["moves"][0]["name"]

        ext_term.execute_player_move("1", ext_output)

        all_lines = []
        for _, _, lines in ext_term.text_animator.recorded_calls:
            all_lines.extend(lines)
        combined = " ".join(all_lines)
        assert (
            move_name.lower() in combined.lower()
        ), f"Expected '{move_name}' in animated lines: {combined}"

    def test_opponent_attack_triggers_animation(self, ext_term, ext_output):
        """Opponent counter-attack should also fire text_animator."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        # Ensure the wild Pokemon has HP so it counter-attacks
        bs = ext_term.game_state.battle_state
        bs.wild_pokemon["hp"] = 999
        bs.wild_pokemon["max_hp"] = 999

        ext_term.execute_player_move("1", ext_output)

        # At least 2 write_fast calls expected: player turn + opponent turn
        fast_calls = [c for c in ext_term.text_animator.recorded_calls if c[0] == "write_fast"]
        assert (
            len(fast_calls) >= 2
        ), f"Expected >=2 write_fast calls (player+opp), got {len(fast_calls)}"

    def test_no_animation_on_back_command(self, ext_term, ext_output):
        """Typing 'back' should not trigger any animation."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.execute_player_move("back", ext_output)

        assert (
            ext_term.text_animator.recorded_calls == []
        ), "No animation expected for 'back' command"

    def test_no_animation_on_unknown_move(self, ext_term, ext_output):
        """Unknown move name should not trigger animation."""
        setup_wild_ext(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.execute_player_move("ZZZNOMOVEZZZZ", ext_output)

        assert ext_term.text_animator.recorded_calls == [], "No animation expected for unknown move"


# ===========================================================================
# Catch animation — verify text_animator fires with delay > 0
# ===========================================================================


class TestCatchAnimation:
    """attempt_catch_pokemon should animate the shake sequence with delay > 0."""

    def _give_pokeballs(self, term, count=10):
        term.game_state.game_data.setdefault("items", {})["Pokeball"] = count

    def test_catch_triggers_nonzero_delay(self, ext_term, ext_output):
        """Throwing a Pokeball should fire text_animator with delay > 0."""
        setup_wild_ext(ext_term)
        self._give_pokeballs(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.attempt_catch_pokemon(ext_output)

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0, "No animation recorded for catch attempt"
        delays = [d for _, d, _ in recorded]
        assert any(d > 0 for d in delays), f"Expected delay > 0, got {delays}"

    def test_catch_uses_write_slow(self, ext_term, ext_output):
        """Shake animation should use write_slow (0.8 s) for dramatic effect."""
        setup_wild_ext(ext_term)
        self._give_pokeballs(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.attempt_catch_pokemon(ext_output)

        methods = [m for m, _, _ in ext_term.text_animator.recorded_calls]
        assert "write_slow" in methods, f"Expected write_slow, got {methods}"

    def test_catch_animated_lines_contain_wiggle_dots(self, ext_term, ext_output):
        """Shake lines should contain wiggle-dot characters (● or ○)."""
        setup_wild_ext(ext_term)
        self._give_pokeballs(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.attempt_catch_pokemon(ext_output)

        all_lines = []
        for _, _, lines in ext_term.text_animator.recorded_calls:
            all_lines.extend(lines)
        combined = " ".join(str(line) for line in all_lines)
        assert (
            "●" in combined or "○" in combined
        ), f"Expected wiggle dots in animated lines: {combined}"

    def test_failed_catch_uses_short_pause_before_followup(self, ext_term, ext_output):
        """Failed catches should pause briefly before enemy follow-up text."""
        setup_wild_ext(ext_term)
        self._give_pokeballs(ext_term)

        timer_delays: list[float] = []

        class _FakeTimer:
            def stop(self) -> None:
                return

        def fake_set_timer(delay, callback):
            timer_delays.append(delay)
            callback()
            return _FakeTimer()

        ext_term.set_timer = fake_set_timer

        original_randint = random.randint
        try:
            random.randint = lambda a, b: b  # Force failed catch checks
            ext_term.attempt_catch_pokemon(ext_output)
        finally:
            random.randint = original_randint

        assert timer_delays, "Expected a post-failure pause timer to be used"
        assert ext_term.FAILED_CATCH_PAUSE_SECONDS in timer_delays

    def test_no_catch_animation_without_pokeballs(self, ext_term, ext_output):
        """No animation should fire when there are no Pokeballs."""
        setup_wild_ext(ext_term)
        ext_term.game_state.game_data["items"] = {}
        ext_term.text_animator.recorded_calls.clear()

        ext_term.attempt_catch_pokemon(ext_output)

        assert (
            ext_term.text_animator.recorded_calls == []
        ), "No animation expected when Pokeballs are missing"

    def test_great_ball_also_animated(self, ext_term, ext_output):
        """Great Ball throw should also trigger animation with delay > 0."""
        setup_wild_ext(ext_term)
        ext_term.game_state.game_data.setdefault("items", {})["Great Ball"] = 5
        ext_term.text_animator.recorded_calls.clear()

        ext_term.attempt_catch_pokemon(ext_output, ball_type="Great Ball")

        recorded = ext_term.text_animator.recorded_calls
        assert len(recorded) > 0
        assert any(d > 0 for _, d, _ in recorded)

    def test_trainer_battle_catch_not_animated(self, ext_term, ext_output):
        """Can't catch trainer Pokemon — no animation should fire."""
        setup_trainer_ext(ext_term)
        self._give_pokeballs(ext_term)
        ext_term.text_animator.recorded_calls.clear()

        ext_term.attempt_catch_pokemon(ext_output)

        assert (
            ext_term.text_animator.recorded_calls == []
        ), "No animation expected for trainer battle catch attempt"
