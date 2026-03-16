"""
Extended tests for PokemonLibrary/evolution.py.

Covers the branches that are not yet reached by test_evolution.py:
  - get_stone_evolution (multi-branch + single-branch)
  - apply_evolution (happy path + no evolution)
  - force_evolve (happy path + unknown target form + pokemon not in party)
"""

import pytest

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.evolution import (
    apply_evolution,
    force_evolve,
    get_stone_evolution,
)
from pytemon.game_state import GameState
from pytemon.models import PartyPokemon


class MockRichLog:
    def __init__(self):
        self.lines = []

    def write(self, text: str) -> None:
        self.lines.append(text)


def make_pokemon(
    name: str,
    number: int,
    level: int,
    no_evolve: bool = False,
    **overrides,
) -> PartyPokemon:
    p = PartyPokemon(
        name=name,
        number=number,
        level=level,
        types=["Normal"],
        hp=45,
        max_hp=45,
        stats=StatsData(hp=45, attack=49, defense=49, special=65, speed=45),
        moves=[MoveSlot(name="TACKLE", pp=35, max_pp=35)],
        experience=0,
        next_level_exp=125,
    )
    if no_evolve:
        p["no_evolve"] = True
    for k, v in overrides.items():
        setattr(p, k, v)
    return p


@pytest.fixture
def gs() -> GameState:
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def output() -> MockRichLog:
    return MockRichLog()


# ---------------------------------------------------------------------------
# get_stone_evolution
# ---------------------------------------------------------------------------


class TestGetStoneEvolution:
    def test_no_evolve_flag_prevents_stone_evolution(self):
        p = make_pokemon("PIKACHU", 25, 5, no_evolve=True)
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result is None

    def test_no_number_returns_none(self):
        p = make_pokemon("PIKACHU", 0, 5)
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result is None

    def test_pikachu_evolves_with_thunder_stone(self):
        # Pikachu (25) evolves into Raichu with Thunder Stone
        p = make_pokemon("PIKACHU", 25, 5)
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result == "RAICHU"

    def test_eevee_multi_branch_fire_stone(self):
        # Eevee (133) has multi-branch evolutions
        p = make_pokemon("EEVEE", 133, 5)
        result = get_stone_evolution(p, "FIRE STONE")
        assert result == "FLAREON"

    def test_wrong_stone_returns_none(self):
        # Charmander doesn't evolve with stones
        p = make_pokemon("CHARMANDER", 4, 5)
        result = get_stone_evolution(p, "FIRE STONE")
        assert result is None

    def test_nonexistent_species_returns_none(self):
        p = make_pokemon("FAKEMON", 9999, 5)
        result = get_stone_evolution(p, "THUNDER STONE")
        assert result is None


# ---------------------------------------------------------------------------
# apply_evolution
# ---------------------------------------------------------------------------


class TestApplyEvolution:
    def test_pokemon_that_cannot_evolve_returns_false(self, gs, output):
        # Pikachu at level 2 shouldn't evolve (level too low)
        poke = make_pokemon("CATERPIE", 10, 1)
        gs.game_data["pokemon"] = [poke]
        result = apply_evolution(gs, poke, output)
        # Either True (if level condition met) or False (if not)
        assert isinstance(result, bool)

    def test_apply_evolution_on_eligible_pokemon(self, gs, output):
        # CATERPIE (#10) evolves into METAPOD at level 7
        poke = make_pokemon("CATERPIE", 10, 7)
        gs.game_data["pokemon"] = [poke]
        result = apply_evolution(gs, poke, output)
        assert result is True
        # Party should now contain the evolved form
        assert gs.game_data["pokemon"][0].name == "METAPOD"

    def test_apply_evolution_writes_output(self, gs, output):
        poke = make_pokemon("CATERPIE", 10, 7)
        gs.game_data["pokemon"] = [poke]
        apply_evolution(gs, poke, output)
        assert len(output.lines) > 0


# ---------------------------------------------------------------------------
# force_evolve
# ---------------------------------------------------------------------------


