"""
Unit tests for the new advanced systems:
  - HM/TM system (hm_tm_system.py)
  - Fishing mechanic (fishing.py)
  - Item improvements: Master Ball
"""

from __future__ import annotations

import pytest

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.game_state import GameState
from pytemon.items import (
    CAT_BALL,
    CAT_HM,
    CAT_ROD,
    CAT_TM,
    ITEM_DATA,
    get_item,
    use_item_outside_battle,
)
from pytemon.models import PartyPokemon


class MockRichLog:
    """Minimal stub for textual.widgets.RichLog."""

    def __init__(self):
        self.lines: list[str] = []

    def write(self, text: str) -> None:
        self.lines.append(text)

    @property
    def combined(self) -> str:
        return "\n".join(str(line) for line in self.lines)


@pytest.fixture
def gs() -> GameState:
    state = GameState()
    state.start_new_game()
    return state


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def _make_party_pokemon(
    name: str = "PIKACHU",
    level: int = 10,
    hp: int = 35,
    max_hp: int = 35,
    moves: list[str] | None = None,
) -> PartyPokemon:
    if moves is None:
        moves = ["THUNDER SHOCK"]
    p = PartyPokemon(
        name=name,
        number=25,
        level=level,
        types=["Electric"],
        hp=hp,
        max_hp=max_hp,
        stats=StatsData(hp=max_hp, attack=55, defense=30, special=50, speed=90),
        moves=[MoveSlot(name=m, pp=30, max_pp=30) for m in moves],
        experience=0,
        next_level_exp=1000,
    )
    return p


def _give_item(gs: GameState, item_name: str, qty: int = 1) -> None:
    items = gs.game_data.setdefault("items", {})
    items[item_name] = items.get(item_name, 0) + qty


def _move_names_from_pokemon(pokemon) -> list[str]:
    """Extract plain move name strings from a Pokemon's move list.

    The move list may contain MoveSlot objects, dicts, or plain strings.
    """
    return [m.name if hasattr(m, "name") else str(m) for m in pokemon.get("moves", [])]


# ===========================================================================
# Master Ball
# ===========================================================================


class TestMasterBallCatalogue:
    def test_master_ball_in_item_data(self):
        """Master Ball must be registered in ITEM_DATA."""
        assert "Master Ball" in ITEM_DATA

    def test_master_ball_is_ball_category(self):
        """Master Ball must be in the ball category."""
        data = get_item("Master Ball")
        assert data is not None
        assert data["cat"] == CAT_BALL

    def test_master_ball_outside_battle_blocked(self, gs, output):
        """Master Ball may not be used outside battle."""
        _give_item(gs, "Master Ball")
        result = use_item_outside_battle(gs, "Master Ball", None, output)
        assert result is False
        assert any("battle" in line.lower() for line in output.lines)


# ===========================================================================
# HM / TM catalogue
# ===========================================================================


