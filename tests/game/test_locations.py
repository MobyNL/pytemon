"""
Unit tests for PokemonLibrary/locations.py.
"""

from pytemon.locations import (
    TYPE_FOREST,
    TYPE_ROUTE,
    TYPE_TOWN,
    Location,
    get_location,
    get_starting_location,
)


class TestLocation:
    """Tests for the Location class."""

    def test_create_minimal_location(self):
        loc = Location(
            name="Test Town",
            location_type=TYPE_TOWN,
            description="A test town",
            exits={},
        )
        assert loc.name == "Test Town"
        assert loc.type == TYPE_TOWN

    def test_can_explore_route(self):
        loc = Location(
            name="Route 99",
            location_type=TYPE_ROUTE,
            description="A test route",
            exits={},
        )
        assert loc.can_explore() is True

    def test_can_explore_forest(self):
        loc = Location(
            name="Dark Forest",
            location_type=TYPE_FOREST,
            description="A test forest",
            exits={},
        )
        assert loc.can_explore() is True

    def test_town_cannot_explore(self):
        loc = Location(
            name="Test Town",
            location_type=TYPE_TOWN,
            description="A test town",
            exits={},
        )
        assert loc.can_explore() is False

    def test_get_available_exits_excludes_blocked(self):
        loc = Location(
            name="Test Town",
            location_type=TYPE_TOWN,
            description="desc",
            exits={
                "North": {"destination": "Route 1"},
                "East": {"destination": "Route 2", "blocked": True, "reason": "Blocked"},
            },
        )
        available = loc.get_available_exits()
        assert "North" in available
        assert "East" not in available

    def test_get_blocked_exits(self):
        loc = Location(
            name="Test Town",
            location_type=TYPE_TOWN,
            description="desc",
            exits={
                "North": {"destination": "Route 1"},
                "East": {"destination": "Route 2", "blocked": True, "reason": "Fence"},
            },
        )
        blocked = loc.get_blocked_exits()
        assert "East" in blocked
        assert blocked["East"] == "Fence"

    def test_defaults_empty_buildings_list(self):
        loc = Location(
            name="Test Town",
            location_type=TYPE_TOWN,
            description="desc",
            exits={},
        )
        assert loc.buildings == []

    def test_defaults_empty_wild_pokemon(self):
        loc = Location(
            name="Route 99",
            location_type=TYPE_ROUTE,
            description="desc",
            exits={},
        )
        assert loc.wild_pokemon == []

    def test_get_exit_min_explores_present(self):
        loc = Location(
            name="Route X",
            location_type=TYPE_ROUTE,
            description="desc",
            exits={"Viridian City": {"destination": "Viridian City", "min_explores": 3}},
        )
        assert loc.get_exit_min_explores("Viridian City") == 3

    def test_get_exit_min_explores_absent_returns_zero(self):
        loc = Location(
            name="Route X",
            location_type=TYPE_ROUTE,
            description="desc",
            exits={"Viridian City": {"destination": "Viridian City"}},
        )
        assert loc.get_exit_min_explores("Viridian City") == 0

    def test_get_exit_min_explores_unknown_exit_returns_zero(self):
        loc = Location(
            name="Route X",
            location_type=TYPE_ROUTE,
            description="desc",
            exits={},
        )
        assert loc.get_exit_min_explores("Nowhere") == 0


class TestGetLocation:
    """Tests for get_location() registry lookup."""

    def test_get_pallet_town(self):
        loc = get_location("Pallet Town")
        assert loc is not None
        assert loc.name == "Pallet Town"

    def test_get_route_1(self):
        loc = get_location("Route 1")
        assert loc is not None

    def test_get_viridian_city(self):
        loc = get_location("Viridian City")
        assert loc is not None

    def test_unknown_location_returns_none(self):
        loc = get_location("Nonexistent Place")
        assert loc is None

    def test_case_sensitive_lookup(self):
        # Registry keys should be exact; wrong case returns None
        loc = get_location("pallet town")
        assert loc is None


