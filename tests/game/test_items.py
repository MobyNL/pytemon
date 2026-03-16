"""
Unit tests for PokemonLibrary/items.py.
"""

import pytest

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.game_state import GameState
from pytemon.items import (
    ITEM_DATA,
    ItemData,
    get_item,
    get_item_canonical_name,
    use_item_outside_battle,
)
from pytemon.models import PartyPokemon


class MockRichLog:
    """Minimal stub for textual.widgets.RichLog."""

    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


def _make_party_pokemon(
    name: str = "PIKACHU",
    number: int = 25,
    level: int = 10,
    hp: int = 35,
    max_hp: int = 35,
    status=None,
) -> PartyPokemon:
    p = PartyPokemon(
        name=name,
        number=number,
        level=level,
        types=["Electric"],
        hp=hp,
        max_hp=max_hp,
        stats=StatsData(hp=max_hp, attack=55, defense=30, special=50, speed=90),
        moves=[MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)],
        experience=0,
        next_level_exp=1000,
    )
    p.status = status
    return p


def _give_item(gs: GameState, item_name: str, qty: int = 1) -> None:
    """Add items to the player's bag."""
    items = gs.game_data.setdefault("items", {})
    items[item_name] = items.get(item_name, 0) + qty


# ---------------------------------------------------------------------------
# ItemData dataclass
# ---------------------------------------------------------------------------


class TestItemData:
    def test_getitem_returns_attribute(self):
        item = ItemData(desc="test", emoji="🧪", cat="heal", heal=20)
        assert item["heal"] == 20

    def test_get_with_valid_key(self):
        item = ItemData(desc="test", emoji="🧪", cat="heal", heal=50)
        assert item.get("heal") == 50

    def test_get_with_missing_key_returns_default(self):
        item = ItemData(desc="test", emoji="🧪", cat="heal")
        assert item.get("nonexistent_key", "fallback") == "fallback"

    def test_get_with_missing_key_returns_none_default(self):
        item = ItemData(desc="test", emoji="🧪", cat="heal")
        assert item.get("nonexistent_key") is None


# ---------------------------------------------------------------------------
# get_item
# ---------------------------------------------------------------------------


class TestGetItem:
    def test_known_item_returns_data(self):
        data = get_item("Potion")
        assert data is not None
        assert data.heal == 20

    def test_case_insensitive_lookup(self):
        data = get_item("potion")
        assert data is not None

    def test_unknown_item_returns_none(self):
        assert get_item("Nonexistent Item") is None

    def test_super_potion_heal_value(self):
        data = get_item("Super Potion")
        assert data is not None
        assert data.heal == 50

    def test_antidote_cures_poison(self):
        data = get_item("Antidote")
        assert data is not None
        assert data.cures == "POISON"


# ---------------------------------------------------------------------------
# get_item_canonical_name
# ---------------------------------------------------------------------------


class TestGetItemCanonicalName:
    def test_exact_name_returns_self(self):
        name = get_item_canonical_name("Potion")
        assert name == "Potion"

    def test_lowercase_returns_canonical(self):
        name = get_item_canonical_name("super potion")
        assert name == "Super Potion"

    def test_unknown_item_returns_none(self):
        assert get_item_canonical_name("Fake Item") is None


# ---------------------------------------------------------------------------
# use_item_outside_battle — unknown item
# ---------------------------------------------------------------------------


class TestUseItemUnknown:
    def test_unknown_item_returns_false(self, gs, output):
        _give_item(gs, "Fake Item")
        result = use_item_outside_battle(gs, "Fake Item", None, output)
        assert result is False

    def test_unknown_item_writes_error(self, gs, output):
        _give_item(gs, "Fake Item")
        use_item_outside_battle(gs, "Fake Item", None, output)
        combined = " ".join(output.lines)
        assert "Unknown" in combined or "❌" in combined


# ---------------------------------------------------------------------------
# use_item_outside_battle — out of stock
# ---------------------------------------------------------------------------


