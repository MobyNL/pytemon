"""
Generation I type effectiveness chart.

TYPE_CHART[attack_type][defend_type] = multiplier
- 2.0 = Super effective
- 0.5 = Not very effective
- 0.0 = No effect
- Missing = 1.0 (neutral)
"""

from .pokemon_data import (
    BUG,
    DRAGON,
    ELECTRIC,
    FIGHTING,
    FIRE,
    FLYING,
    GHOST,
    GRASS,
    GROUND,
    ICE,
    NORMAL,
    POISON,
    PSYCHIC,
    ROCK,
    WATER,
)

TYPE_CHART = {
    NORMAL: {ROCK: 0.5, GHOST: 0.0},
    FIRE: {FIRE: 0.5, WATER: 0.5, GRASS: 2.0, ICE: 2.0, BUG: 2.0, ROCK: 0.5, DRAGON: 0.5},
    WATER: {FIRE: 2.0, WATER: 0.5, GRASS: 0.5, GROUND: 2.0, ROCK: 2.0, DRAGON: 0.5},
    GRASS: {
        FIRE: 0.5,
        WATER: 2.0,
        GRASS: 0.5,
        POISON: 0.5,
        GROUND: 2.0,
        FLYING: 0.5,
        BUG: 0.5,
        ROCK: 2.0,
        DRAGON: 0.5,
    },
    ELECTRIC: {WATER: 2.0, ELECTRIC: 0.5, GRASS: 0.5, GROUND: 0.0, FLYING: 2.0, DRAGON: 0.5},
    ICE: {WATER: 0.5, GRASS: 2.0, ICE: 0.5, GROUND: 2.0, FLYING: 2.0, DRAGON: 2.0},
    FIGHTING: {
        NORMAL: 2.0,
        ICE: 2.0,
        POISON: 0.5,
        FLYING: 0.5,
        PSYCHIC: 0.5,
        BUG: 0.5,
        ROCK: 2.0,
        GHOST: 0.0,
    },
    POISON: {GRASS: 2.0, POISON: 0.5, GROUND: 0.5, BUG: 2.0, ROCK: 0.5, GHOST: 0.5},
    GROUND: {FIRE: 2.0, ELECTRIC: 2.0, GRASS: 0.5, POISON: 2.0, FLYING: 0.0, BUG: 0.5, ROCK: 2.0},
    FLYING: {ELECTRIC: 0.5, GRASS: 2.0, FIGHTING: 2.0, BUG: 2.0, ROCK: 0.5},
    PSYCHIC: {FIGHTING: 2.0, POISON: 2.0, PSYCHIC: 0.5},
    BUG: {FIRE: 0.5, GRASS: 2.0, FIGHTING: 0.5, POISON: 2.0, FLYING: 0.5, PSYCHIC: 2.0, GHOST: 0.5},
    ROCK: {FIRE: 2.0, ICE: 2.0, FIGHTING: 0.5, GROUND: 0.5, FLYING: 2.0, BUG: 2.0},
    GHOST: {NORMAL: 0.0, PSYCHIC: 0.0, GHOST: 2.0},  # Gen 1 bug: Ghost is immune to Psychic
    DRAGON: {DRAGON: 2.0},
}


def get_type_effectiveness(attack_type: str, defender_types: list[str]) -> float:
    """
    Calculate the type effectiveness multiplier for an attack against a defender.
    Considers all of the defender's types (if dual-type).

    Args:
        attack_type: The type of the attacking move
        defender_types: List of the defender's types (1 or 2 types)

    Returns:
        float: Multiplier (0.0, 0.25, 0.5, 1.0, 2.0, or 4.0)
    """
    multiplier = 1.0
    for def_type in defender_types:
        if attack_type in TYPE_CHART:
            multiplier *= TYPE_CHART[attack_type].get(def_type, 1.0)
    return multiplier