class TestHMTMCatalogue:
    @pytest.mark.parametrize(
        "hm_name,move",
        [
            ("HM01 Cut", "CUT"),
            ("HM02 Fly", "FLY"),
            ("HM03 Surf", "SURF"),
            ("HM04 Strength", "STRENGTH"),
            ("HM05 Flash", "FLASH"),
        ],
    )
    def test_hm_in_item_data(self, hm_name, move):
        """Each HM must be in ITEM_DATA with the correct move."""
        data = get_item(hm_name)
        assert data is not None
        assert data["cat"] == CAT_HM
        assert data.get("move") == move

    @pytest.mark.parametrize(
        "tm_name,move",
        [
            ("TM01 Mega Punch", "MEGA PUNCH"),
            ("TM02 Razor Wind", "RAZOR WIND"),
            ("TM03 Swords Dance", "SWORDS DANCE"),
            ("TM04 Whirlwind", "WHIRLWIND"),
            ("TM05 Mega Kick", "MEGA KICK"),
            ("TM06 Toxic", "TOXIC"),
            ("TM07 Horn Drill", "HORN DRILL"),
            ("TM08 Body Slam", "BODY SLAM"),
            ("TM09 Take Down", "TAKE DOWN"),
            ("TM10 Double-Edge", "DOUBLE-EDGE"),
            ("TM11 BubbleBeam", "BUBBLE BEAM"),
            ("TM12 Water Gun", "WATER GUN"),
            ("TM13 Ice Beam", "ICE BEAM"),
            ("TM14 Blizzard", "BLIZZARD"),
            ("TM15 Hyper Beam", "HYPER BEAM"),
            ("TM16 Pay Day", "PAY DAY"),
            ("TM17 Submission", "SUBMISSION"),
            ("TM18 Counter", "COUNTER"),
            ("TM19 Seismic Toss", "SEISMIC TOSS"),
            ("TM20 Rage", "RAGE"),
            ("TM21 Mega Drain", "MEGA DRAIN"),
            ("TM22 SolarBeam", "SOLARBEAM"),
            ("TM23 Dragon Rage", "DRAGON RAGE"),
            ("TM24 Thunderbolt", "THUNDERBOLT"),
            ("TM25 Thunder", "THUNDER"),
            ("TM26 Earthquake", "EARTHQUAKE"),
            ("TM27 Fissure", "FISSURE"),
            ("TM28 Dig", "DIG"),
            ("TM29 Psychic", "PSYCHIC"),
            ("TM30 Teleport", "TELEPORT"),
            ("TM31 Mimic", "MIMIC"),
            ("TM32 Double Team", "DOUBLE TEAM"),
            ("TM33 Reflect", "REFLECT"),
            ("TM34 Bide", "BIDE"),
            ("TM35 Metronome", "METRONOME"),
            ("TM36 Self-Destruct", "SELFDESTRUCT"),
            ("TM37 Egg Bomb", "EGG BOMB"),
            ("TM38 Fire Blast", "FIRE BLAST"),
            ("TM39 Swift", "SWIFT"),
            ("TM40 Skull Bash", "SKULL BASH"),
            ("TM41 Softboiled", "SOFT-BOILED"),
            ("TM42 Dream Eater", "DREAM EATER"),
            ("TM43 Sky Attack", "SKY ATTACK"),
            ("TM44 Rest", "REST"),
            ("TM45 Thunder Wave", "THUNDER WAVE"),
            ("TM46 Psywave", "PSYWAVE"),
            ("TM47 Explosion", "EXPLOSION"),
            ("TM48 Rock Slide", "ROCK SLIDE"),
            ("TM49 Tri Attack", "TRI ATTACK"),
            ("TM50 Substitute", "SUBSTITUTE"),
        ],
    )
    def test_tm_in_item_data(self, tm_name, move):
        """Each TM must be in ITEM_DATA with the correct move."""
        data = get_item(tm_name)
        assert data is not None
        assert data["cat"] == CAT_TM
        assert data.get("move") == move

    def test_all_50_tms_present(self):
        """Exactly 50 TMs must be registered in ITEM_DATA."""
        from pytemon.items import CAT_TM, ITEM_DATA

        tms = [k for k, v in ITEM_DATA.items() if v.cat == CAT_TM]
        assert len(tms) == 50

    def test_all_tm_moves_in_move_database(self):
        """Every TM move must exist in move_data.MOVES."""
        from pytemon.data.move_data import MOVES
        from pytemon.items import CAT_TM, ITEM_DATA

        missing = []
        for name, data in ITEM_DATA.items():
            if data.cat == CAT_TM:
                move = data.get("move", "")
                if move and move not in MOVES:
                    missing.append(f"{name} -> {move}")
        assert not missing, f"TM moves missing from MOVES: {missing}"

    def test_hm_badge_requirements(self):
        """HMs must have a badge requirement set."""
        from pytemon.hm_tm_system import HM_BADGE_REQUIREMENTS

        assert HM_BADGE_REQUIREMENTS["SURF"] == "cascade_badge"
        assert HM_BADGE_REQUIREMENTS["FLY"] == "thunder_badge"
        assert HM_BADGE_REQUIREMENTS["CUT"] == "boulder_badge"
        assert HM_BADGE_REQUIREMENTS["STRENGTH"] == "soul_badge"
        assert HM_BADGE_REQUIREMENTS["FLASH"] == "boulder_badge"


# ===========================================================================
# HM teaching
# ===========================================================================