class TestGetStartingLocation:
    """Tests for get_starting_location()."""

    def test_returns_string(self):
        name = get_starting_location()
        assert isinstance(name, str)

    def test_starting_location_exists_in_registry(self):
        name = get_starting_location()
        loc = get_location(name)
        assert loc is not None

    def test_starting_location_is_pallet_town(self):
        assert get_starting_location() == "Pallet Town"


class TestRoute24:
    """Tests for Route 24 location data."""

    def test_route_24_exists_in_registry(self):
        loc = get_location("Route 24")
        assert loc is not None

    def test_route_24_is_route_type(self):
        loc = get_location("Route 24")
        assert loc.type == TYPE_ROUTE

    def test_route_24_has_bills_house_building(self):
        loc = get_location("Route 24")
        assert "Bill's House" in loc.buildings

    def test_route_24_wild_pokemon_includes_bellsprout(self):
        loc = get_location("Route 24")
        assert "BELLSPROUT" in loc.wild_pokemon

    def test_route_24_wild_pokemon_includes_abra(self):
        loc = get_location("Route 24")
        assert "ABRA" in loc.wild_pokemon

    def test_route_24_wild_pokemon_includes_oddish(self):
        loc = get_location("Route 24")
        assert "ODDISH" in loc.wild_pokemon

    def test_route_24_exits_south_to_cerulean(self):
        loc = get_location("Route 24")
        exit_names_lower = [k.lower() for k in loc.exits.keys()]
        assert any("cerulean" in name for name in exit_names_lower)

    def test_route_24_wild_level_range(self):
        loc = get_location("Route 24")
        assert loc.wild_level_range == (14, 18)

    def test_cerulean_city_has_route_24_exit(self):
        loc = get_location("Cerulean City")
        assert loc is not None
        assert "Route 24" in loc.exits


class TestCeruleanCityUpdatedExits:
    """Tests for updated Cerulean City connections."""

    def test_cerulean_city_has_route_5_exit(self):
        loc = get_location("Cerulean City")
        assert loc is not None
        assert "Route 5" in loc.exits

    def test_cerulean_city_route_5_not_blocked(self):
        loc = get_location("Cerulean City")
        assert not loc.exits["Route 5"].get("blocked", False)

    def test_cerulean_city_has_route_9_exit(self):
        loc = get_location("Cerulean City")
        assert "Route 9" in loc.exits

    def test_cerulean_city_route_9_direction_east(self):
        loc = get_location("Cerulean City")
        assert loc.exits["Route 9"]["direction"] == "east"


class TestRoute2NorthDiglettsCave:
    """Tests for Diglett's Cave exit from Route 2 North."""

    def test_route_2_north_has_digletts_cave_exit(self):
        loc = get_location("Route 2 North")
        assert loc is not None
        assert "Diglett's Cave" in loc.exits

    def test_route_2_north_digletts_cave_not_blocked(self):
        loc = get_location("Route 2 North")
        assert not loc.exits["Diglett's Cave"].get("blocked", False)


class TestRoute5:
    """Tests for Route 5 location."""

    def test_route_5_exists(self):
        loc = get_location("Route 5")
        assert loc is not None

    def test_route_5_is_route_type(self):
        loc = get_location("Route 5")
        assert loc.type == TYPE_ROUTE

    def test_route_5_can_explore(self):
        loc = get_location("Route 5")
        assert loc.can_explore() is True

    def test_route_5_has_cerulean_exit(self):
        loc = get_location("Route 5")
        assert "Cerulean City" in loc.exits

    def test_route_5_has_underground_path_exit(self):
        loc = get_location("Route 5")
        assert "Underground Path (North)" in loc.exits

    def test_route_5_wild_pokemon(self):
        loc = get_location("Route 5")
        assert "PIDGEY" in loc.wild_pokemon
        assert "MEOWTH" in loc.wild_pokemon
        assert "MANKEY" in loc.wild_pokemon

    def test_route_5_wild_level_range(self):
        loc = get_location("Route 5")
        assert loc.wild_level_range == (13, 17)

    def test_route_5_has_trainers(self):
        loc = get_location("Route 5")
        assert loc.trainers >= 1