class TestUseItemNoStock:
    def test_no_stock_returns_false(self, gs, output):
        # Don't give item to bag
        result = use_item_outside_battle(gs, "Potion", None, output)
        assert result is False

    def test_no_stock_writes_error(self, gs, output):
        use_item_outside_battle(gs, "Potion", None, output)
        combined = " ".join(output.lines)
        assert "no" in combined.lower() or "❌" in combined


# ---------------------------------------------------------------------------
# use_item_outside_battle — healing
# ---------------------------------------------------------------------------


class TestUseHealItem:
    def test_potion_heals_active_pokemon(self, gs, output):
        poke = _make_party_pokemon(hp=10, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Potion")
        result = use_item_outside_battle(gs, "Potion", None, output)
        assert result is True
        assert poke.hp == 30  # 10 + 20

    def test_potion_does_not_overheal(self, gs, output):
        poke = _make_party_pokemon(hp=34, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Potion")
        use_item_outside_battle(gs, "Potion", None, output)
        assert poke.hp == 35  # capped at max_hp

    def test_potion_consumed_from_bag(self, gs, output):
        poke = _make_party_pokemon(hp=10, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Potion", 2)
        use_item_outside_battle(gs, "Potion", None, output)
        assert gs.game_data["items"]["Potion"] == 1

    def test_max_potion_fully_heals(self, gs, output):
        poke = _make_party_pokemon(hp=1, max_hp=50)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Max Potion")
        use_item_outside_battle(gs, "Max Potion", None, output)
        assert poke.hp == 50

    def test_potion_on_fainted_pokemon_fails(self, gs, output):
        poke = _make_party_pokemon(hp=0, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Potion")
        result = use_item_outside_battle(gs, "Potion", None, output)
        assert result is False

    def test_potion_with_target_name(self, gs, output):
        poke = _make_party_pokemon(name="CHARMANDER", number=4, hp=10, max_hp=39)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Potion")
        result = use_item_outside_battle(gs, "Potion", "Charmander", output)
        assert result is True

    def test_potion_with_invalid_target(self, gs, output):
        poke = _make_party_pokemon(hp=10, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Potion")
        result = use_item_outside_battle(gs, "Potion", "NONEXISTENT", output)
        assert result is False


# ---------------------------------------------------------------------------
# use_item_outside_battle — cures
# ---------------------------------------------------------------------------


class TestUseCureItem:
    def test_antidote_cures_poison(self, gs, output):
        poke = _make_party_pokemon(status="POISON")
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Antidote")
        result = use_item_outside_battle(gs, "Antidote", None, output)
        assert result is True
        assert poke.status is None

    def test_antidote_on_non_poisoned_fails(self, gs, output):
        poke = _make_party_pokemon(status=None)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Antidote")
        result = use_item_outside_battle(gs, "Antidote", None, output)
        assert result is False

    def test_full_heal_cures_any_status(self, gs, output):
        poke = _make_party_pokemon(status="PARALYSIS")
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Full Heal")
        result = use_item_outside_battle(gs, "Full Heal", None, output)
        assert result is True
        assert poke.status is None


# ---------------------------------------------------------------------------
# use_item_outside_battle — revive
# ---------------------------------------------------------------------------


class TestUseReviveItem:
    def test_revive_revives_fainted_pokemon(self, gs, output):
        poke = _make_party_pokemon(hp=0, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Revive")
        result = use_item_outside_battle(gs, "Revive", None, output)
        assert result is True
        assert poke.hp > 0

    def test_revive_restores_half_hp(self, gs, output):
        poke = _make_party_pokemon(hp=0, max_hp=40)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Revive")
        use_item_outside_battle(gs, "Revive", None, output)
        assert poke.hp == 20  # half of 40

    def test_max_revive_fully_restores_hp(self, gs, output):
        poke = _make_party_pokemon(hp=0, max_hp=40)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Max Revive")
        use_item_outside_battle(gs, "Max Revive", None, output)
        assert poke.hp == 40

    def test_revive_no_fainted_fails(self, gs, output):
        poke = _make_party_pokemon(hp=35, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Revive")
        result = use_item_outside_battle(gs, "Revive", None, output)
        assert result is False

    def test_revive_on_not_fainted_target_fails(self, gs, output):
        poke = _make_party_pokemon(name="PIKACHU", hp=25, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Revive")
        result = use_item_outside_battle(gs, "Revive", "PIKACHU", output)
        assert result is False


# ---------------------------------------------------------------------------
# use_item_outside_battle — stat booster
# ---------------------------------------------------------------------------


class TestUseStatBooster:
    def test_hp_up_raises_max_hp(self, gs, output):
        poke = _make_party_pokemon(hp=35, max_hp=35)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "HP Up")
        original_max = poke.max_hp
        result = use_item_outside_battle(gs, "HP Up", "PIKACHU", output)
        assert result is True
        assert poke.max_hp == original_max + 10

    def test_stat_booster_requires_target(self, gs, output):
        poke = _make_party_pokemon()
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "HP Up")
        result = use_item_outside_battle(gs, "HP Up", None, output)
        assert result is False

    def test_protein_raises_attack(self, gs, output):
        poke = _make_party_pokemon()
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Protein")
        old_attack = poke.stats.attack
        result = use_item_outside_battle(gs, "Protein", "PIKACHU", output)
        assert result is True
        assert poke.stats.attack == old_attack + 5


# ---------------------------------------------------------------------------
# use_item_outside_battle — Rare Candy
# ---------------------------------------------------------------------------


class TestUseRareCandy:
    def test_rare_candy_levels_up_pokemon(self, gs, output):
        poke = _make_party_pokemon(level=5)
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Rare Candy")
        use_item_outside_battle(gs, "Rare Candy", "PIKACHU", output)
        assert poke.level == 6

    def test_rare_candy_requires_target(self, gs, output):
        poke = _make_party_pokemon()
        gs.game_data["pokemon"] = [poke]
        _give_item(gs, "Rare Candy")
        result = use_item_outside_battle(gs, "Rare Candy", None, output)
        assert result is False


# ---------------------------------------------------------------------------
# use_item_outside_battle — ball (battle-only)
# ---------------------------------------------------------------------------


class TestUseBallItem:
    def test_pokeball_cannot_be_used_outside_battle(self, gs, output):
        _give_item(gs, "Pokeball")
        result = use_item_outside_battle(gs, "Pokeball", None, output)
        assert result is False
        combined = " ".join(output.lines)
        assert "battle" in combined.lower()


# ---------------------------------------------------------------------------
# ITEM_DATA catalogue — sanity checks
# ---------------------------------------------------------------------------


class TestItemDataCatalogue:
    def test_potion_exists(self):
        assert "Potion" in ITEM_DATA

    def test_rare_candy_exists(self):
        assert "Rare Candy" in ITEM_DATA

    def test_ultra_ball_exists(self):
        assert "Ultra Ball" in ITEM_DATA

    def test_all_items_have_desc(self):
        for name, data in ITEM_DATA.items():
            assert data.desc, f"{name} missing description"

    def test_all_items_have_cat(self):
        for name, data in ITEM_DATA.items():
            assert data.cat, f"{name} missing category"


# ===========================================================================
# Additional tests for uncovered branches
# ===========================================================================


class TestUseItemOutsideBattleExtra:
    def test_unknown_item_shows_error(self, gs, output):
        gs.game_data["items"] = {"Fake Item": 1}
        result = use_item_outside_battle(gs, "fake_item_9999", None, output)
        assert result is False
        assert "Unknown" in " ".join(output.lines) or "❌" in " ".join(output.lines)

    def test_ball_cannot_be_used_outside_battle(self, gs, output):
        gs.game_data["items"] = {"Pokeball": 5}
        result = use_item_outside_battle(gs, "Pokeball", None, output)
        assert result is False
        assert "battle" in " ".join(output.lines).lower()

    def test_heal_item_full_hp_shows_warning(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["hp"] = p["max_hp"]
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Potion": 5}
        result = use_item_outside_battle(gs, "Potion", None, output)
        assert result is False
        assert "full" in " ".join(output.lines).lower()

    def test_heal_item_low_hp_heals(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["hp"] = 5
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Potion": 5}
        result = use_item_outside_battle(gs, "Potion", None, output)
        assert result is True
        assert p["hp"] > 5

    def test_heal_item_specific_target(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p1 = bs.generate_wild_pokemon("PIKACHU", 10)
        p2 = bs.generate_wild_pokemon("CHARMANDER", 10)
        p2["hp"] = 5
        gs.game_data["pokemon"] = [p1, p2]
        gs.game_data["items"] = {"Potion": 5}
        result = use_item_outside_battle(gs, "Potion", "charmander", output)
        assert result is True
        assert p2["hp"] > 5

    def test_heal_item_unknown_target(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Potion": 5}
        result = use_item_outside_battle(gs, "Potion", "fakemon99999", output)
        assert result is False

    def test_cure_item_no_status_shows_warning(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["status"] = None
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Antidote": 3}
        result = use_item_outside_battle(gs, "Antidote", None, output)
        assert result is False
        assert "no status" in " ".join(output.lines).lower()

    def test_cure_item_wrong_status_shows_warning(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["status"] = "SLEEP"
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Antidote": 3}
        result = use_item_outside_battle(gs, "Antidote", None, output)
        assert result is False

    def test_cure_item_correct_status_cures(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["status"] = "POISON"
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Antidote": 3}
        result = use_item_outside_battle(gs, "Antidote", None, output)
        assert result is True
        assert p["status"] is None

    def test_revive_heals_fainted_pokemon(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["hp"] = 0
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Revive": 1}
        result = use_item_outside_battle(gs, "Revive", None, output)
        assert result is True
        assert p["hp"] > 0

    def test_revive_no_fainted_shows_warning(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        p["hp"] = 20
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Revive": 1}
        result = use_item_outside_battle(gs, "Revive", None, output)
        assert result is False

    def test_rare_candy_levels_up_pokemon(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Rare Candy": 3}
        old_level = p["level"]
        result = use_item_outside_battle(gs, "Rare Candy", "pikachu", output)
        assert result is True
        assert p["level"] == old_level + 1

    def test_rare_candy_level_100_shows_warning(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 100)
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"Rare Candy": 3}
        result = use_item_outside_battle(gs, "Rare Candy", "pikachu", output)
        assert result is False
        assert "100" in " ".join(output.lines) or "already" in " ".join(output.lines).lower()

    def test_stat_item_requires_target(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"HP Up": 1}
        result = use_item_outside_battle(gs, "HP Up", None, output)
        assert result is False

    def test_stat_item_boosts_stat(self, gs, output):
        from pytemon.engine import BattleState

        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        old_max_hp = p["max_hp"]
        gs.game_data["pokemon"] = [p]
        gs.game_data["items"] = {"HP Up": 1}
        result = use_item_outside_battle(gs, "HP Up", "pikachu", output)
        assert result is True
        assert p["max_hp"] > old_max_hp

    def test_repel_adds_repel_steps(self, gs, output):
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        gs.game_data["items"] = {"Repel": 2}
        initial_steps = gs.game_data.get("repel_steps", 0)
        result = use_item_outside_battle(gs, "Repel", None, output)
        assert result is True
        assert gs.game_data.get("repel_steps", 0) > initial_steps

    def test_escape_rope_from_route(self, gs, output):
        from pytemon.locations import get_location

        gs.current_location = get_location("Route 1")
        gs.game_data["items"] = {"Escape Rope": 1}
        result = use_item_outside_battle(gs, "Escape Rope", None, output)
        assert result is True

    def test_escape_rope_in_town_shows_warning(self, gs, output):
        from pytemon.locations import get_location

        gs.current_location = get_location("Pallet Town")
        gs.game_data["items"] = {"Escape Rope": 1}
        result = use_item_outside_battle(gs, "Escape Rope", None, output)
        assert result is False
        assert (
            "town" in " ".join(output.lines).lower() or "already" in " ".join(output.lines).lower()
        )