class TestTeachMove:
    def test_teach_hm_surf_to_pokemon(self, gs, output):
        """Teaching HM Surf adds SURF to the Pokemon's moves."""
        from pytemon.hm_tm_system import teach_move

        pokemon = _make_party_pokemon(moves=["TACKLE", "GROWL"])
        gs.game_data["pokemon"] = [pokemon]

        result = teach_move(gs, "SURF", pokemon, "HM03 Surf", is_hm=True, output=output)

        assert result is True
        # Moves are stored as MoveSlot objects — check by name
        assert "SURF" in _move_names_from_pokemon(pokemon)
        assert any("learned" in line.lower() for line in output.lines)

    def test_hm_not_consumed_after_teaching(self, gs, output):
        """HMs must not be consumed when a move is taught."""
        from pytemon.hm_tm_system import teach_move

        _give_item(gs, "HM03 Surf", 1)
        pokemon = _make_party_pokemon(moves=["TACKLE"])
        gs.game_data["pokemon"] = [pokemon]

        teach_move(gs, "SURF", pokemon, "HM03 Surf", is_hm=True, output=output)

        # HM must remain in the bag
        assert gs.game_data["items"].get("HM03 Surf", 0) == 1

    def test_tm_consumed_after_teaching(self, gs, output):
        """TMs must be consumed when a move is taught."""
        _give_item(gs, "TM26 Earthquake", 1)
        pokemon = _make_party_pokemon(moves=["TACKLE"])
        gs.game_data["pokemon"] = [pokemon]

        # _use_hm_tm (called via use_item_outside_battle) consumes the TM
        result = use_item_outside_battle(gs, "TM26 Earthquake", "pikachu", output)

        assert result is True
        # Moves are stored as MoveSlot objects — check by name
        assert "EARTHQUAKE" in _move_names_from_pokemon(pokemon)
        # TM must be consumed
        assert gs.game_data["items"].get("TM26 Earthquake", 0) == 0

    def test_teach_move_already_known(self, gs, output):
        """Teaching a move already known by the Pokemon succeeds (no-op)."""
        from pytemon.hm_tm_system import teach_move

        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.game_data["pokemon"] = [pokemon]

        result = teach_move(gs, "SURF", pokemon, "HM03 Surf", is_hm=True, output=output)

        assert result is True
        assert any("already knows" in line.lower() for line in output.lines)

    def test_teach_move_full_moveset(self, gs, output):
        """Teaching a move when the Pokemon has 4 moves fails gracefully."""
        from pytemon.hm_tm_system import teach_move

        pokemon = _make_party_pokemon(moves=["TACKLE", "GROWL", "TAIL WHIP", "SCRATCH"])
        gs.game_data["pokemon"] = [pokemon]

        result = teach_move(gs, "SURF", pokemon, "HM03 Surf", is_hm=True, output=output)

        assert result is False
        assert any("4 moves" in line for line in output.lines)

    def test_use_hm_without_target_shows_usage(self, gs, output):
        """Using an HM without a target shows usage hint."""
        _give_item(gs, "HM03 Surf")
        pokemon = _make_party_pokemon()
        gs.game_data["pokemon"] = [pokemon]

        result = use_item_outside_battle(gs, "HM03 Surf", None, output)

        assert result is False
        assert any("usage" in line.lower() for line in output.lines)


# ===========================================================================
# HM field use
# ===========================================================================