class TestRoute6:
    """Tests for Route 6 location."""

    def test_route_6_exists(self):
        loc = get_location("Route 6")
        assert loc is not None

    def test_route_6_is_route_type(self):
        loc = get_location("Route 6")
        assert loc.type == TYPE_ROUTE

    def test_route_6_has_underground_path_exit(self):
        loc = get_location("Route 6")
        assert "Underground Path (South)" in loc.exits

    def test_route_6_has_vermillion_exit(self):
        loc = get_location("Route 6")
        assert "Vermillion City" in loc.exits

    def test_route_6_wild_pokemon(self):
        loc = get_location("Route 6")
        assert "PIDGEY" in loc.wild_pokemon
        assert "MEOWTH" in loc.wild_pokemon
        assert "MANKEY" in loc.wild_pokemon

    def test_route_6_wild_level_range(self):
        loc = get_location("Route 6")
        assert loc.wild_level_range == (14, 18)


class TestUndergroundPath:
    """Tests for the Underground Path locations."""

    def test_underground_path_north_exists(self):
        loc = get_location("Underground Path (North)")
        assert loc is not None

    def test_underground_path_south_exists(self):
        loc = get_location("Underground Path (South)")
        assert loc is not None

    def test_underground_path_north_is_dungeon(self):
        from pytemon.locations import TYPE_DUNGEON

        loc = get_location("Underground Path (North)")
        assert loc.type == TYPE_DUNGEON

    def test_underground_path_south_is_dungeon(self):
        from pytemon.locations import TYPE_DUNGEON

        loc = get_location("Underground Path (South)")
        assert loc.type == TYPE_DUNGEON

    def test_underground_path_north_connects_to_south(self):
        loc = get_location("Underground Path (North)")
        assert "Underground Path (South)" in loc.exits

    def test_underground_path_south_connects_to_north(self):
        loc = get_location("Underground Path (South)")
        assert "Underground Path (North)" in loc.exits

    def test_underground_path_north_connects_to_route_5(self):
        loc = get_location("Underground Path (North)")
        assert "Route 5" in loc.exits

    def test_underground_path_south_connects_to_route_6(self):
        loc = get_location("Underground Path (South)")
        assert "Route 6" in loc.exits

    def test_underground_path_no_wild_pokemon(self):
        loc_n = get_location("Underground Path (North)")
        loc_s = get_location("Underground Path (South)")
        assert loc_n.wild_pokemon == []
        assert loc_s.wild_pokemon == []

    def test_underground_path_no_wild_encounter_rate(self):
        loc = get_location("Underground Path (North)")
        assert loc.wild_encounter_rate == 0.0


class TestVermillionCity:
    """Tests for Vermillion City location."""

    def test_vermillion_city_exists(self):
        loc = get_location("Vermillion City")
        assert loc is not None

    def test_vermillion_city_is_town(self):
        loc = get_location("Vermillion City")
        assert loc.type == TYPE_TOWN

    def test_vermillion_city_has_pokemon_center(self):
        loc = get_location("Vermillion City")
        assert "Pokemon Center" in loc.buildings

    def test_vermillion_city_has_gym(self):
        loc = get_location("Vermillion City")
        assert "Gym" in loc.buildings

    def test_vermillion_city_has_route_6_exit(self):
        loc = get_location("Vermillion City")
        assert "Route 6" in loc.exits

    def test_vermillion_city_has_route_11_exit(self):
        loc = get_location("Vermillion City")
        assert "Route 11" in loc.exits

    def test_vermillion_city_route_11_direction_east(self):
        loc = get_location("Vermillion City")
        assert loc.exits["Route 11"]["direction"] == "east"


