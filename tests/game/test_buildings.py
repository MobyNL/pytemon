"""
Comprehensive tests for PokemonLibrary/buildings.py

Covers: enter_building, enter_pokemon_center, enter_pokemart, show_shop_menu,
process_shop_command, enter_players_house, perform_pokemon_center_heal,
perform_mom_heal, enter_rivals_house, enter_oaks_lab, choose_starter_pokemon.
"""

import pytest

from pytemon.buildings import (
    choose_starter_pokemon,
    enter_bills_house,
    enter_building,
    enter_museum,
    enter_oaks_lab,
    enter_players_house,
    enter_pokemart,
    enter_pokemon_center,
    enter_rivals_house,
    perform_mom_heal,
    perform_pokemon_center_heal,
    process_shop_command,
    show_shop_menu,
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


def make_party_pokemon(gs, name="PIKACHU", level=10, hp=None):
    from pytemon.engine import BattleState

    bs = BattleState()
    p = bs.generate_wild_pokemon(name, level)
    if hp is not None:
        p["hp"] = hp
    gs.game_data.setdefault("pokemon", []).append(p)
    return p


# ===========================================================================
# enter_building
# ===========================================================================


class TestEnterBuilding:
    def test_no_location_shows_error(self, gs, output):
        gs.current_location = None
        enter_building(gs, "Pokemon Center", output, noop)
        assert "❌" in output.combined

    def test_non_town_shows_no_buildings(self, gs, output):
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        enter_building(gs, "Pokemon Center", output, noop)
        assert "no buildings" in output.combined.lower()

    def test_unknown_building_shows_error(self, gs, output):
        enter_building(gs, "Nonexistent Building 9999", output, noop)
        assert "not found" in output.combined.lower() or "❌" in output.combined

    def test_enter_pokemon_center(self, gs, output):
        pending = []
        make_party_pokemon(gs)
        enter_building(gs, "Pokemon Center", output, lambda cmd: pending.append(cmd))
        assert len(output.lines) > 0

    def test_enter_pokemart(self, gs, output):
        pending = []
        enter_building(gs, "Pokemart", output, lambda cmd: pending.append(cmd))
        assert len(output.lines) > 0

    def test_enter_players_house(self, gs, output):
        enter_building(gs, "Player's House", output, noop)
        assert len(output.lines) > 0

    def test_enter_rivals_house(self, gs, output):
        enter_building(gs, "Rival's House", output, noop)
        assert len(output.lines) > 0

    def test_enter_oaks_lab(self, gs, output):
        pending = []
        enter_building(gs, "Oak's Lab", output, lambda cmd: pending.append(cmd))
        assert len(output.lines) > 0


# ===========================================================================
# enter_pokemon_center
# ===========================================================================


class TestEnterPokemonCenter:
    def test_no_pokemon_exits_immediately(self, gs, output):
        gs.game_data["pokemon"] = []
        enter_pokemon_center(gs, output, noop)
        assert "don't have any" in output.combined.lower() or "no Pokemon" in output.combined

    def test_with_pokemon_sets_pending_command(self, gs, output):
        pending = []
        make_party_pokemon(gs)
        enter_pokemon_center(gs, output, lambda cmd: pending.append(cmd))
        assert "pokemon_center" in pending

    def test_writes_welcome_message(self, gs, output):
        make_party_pokemon(gs)
        enter_pokemon_center(gs, output, noop)
        assert "Nurse Joy" in output.combined or "Pokemon Center" in output.combined


# ===========================================================================
# enter_pokemart
# ===========================================================================


class TestEnterPokemart:
    def test_writes_shop_menu(self, gs, output):
        pending = []
        enter_pokemart(gs, output, lambda cmd: pending.append(cmd))
        assert "Pokemart" in output.combined or "shop" in output.combined.lower()

    def test_sets_shop_pending_command(self, gs, output):
        pending = []
        enter_pokemart(gs, output, lambda cmd: pending.append(cmd))
        assert "shop" in pending

    def test_calls_show_pokemart_callback(self, gs, output):
        called = []
        enter_pokemart(gs, output, noop, show_pokemart_panel_callback=lambda: called.append(True))
        assert called


# ===========================================================================
# show_shop_menu
# ===========================================================================


class TestShowShopMenu:
    def test_writes_items(self, gs, output):
        show_shop_menu(gs, output)
        assert len(output.lines) > 0

    def test_shows_pokeball(self, gs, output):
        show_shop_menu(gs, output)
        assert "Pokeball" in output.combined

    def test_shows_money(self, gs, output):
        gs.game_data["money"] = 9999
        show_shop_menu(gs, output)
        assert "9999" in output.combined


# ===========================================================================
# process_shop_command
# ===========================================================================


class TestProcessShopCommand:
    def test_leave_exits_shop(self, gs, output):
        pending = []
        process_shop_command(gs, "leave", output, lambda cmd: pending.append(cmd))
        assert "Thank you" in output.combined or "leave" in output.combined.lower()
        assert "shop" not in pending  # Should NOT re-set shop pending on leave

    def test_buy_known_item(self, gs, output):
        gs.game_data["money"] = 10000
        pending = []
        process_shop_command(gs, "buy potion", output, lambda cmd: pending.append(cmd))
        assert gs.game_data.get("items", {}).get("Potion", 0) >= 1

    def test_buy_with_quantity(self, gs, output):
        gs.game_data["money"] = 10000
        pending = []
        process_shop_command(gs, "buy 3 potion", output, lambda cmd: pending.append(cmd))
        assert gs.game_data.get("items", {}).get("Potion", 0) >= 3

    def test_buy_unknown_item_shows_error(self, gs, output):
        gs.game_data["money"] = 10000
        pending = []
        process_shop_command(gs, "buy nonexistent", output, lambda cmd: pending.append(cmd))
        assert "not sold" in output.combined.lower() or "❌" in output.combined

    def test_buy_not_enough_money(self, gs, output):
        gs.game_data["money"] = 0
        pending = []
        process_shop_command(gs, "buy potion", output, lambda cmd: pending.append(cmd))
        assert "money" in output.combined.lower() or "❌" in output.combined

    def test_unrecognized_command_shows_prompt(self, gs, output):
        pending = []
        process_shop_command(gs, "dance", output, lambda cmd: pending.append(cmd))
        assert "shop" in pending or "don't understand" in output.combined.lower()

    def test_buy_plural_item_name(self, gs, output):
        gs.game_data["money"] = 10000
        pending = []
        process_shop_command(gs, "buy pokeballs", output, lambda cmd: pending.append(cmd))
        assert gs.game_data.get("items", {}).get("Pokeball", 0) >= 1

    def test_exit_synonyms(self, gs, output):
        for cmd in ("exit", "done", "goodbye", "bye", "no", "back"):
            out = MockRichLog()
            gs2 = GameState()
            gs2.start_new_game()
            process_shop_command(gs2, cmd, out, noop)
            assert len(out.lines) > 0


# ===========================================================================
# enter_players_house
# ===========================================================================


class TestEnterPlayersHouse:
    def test_no_pokemon_shows_mom_dialogue(self, gs, output):
        gs.game_data["pokemon"] = []
        enter_players_house(gs, output, noop)
        assert "Mom" in output.combined

    def test_healthy_pokemon_shows_healthy_message(self, gs, output):
        make_party_pokemon(gs)  # Full HP by default
        enter_players_house(gs, output, noop)
        assert len(output.lines) > 0

    def test_injured_pokemon_sets_pending(self, gs, output):
        make_party_pokemon(gs, hp=5)
        pending = []
        enter_players_house(gs, output, lambda cmd: pending.append(cmd))
        assert "confirm_heal_mom" in pending

    def test_player_name_shown(self, gs, output):
        gs.game_data["player_name"] = "TestTrainer"
        gs.game_data["pokemon"] = []
        enter_players_house(gs, output, noop)
        assert "TESTTRAINER" in output.combined


# ===========================================================================
# perform_pokemon_center_heal
# ===========================================================================


class TestPerformPokemonCenterHeal:
    def test_heals_all_pokemon(self, gs, output):
        p = make_party_pokemon(gs, hp=1)
        perform_pokemon_center_heal(gs, output)
        assert p["hp"] == p["max_hp"]

    def test_cures_status(self, gs, output):
        p = make_party_pokemon(gs)
        p["status"] = "POISON"
        perform_pokemon_center_heal(gs, output)
        assert p["status"] is None

    def test_restores_pp(self, gs, output):
        p = make_party_pokemon(gs)
        for move in p.get("moves", []):
            move["pp"] = 0
        perform_pokemon_center_heal(gs, output)
        for move in p.get("moves", []):
            assert move["pp"] > 0

    def test_writes_output(self, gs, output):
        make_party_pokemon(gs)
        perform_pokemon_center_heal(gs, output)
        assert len(output.lines) > 0

    def test_records_last_pokemon_center(self, gs, output):
        make_party_pokemon(gs)
        perform_pokemon_center_heal(gs, output)
        assert gs.game_data.get("last_pokemon_center") is not None


# ===========================================================================
# perform_mom_heal
# ===========================================================================


class TestPerformMomHeal:
    def test_heals_all_pokemon(self, gs, output):
        p = make_party_pokemon(gs, hp=5)
        perform_mom_heal(gs, output)
        assert p["hp"] == p["max_hp"]

    def test_cures_status(self, gs, output):
        p = make_party_pokemon(gs)
        p["status"] = "PARALYSIS"
        perform_mom_heal(gs, output)
        assert p["status"] is None

    def test_writes_output(self, gs, output):
        make_party_pokemon(gs)
        perform_mom_heal(gs, output)
        assert "Mom" in output.combined


# ===========================================================================
# enter_rivals_house
# ===========================================================================


class TestEnterRivalsHouse:
    def test_no_pokemon_shows_rival_not_here(self, gs, output):
        gs.game_data["pokemon"] = []
        enter_rivals_house(gs, output)
        assert len(output.lines) > 0

    def test_with_pokemon_shows_journey_message(self, gs, output):
        make_party_pokemon(gs)
        enter_rivals_house(gs, output)
        assert len(output.lines) > 0

    def test_uses_rival_name(self, gs, output):
        gs.game_data["rival_name"] = "Gary"
        enter_rivals_house(gs, output)
        assert "GARY" in output.combined


# ===========================================================================
# enter_oaks_lab
# ===========================================================================


class TestEnterOaksLab:
    def test_no_pokemon_shows_starter_choice(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = False
        pending = []
        enter_oaks_lab(gs, output, lambda cmd: pending.append(cmd))
        assert "choose_starter" in pending
        assert "Bulbasaur" in output.combined or "Charmander" in output.combined

    def test_pikachu_mode_shows_pikachu(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = True
        pending = []
        enter_oaks_lab(gs, output, lambda cmd: pending.append(cmd))
        assert "Pikachu" in output.combined

    def test_with_pokemon_shows_pokedex_message(self, gs, output):
        make_party_pokemon(gs)
        enter_oaks_lab(gs, output, noop)
        assert "Oak" in output.combined or "Pokedex" in output.combined

    def test_starter_panel_callback_called(self, gs, output):
        gs.game_data["pokemon"] = []
        called = []
        enter_oaks_lab(
            gs, output, noop, show_starter_panel_callback=lambda pika: called.append(pika)
        )
        assert called


# ===========================================================================
# choose_starter_pokemon
# ===========================================================================


class TestChooseStarterPokemon:
    def test_choose_bulbasaur(self, gs, output):
        gs.game_data["pokemon"] = []
        pending = []
        choose_starter_pokemon(gs, "bulbasaur", output, lambda cmd: pending.append(cmd))
        names = [p.get("name") for p in gs.game_data.get("pokemon", [])]
        assert "BULBASAUR" in names
        pokedex_data = gs.game_data.get("pokedex", {})
        assert "BULBASAUR" in pokedex_data.get("caught", [])
        assert "BULBASAUR" in pokedex_data.get("seen", [])

    def test_choose_charmander(self, gs, output):
        gs.game_data["pokemon"] = []
        pending = []
        choose_starter_pokemon(gs, "charmander", output, lambda cmd: pending.append(cmd))
        names = [p.get("name") for p in gs.game_data.get("pokemon", [])]
        assert "CHARMANDER" in names

    def test_choose_squirtle(self, gs, output):
        gs.game_data["pokemon"] = []
        pending = []
        choose_starter_pokemon(gs, "squirtle", output, lambda cmd: pending.append(cmd))
        names = [p.get("name") for p in gs.game_data.get("pokemon", [])]
        assert "SQUIRTLE" in names

    def test_choose_with_prefix(self, gs, output):
        gs.game_data["pokemon"] = []
        pending = []
        choose_starter_pokemon(gs, "choose bulbasaur", output, lambda cmd: pending.append(cmd))
        names = [p.get("name") for p in gs.game_data.get("pokemon", [])]
        assert "BULBASAUR" in names

    def test_invalid_starter_shows_error(self, gs, output):
        gs.game_data["pokemon"] = []
        pending = []
        choose_starter_pokemon(gs, "Mewtwo", output, lambda cmd: pending.append(cmd))
        assert "Invalid" in output.combined or "choose_starter" in pending

    def test_pikachu_without_mode_shows_error(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = False
        pending = []
        choose_starter_pokemon(gs, "pikachu", output, lambda cmd: pending.append(cmd))
        assert "not an available" in output.combined.lower() or "❌" in output.combined

    def test_pikachu_with_mode_gives_pikachu(self, gs, output):
        gs.game_data["pokemon"] = []
        gs.pikachu_mode = True
        pending = []
        choose_starter_pokemon(gs, "pikachu", output, lambda cmd: pending.append(cmd))
        # May trigger a battle with rival, so check if pikachu was added or battle started
        assert len(output.lines) > 0
        pokedex_data = gs.game_data.get("pokedex", {})
        assert "PIKACHU" in pokedex_data.get("caught", [])
        assert "PIKACHU" in pokedex_data.get("seen", [])

    def test_gives_starter_potions(self, gs, output):
        gs.game_data["pokemon"] = []
        choose_starter_pokemon(gs, "charmander", output, noop)
        assert gs.game_data.get("items", {}).get("Potion", 0) > 0


# ===========================================================================
# enter_bills_house
# ===========================================================================


class TestEnterBillsHouse:
    def test_first_visit_shows_bill_header(self, gs, output):
        enter_bills_house(gs, output)
        assert "BILL" in output.combined.upper() or "Bill" in output.combined

    def test_first_visit_gives_ss_anne_ticket(self, gs, output):
        enter_bills_house(gs, output)
        bag = gs.game_data.get("bag", {})
        assert bag.get("S.S. Anne Ticket", 0) >= 1

    def test_first_visit_sets_received_ss_ticket_flag(self, gs, output):
        enter_bills_house(gs, output)
        assert gs.game_data["story_flags"].get("received_ss_ticket") is True

    def test_first_visit_sets_visited_bills_house_flag(self, gs, output):
        enter_bills_house(gs, output)
        assert gs.game_data["story_flags"].get("visited_bills_house") is True

    def test_repeat_visit_does_not_add_second_ticket(self, gs, output):
        enter_bills_house(gs, output)
        output.lines.clear()
        enter_bills_house(gs, output)
        bag = gs.game_data.get("bag", {})
        assert bag.get("S.S. Anne Ticket", 0) == 1

    def test_repeat_visit_shows_repeat_dialogue(self, gs, output):
        enter_bills_house(gs, output)
        output.lines.clear()
        enter_bills_house(gs, output)
        combined = output.combined.lower()
        assert "welcome back" in combined or "smoothly" in combined or "remember" in combined

    def test_ticket_awarded_only_once_across_many_visits(self, gs, output):
        for _ in range(3):
            enter_bills_house(gs, output)
        bag = gs.game_data.get("bag", {})
        assert bag.get("S.S. Anne Ticket", 0) == 1

    def test_enter_building_routes_to_bills_house(self, gs, output):
        from pytemon.locations import TYPE_TOWN, Location

        # enter_building only routes to buildings for town-type locations;
        # create a stub town that lists "Bill's House" so the routing branch fires.
        fake_town = Location(
            name="Fake Town",
            location_type=TYPE_TOWN,
            description="test",
            exits={},
            buildings=["Bill's House"],
        )
        gs.current_location = fake_town
        enter_building(gs, "Bill's House", output, noop)
        assert "Bill" in output.combined or "BILL" in output.combined.upper()


# ===========================================================================
# enter_museum - Fossil Scientist NPC
# ===========================================================================


class TestEnterMuseumFossilScientist:
    def test_no_fossil_flag_scientist_block_absent(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = False
        enter_museum(gs, output, lambda cmd: None)
        assert "Scientist" not in output.combined

    def test_dome_fossil_mentions_kabuto(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = True
        gs.game_data["bag"] = {"Dome Fossil": 1}
        enter_museum(gs, output, lambda cmd: None)
        assert "KABUTO" in output.combined

    def test_dome_fossil_mentions_cinnabar(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = True
        gs.game_data["bag"] = {"Dome Fossil": 1}
        enter_museum(gs, output, lambda cmd: None)
        assert "Cinnabar" in output.combined

    def test_helix_fossil_mentions_omanyte(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = True
        gs.game_data["bag"] = {"Helix Fossil": 1}
        enter_museum(gs, output, lambda cmd: None)
        assert "OMANYTE" in output.combined

    def test_helix_fossil_mentions_cinnabar(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = True
        gs.game_data["bag"] = {"Helix Fossil": 1}
        enter_museum(gs, output, lambda cmd: None)
        assert "Cinnabar" in output.combined

    def test_flag_set_no_fossil_in_bag_asks_if_passed_along(self, gs, output):
        gs.game_data.setdefault("story_flags", {})["received_mt_moon_fossil"] = True
        gs.game_data["bag"] = {}
        enter_museum(gs, output, lambda cmd: None)
        assert "already pass" in output.combined.lower() or "pass it" in output.combined.lower()


# ===========================================================================
# SS Anne
# ===========================================================================


class TestEnterSSAnne:
    """Tests for enter_ss_anne."""

    def test_ss_anne_no_ticket_blocked(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data["bag"] = {}
        gs.game_data["items"] = {}
        enter_ss_anne(gs, output)
        assert "ticket" in output.combined.lower()

    def test_ss_anne_with_ticket_awards_hm01_cut(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data["bag"] = {"S.S. Anne Ticket": 1}
        gs.game_data["items"] = {}
        enter_ss_anne(gs, output)
        items = gs.game_data.get("items", {})
        assert items.get("HM01 Cut", 0) >= 1

    def test_ss_anne_sets_received_hm01_cut_flag(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data["bag"] = {"S.S. Anne Ticket": 1}
        gs.game_data["items"] = {}
        enter_ss_anne(gs, output)
        assert gs.game_data["story_flags"].get("received_hm01_cut") is True

    def test_ss_anne_second_visit_marks_departed(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data["bag"] = {"S.S. Anne Ticket": 1}
        gs.game_data["items"] = {}
        gs.game_data.setdefault("story_flags", {})["received_hm01_cut"] = True
        enter_ss_anne(gs, output)
        assert gs.game_data["story_flags"].get("ss_anne_departed") is True

    def test_ss_anne_after_departure_shows_empty_dock(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data.setdefault("story_flags", {})["ss_anne_departed"] = True
        enter_ss_anne(gs, output)
        assert "departed" in output.combined.lower() or "sail" in output.combined.lower()

    def test_ss_anne_shows_captain_dialogue(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data["bag"] = {"S.S. Anne Ticket": 1}
        gs.game_data["items"] = {}
        enter_ss_anne(gs, output)
        assert "Captain" in output.combined

    def test_ss_anne_ticket_in_items_also_works(self, gs, output):
        from pytemon.buildings import enter_ss_anne

        gs.game_data["bag"] = {}
        gs.game_data["items"] = {"S.S. Anne Ticket": 1}
        enter_ss_anne(gs, output)
        items = gs.game_data.get("items", {})
        assert items.get("HM01 Cut", 0) >= 1


# ===========================================================================
# Pokemon Tower
# ===========================================================================


class TestEnterPokemonTower:
    """Tests for enter_pokemon_tower."""

    def test_pokemon_tower_first_visit_shows_mr_fuji(self, gs, output):
        from pytemon.buildings import enter_pokemon_tower

        enter_pokemon_tower(gs, output)
        assert "Mr. Fuji" in output.combined or "Fuji" in output.combined

    def test_pokemon_tower_first_visit_sets_visited_flag(self, gs, output):
        from pytemon.buildings import enter_pokemon_tower

        enter_pokemon_tower(gs, output)
        assert gs.game_data["story_flags"].get("pokemon_tower_visited") is True

    def test_pokemon_tower_ghost_appeared_shows_marowak(self, gs, output):
        from pytemon.buildings import enter_pokemon_tower

        gs.game_data.setdefault("story_flags", {})["pokemon_tower_ghost_appeared"] = True
        enter_pokemon_tower(gs, output)
        assert "Marowak" in output.combined or "ghost" in output.combined.lower()

    def test_pokemon_tower_after_rescue_gives_poke_flute(self, gs, output):
        from pytemon.buildings import enter_pokemon_tower

        gs.game_data.setdefault("story_flags", {})["pokemon_tower_mr_fuji_rescued"] = True
        enter_pokemon_tower(gs, output)
        items = gs.game_data.get("items", {})
        assert items.get("Poke Flute", 0) >= 1

    def test_pokemon_tower_poke_flute_flag_set(self, gs, output):
        from pytemon.buildings import enter_pokemon_tower

        gs.game_data.setdefault("story_flags", {})["pokemon_tower_mr_fuji_rescued"] = True
        enter_pokemon_tower(gs, output)
        assert gs.game_data["story_flags"].get("received_poke_flute") is True

    def test_pokemon_tower_poke_flute_not_given_twice(self, gs, output):
        from pytemon.buildings import enter_pokemon_tower

        flags = gs.game_data.setdefault("story_flags", {})
        flags["pokemon_tower_mr_fuji_rescued"] = True
        flags["received_poke_flute"] = True
        gs.game_data.setdefault("items", {})["Poke Flute"] = 1
        enter_pokemon_tower(gs, output)
        assert gs.game_data.get("items", {}).get("Poke Flute", 0) == 1