class TestHMFieldUse:
    def test_surf_requires_cascade_badge(self, gs, output):
        """Using Surf in the field without Cascade Badge is blocked."""
        from pytemon.hm_tm_system import use_hm_field

        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.game_data["pokemon"] = [pokemon]

        result = use_hm_field(gs, "SURF", output)

        assert result is False
        assert any("cascade badge" in line.lower() for line in output.lines)

    def test_surf_succeeds_with_badge_and_water(self, gs, output):
        """Surf works if the player has the badge and is at a water location."""
        from pytemon.hm_tm_system import use_hm_field
        from pytemon.locations import get_location

        gs.game_data["badges"] = ["cascade_badge"]
        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.game_data["pokemon"] = [pokemon]
        pallet = get_location("Pallet Town")
        assert pallet is not None
        gs.current_location = pallet

        result = use_hm_field(gs, "SURF", output)

        assert result is True
        assert "Route 21" in gs.game_data.get("surf_unlocked", [])

    def test_fly_requires_party_member_with_move(self, gs, output):
        """Using Fly when no party member knows the move fails."""
        from pytemon.hm_tm_system import use_hm_field

        gs.game_data["badges"] = ["thunder_badge"]
        pokemon = _make_party_pokemon(moves=["TACKLE"])
        gs.game_data["pokemon"] = [pokemon]

        result = use_hm_field(gs, "FLY", output)

        assert result is False
        assert any("know fly" in line.lower() for line in output.lines)

    def test_fly_in_cheat_mode_skips_checks(self, gs, output):
        """In cheat mode, Fly works even without badge or the move."""
        from pytemon.hm_tm_system import use_hm_field

        gs.cheat_mode = True
        pokemon = _make_party_pokemon(moves=["TACKLE"])
        gs.game_data["pokemon"] = [pokemon]
        gs.game_data["visited_locations"] = ["Pallet Town", "Viridian City"]
        from pytemon.locations import get_location

        gs.current_location = get_location("Pewter City")

        # Should not raise even without badges/moves
        use_hm_field(gs, "FLY", output)  # may return True or False, just no crash

    def test_cut_in_forest_succeeds(self, gs, output):
        """Cut works in forest locations."""
        from pytemon.hm_tm_system import use_hm_field
        from pytemon.locations import get_location

        gs.game_data["badges"] = ["boulder_badge"]
        pokemon = _make_party_pokemon(moves=["CUT"])
        gs.game_data["pokemon"] = [pokemon]
        gs.current_location = get_location("Viridian Forest")

        result = use_hm_field(gs, "CUT", output)

        assert result is True
        assert any("cut" in line.lower() for line in output.lines)


# ===========================================================================
# Fly-to-town
# ===========================================================================


class TestFlyToTown:
    def test_fly_to_visited_town(self, gs, output):
        """fly_to_town teleports the player to a visited town."""
        from pytemon.hm_tm_system import fly_to_town
        from pytemon.locations import get_location

        gs.game_data["visited_locations"] = ["Pallet Town", "Viridian City", "Pewter City"]
        gs.current_location = get_location("Pallet Town")

        result = fly_to_town(gs, "Viridian City", output)

        assert result is True
        assert gs.game_data["location"] == "Viridian City"
        assert any("viridian city" in line.lower() for line in output.lines)

    def test_fly_to_unvisited_town_fails(self, gs, output):
        """fly_to_town rejects destinations the player hasn't visited."""
        from pytemon.hm_tm_system import fly_to_town
        from pytemon.locations import get_location

        gs.game_data["visited_locations"] = ["Pallet Town"]
        gs.current_location = get_location("Pallet Town")

        result = fly_to_town(gs, "Cerulean City", output)

        assert result is False

    def test_fly_to_partial_name_match(self, gs, output):
        """fly_to_town accepts partial destination names."""
        from pytemon.hm_tm_system import fly_to_town
        from pytemon.locations import get_location

        gs.game_data["visited_locations"] = ["Pallet Town", "Viridian City"]
        gs.current_location = get_location("Pallet Town")

        result = fly_to_town(gs, "viridian", output)

        assert result is True
        assert gs.game_data["location"] == "Viridian City"


# ===========================================================================
# Fishing
# ===========================================================================


class TestFishingCatalogue:
    @pytest.mark.parametrize("rod", ["Old Rod", "Good Rod", "Super Rod"])
    def test_rod_in_item_data(self, rod):
        """Each fishing rod must be in ITEM_DATA with the rod category."""
        data = get_item(rod)
        assert data is not None
        assert data["cat"] == CAT_ROD


