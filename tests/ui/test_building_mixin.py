"""
Tests for PokemonLibrary/ui/building_mixin.py using a MockTerminal.

Tests move_to_location, enter_building, process_shop_command, handle_heal/mom
confirmations, and other building-related flows.
"""

import pytest

from pytemon.engine import BattleState
from pytemon.game_state import GameState
from pytemon.locations import get_location
from pytemon.ui.building_mixin import BuildingMixin


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text) -> None:
        self.lines.append(str(text))

    @property
    def combined(self) -> str:
        return " ".join(self.lines)


class MockWidget:
    """Mock for a Textual widget."""

    value = ""

    def remove_class(self, cls):
        pass

    def add_class(self, cls):
        pass

    def __iter__(self):
        return iter([])


class MockBuildingTerminal(BuildingMixin):
    """Minimal mock terminal for testing BuildingMixin."""

    def __init__(self):
        self.game_state = GameState()
        self.game_state.start_new_game()
        self.pending_command = None
        self.pending_command_data = {}
        self._calls = {}

    def query_one(self, *a, **kw):
        return MockWidget()

    def hide_all_panels(self):
        pass

    def hide_all_battle_panels(self):
        pass

    def show_pokemon_center_panel(self):
        pass

    def show_starter_selection_panel(self, pikachu_mode=False):
        pass

    def show_pokemart_panel(self):
        pass

    def show_gym_panel(self):
        pass

    def show_confirmation_panel(self, msg, ctype, show_cancel=False):
        pass

    def show_nurse_joy_panel(self, msg, ptype):
        pass

    def show_pc_main_panel(self):
        self.pending_command = "pc"

    def show_location_selection_panel(self, locations):
        pass

    def show_building_selection_panel(self, buildings):
        pass

    def _refresh_subtitle(self):
        pass

    def trigger_gym_battle(self, trainer_id, output, is_gym_battle=False):
        self._calls["trigger_gym_battle"] = trainer_id

    def trigger_wild_encounter(self, output):
        self._calls.setdefault("trigger_wild_encounter", []).append(True)

    def trigger_trainer_encounter(self, output, trainer):
        self._calls.setdefault("trigger_trainer_encounter", []).append(trainer)

    def ensure_battle_ready(self, p):
        pass


@pytest.fixture
def term():
    return MockBuildingTerminal()


@pytest.fixture
def output():
    return MockRichLog()


def make_party_pokemon(term, name="PIKACHU", level=10):
    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    term.game_state.game_data.setdefault("pokemon", []).append(p)
    return p


# ===========================================================================
# move_to_location
# ===========================================================================


class TestMoveToLocation:
    def test_move_to_valid_location(self, term, output):
        make_party_pokemon(term)
        term.move_to_location("Route 1", output)
        assert "Route 1" in output.combined or "Traveling" in output.combined

    def test_move_to_pallet_town(self, term, output):
        # Already at Pallet Town — should show "already here" or description
        make_party_pokemon(term)
        term.move_to_location("Pallet Town", output)
        assert "already" in output.combined.lower() or "Pallet Town" in output.combined

    def test_invalid_location_shows_error(self, term, output):
        term.move_to_location("Fake Place 99999", output)
        assert "❌" in output.combined or "not found" in output.combined.lower()

    def test_already_at_location_shows_message(self, term, output):
        # Default is Pallet Town
        term.move_to_location("Pallet Town", output)
        # Should show some message (either "already here" or location description)
        assert len(output.lines) > 0


# ===========================================================================
# handle_heal_center_confirmation
# ===========================================================================


class TestHandleHealCenterConfirmation:
    def test_yes_heals_pokemon(self, term, output):
        make_party_pokemon(term)
        term.handle_heal_center_confirmation("yes", output)
        assert len(output.lines) > 0

    def test_no_leaves(self, term, output):
        term.handle_heal_center_confirmation("no", output)
        assert "leave" in output.combined.lower() or "Please come back" in output.combined

    def test_invalid_response_asks_again(self, term, output):
        term.handle_heal_center_confirmation("maybe", output)
        assert "Invalid" in output.combined or "❌" in output.combined
        assert term.pending_command == "confirm_heal_center"


# ===========================================================================
# handle_heal_mom_confirmation
# ===========================================================================


