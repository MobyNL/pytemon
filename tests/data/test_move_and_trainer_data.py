"""
Unit tests for PokemonLibrary/data/move_data.py and PokemonLibrary/data/trainer_data.py.
"""

from pytemon.data.move_data import (
    MOVES,
    MoveData,
    MoveSlot,
    get_move,
)
from pytemon.data.trainer_data import (
    TRAINERS,
    Trainer,
    TrainerPokemon,
    get_trainer,
    get_trainer_class_info,
    get_trainers_by_location,
)

# ===========================================================================
# MoveData dataclass
# ===========================================================================


class TestMoveData:
    def test_getitem_returns_field(self):
        m = MoveData(
            name="TACKLE", type="Normal", category="physical", power=40, accuracy=100, pp=35
        )
        assert m["name"] == "TACKLE"
        assert m["power"] == 40

    def test_get_existing_field(self):
        m = MoveData(
            name="TACKLE", type="Normal", category="physical", power=40, accuracy=100, pp=35
        )
        assert m.get("type") == "Normal"

    def test_get_missing_field_returns_default(self):
        m = MoveData(
            name="TACKLE", type="Normal", category="physical", power=40, accuracy=100, pp=35
        )
        assert m.get("nonexistent", "sentinel") == "sentinel"

    def test_get_missing_field_returns_none_by_default(self):
        m = MoveData(
            name="TACKLE", type="Normal", category="physical", power=40, accuracy=100, pp=35
        )
        assert m.get("nonexistent") is None

    def test_optional_effect_defaults_to_none(self):
        m = MoveData(
            name="TACKLE", type="Normal", category="physical", power=40, accuracy=100, pp=35
        )
        assert m.effect is None
        assert m.effect_chance is None


# ===========================================================================
# MoveSlot dataclass
# ===========================================================================


class TestMoveSlot:
    def test_getitem_returns_field(self):
        slot = MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)
        assert slot["name"] == "THUNDER SHOCK"
        assert slot["pp"] == 30

    def test_setitem_updates_field(self):
        slot = MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)
        slot["pp"] = 25
        assert slot.pp == 25

    def test_get_existing_field(self):
        slot = MoveSlot(name="TACKLE", pp=35, max_pp=35)
        assert slot.get("max_pp") == 35

    def test_get_missing_field_returns_default(self):
        slot = MoveSlot(name="TACKLE", pp=35, max_pp=35)
        assert slot.get("missing_field", 99) == 99

    def test_get_missing_field_returns_none_by_default(self):
        slot = MoveSlot(name="TACKLE", pp=35, max_pp=35)
        assert slot.get("missing_field") is None


# ===========================================================================
# get_move
# ===========================================================================


class TestGetMove:
    def test_known_move_returns_data(self):
        move = get_move("TACKLE")
        assert move is not None
        assert move.name == "TACKLE"

    def test_case_insensitive(self):
        move = get_move("tackle")
        assert move is not None

    def test_unknown_move_returns_none(self):
        assert get_move("FAKE MOVE XYZ") is None

    def test_thunder_shock_is_electric(self):
        move = get_move("THUNDERSHOCK")
        assert move is not None
        assert move.type == "Electric"

    def test_move_has_required_fields(self):
        move = get_move("TACKLE")
        assert move is not None
        assert move.category in ("physical", "special", "status")
        assert move.pp > 0

    def test_moves_dict_is_populated(self):
        assert len(MOVES) > 50  # Gen 1 has many moves

    def test_space_to_hyphen_normalization(self):
        """Test that moves with hyphens can be looked up with spaces."""
        # DOUBLE-EDGE is stored with a hyphen in MOVES dict
        move_hyphen = get_move("DOUBLE-EDGE")
        move_space = get_move("DOUBLE EDGE")

        assert move_hyphen is not None
        assert move_space is not None
        assert move_hyphen.name == "DOUBLE-EDGE"
        assert move_space.name == "DOUBLE-EDGE"
        assert move_hyphen is move_space  # Should be the same object

    def test_normalization_case_insensitive(self):
        """Test that normalization works with any case."""
        move = get_move("double edge")
        assert move is not None
        assert move.name == "DOUBLE-EDGE"