class TestRoute11:
    """Tests for Route 11 location."""

    def test_route_11_exists(self):
        loc = get_location("Route 11")
        assert loc is not None

    def test_route_11_is_route_type(self):
        loc = get_location("Route 11")
        assert loc.type == TYPE_ROUTE

    def test_route_11_has_vermillion_exit(self):
        loc = get_location("Route 11")
        assert "Vermillion City" in loc.exits

    def test_route_11_has_digletts_cave_exit(self):
        loc = get_location("Route 11")
        assert "Diglett's Cave" in loc.exits

    def test_route_11_wild_pokemon(self):
        loc = get_location("Route 11")
        assert "EKANS" in loc.wild_pokemon
        assert "SPEAROW" in loc.wild_pokemon
        assert "DROWZEE" in loc.wild_pokemon

    def test_route_11_wild_level_range(self):
        loc = get_location("Route 11")
        assert loc.wild_level_range == (13, 19)

    def test_route_11_has_trainers(self):
        loc = get_location("Route 11")
        assert loc.trainers >= 2


class TestDiglettsCave:
    """Tests for Diglett's Cave location."""

    def test_digletts_cave_exists(self):
        loc = get_location("Diglett's Cave")
        assert loc is not None

    def test_digletts_cave_is_dungeon(self):
        from pytemon.locations import TYPE_DUNGEON

        loc = get_location("Diglett's Cave")
        assert loc.type == TYPE_DUNGEON

    def test_digletts_cave_has_route_2_north_exit(self):
        loc = get_location("Diglett's Cave")
        assert "Route 2 North" in loc.exits

    def test_digletts_cave_has_route_11_exit(self):
        loc = get_location("Diglett's Cave")
        assert "Route 11" in loc.exits

    def test_digletts_cave_wild_pokemon(self):
        loc = get_location("Diglett's Cave")
        assert "DIGLETT" in loc.wild_pokemon
        assert "DUGTRIO" in loc.wild_pokemon

    def test_digletts_cave_level_range(self):
        loc = get_location("Diglett's Cave")
        assert loc.wild_level_range == (15, 22)

    def test_digletts_cave_high_encounter_rate(self):
        loc = get_location("Diglett's Cave")
        assert loc.wild_encounter_rate >= 0.50

    def test_digletts_cave_no_trainers(self):
        loc = get_location("Diglett's Cave")
        assert loc.trainers == 0


class TestRoute9:
    """Tests for Route 9 location."""

    def test_route_9_exists(self):
        loc = get_location("Route 9")
        assert loc is not None

    def test_route_9_is_route_type(self):
        loc = get_location("Route 9")
        assert loc.type == TYPE_ROUTE

    def test_route_9_has_cerulean_exit(self):
        loc = get_location("Route 9")
        assert "Cerulean City" in loc.exits

    def test_route_9_has_route_10_exit(self):
        loc = get_location("Route 9")
        assert "Route 10" in loc.exits

    def test_route_9_wild_pokemon(self):
        loc = get_location("Route 9")
        assert "RATTATA" in loc.wild_pokemon
        assert "EKANS" in loc.wild_pokemon
        assert "SPEAROW" in loc.wild_pokemon

    def test_route_9_wild_level_range(self):
        loc = get_location("Route 9")
        assert loc.wild_level_range == (15, 21)

    def test_route_9_has_trainers(self):
        loc = get_location("Route 9")
        assert loc.trainers >= 2


class TestRoute10:
    """Tests for Route 10 location."""

    def test_route_10_exists(self):
        loc = get_location("Route 10")
        assert loc is not None

    def test_route_10_is_route_type(self):
        loc = get_location("Route 10")
        assert loc.type == TYPE_ROUTE

    def test_route_10_has_route_9_exit(self):
        loc = get_location("Route 10")
        assert "Route 9" in loc.exits

    def test_route_10_has_rock_tunnel_exit(self):
        loc = get_location("Route 10")
        assert "Rock Tunnel" in loc.exits

    def test_route_10_wild_pokemon(self):
        loc = get_location("Route 10")
        assert "VOLTORB" in loc.wild_pokemon
        assert "MAGNEMITE" in loc.wild_pokemon

    def test_route_10_wild_level_range(self):
        loc = get_location("Route 10")
        assert loc.wild_level_range == (17, 23)