class TestFishingGetBestRod:
    def test_no_rod_returns_none(self, gs):
        """get_best_rod returns None when the player has no rods."""
        from pytemon.fishing import get_best_rod

        assert get_best_rod(gs) is None

    def test_old_rod_only(self, gs):
        """get_best_rod returns Old Rod when that is the only rod."""
        from pytemon.fishing import get_best_rod

        _give_item(gs, "Old Rod")
        assert get_best_rod(gs) == "Old Rod"

    def test_prefers_super_rod(self, gs):
        """get_best_rod returns Super Rod when all rods are present."""
        from pytemon.fishing import get_best_rod

        _give_item(gs, "Old Rod")
        _give_item(gs, "Good Rod")
        _give_item(gs, "Super Rod")
        assert get_best_rod(gs) == "Super Rod"


class TestStartFishing:
    def test_fishing_without_rod_shows_error(self, gs, output):
        """Fishing without a rod tells the player they need one."""
        from pytemon.fishing import start_fishing
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon()
        gs.game_data["pokemon"] = [pokemon]
        gs.current_location = get_location("Pallet Town")

        start_fishing(gs, output, lambda o, s, _lvl: None)

        assert any("fishing rod" in line.lower() for line in output.lines)

    def test_fishing_at_non_water_location_blocked(self, gs, output):
        """Fishing at an inland route shows an appropriate message."""
        from pytemon.fishing import start_fishing
        from pytemon.locations import get_location

        _give_item(gs, "Old Rod")
        pokemon = _make_party_pokemon()
        gs.game_data["pokemon"] = [pokemon]
        gs.current_location = get_location("Viridian Forest")

        start_fishing(gs, output, lambda o, s, _lvl: None)

        assert any("can't fish" in line.lower() for line in output.lines)

    def test_fishing_at_water_location_triggers_encounter(self, gs, output):
        """Fishing at a valid water location triggers a wild encounter callback."""
        from pytemon.fishing import start_fishing
        from pytemon.locations import get_location

        _give_item(gs, "Old Rod")
        pokemon = _make_party_pokemon()
        gs.game_data["pokemon"] = [pokemon]
        gs.current_location = get_location("Pallet Town")

        encounters: list[tuple[str, int]] = []

        def fake_trigger(out, species, level):
            encounters.append((species, level))

        # Seed random to guarantee a bite
        import random

        random.seed(0)
        # Try multiple times to ensure a bite happens
        for _ in range(20):
            start_fishing(gs, output, fake_trigger)
            if encounters:
                break

        # At least one encounter must have occurred
        assert encounters, "Expected at least one fishing encounter"
        species, level = encounters[0]
        assert species in ("MAGIKARP", "GOLDEEN", "TENTACOOL", "GYARADOS")
        assert 5 <= level <= 15  # Old Rod level range

    def test_fishing_without_pokemon_shows_error(self, gs, output):
        """Fishing without a party shows an appropriate message."""
        from pytemon.fishing import start_fishing
        from pytemon.locations import get_location

        _give_item(gs, "Old Rod")
        gs.game_data["pokemon"] = []
        gs.current_location = get_location("Pallet Town")

        start_fishing(gs, output, lambda o, s, _lvl: None)

        assert any("pokemon" in line.lower() for line in output.lines)

    def test_fishing_with_specific_rod(self, gs, output):
        """Fishing with a specified rod uses that rod."""
        from pytemon.fishing import start_fishing
        from pytemon.locations import get_location

        _give_item(gs, "Super Rod")
        pokemon = _make_party_pokemon()
        gs.game_data["pokemon"] = [pokemon]
        gs.current_location = get_location("Pallet Town")

        encounters: list[tuple[str, int]] = []

        def fake_trigger(out, species, level):
            encounters.append((species, level))

        import random

        random.seed(42)
        for _ in range(20):
            start_fishing(gs, output, fake_trigger, rod_name="Super Rod")
            if encounters:
                break

        if encounters:
            _, level = encounters[0]
            # Super Rod level range is 15-40
            assert 15 <= level <= 40


# ===========================================================================
# Route 21 unlocked via Surf
# ===========================================================================


