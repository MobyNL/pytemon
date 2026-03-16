"""
Game state management for Pokemon Terminal.

This module handles save/load functionality and game state tracking.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from .engine import BattleState
from .locations import Location, get_location, get_starting_location
from .models import PartyPokemon


class GameState:
    """Game state manager."""

    def __init__(self):
        """Initialize game state."""
        self.in_menu = True
        self.in_game = False
        self.current_save: Optional[Path] = None
        self.game_data: Dict[str, Any] = {}
        self.saves_dir = Path.cwd() / "saves"
        self.current_location: Optional[Location] = None
        # Autosave settings
        self.autosave_enabled = True
        self.autosave_frequency = 20  # Save every 20 commands by default
        self.commands_since_autosave = 0
        self.in_battle = False  # Track if in battle to skip autosave
        # Easter egg: Pokemon Yellow mode
        self.pikachu_mode = False  # Activated by secret command
        # Dev/Cheat mode
        self.cheat_mode = False  # Activated by secret phrase
        # Battle state
        self.battle_state: Optional[BattleState] = None

    @property
    def autosaves_dir(self) -> Path:
        """Subdirectory used exclusively for autosave files."""
        return self.saves_dir / "autosaves"

    def start_new_game(self) -> None:
        """Start a new game."""
        self.in_menu = False
        self.in_game = True
        self.current_save = None
        self.current_location = get_location(get_starting_location())
        self.game_data = {
            "player_name": "Trainer",
            "rival_name": "Rival",
            "location": get_starting_location(),
            "pokemon": [],
            "rival_pokemon": [],
            "badges": [],  # List of badge IDs earned
            "money": 3000,
            "items": {},
            "defeated_trainers": [],  # Track defeated trainer IDs
            "pikachu_mode": False,
            "save_name": None,  # Track the save file name
            "last_pokemon_center": None,  # Track last visited Pokemon Center for respawning
            "pokedex": {  # Track seen and caught Pokemon
                "seen": [],
                "caught": [],
            },
            "settings": {"autosave_enabled": True, "autosave_frequency": 20},
            "pc_storage": {},  # Bill's PC - stores extra Pokemon
            "route_progress": {},  # Explores completed per route/forest location
            "previous_location": None,  # Last location before the current one
            "stats": {},  # Adventure statistics (see stats.py)
            "found_items": {},  # Ground items collected per location (see exploration.py)
        }
        # Load settings from game_data
        self.autosave_enabled = True
        self.autosave_frequency = 20
        self.commands_since_autosave = 0
        self.pikachu_mode = False

    def load_game(self, save_file: Path) -> bool:
        """
        Load a game from a save file.

        Args:
            save_file: Path to the save file

        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            with open(save_file) as f:
                self.game_data = json.load(f)
            self.current_save = save_file
            self.in_menu = False
            self.in_game = True
            # Set the current location from the save data
            location_name = self.game_data.get("location", get_starting_location())
            self.current_location = get_location(location_name)
            # Load settings from save file
            settings = self.game_data.get("settings", {})
            self.autosave_enabled = settings.get("autosave_enabled", True)
            self.autosave_frequency = settings.get("autosave_frequency", 20)
            self.commands_since_autosave = 0
            # Load Pikachu mode status
            self.pikachu_mode = self.game_data.get("pikachu_mode", False)
            # Ensure save_name is set (for backward compatibility with old saves)
            if "save_name" not in self.game_data or not self.game_data["save_name"]:
                self.game_data["save_name"] = save_file.stem
            # Ensure last_pokemon_center is set (for backward compatibility with old saves)
            if "last_pokemon_center" not in self.game_data:
                self.game_data["last_pokemon_center"] = None
            # Ensure badges is a list (backward compatibility with old saves that stored 0)
            if not isinstance(self.game_data.get("badges"), list):
                self.game_data["badges"] = []
            # Ensure pc_storage exists (backward compatibility with old saves)
            if "pc_storage" not in self.game_data:
                self.game_data["pc_storage"] = {}
            # Ensure route_progress exists (backward compatibility with old saves)
            if "route_progress" not in self.game_data:
                self.game_data["route_progress"] = {}
            # Ensure previous_location exists (backward compatibility with old saves)
            if "previous_location" not in self.game_data:
                self.game_data["previous_location"] = None
            # Ensure stats dict exists (backward compatibility with old saves)
            if "stats" not in self.game_data or not isinstance(self.game_data.get("stats"), dict):
                self.game_data["stats"] = {}
            # Ensure found_items exists (backward compatibility with old saves)
            if "found_items" not in self.game_data or not isinstance(
                self.game_data.get("found_items"), dict
            ):
                self.game_data["found_items"] = {}
            # Migrate Pokedex data for existing saves (register party Pokemon)
            self._migrate_pokedex()
            # Deserialize party pokemon to PartyPokemon objects
            self._deserialize_party()
            return True
        except Exception:
            return False

    def _migrate_pokedex(self) -> None:
        """Migrate existing saves to include Pokedex data for party Pokemon."""
        try:
            from . import pokedex

            # This will initialize Pokedex and register all party Pokemon as caught
            registered = pokedex.migrate_existing_save(self)
            # Note: We don't output messages here since this runs silently on load
            # The player will see their party Pokemon in the Pokedex next time they check
        except Exception:
            # Silently fail if migration has issues - game will still work
            pass

    def _deserialize_party(self) -> None:
        """Convert raw party pokemon dicts to PartyPokemon objects after loading."""
        party = self.game_data.get("pokemon", [])
        self.game_data["pokemon"] = [
            PartyPokemon.from_dict(p) if isinstance(p, dict) else p for p in party
        ]
        # Also deserialize PC storage
        pc_storage = self.game_data.get("pc_storage", {})
        for box_key, slots in pc_storage.items():
            pc_storage[box_key] = [
                PartyPokemon.from_dict(p) if isinstance(p, dict) else p for p in slots
            ]

    @staticmethod
    def _serialize_pokemon(p) -> Optional[Dict[str, Any]]:
        """Convert a single party/PC entry to a JSON-safe plain dict."""
        if p is None:
            return None
        if isinstance(p, PartyPokemon):
            return p.to_dict()
        # Plain dict may still contain StatsData / MoveSlot dataclass objects —
        # normalise through PartyPokemon.from_dict → to_dict to sanitise them.
        if isinstance(p, dict):
            return PartyPokemon.from_dict(p).to_dict()
        return p

    def _serialize_party(self) -> List[Dict[str, Any]]:
        """Return party as a list of plain dicts for JSON serialization."""
        return [self._serialize_pokemon(p) for p in self.game_data.get("pokemon", [])]

    def _serialize_pc(self) -> Dict[str, List]:
        """Return PC storage as plain dicts for JSON serialization."""
        result = {}
        for box_key, slots in self.game_data.get("pc_storage", {}).items():
            result[box_key] = [self._serialize_pokemon(p) for p in slots]
        return result

    def save_game(self, save_name: Optional[str] = None) -> Path:
        """
        Save the current game.

        Args:
            save_name: Optional name for the save file

        Returns:
            Path to the saved file
        """
        # Create saves directory if it doesn't exist
        self.saves_dir.mkdir(exist_ok=True)

        # Generate save file name
        if save_name:
            save_file = self.saves_dir / f"{save_name}.json"
        elif self.current_save:
            save_file = self.current_save
        else:
            # Generate default name with timestamp
            import datetime

            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            save_file = self.saves_dir / f"save_{timestamp}.json"

        # Store the save name in the game data (without .json extension)
        self.game_data["save_name"] = save_file.stem

        # Build a JSON-safe snapshot (party pokemon serialized to dicts)
        save_snapshot = dict(self.game_data)
        save_snapshot["pokemon"] = self._serialize_party()
        save_snapshot["pc_storage"] = self._serialize_pc()

        # Save the game data
        with open(save_file, "w") as f:
            json.dump(save_snapshot, f, indent=2)

        self.current_save = save_file
        return save_file

    def get_available_saves(self) -> List[Path]:
        """
        Get list of available save files.

        Returns:
            List of save file paths
        """
        if not self.saves_dir.exists():
            return []

        return sorted(self.saves_dir.glob("*.json"))

    def get_available_autosaves(self) -> List[Path]:
        """
        Get list of autosave files from the autosaves subdirectory.

        Returns:
            List of autosave file paths, newest first.
        """
        if not self.autosaves_dir.exists():
            return []
        return sorted(self.autosaves_dir.glob("*.json"), reverse=True)

    def autosave_on_location_change(self) -> Optional[Path]:
        """
        Silently save to ``{save_name}_autosave.json`` after moving locations.

        Only fires when the game is active and autosave is enabled.
        The autosave file is separate from the player's main save so it can
        never accidentally overwrite a named save.

        Returns:
            Path the autosave was written to, or None if skipped.
        """
        if not self.in_game or not self.autosave_enabled:
            return None

        base_name = self.game_data.get("save_name") or ""
        if not base_name and self.current_save:
            base_name = self.current_save.stem
        # Strip any existing _autosave suffix so we don't stack them
        if base_name.endswith("_autosave"):
            base_name = base_name[: -len("_autosave")]
        if not base_name:
            base_name = "player"

        autosave_name = f"{base_name}_autosave"
        self.autosaves_dir.mkdir(parents=True, exist_ok=True)
        autosave_file = self.autosaves_dir / f"{autosave_name}.json"

        # Write without touching self.current_save or game_data['save_name']
        save_snapshot = dict(self.game_data)
        save_snapshot["save_name"] = autosave_name
        save_snapshot["pokemon"] = self._serialize_party()
        save_snapshot["pc_storage"] = self._serialize_pc()
        with open(autosave_file, "w") as f:
            json.dump(save_snapshot, f, indent=2)
        return autosave_file

    def get_active_pokemon(self) -> Optional[PartyPokemon]:
        """
        Return the first non-fainted Pokemon in the party.

        Also initialises battle stats if needed (via ensure_battle_ready).

        Returns:
            PartyPokemon, or None if the party is empty or all have fainted.
        """
        from .battle.battle_actions import ensure_battle_ready

        for p in self.game_data.get("pokemon", []):
            if isinstance(p, dict):
                ensure_battle_ready(p)
                if p.get("hp", 0) > 0:
                    return p
            elif isinstance(p, PartyPokemon):
                if p.hp > 0:
                    return p
        return None

    def find_pokemon(self, identifier: str) -> "tuple[Optional[PartyPokemon], int]":
        """
        Find a Pokemon in the party by name or 1-based slot number.

        Args:
            identifier: Pokemon name (partial match accepted) or slot number (1-6).

        Returns:
            Tuple of (PartyPokemon, 0-based index), or (None, -1) if not found.
        """
        pokemon_list = self.game_data.get("pokemon", [])
        try:
            slot = int(identifier)
            if 1 <= slot <= len(pokemon_list):
                p = pokemon_list[slot - 1]
                if p is not None:
                    return p, slot - 1
        except ValueError:
            pass
        identifier_lower = identifier.lower()
        for idx, p in enumerate(pokemon_list):
            if p is None:
                continue
            name = (p.name if isinstance(p, PartyPokemon) else p.get("name", "")).lower()
            if name == identifier_lower or identifier_lower in name:
                return p, idx
        return None, -1

    def get_route_progress(self, location_name: str) -> int:
        """
        Return how many explores the player has completed at the given location.

        Args:
            location_name: Name of the route or forest.

        Returns:
            int: Explore count accumulated (0 if never visited).
        """
        return self.game_data.get("route_progress", {}).get(location_name, 0)

    def increment_route_progress(self, location_name: str, steps: int = 1) -> int:
        """
        Increment the explore counter for the given location.

        Args:
            location_name: Name of the route or forest.
            steps: How many explore steps to add (default 1; pass 2 when cycling).

        Returns:
            int: New explore count after incrementing.
        """
        if "route_progress" not in self.game_data:
            self.game_data["route_progress"] = {}
        self.game_data["route_progress"][location_name] = (
            self.game_data["route_progress"].get(location_name, 0) + steps
        )
        return self.game_data["route_progress"][location_name]