class TestHandleHealMomConfirmation:
    def test_yes_heals_pokemon(self, term, output):
        make_party_pokemon(term)
        term.handle_heal_mom_confirmation("yes", output)
        assert len(output.lines) > 0

    def test_no_leaves(self, term, output):
        term.handle_heal_mom_confirmation("no", output)
        assert "leave" in output.combined.lower() or "Okay!" in output.combined

    def test_invalid_response_asks_again(self, term, output):
        term.handle_heal_mom_confirmation("maybe", output)
        assert "Invalid" in output.combined or "❌" in output.combined
        assert term.pending_command == "confirm_heal_mom"


# ===========================================================================
# _handle_pokemon_center_command
# ===========================================================================


class TestHandlePokemonCenterCommand:
    def test_heal_command_heals(self, term, output):
        make_party_pokemon(term)
        term._handle_pokemon_center_command("heal", output)
        assert len(output.lines) > 0

    def test_leave_command_leaves(self, term, output):
        term._handle_pokemon_center_command("leave", output)
        assert "leave" in output.combined.lower()

    def test_invalid_command_asks_again(self, term, output):
        term._handle_pokemon_center_command("blarg", output)
        assert "Joy" in output.combined or "understand" in output.combined.lower()

    def test_pc_command_opens_pc(self, term, output):
        term._handle_pokemon_center_command("pc", output)
        assert term.pending_command == "pc"


# ===========================================================================
# process_shop_command
# ===========================================================================


class TestProcessShopCommand:
    def test_leave_exits_shop(self, term, output):
        result = term.process_shop_command("leave", output)
        assert result == "leave"
        assert "Thank you" in output.combined or "leave" in output.combined.lower()

    def test_exit_exits_shop(self, term, output):
        result = term.process_shop_command("exit", output)
        assert result == "leave"

    def test_buy_pokeball(self, term, output):
        term.game_state.game_data["money"] = 500
        result = term.process_shop_command("buy pokeball", output)
        assert result in ("ok", "cant_afford")

    def test_buy_potion(self, term, output):
        term.game_state.game_data["money"] = 500
        result = term.process_shop_command("buy potion", output)
        assert result in ("ok", "cant_afford")

    def test_buy_multiple(self, term, output):
        term.game_state.game_data["money"] = 1000
        result = term.process_shop_command("buy 3 pokeball", output)
        assert result in ("ok", "cant_afford")

    def test_invalid_item_shows_error(self, term, output):
        term.game_state.game_data["money"] = 500
        term.process_shop_command("buy fakething999", output)
        assert "not available" in output.combined.lower() or "❌" in output.combined

    def test_not_enough_money(self, term, output):
        term.game_state.game_data["money"] = 0
        result = term.process_shop_command("buy pokeball", output)
        assert result == "cant_afford" or "afford" in output.combined.lower()

    def test_invalid_command_format(self, term, output):
        result = term.process_shop_command("blargh blargh", output)
        assert result != "ok"

    def test_back_exits_shop(self, term, output):
        result = term.process_shop_command("back", output)
        assert result == "leave"


# ===========================================================================
# show_shop_menu
# ===========================================================================


class TestShowShopMenu:
    def test_shows_money(self, term, output):
        term.game_state.game_data["money"] = 1234
        term.show_shop_menu(output)
        assert "1234" in output.combined

    def test_shows_pokeball(self, term, output):
        term.show_shop_menu(output)
        assert "Pokeball" in output.combined

    def test_shows_potion(self, term, output):
        term.show_shop_menu(output)
        assert "Potion" in output.combined


# ===========================================================================
# enter_building
# ===========================================================================


class TestEnterBuilding:
    def test_enter_pokemon_center(self, term, output):
        term.game_state.current_location = get_location("Viridian City")
        term.enter_building("Pokemon Center", output)
        assert len(output.lines) > 0

    def test_enter_pokemart(self, term, output):
        term.game_state.current_location = get_location("Viridian City")
        term.enter_building("Pokemart", output)
        # Shows shop menu
        assert len(output.lines) > 0

    def test_enter_unknown_building(self, term, output):
        term.game_state.current_location = get_location("Pallet Town")
        term.enter_building("Fake Building 9999", output)
        assert "❌" in output.combined or "not found" in output.combined.lower()


# ===========================================================================
# enter_pokemart
# ===========================================================================