class TestRockTunnel:
    """Tests for Rock Tunnel location."""

    def test_rock_tunnel_exists(self):
        loc = get_location("Rock Tunnel")
        assert loc is not None

    def test_rock_tunnel_is_dungeon(self):
        from pytemon.locations import TYPE_DUNGEON

        loc = get_location("Rock Tunnel")
        assert loc.type == TYPE_DUNGEON

    def test_rock_tunnel_has_route_10_exit(self):
        loc = get_location("Rock Tunnel")
        assert "Route 10" in loc.exits

    def test_rock_tunnel_wild_pokemon(self):
        loc = get_location("Rock Tunnel")
        assert "ZUBAT" in loc.wild_pokemon
        assert "GEODUDE" in loc.wild_pokemon
        assert "MACHOP" in loc.wild_pokemon
        assert "ONIX" in loc.wild_pokemon

    def test_rock_tunnel_wild_level_range(self):
        loc = get_location("Rock Tunnel")
        assert loc.wild_level_range == (15, 23)

    def test_rock_tunnel_high_encounter_rate(self):
        loc = get_location("Rock Tunnel")
        assert loc.wild_encounter_rate >= 0.60

    def test_rock_tunnel_has_trainers(self):
        loc = get_location("Rock Tunnel")
        assert loc.trainers >= 3

    def test_rock_tunnel_can_explore(self):
        loc = get_location("Rock Tunnel")
        assert loc.can_explore() is True


class TestRockTunnelPhase2:
    """Tests for Rock Tunnel Phase 2 update — south exit to Lavender Town."""

    def test_rock_tunnel_has_lavender_town_exit(self):
        loc = get_location("Rock Tunnel")
        assert "Lavender Town" in loc.exits

    def test_rock_tunnel_lavender_town_exit_not_blocked(self):
        loc = get_location("Rock Tunnel")
        assert not loc.exits["Lavender Town"].get("blocked", False)

    def test_rock_tunnel_lavender_town_exit_direction_south(self):
        loc = get_location("Rock Tunnel")
        assert loc.exits["Lavender Town"]["direction"] == "south"


class TestLavenderTown:
    """Tests for Lavender Town location."""

    def test_lavender_town_exists(self):
        loc = get_location("Lavender Town")
        assert loc is not None

    def test_lavender_town_is_town_type(self):
        loc = get_location("Lavender Town")
        assert loc.type == TYPE_TOWN

    def test_lavender_town_cannot_explore(self):
        loc = get_location("Lavender Town")
        assert loc.can_explore() is False

    def test_lavender_town_has_pokemon_center(self):
        loc = get_location("Lavender Town")
        assert any("Pokemon Center" in b for b in loc.buildings)

    def test_lavender_town_has_pokemart(self):
        loc = get_location("Lavender Town")
        assert any("Pokemart" in b for b in loc.buildings)

    def test_lavender_town_has_pokemon_tower(self):
        loc = get_location("Lavender Town")
        assert any("Pokemon Tower" in b for b in loc.buildings)

    def test_lavender_town_has_rock_tunnel_exit(self):
        loc = get_location("Lavender Town")
        assert "Rock Tunnel" in loc.exits

    def test_lavender_town_has_route_8_exit(self):
        loc = get_location("Lavender Town")
        assert "Route 8" in loc.exits

    def test_lavender_town_has_route_12_exit(self):
        loc = get_location("Lavender Town")
        assert "Route 12" in loc.exits