# ===========================================================================
# TrainerPokemon dataclass
# ===========================================================================


class TestTrainerPokemon:
    def test_getitem_returns_field(self):
        tp = TrainerPokemon(species="PIKACHU", level=10)
        assert tp["species"] == "PIKACHU"
        assert tp["level"] == 10

    def test_get_existing_field(self):
        tp = TrainerPokemon(species="CHARMANDER", level=5)
        assert tp.get("species") == "CHARMANDER"

    def test_get_missing_field_returns_default(self):
        tp = TrainerPokemon(species="BULBASAUR", level=5)
        assert tp.get("nonexistent", "fallback") == "fallback"

    def test_get_missing_field_returns_none_by_default(self):
        tp = TrainerPokemon(species="SQUIRTLE", level=8)
        assert tp.get("nonexistent") is None


# ===========================================================================
# Trainer dataclass
# ===========================================================================


class TestTrainerDataclass:
    def _make_trainer(self, trainer_id="test_trainer", location="Pallet Town"):
        return Trainer(
            id=trainer_id,
            name="Test Trainer",
            trainer_class="Youngster",
            location=location,
            pokemon=[TrainerPokemon(species="RATTATA", level=5)],
            prize_money=100,
            intro_text=["Ready to battle!"],
            defeat_text=["I lost!"],
            victory_text=["I won!"],
        )

    def test_trainer_has_correct_id(self):
        t = self._make_trainer()
        assert t.id == "test_trainer"

    def test_trainer_has_pokemon(self):
        t = self._make_trainer()
        assert len(t.pokemon) == 1

    def test_trainer_location(self):
        t = self._make_trainer(location="Viridian City")
        assert t.location == "Viridian City"


# ===========================================================================
# get_trainer
# ===========================================================================


class TestGetTrainer:
    def test_known_trainer_returns_trainer(self):
        # Use an existing trainer from the data
        trainer_id = next(iter(TRAINERS))
        result = get_trainer(trainer_id)
        assert result is not None
        assert isinstance(result, Trainer)

    def test_unknown_trainer_returns_none(self):
        assert get_trainer("nonexistent_trainer_xyz") is None

    def test_returns_correct_trainer(self):
        trainer_id = next(iter(TRAINERS))
        trainer = get_trainer(trainer_id)
        assert trainer is not None
        assert trainer.id == trainer_id


# ===========================================================================
# get_trainers_by_location
# ===========================================================================


class TestGetTrainersByLocation:
    def test_returns_list(self):
        result = get_trainers_by_location("Pallet Town")
        assert isinstance(result, list)

    def test_unknown_location_returns_empty_list(self):
        result = get_trainers_by_location("Nonexistent Location")
        assert result == []

    def test_trainers_are_trainer_instances(self):
        # Find a location that has trainers
        locations = {t.location for t in TRAINERS.values()}
        if locations:
            loc = next(iter(locations))
            trainers = get_trainers_by_location(loc)
            assert all(isinstance(t, Trainer) for t in trainers)

    def test_trainers_have_correct_location(self):
        locations = {t.location for t in TRAINERS.values()}
        if locations:
            loc = next(iter(locations))
            trainers = get_trainers_by_location(loc)
            for t in trainers:
                assert t.location == loc


# ===========================================================================
# get_trainer_class_info
# ===========================================================================


class TestGetTrainerClassInfo:
    def test_known_class_returns_dict(self):
        # Find a class that exists
        classes_in_trainers = {t.trainer_class for t in TRAINERS.values()}
        if classes_in_trainers:
            cls = next(iter(classes_in_trainers))
            result = get_trainer_class_info(cls)
            assert isinstance(result, dict)

    def test_unknown_class_returns_empty_dict(self):
        result = get_trainer_class_info("Nonexistent Class XYZ")
        assert result == {}