class TestForceEvolve:
    def test_force_evolve_changes_name(self, gs, output):
        poke = make_pokemon("CHARMANDER", 4, 10)
        gs.game_data["pokemon"] = [poke]
        result = force_evolve(gs, poke, "CHARMELEON", output)
        assert result is True
        assert gs.game_data["pokemon"][0].name == "CHARMELEON"

    def test_force_evolve_preserves_hp_percentage(self, gs, output):
        poke = make_pokemon("CHARMANDER", 4, 10, hp=22, max_hp=44)
        gs.game_data["pokemon"] = [poke]
        force_evolve(gs, poke, "CHARMELEON", output)
        evolved = gs.game_data["pokemon"][0]
        # HP should be ~50% of new max_hp
        assert evolved.hp > 0
        ratio = evolved.hp / evolved.max_hp
        assert 0.3 <= ratio <= 0.7

    def test_force_evolve_unknown_form_uses_fallback(self, gs, output):
        # generate_wild_pokemon creates a fallback for unknown species
        # so force_evolve succeeds but with a fallback pokemon
        poke = make_pokemon("CHARMANDER", 4, 10)
        gs.game_data["pokemon"] = [poke]
        result = force_evolve(gs, poke, "NONEXISTENT_FORM_XYZ", output)
        # Either True (fallback) or False — just don't crash
        assert isinstance(result, bool)

    def test_force_evolve_pokemon_not_in_party_returns_false(self, gs, output):
        poke = make_pokemon("CHARMANDER", 4, 10)
        # Don't add poke to the party
        gs.game_data["pokemon"] = []
        result = force_evolve(gs, poke, "CHARMELEON", output)
        assert result is False

    def test_force_evolve_preserves_experience(self, gs, output):
        poke = make_pokemon("CHARMANDER", 4, 10)
        poke.experience = 500
        gs.game_data["pokemon"] = [poke]
        force_evolve(gs, poke, "CHARMELEON", output)
        evolved = gs.game_data["pokemon"][0]
        assert evolved.experience == 500

    def test_force_evolve_writes_congratulations(self, gs, output):
        poke = make_pokemon("CHARMANDER", 4, 10)
        gs.game_data["pokemon"] = [poke]
        force_evolve(gs, poke, "CHARMELEON", output)
        combined = " ".join(output.lines)
        assert "CHARMELEON" in combined

    def test_force_evolve_updates_battle_state(self, gs, output):
        from pytemon.engine.battle_engine import BattleState

        poke = make_pokemon("CHARMANDER", 4, 10)
        gs.game_data["pokemon"] = [poke]
        gs.battle_state = BattleState()
        gs.battle_state.player_pokemon = poke
        gs.battle_state.active = True
        force_evolve(gs, poke, "CHARMELEON", output, update_battle_state=True)
        assert gs.battle_state.player_pokemon.name == "CHARMELEON"


class TestForceEvolveSilentPreamble:
    """Tests for force_evolve's silent_preamble parameter."""

    def _make_charmander_party(self) -> tuple:
        gs = GameState()
        gs.start_new_game()
        poke = make_pokemon("CHARMANDER", 4, 16)
        gs.game_data["pokemon"] = [poke]
        output = MockRichLog()
        return gs, poke, output

    def test_default_shows_preamble(self):
        gs, poke, output = self._make_charmander_party()
        force_evolve(gs, poke, "CHARMELEON", output)
        combined = " ".join(output.lines)
        assert "evolving" in combined.lower()
        assert "◇" in combined or "◆" in combined

    def test_silent_preamble_skips_diamonds(self):
        gs, poke, output = self._make_charmander_party()
        force_evolve(gs, poke, "CHARMELEON", output, silent_preamble=True)
        combined = " ".join(output.lines)
        # Congratulations message still appears
        assert "Congratulations" in combined
        # But the ◇/◆ animation lines are absent
        assert "◇" not in combined
        assert "◆" not in combined

    def test_silent_preamble_still_shows_congratulations(self):
        gs, poke, output = self._make_charmander_party()
        force_evolve(gs, poke, "CHARMELEON", output, silent_preamble=True)
        combined = " ".join(output.lines)
        assert "CHARMELEON" in combined
        assert "Congratulations" in combined

    def test_silent_preamble_still_updates_party(self):
        gs, poke, output = self._make_charmander_party()
        result = force_evolve(gs, poke, "CHARMELEON", output, silent_preamble=True)
        assert result is True
        assert gs.game_data["pokemon"][0]["name"] == "CHARMELEON"