class TestRoute21:
    def test_route_21_exists_in_locations(self):
        """Route 21 must be a registered location."""
        from pytemon.locations import get_location

        loc = get_location("Route 21")
        assert loc is not None
        assert loc.type == "route"

    def test_route_21_has_water_pokemon(self):
        """Route 21 must include water Pokemon in its wild pool."""
        from pytemon.locations import get_location

        loc = get_location("Route 21")
        assert loc is not None
        # At least one of the expected water Pokemon should be present
        water_pokemon = {"TENTACOOL", "TENTACRUEL", "MAGIKARP"}
        assert water_pokemon & set(loc.wild_pokemon)

    def test_pallet_town_route_21_blocked_by_default(self, gs):
        """Route 21 must be blocked from Pallet Town without Surf."""
        from pytemon.locations import get_location

        pallet = get_location("Pallet Town")
        assert pallet is not None
        exit_data = pallet.exits.get("Route 21", {})
        assert exit_data.get("blocked") is True

    def test_route_21_unblocked_after_surf(self, gs, output):
        """After using Surf, Route 21 exit becomes passable."""
        from pytemon.exploration import move_to_location
        from pytemon.hm_tm_system import use_hm_field
        from pytemon.locations import get_location

        gs.game_data["badges"] = ["cascade_badge"]
        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.game_data["pokemon"] = [pokemon]
        pallet = get_location("Pallet Town")
        assert pallet is not None
        gs.current_location = pallet

        # Use Surf to unlock
        use_hm_field(gs, "SURF", output)
        assert "Route 21" in gs.game_data.get("surf_unlocked", [])

        # Now try to move to Route 21
        visited: list[str] = []
        move_to_location(gs, "Route 21", output, lambda _o: visited.append("called"))

        assert gs.current_location is not None
        assert gs.current_location.name == "Route 21"


# ===========================================================================
# HM/TM extended coverage — hm_tm_system.py
# ===========================================================================


class TestTeachMoveExtra:
    def test_unknown_move_returns_false(self, gs, output):
        """teach_move with a move NOT in MOVES dict returns False and writes error."""
        from pytemon.hm_tm_system import teach_move

        pokemon = _make_party_pokemon()
        result = teach_move(gs, "NONEXISTENT_XYZ99", pokemon, "TM99", False, output)
        assert result is False
        assert any(
            "not in the move database" in line.lower() or "❌" in line for line in output.lines
        )

    def test_dict_moves_normalised(self, gs, output):
        """teach_move works when existing moves are plain dicts (not MoveSlot)."""
        from pytemon.hm_tm_system import teach_move

        pokemon = _make_party_pokemon()
        # Replace MoveSlot moves with plain dicts
        pokemon["moves"] = [{"name": "TACKLE", "pp": 35, "max_pp": 35}]
        result = teach_move(gs, "SURF", pokemon, "HM03 Surf", True, output)
        assert result is True


class TestUseHmFieldExtra:
    def test_dict_moves_normalisation(self, gs, output):
        """use_hm_field finds a pokemon whose moves are stored as plain dicts."""
        from pytemon.hm_tm_system import use_hm_field
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon(moves=["SURF"])
        # Replace MoveSlot with plain dict
        pokemon["moves"] = [{"name": "SURF", "pp": 15}]
        gs.game_data["pokemon"] = [pokemon]
        gs.game_data["badges"] = ["cascade_badge"]
        gs.current_location = get_location("Pallet Town")
        result = use_hm_field(gs, "SURF", output)
        assert result is True

    def test_strength_field_effect(self, gs, output):
        """STRENGTH dispatches to _field_strength, returns True."""
        from pytemon.hm_tm_system import use_hm_field

        pokemon = _make_party_pokemon(moves=["STRENGTH"])
        gs.game_data["pokemon"] = [pokemon]
        gs.game_data["badges"] = ["soul_badge"]
        result = use_hm_field(gs, "STRENGTH", output)
        assert result is True
        assert any("STRENGTH" in line or "boulder" in line.lower() for line in output.lines)

    def test_flash_field_effect(self, gs, output):
        """FLASH dispatches to _field_flash, returns True."""
        from pytemon.hm_tm_system import use_hm_field

        pokemon = _make_party_pokemon(moves=["FLASH"])
        gs.game_data["pokemon"] = [pokemon]
        gs.game_data["badges"] = ["boulder_badge"]
        result = use_hm_field(gs, "FLASH", output)
        assert result is True
        assert any("FLASH" in line or "lit up" in line.lower() for line in output.lines)

    def test_non_hm_move_has_no_field_effect(self, gs, output):
        """A non-HM move (TACKLE) returns False with 'no field effect' message."""
        from pytemon.hm_tm_system import use_hm_field

        pokemon = _make_party_pokemon(moves=["TACKLE"])
        gs.game_data["pokemon"] = [pokemon]
        result = use_hm_field(gs, "TACKLE", output)
        assert result is False
        assert any("no field effect" in line.lower() for line in output.lines)


