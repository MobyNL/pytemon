"""
Unit tests for PokemonLibrary/engine/battle_engine.py (BattleState).
"""

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.engine.battle_engine import BattleState
from pytemon.models import PartyPokemon


def make_pokemon(name="PIKACHU", number=25, level=10, **overrides) -> PartyPokemon:
    """Helper: create a minimal PartyPokemon for battle testing."""
    defaults = {
        "name": name,
        "number": number,
        "level": level,
        "types": ["Electric"],
        "hp": 35,
        "max_hp": 35,
        "stats": StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
        "moves": [MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)],
        "experience": 0,
        "next_level_exp": 1000,
    }
    defaults.update(overrides)
    return PartyPokemon(**defaults)


class TestBattleStateInit:
    """Tests for BattleState initialization."""

    def test_initial_state_not_active(self):
        bs = BattleState()
        assert bs.active is False

    def test_initial_no_pokemon(self):
        bs = BattleState()
        assert bs.player_pokemon is None
        assert bs.wild_pokemon is None

    def test_initial_turn_count_zero(self):
        bs = BattleState()
        assert bs.turn_count == 0


class TestCalculateStats:
    """Tests for BattleState.calculate_stats()."""

    def test_stats_increase_with_level(self):
        bs = BattleState()
        base = StatsData(hp=45, attack=49, defense=49, special=65, speed=45)
        stats_5 = bs.calculate_stats(base, 5)
        stats_20 = bs.calculate_stats(base, 20)
        assert stats_20.hp > stats_5.hp
        assert stats_20.attack > stats_5.attack

    def test_hp_stat_formula(self):
        bs = BattleState()
        base = StatsData(hp=45, attack=49, defense=49, special=65, speed=45)
        stats = bs.calculate_stats(base, 5)
        # HP = ((45 + 8) * 2 * 5 / 100) + 5 + 10 = (53 * 10 / 100) + 15 = 5 + 15 = 20
        expected = int(((45 + 8) * 2 * 5 / 100) + 5 + 10)
        assert stats.hp == expected

    def test_attack_stat_formula(self):
        bs = BattleState()
        base = StatsData(hp=45, attack=49, defense=49, special=65, speed=45)
        stats = bs.calculate_stats(base, 5)
        expected = int(((49 + 8) * 2 * 5 / 100) + 5)
        assert stats.attack == expected

    def test_returns_stats_data(self):
        bs = BattleState()
        base = StatsData(hp=45, attack=49, defense=49, special=65, speed=45)
        result = bs.calculate_stats(base, 10)
        assert isinstance(result, StatsData)


class TestGenerateWildPokemon:
    """Tests for BattleState.generate_wild_pokemon()."""

    def test_generates_known_species(self):
        bs = BattleState()
        p = bs.generate_wild_pokemon("PIKACHU", 10)
        assert p.name == "PIKACHU"

    def test_level_is_correct(self):
        bs = BattleState()
        p = bs.generate_wild_pokemon("CHARMANDER", 15)
        assert p.level == 15

    def test_has_valid_hp(self):
        bs = BattleState()
        p = bs.generate_wild_pokemon("BULBASAUR", 5)
        assert p.hp > 0
        assert p.max_hp >= p.hp

    def test_has_at_least_one_move(self):
        bs = BattleState()
        p = bs.generate_wild_pokemon("SQUIRTLE", 5)
        assert len(p.moves) >= 1

    def test_unknown_species_fallback(self):
        bs = BattleState()
        p = bs.generate_wild_pokemon("UNKNOWNMON", 5)
        assert p is not None
        assert p.hp > 0

    def test_returns_party_pokemon(self):
        bs = BattleState()
        p = bs.generate_wild_pokemon("RATTATA", 3)
        assert isinstance(p, PartyPokemon)


