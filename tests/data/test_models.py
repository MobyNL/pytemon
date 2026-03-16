"""
Unit tests for PokemonLibrary/models.py (PartyPokemon dataclass).
"""

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.models import PartyPokemon


def make_pokemon(**overrides) -> PartyPokemon:
    """Helper: create a minimal valid PartyPokemon for testing."""
    defaults = {
        "name": "BULBASAUR",
        "number": 1,
        "level": 5,
        "types": ["Grass", "Poison"],
        "hp": 45,
        "max_hp": 45,
        "stats": StatsData(hp=45, attack=49, defense=49, special=65, speed=45),
        "moves": [MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        "experience": 0,
        "next_level_exp": 125,
    }
    defaults.update(overrides)
    return PartyPokemon(**defaults)


class TestPartyPokemonBasics:
    """Tests for basic PartyPokemon construction and attribute access."""

    def test_create_pokemon(self):
        p = make_pokemon()
        assert p.name == "BULBASAUR"
        assert p.level == 5
        assert p.hp == 45

    def test_is_fainted_false_when_alive(self):
        p = make_pokemon(hp=10)
        assert not p.is_fainted()

    def test_is_fainted_true_when_zero_hp(self):
        p = make_pokemon(hp=0)
        assert p.is_fainted()

    def test_is_fainted_true_when_negative_hp(self):
        p = make_pokemon(hp=-5)
        assert p.is_fainted()

    def test_dict_style_get_item(self):
        p = make_pokemon()
        assert p["name"] == "BULBASAUR"
        assert p["level"] == 5

    def test_dict_style_set_item(self):
        p = make_pokemon()
        p["hp"] = 20
        assert p.hp == 20

    def test_contains_existing_key(self):
        p = make_pokemon()
        assert "name" in p

    def test_contains_missing_key(self):
        p = make_pokemon()
        assert "nonexistent_key" not in p

    def test_get_existing_key(self):
        p = make_pokemon()
        assert p.get("name") == "BULBASAUR"

    def test_get_missing_key_default(self):
        p = make_pokemon()
        assert p.get("missing", "default") == "default"


class TestPartyPokemonHeal:
    """Tests for the heal() method."""

    def test_heal_increases_hp(self):
        p = make_pokemon(hp=20, max_hp=45)
        healed = p.heal(10)
        assert p.hp == 30
        assert healed == 10

    def test_heal_cannot_exceed_max_hp(self):
        p = make_pokemon(hp=40, max_hp=45)
        healed = p.heal(20)
        assert p.hp == 45
        assert healed == 5

    def test_heal_when_already_at_max(self):
        p = make_pokemon(hp=45, max_hp=45)
        healed = p.heal(10)
        assert p.hp == 45
        assert healed == 0

    def test_full_heal(self):
        p = make_pokemon(hp=0, max_hp=45)
        p.heal(45)
        assert p.hp == 45


class TestPartyPokemonStatus:
    """Tests for apply_status() and clear_status()."""

    def test_apply_status_sets_it(self):
        p = make_pokemon()
        p.apply_status("PSN")
        assert p.status == "PSN"

    def test_apply_status_does_not_overwrite_existing(self):
        p = make_pokemon()
        p.apply_status("PSN")
        p.apply_status("BRN")
        assert p.status == "PSN"

    def test_clear_status(self):
        p = make_pokemon()
        p.apply_status("SLP")
        p.clear_status()
        assert p.status is None

    def test_clear_status_when_no_status(self):
        p = make_pokemon()
        p.clear_status()  # Should not raise
        assert p.status is None


class TestPartyPokemonSerialization:
    """Tests for to_dict() / from_dict() round-trip."""

    def test_to_dict_returns_dict(self):
        p = make_pokemon()
        d = p.to_dict()
        assert isinstance(d, dict)

    def test_to_dict_contains_required_keys(self):
        p = make_pokemon()
        d = p.to_dict()
        for key in (
            "name",
            "number",
            "level",
            "types",
            "hp",
            "max_hp",
            "stats",
            "moves",
            "experience",
            "next_level_exp",
        ):
            assert key in d, f"Missing key: {key}"

    def test_round_trip_preserves_name(self):
        p = make_pokemon(name="PIKACHU", number=25)
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.name == "PIKACHU"

    def test_round_trip_preserves_level(self):
        p = make_pokemon(level=42)
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.level == 42

    def test_round_trip_preserves_hp(self):
        p = make_pokemon(hp=20, max_hp=45)
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.hp == 20
        assert p2.max_hp == 45

    def test_round_trip_preserves_moves(self):
        p = make_pokemon(moves=[MoveSlot(name="SCRATCH", pp=10, max_pp=35)])
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.moves[0].name == "SCRATCH"
        assert p2.moves[0].pp == 10

    def test_round_trip_preserves_stats(self):
        stats = StatsData(hp=45, attack=49, defense=49, special=65, speed=45)
        p = make_pokemon(stats=stats)
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.stats.attack == 49

    def test_round_trip_preserves_status(self):
        p = make_pokemon()
        p.apply_status("PSN")
        d = p.to_dict()
        p2 = PartyPokemon.from_dict(d)
        assert p2.status == "PSN"

    def test_from_dict_missing_fields_uses_defaults(self):
        """from_dict should not crash when optional fields are absent."""
        minimal = {"name": "RATTATA", "number": 19}
        p = PartyPokemon.from_dict(minimal)
        assert p.name == "RATTATA"
        assert p.level == 5  # default

    def test_to_dict_moves_are_plain_dicts(self):
        p = make_pokemon()
        d = p.to_dict()
        assert isinstance(d["moves"][0], dict)

    def test_to_dict_stats_is_plain_dict(self):
        p = make_pokemon()
        d = p.to_dict()
        assert isinstance(d["stats"], dict)
