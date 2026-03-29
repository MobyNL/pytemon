"""
Dataclass models for in-memory Pokemon party representation.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from .data.move_data import MoveSlot
from .data.pokemon_data import StatsData


@dataclass
class PartyPokemon:
    """A Pokemon in the player's party (in-memory representation)."""

    # Required fields
    name: str
    number: int
    level: int
    types: List[str]
    hp: int
    max_hp: int
    stats: StatsData
    moves: List[MoveSlot]
    experience: int
    next_level_exp: int

    # Optional fields with defaults
    status: Optional[str] = None
    no_evolve: bool = False
    catch_rate: int = 255
    base_exp: int = 50
    sleep_count: int = 0
    toxic_counter: int = 0
    hp_bonus: int = 0
    attack_bonus: int = 0
    defense_bonus: int = 0
    special_bonus: int = 0
    speed_bonus: int = 0

    def __post_init__(self) -> None:
        # Normalize stats: dict → StatsData
        if isinstance(self.stats, dict):
            self.stats = StatsData(
                hp=self.stats.get("hp", self.max_hp),
                attack=self.stats.get("attack", 50),
                defense=self.stats.get("defense", 50),
                special=self.stats.get("special", 50),
                speed=self.stats.get("speed", 50),
            )
        # Normalize moves: list of dicts → list of MoveSlot
        self.moves = [
            MoveSlot(**m) if isinstance(m, dict) else m
            for m in self.moves
        ]

    def is_fainted(self) -> bool:
        """Return True if this Pokemon has 0 or fewer HP."""
        return self.hp <= 0

    def heal(self, amount: int) -> int:
        """Heal by *amount* HP (capped at max_hp). Returns actual HP restored."""
        old_hp = self.hp
        self.hp = min(self.hp + amount, self.max_hp)
        return self.hp - old_hp

    def apply_status(self, status: str) -> None:
        """Set a status condition (only if none is currently active)."""
        if not self.status:
            self.status = status

    def clear_status(self) -> None:
        """Remove any status condition."""
        self.status = None

    # ------------------------------------------------------------------
    # Dict-style access shims for backward compatibility with callers
    # that still use pokemon["key"] or pokemon.get("key") notation.
    # ------------------------------------------------------------------

    def __getitem__(self, key: str):
        return getattr(self, key)

    def __setitem__(self, key: str, value) -> None:
        setattr(self, key, value)

    def __contains__(self, key: str) -> bool:
        return hasattr(self, key)

    def get(self, key: str, default=None):
        try:
            return getattr(self, key)
        except AttributeError:
            return default

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a plain dict suitable for JSON save."""
        return {
            "name": self.name,
            "number": self.number,
            "level": self.level,
            "types": self.types,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "stats": {
                "hp": self.stats.hp,
                "attack": self.stats.attack,
                "defense": self.stats.defense,
                "special": self.stats.special,
                "speed": self.stats.speed,
            },
            "moves": [{"name": m.name, "pp": m.pp, "max_pp": m.max_pp} for m in self.moves],
            "experience": self.experience,
            "next_level_exp": self.next_level_exp,
            "status": self.status,
            "no_evolve": self.no_evolve,
            "catch_rate": self.catch_rate,
            "base_exp": self.base_exp,
            "sleep_count": self.sleep_count,
            "toxic_counter": self.toxic_counter,
            "hp_bonus": self.hp_bonus,
            "attack_bonus": self.attack_bonus,
            "defense_bonus": self.defense_bonus,
            "special_bonus": self.special_bonus,
            "speed_bonus": self.speed_bonus,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> PartyPokemon:
        """Deserialize from a dict (JSON save format or legacy format)."""
        stats_raw = d.get("stats", {})
        if isinstance(stats_raw, StatsData):
            stats = stats_raw
        elif isinstance(stats_raw, dict):
            stats = StatsData(
                hp=stats_raw.get("hp", 50),
                attack=stats_raw.get("attack", 50),
                defense=stats_raw.get("defense", 50),
                special=stats_raw.get("special", 50),
                speed=stats_raw.get("speed", 50),
            )
        else:
            stats = StatsData(hp=50, attack=50, defense=50, special=50, speed=50)

        moves_raw = d.get("moves", [])
        moves = []
        for m in moves_raw:
            if isinstance(m, MoveSlot):
                moves.append(m)
            elif isinstance(m, dict):
                moves.append(
                    MoveSlot(
                        name=m.get("name", "TACKLE"),
                        pp=m.get("pp", 35),
                        max_pp=m.get("max_pp", 35),
                    )
                )
            else:
                moves.append(MoveSlot(name=str(m), pp=35, max_pp=35))

        return cls(
            name=d.get("name", "UNKNOWN"),
            number=d.get("number", 0),
            level=d.get("level", 5),
            types=d.get("types", ["Normal"]),
            hp=d.get("hp", 20),
            max_hp=d.get("max_hp", 20),
            stats=stats,
            moves=moves,
            experience=d.get("experience", 0),
            next_level_exp=d.get("next_level_exp", 125),
            status=d.get("status"),
            no_evolve=d.get("no_evolve", False),
            catch_rate=d.get("catch_rate", 255),
            base_exp=d.get("base_exp", 50),
            sleep_count=d.get("sleep_count", 0),
            toxic_counter=d.get("toxic_counter", 0),
            hp_bonus=d.get("hp_bonus", 0),
            attack_bonus=d.get("attack_bonus", 0),
            defense_bonus=d.get("defense_bonus", 0),
            special_bonus=d.get("special_bonus", 0),
            speed_bonus=d.get("speed_bonus", 0),
        )