class TestRoute8:
    """Tests for Route 8 (Saffron City ↔ Lavender Town)."""

    def test_route_8_exists(self):
        loc = get_location("Route 8")
        assert loc is not None

    def test_route_8_is_route_type(self):
        loc = get_location("Route 8")
        assert loc.type == TYPE_ROUTE

    def test_route_8_can_explore(self):
        loc = get_location("Route 8")
        assert loc.can_explore() is True

    def test_route_8_has_lavender_exit(self):
        loc = get_location("Route 8")
        assert "Lavender Town" in loc.exits

    def test_route_8_saffron_exit_is_blocked(self):
        loc = get_location("Route 8")
        assert "Saffron City" in loc.exits
        assert loc.exits["Saffron City"].get("blocked", False) is True

    def test_route_8_has_wild_pokemon(self):
        loc = get_location("Route 8")
        assert len(loc.wild_pokemon) > 0
        assert "GROWLITHE" in loc.wild_pokemon or "DROWZEE" in loc.wild_pokemon

    def test_route_8_wild_level_range(self):
        loc = get_location("Route 8")
        low, high = loc.wild_level_range
        assert low >= 15
        assert high <= 30

    def test_route_8_has_trainers(self):
        loc = get_location("Route 8")
        assert loc.trainers >= 2


class TestRoute7:
    """Tests for Route 7 (Celadon City ↔ Saffron City)."""

    def test_route_7_exists(self):
        loc = get_location("Route 7")
        assert loc is not None

    def test_route_7_is_route_type(self):
        loc = get_location("Route 7")
        assert loc.type == TYPE_ROUTE

    def test_route_7_can_explore(self):
        loc = get_location("Route 7")
        assert loc.can_explore() is True

    def test_route_7_celadon_exit_is_blocked(self):
        loc = get_location("Route 7")
        assert "Celadon City" in loc.exits
        assert loc.exits["Celadon City"].get("blocked", False) is True

    def test_route_7_saffron_exit_is_blocked(self):
        loc = get_location("Route 7")
        assert "Saffron City" in loc.exits
        assert loc.exits["Saffron City"].get("blocked", False) is True

    def test_route_7_has_wild_pokemon(self):
        loc = get_location("Route 7")
        assert len(loc.wild_pokemon) > 0

    def test_route_7_has_trainers(self):
        loc = get_location("Route 7")
        assert loc.trainers >= 2


class TestRoute12:
    """Tests for Route 12 (south of Lavender Town, fishing route)."""

    def test_route_12_exists(self):
        loc = get_location("Route 12")
        assert loc is not None

    def test_route_12_is_route_type(self):
        loc = get_location("Route 12")
        assert loc.type == TYPE_ROUTE

    def test_route_12_can_explore(self):
        loc = get_location("Route 12")
        assert loc.can_explore() is True

    def test_route_12_has_lavender_exit(self):
        loc = get_location("Route 12")
        assert "Lavender Town" in loc.exits

    def test_route_12_south_exit_is_blocked(self):
        loc = get_location("Route 12")
        assert "Route 13" in loc.exits
        assert loc.exits["Route 13"].get("blocked", False) is True

    def test_route_12_has_water_pokemon(self):
        loc = get_location("Route 12")
        water_types = {"TENTACOOL", "GOLDEEN", "MAGIKARP", "SEAKING"}
        assert len(water_types.intersection(set(loc.wild_pokemon))) > 0

    def test_route_12_has_trainers(self):
        loc = get_location("Route 12")
        assert loc.trainers >= 2


class TestPokemonTower:
    """Tests for Pokemon Tower dungeon location."""

    def test_pokemon_tower_exists(self):
        from pytemon.locations import TYPE_DUNGEON

        loc = get_location("Pokemon Tower")
        assert loc is not None
        assert loc.type == TYPE_DUNGEON

    def test_pokemon_tower_can_explore(self):
        loc = get_location("Pokemon Tower")
        assert loc.can_explore() is True

    def test_pokemon_tower_has_lavender_exit(self):
        loc = get_location("Pokemon Tower")
        assert "Lavender Town" in loc.exits

    def test_pokemon_tower_has_ghost_pokemon(self):
        loc = get_location("Pokemon Tower")
        assert "GASTLY" in loc.wild_pokemon or "HAUNTER" in loc.wild_pokemon

    def test_pokemon_tower_has_cubone(self):
        loc = get_location("Pokemon Tower")
        assert "CUBONE" in loc.wild_pokemon

    def test_pokemon_tower_has_trainers(self):
        loc = get_location("Pokemon Tower")
        assert loc.trainers >= 2