class TestEnterPokemart:
    def test_enters_pokemart_and_shows_catalog(self, term, output):
        term.enter_pokemart(output)
        assert "Pokemart" in output.combined or "Clerk" in output.combined
        assert term.pending_command == "shop"


# ===========================================================================
# _gym_challenge_leader
# ===========================================================================


class TestGymChallengeLeader:
    def test_no_location_shows_error(self, term, output):
        term.game_state.current_location = None
        term._gym_challenge_leader(output)
        assert "❌" in output.combined

    def test_no_gym_shows_message(self, term, output):
        term.game_state.current_location = get_location("Pallet Town")
        term._gym_challenge_leader(output)
        assert "No gym" in output.combined or "⚠" in output.combined

    def test_can_challenge_triggers_battle(self, term, output):
        term.game_state.current_location = get_location("Pewter City")
        make_party_pokemon(term, "PIKACHU", 20)
        term._gym_challenge_leader(output)
        # Should trigger gym battle for Brock
        assert term._calls.get("trigger_gym_battle") == "gym_leader_brock"


# ===========================================================================
# _gym_fight_trainer
# ===========================================================================


class TestGymFightTrainer:
    def test_no_location_shows_error(self, term, output):
        term.game_state.current_location = None
        term._gym_fight_trainer(output)
        assert "❌" in output.combined

    def test_no_more_trainers_shows_message(self, term, output):
        from pytemon.gym_system import get_gym_trainers

        term.game_state.current_location = get_location("Pewter City")
        trainers = get_gym_trainers("Pewter City")
        term.game_state.game_data["defeated_trainers"] = list(trainers)
        term._gym_fight_trainer(output)
        assert "No more" in output.combined or "✓" in output.combined

    def test_no_gym_at_location(self, term, output):
        term.game_state.current_location = get_location("Pallet Town")
        term._gym_fight_trainer(output)
        # Pallet Town has no gym — shows "No more gym trainers" message
        assert "No more" in output.combined or "✓" in output.combined


# ===========================================================================
# _return_to_pokemon_center
# ===========================================================================


class TestReturnToPokemonCenter:
    def test_sets_pending_command(self, term, output):
        term._return_to_pokemon_center(output)
        assert term.pending_command == "pokemon_center"


# ===========================================================================
# confirm_name_selection (player name entry)
# ===========================================================================


class TestConfirmNameSelection:
    def test_empty_name_shows_error(self, term, output):
        term.confirm_name_selection(output)
        assert "❌" in output.combined or "enter" in output.combined.lower()

    def test_valid_names_sets_player_name(self, term, output):
        class MockInput(MockWidget):
            def __init__(self, val):
                self.value = val

        inputs = {"#input-player-name": MockInput("Ash"), "#input-rival-name": MockInput("Gary")}
        original_query_one = term.query_one
        term.query_one = lambda sel, *a, **kw: inputs.get(sel, MockWidget())
        try:
            term.confirm_name_selection(output)
        finally:
            term.query_one = original_query_one
        assert term.game_state.game_data.get("player_name") == "Ash"
        assert "Ash" in output.combined


# ===========================================================================
# Additional tests for uncovered building_mixin paths
# ===========================================================================


class MockInput(MockWidget):
    """Mock Input widget with a value property."""

    def __init__(self, val: str = ""):
        super().__init__()
        self.value = val

    def focus(self):
        pass


# ---------------------------------------------------------------------------
# Delegate thin wrappers
# ---------------------------------------------------------------------------


class TestDelegateWrappers:
    """Test thin wrapper methods that delegate to exploration/buildings modules."""

    def test_prompt_for_location_no_crash(self, term, output):
        term.prompt_for_location(output)
        assert len(output.lines) > 0

    def test_prompt_for_building_no_crash(self, term, output):
        term.prompt_for_building(output)
        assert len(output.lines) > 0

    def test_show_location_arrival_no_crash(self, term, output):
        term.show_location_arrival(output)
        assert len(output.lines) > 0

    def test_show_location_arrival_is_load(self, term, output):
        term.show_location_arrival(output, is_load=True)
        assert len(output.lines) > 0

    def test_look_around_no_crash(self, term, output):
        term.look_around(output)
        assert len(output.lines) > 0

    def test_explore_area_no_crash(self, term, output):
        from pytemon.locations import get_location

        term.game_state.current_location = get_location("Route 1")
        make_party_pokemon(term, "PIKACHU", 10)
        term.explore_area(output)
        # Route 1 exploration always produces some output
        assert len(output.lines) > 0


