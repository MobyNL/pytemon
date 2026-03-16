"""
Shared pytest fixtures for the Pokemon library test suite.
"""

import pytest

from pytemon.data.move_data import MoveSlot
from pytemon.data.pokemon_data import StatsData
from pytemon.game_state import GameState
from pytemon.models import PartyPokemon


@pytest.fixture
def game_state() -> GameState:
    """Return a fresh GameState with a new game started."""
    gs = GameState()
    gs.start_new_game()
    return gs


@pytest.fixture
def pikachu() -> PartyPokemon:
    """Return a test Pikachu PartyPokemon at level 10."""
    return PartyPokemon(
        name="PIKACHU",
        number=25,
        level=10,
        types=["Electric"],
        hp=35,
        max_hp=35,
        stats=StatsData(hp=35, attack=55, defense=30, special=50, speed=90),
        moves=[MoveSlot(name="THUNDER SHOCK", pp=30, max_pp=30)],
        experience=0,
        next_level_exp=1000,
    )


@pytest.fixture
def charmander() -> PartyPokemon:
    """Return a test Charmander PartyPokemon at level 5."""
    return PartyPokemon(
        name="CHARMANDER",
        number=4,
        level=5,
        types=["Fire"],
        hp=39,
        max_hp=39,
        stats=StatsData(hp=39, attack=52, defense=43, special=50, speed=65),
        moves=[MoveSlot(name="SCRATCH", pp=35, max_pp=35)],
        experience=0,
        next_level_exp=125,
    )