class TestStartWildBattle:
    """Tests for BattleState.start_wild_battle()."""

    def test_battle_becomes_active(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 3)
        assert bs.active is True

    def test_player_pokemon_is_set(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 3)
        assert bs.player_pokemon is player

    def test_wild_pokemon_is_generated(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "PIDGEY", 4)
        assert bs.wild_pokemon is not None
        assert bs.wild_pokemon.name == "PIDGEY"

    def test_is_not_trainer_battle(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 3)
        assert bs.is_trainer_battle is False

    def test_player_can_run_wild(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 3)
        assert bs.player_can_run is True


class TestCalculateDamage:
    """Tests for BattleState.calculate_damage()."""

    def test_damage_is_positive(self):
        bs = BattleState()
        attacker = make_pokemon(
            name="PIKACHU",
            number=25,
            level=10,
            types=["Electric"],
            stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
            moves=[MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)],
        )
        defender = make_pokemon(
            name="RATTATA",
            number=19,
            level=5,
            types=["Normal"],
            stats=StatsData(hp=30, attack=56, defense=35, special=25, speed=72),
            moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        )
        damage, _effectiveness_msg, _critical = bs.calculate_damage(
            attacker, defender, "THUNDER SHOCK"
        )
        assert damage >= 0

    def test_returns_tuple_of_three(self):
        bs = BattleState()
        attacker = make_pokemon()
        defender = make_pokemon(
            name="RATTATA",
            number=19,
            level=5,
            types=["Normal"],
            stats=StatsData(hp=30, attack=56, defense=35, special=25, speed=72),
            moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        )
        result = bs.calculate_damage(attacker, defender, "THUNDER SHOCK")
        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_immune_returns_zero_damage(self):
        bs = BattleState()
        # Electric vs Ground: 0 damage
        attacker = make_pokemon(
            name="PIKACHU",
            types=["Electric"],
            stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
        )
        defender = make_pokemon(
            name="DIGLETT",
            number=50,
            level=10,
            types=["Ground"],
            stats=StatsData(hp=10, attack=55, defense=25, special=45, speed=95),
            moves=[MoveSlot(name="SCRATCH", pp=35, max_pp=35)],
        )
        damage, _msg, _ = bs.calculate_damage(attacker, defender, "THUNDER SHOCK")
        assert damage == 0


class TestCalculateExpForLevel:
    """Tests for BattleState.calculate_exp_for_level()."""

    def test_level_2_exp_is_positive(self):
        bs = BattleState()
        exp = bs.calculate_exp_for_level(2)
        assert exp > 0

    def test_exp_increases_with_level(self):
        bs = BattleState()
        assert bs.calculate_exp_for_level(10) < bs.calculate_exp_for_level(20)

    def test_level_1_exp(self):
        bs = BattleState()
        exp = bs.calculate_exp_for_level(1)
        assert exp == 1  # 1^3 = 1


class TestCheckLevelUp:
    """Tests for BattleState.check_level_up()."""

    def test_no_level_up_below_threshold(self):
        bs = BattleState()
        p = make_pokemon(level=5, experience=0, next_level_exp=125)
        leveled_up, new_level = bs.check_level_up(p)
        assert not leveled_up
        assert new_level == 5

    def test_level_up_at_threshold(self):
        bs = BattleState()
        p = make_pokemon(level=5, experience=125, next_level_exp=125)
        leveled_up, new_level = bs.check_level_up(p)
        assert leveled_up
        assert new_level == 6

    def test_level_up_above_threshold(self):
        bs = BattleState()
        p = make_pokemon(level=5, experience=200, next_level_exp=125)
        leveled_up, _new_level = bs.check_level_up(p)
        assert leveled_up


class TestEndBattle:
    """Tests for BattleState.end_battle()."""

    def test_end_battle_deactivates(self):
        bs = BattleState()
        player = make_pokemon()
        bs.start_wild_battle(player, "RATTATA", 3)
        bs.end_battle()
        assert bs.active is False