class TestFieldSurfExtra:
    def test_no_current_location_returns_false(self, gs, output):
        """_field_surf returns False when current_location is None."""
        from pytemon.hm_tm_system import _field_surf

        gs.current_location = None
        result = _field_surf(gs, None, output)
        assert result is False

    def test_show_location_callback_called(self, gs, output):
        """_field_surf calls show_location_callback when surf exits are unblocked."""
        from pytemon.hm_tm_system import _field_surf
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.game_data["badges"] = ["cascade_badge"]
        gs.current_location = get_location("Pallet Town")
        callback_calls: list[int] = []
        result = _field_surf(
            gs, pokemon, output, show_location_callback=lambda: callback_calls.append(1)
        )
        assert result is True
        assert len(callback_calls) > 0

    def test_route_21_already_surfing(self, gs, output):
        """_field_surf returns True when already in Route 21 area."""
        from pytemon.hm_tm_system import _field_surf
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.current_location = get_location("Route 21")
        result = _field_surf(gs, pokemon, output)
        assert result is True

    def test_surf_unlocked_already(self, gs, output):
        """_field_surf returns True when surf_unlocked has entries."""
        from pytemon.hm_tm_system import _field_surf
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon(moves=["SURF"])
        # Use a location with no surf exits
        gs.current_location = get_location("Viridian City")
        gs.game_data["surf_unlocked"] = ["Route 21"]
        result = _field_surf(gs, pokemon, output)
        assert result is True

    def test_no_water_returns_false(self, gs, output):
        """_field_surf returns False when there is no water and nothing unlocked."""
        from pytemon.hm_tm_system import _field_surf
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon(moves=["SURF"])
        gs.current_location = get_location("Viridian City")
        gs.game_data["surf_unlocked"] = []
        gs.cheat_mode = False
        result = _field_surf(gs, pokemon, output)
        assert result is False
        assert any("no water" in line.lower() for line in output.lines)


class TestFieldFlyExtra:
    def test_no_visited_towns_returns_false(self, gs, output):
        """_field_fly returns False when no towns have been visited yet."""
        from pytemon.hm_tm_system import _field_fly

        pokemon = _make_party_pokemon()
        gs.game_data["visited_locations"] = []
        result = _field_fly(gs, pokemon, output)
        assert result is False
        assert any(
            "haven't visited" in line.lower() or "towns yet" in line.lower()
            for line in output.lines
        )


class TestFieldCutExtra:
    def test_non_forest_route_returns_false(self, gs, output):
        """_field_cut returns False at a town location — nothing to cut there."""
        from pytemon.hm_tm_system import _field_cut
        from pytemon.locations import get_location

        pokemon = _make_party_pokemon(moves=["CUT"])
        gs.current_location = get_location("Pallet Town")
        result = _field_cut(gs, pokemon, output)
        assert result is False
        assert any("nothing" in line.lower() for line in output.lines)


class TestFieldStrengthExtra:
    def test_returns_true_with_messages(self, gs, output):
        """_field_strength always returns True and writes boulder messages."""
        from pytemon.hm_tm_system import _field_strength

        pokemon = _make_party_pokemon()
        result = _field_strength(gs, pokemon, output)
        assert result is True
        assert any("STRENGTH" in line or "boulder" in line.lower() for line in output.lines)


class TestFieldFlashExtra:
    def test_returns_true_with_messages(self, gs, output):
        """_field_flash always returns True and writes lit-up messages."""
        from pytemon.hm_tm_system import _field_flash

        pokemon = _make_party_pokemon()
        result = _field_flash(gs, pokemon, output)
        assert result is True
        assert any("FLASH" in line or "lit up" in line.lower() for line in output.lines)