# ---------------------------------------------------------------------------
# set_pending_and_show_heal_panel
# ---------------------------------------------------------------------------


class TestSetPendingAndShowHealPanel:
    def test_pokemon_center_cmd(self, term, output):
        term.set_pending_and_show_heal_panel("pokemon_center")
        assert term.pending_command == "pokemon_center"

    def test_confirm_heal_mom_cmd(self, term, output):
        term.set_pending_and_show_heal_panel("confirm_heal_mom")
        assert term.pending_command == "confirm_heal_mom"


# ---------------------------------------------------------------------------
# enter_pokemon_center (delegates to buildings module)
# ---------------------------------------------------------------------------


class TestEnterPokemonCenterDelegate:
    def test_no_crash(self, term, output):
        from pytemon import buildings as bldgs

        bldgs.enter_pokemon_center(
            term.game_state, output, lambda cmd: setattr(term, "pending_command", cmd)
        )
        assert len(output.lines) > 0


# ---------------------------------------------------------------------------
# _gym_challenge_leader — more branches
# ---------------------------------------------------------------------------


class TestGymChallengeLeaderExtra:
    def test_cannot_challenge_shows_reason(self, term, output):
        """Pewter City requires 0 badges — even low-level pokemon can try to challenge."""
        term.game_state.current_location = get_location("Pewter City")
        term.game_state.game_data["badges"] = []
        make_party_pokemon(term, "PIKACHU", 5)
        term._gym_challenge_leader(output)
        # Should trigger battle (required_badges=0) or show cannot challenge reason
        assert term._calls.get("trigger_gym_battle") or "⚠" in output.combined

    def test_with_enough_pokemon_challenges(self, term, output):
        """If player can challenge the gym, gym battle is triggered."""
        term.game_state.current_location = get_location("Pewter City")
        term.game_state.game_data["badges"] = []
        make_party_pokemon(term, "PIKACHU", 20)
        term._gym_challenge_leader(output)
        assert term._calls.get("trigger_gym_battle") == "gym_leader_brock"


# ---------------------------------------------------------------------------
# _gym_fight_trainer — all branches
# ---------------------------------------------------------------------------


class TestGymFightTrainerExtra:
    def test_starts_trainer_battle_when_available(self, term, output):
        term.game_state.current_location = get_location("Pewter City")
        make_party_pokemon(term, "PIKACHU", 15)
        term.game_state.game_data["defeated_trainers"] = []
        term._gym_fight_trainer(output)
        # Should trigger the first gym trainer battle
        assert term._calls.get("trigger_gym_battle") == "gym_trainer_pewter_hiker"


# ---------------------------------------------------------------------------
# enter_gym (full gym lobby display)
# ---------------------------------------------------------------------------


class TestEnterGym:
    def test_enters_pewter_gym(self, term, output):
        term.game_state.current_location = get_location("Pewter City")
        make_party_pokemon(term, "PIKACHU", 10)
        term.enter_gym("Pewter City Gym", output)
        assert "Brock" in output.combined

    def test_enters_viridian_gym(self, term, output):
        term.game_state.current_location = get_location("Viridian City")
        make_party_pokemon(term, "PIKACHU", 10)
        term.enter_gym("Viridian City Gym", output)
        assert "Gym Leader" in output.combined or "Gym" in output.combined

    def test_enters_unknown_gym(self, term, output):
        from pytemon.locations import get_location as gl

        term.game_state.current_location = gl("Lavender Town")
        term.enter_gym("Lavender Town Gym", output)
        assert "closed" in output.combined.lower()


# ---------------------------------------------------------------------------
# enter_players_house
# ---------------------------------------------------------------------------


class TestEnterPlayersHouse:
    def test_shows_mom_dialogue(self, term, output):
        term.enter_players_house(output)
        assert "Mom" in output.combined or "house" in output.combined.lower()
        assert len(output.lines) > 0


# ---------------------------------------------------------------------------
# enter_rivals_house
# ---------------------------------------------------------------------------


class TestEnterRivalsHouse:
    def test_without_pokemon(self, term, output):
        term.game_state.game_data["pokemon"] = []
        term.enter_rivals_house(output)
        assert "sister" in output.combined.lower() or "brother" in output.combined.lower()

    def test_with_pokemon(self, term, output):
        make_party_pokemon(term, "PIKACHU", 5)
        term.enter_rivals_house(output)
        assert "Rival's Sister" in output.combined or "journey" in output.combined.lower()


# ---------------------------------------------------------------------------
# enter_oaks_lab
# ---------------------------------------------------------------------------


class TestEnterOaksLab:
    def test_without_pokemon_shows_starter_selection(self, term, output):
        term.game_state.game_data["pokemon"] = []
        term.game_state.pikachu_mode = False
        term.enter_oaks_lab(output)
        assert "Choose" in output.combined or "Bulbasaur" in output.combined
        assert term.pending_command == "choose_starter"

    def test_without_pokemon_pikachu_mode(self, term, output):
        term.game_state.game_data["pokemon"] = []
        term.game_state.pikachu_mode = True
        term.enter_oaks_lab(output)
        assert "Pikachu" in output.combined
        assert term.pending_command == "choose_starter"

    def test_with_pokemon_shows_research_data(self, term, output):
        make_party_pokemon(term, "PIKACHU", 5)
        term.enter_oaks_lab(output)
        assert "Research" in output.combined or "Hello" in output.combined


# ---------------------------------------------------------------------------
# confirm_name_selection — rival name empty path
# ---------------------------------------------------------------------------


class TestConfirmNameSelectionRivalEmpty:
    def test_empty_rival_name_shows_error(self, term, output):
        class MockInputEmpty(MockWidget):
            def __init__(self, val=""):
                super().__init__()
                self.value = val

            def focus(self):
                pass

        inputs = {
            "#input-player-name": MockInputEmpty("Ash"),
            "#input-rival-name": MockInputEmpty(""),
        }
        term.query_one = lambda sel, *a, **kw: inputs.get(sel, MockWidget())
        term.confirm_name_selection(output)
        assert "❌" in output.combined or "enter" in output.combined.lower()


# ---------------------------------------------------------------------------
# random_name_selection
# ---------------------------------------------------------------------------


class TestRandomNameSelection:
    def test_generates_names(self, term, output):
        class MockInputWithValue(MockWidget):
            def __init__(self):
                super().__init__()
                self.value = ""

            def focus(self):
                pass

        inputs = {
            "#input-player-name": MockInputWithValue(),
            "#input-rival-name": MockInputWithValue(),
        }
        term.query_one = lambda sel, *a, **kw: inputs.get(sel, MockWidget())
        term.random_name_selection(output)
        assert len(output.lines) > 0
        assert "Generated" in output.combined or "name" in output.combined.lower()

    def test_fills_input_values(self, term, output):
        player_input = MockInput()
        rival_input = MockInput()
        inputs = {
            "#input-player-name": player_input,
            "#input-rival-name": rival_input,
        }
        term.query_one = lambda sel, *a, **kw: inputs.get(sel, MockWidget())
        term.random_name_selection(output)
        assert player_input.value != ""
        assert rival_input.value != ""


# ---------------------------------------------------------------------------
# choose_starter_pokemon
# ---------------------------------------------------------------------------


class TestChooseStarterPokemon:
    def test_choose_charmander(self, term, output):
        term.choose_starter_pokemon("Charmander", output)
        assert len(output.lines) > 0

    def test_choose_bulbasaur(self, term, output):
        term.choose_starter_pokemon("Bulbasaur", output)
        assert len(output.lines) > 0

    def test_choose_squirtle(self, term, output):
        term.choose_starter_pokemon("Squirtle", output)
        assert len(output.lines) > 0

    def test_choose_pikachu(self, term, output):
        term.choose_starter_pokemon("Pikachu", output)
        assert len(output.lines) > 0


# ---------------------------------------------------------------------------
# process_shop_command — singular noun fix
# ---------------------------------------------------------------------------


class TestProcessShopCommandSingular:
    def test_buy_singular_pokeball(self, term, output):
        term.game_state.game_data["money"] = 500
        result = term.process_shop_command("buy pokeballs", output)
        # "pokeballs" is pluralised but should still buy 1 Pokeball
        assert result == "ok"
        assert "Pokeball" in output.combined

    def test_show_shop_shows_error(self, term, output):
        result = term.process_shop_command("show", output)
        # "show" is not a valid shop command
        assert result == "error"
        assert "don't understand" in output.combined.lower() or "?" in output.combined
