"""
Dungeon system for pytemon.

Provides the ``DungeonDefinition`` data model, per-floor encounter tables,
checkpoint support, and helpers for navigating multi-floor dungeons.

Dungeon flow
------------
1. Player moves to a dungeon ``Location`` (e.g. "Mt. Moon").
2. ``enter_dungeon()`` is called automatically; it sets
   ``game_state.game_data["dungeon_state"]`` and places the player on
   the entrance floor.
3. The player types ``explore`` — ``explore_area()`` delegates to the
   active floor's encounter table instead of the flat ``Location`` table.
4. The player types ``go down`` / ``go up`` / ``take stairs`` etc.  —
   ``dungeon_navigate()`` moves between floors and fires event hooks when
   a new floor is reached for the first time.
5. Floors marked ``is_checkpoint = True`` are saved automatically on
   arrival, so a blackout respawns the player there (see
   ``handle_dungeon_blackout()``).
6. On ``move_to_location()`` out of the dungeon, ``exit_dungeon()``
   clears the transient dungeon state.
7. ``dungeon_where()`` prints a status panel usable via the ``where``
   command.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from textual.widgets import RichLog

from .texts.en import dungeon as T  # noqa: N812
from .ui.formatters import write_lines, write_lines_fmt

if TYPE_CHECKING:
    from .game_state import GameState


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class DungeonFloorExit:
    """A one-directional link from one floor to another (or out of the dungeon).

    Attributes:
        direction: Player-facing direction label (``"up"``, ``"down"``,
            ``"north"``, ``"south"``, ``"ladder"``, ``"stairs"``, ``"warp"``).
        label: Short description shown in the ``where`` panel.
        target_floor: ``floor_id`` of the destination floor.  Use the
            sentinel ``"EXIT"`` to signal that this exit leaves the dungeon
            entirely; ``target_location`` is used in that case.
        target_location: Destination ``Location`` name when
            ``target_floor == "EXIT"``.
        one_way: If ``True`` the player cannot go back through this exit.
        requires_flag: Optional story-flag key that must be ``True`` in
            ``game_state.game_data["story_flags"]`` before the exit opens.
        requires_item: Optional item name that must be in the player's bag.
        requires_badge: Optional badge id that must be in
            ``game_state.game_data["badges"]``.
    """

    direction: str
    label: str
    target_floor: str
    target_location: str = ""
    one_way: bool = False
    requires_flag: Optional[str] = None
    requires_item: Optional[str] = None
    requires_badge: Optional[str] = None


@dataclass
class DungeonFloor:
    """A single named floor or room inside a dungeon.

    Attributes:
        floor_id: Unique identifier (e.g. ``"mt_moon_b1f"``).
        name: Human-readable name shown in ``dungeon_where()`` and arrival
            text (e.g. ``"Mt. Moon B1F"``).
        description: Flavour description shown on arrival.
        exits: List of :class:`DungeonFloorExit` objects leading elsewhere.
        wild_pokemon: Species keys (uppercase) that can be encountered here.
        level_range: ``(min_level, max_level)`` for wild encounters.
        encounter_rate: Probability (0-1) of a wild encounter per explore.
        encounter_weights: Optional ``{species: int}`` weights for random
            selection.  If ``None``, all species are chosen uniformly.
        trainer_ids: List of trainer IDs (from ``trainer_data.py``) that
            appear on this floor.
        item_pickups: One-time items awarded on first visit / triggered event.
            These are added to the bag when the ``item_flag`` event fires.
        item_flag: Story-flag key set when ``item_pickups`` are awarded.
            The flag is checked so items are only given once per save.
        is_checkpoint: If ``True``, arriving here updates the dungeon
            checkpoint so a blackout respawns here.
        event_hook: Named event string fired on the player's **first** arrival
            (handled by :func:`_fire_event_hook`).
    """

    floor_id: str
    name: str
    description: str
    exits: List[DungeonFloorExit]
    wild_pokemon: List[str]
    level_range: Tuple[int, int] = (5, 10)
    encounter_rate: float = 0.55
    encounter_weights: Optional[Dict[str, int]] = None
    trainer_ids: List[str] = field(default_factory=list)
    item_pickups: List[str] = field(default_factory=list)
    item_flag: Optional[str] = None
    is_checkpoint: bool = False
    event_hook: Optional[str] = None


@dataclass
class DungeonDefinition:
    """Complete multi-floor dungeon definition.

    Attributes:
        dungeon_id: Unique identifier used as a key in ``DUNGEONS``.
        name: Human-readable name (usually matches the ``Location`` name).
        location_name: The ``Location.name`` value that triggers this dungeon.
        entrance_floor: ``floor_id`` of the floor the player lands on when
            entering the dungeon from the overworld.
        floors: ``{floor_id: DungeonFloor}`` mapping.
        escape_to: Town name for Escape Rope (BFS fallback is also used, but
            this gives a definitive destination).
        completion_flag: Optional story-flag key set when the player exits
            through the *final* exit (``target_floor == "EXIT"``).
        blackout_floor: Floor to respawn at after a blackout.  Defaults to
            ``entrance_floor`` when ``None``.
    """

    dungeon_id: str
    name: str
    location_name: str
    entrance_floor: str
    floors: Dict[str, DungeonFloor]
    escape_to: str
    completion_flag: Optional[str] = None
    blackout_floor: Optional[str] = None

    def get_floor(self, floor_id: str) -> Optional[DungeonFloor]:
        """Return the floor with *floor_id*, or ``None`` if not found."""
        return self.floors.get(floor_id)

    def respawn_floor(self) -> str:
        """Return the floor_id to respawn on after a blackout."""
        return self.blackout_floor or self.entrance_floor


# ---------------------------------------------------------------------------
# Dungeon registry
# ---------------------------------------------------------------------------

DUNGEONS: Dict[str, DungeonDefinition] = {
    # ══════════════════════════════════════════════════════════════════════
    # MT. MOON  (3 floors)
    # ══════════════════════════════════════════════════════════════════════
    "mt_moon": DungeonDefinition(
        dungeon_id="mt_moon",
        name="Mt. Moon",
        location_name="Mt. Moon",
        entrance_floor="mt_moon_1f",
        escape_to="Pewter City",
        completion_flag="mt_moon_completed",
        floors={
            "mt_moon_1f": DungeonFloor(
                floor_id="mt_moon_1f",
                name="Mt. Moon 1F",
                description=(
                    "The cave entrance reeks of damp stone and Zubat guano. "
                    "Hikers have left rope markings on the walls. A ladder descends into darkness."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="down",
                        label="Ladder to B1F",
                        target_floor="mt_moon_b1f",
                    ),
                ],
                wild_pokemon=["ZUBAT", "GEODUDE", "PARAS"],
                level_range=(8, 12),
                encounter_rate=0.55,
                encounter_weights={"ZUBAT": 50, "GEODUDE": 35, "PARAS": 15},
                trainer_ids=["hiker_alan", "hiker_wayne"],
                is_checkpoint=True,
            ),
            "mt_moon_b1f": DungeonFloor(
                floor_id="mt_moon_b1f",
                name="Mt. Moon B1F",
                description=(
                    "The air grows colder. Sparkling mineral deposits line the walls. "
                    "Clefairy dance in the moonlight filtering through a crack above. "
                    "A passage leads further down."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="up",
                        label="Ladder to 1F",
                        target_floor="mt_moon_1f",
                    ),
                    DungeonFloorExit(
                        direction="down",
                        label="Ladder to B2F (Fossil Chamber)",
                        target_floor="mt_moon_b2f",
                    ),
                ],
                wild_pokemon=["ZUBAT", "GEODUDE", "CLEFAIRY", "PARAS"],
                level_range=(9, 13),
                encounter_rate=0.60,
                encounter_weights={"ZUBAT": 40, "GEODUDE": 30, "CLEFAIRY": 20, "PARAS": 10},
                trainer_ids=["hiker_lenny"],
                item_pickups=["Moon Stone"],
                item_flag="mt_moon_b1f_moon_stone",
                is_checkpoint=True,
                event_hook="mt_moon_b1f_arrival",
            ),
            "mt_moon_b2f": DungeonFloor(
                floor_id="mt_moon_b2f",
                name="Mt. Moon B2F — Fossil Chamber",
                description=(
                    "A vast underground chamber. Two scientists argue over fossils embedded in "
                    "the rock — one is from Team Rocket! Clefairy can be seen in the shadows. "
                    "A rocky passage leads east toward Route 4."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="up",
                        label="Ladder to B1F",
                        target_floor="mt_moon_b1f",
                    ),
                    DungeonFloorExit(
                        direction="east",
                        label="Rocky passage to Route 4",
                        target_floor="EXIT",
                        target_location="Route 4",
                    ),
                ],
                wild_pokemon=["ZUBAT", "CLEFAIRY", "GEODUDE"],
                level_range=(10, 14),
                encounter_rate=0.50,
                encounter_weights={"ZUBAT": 45, "CLEFAIRY": 40, "GEODUDE": 15},
                trainer_ids=[],
                item_pickups=["Dome Fossil", "Helix Fossil"],
                item_flag="received_mt_moon_fossil",
                is_checkpoint=False,
                event_hook="mt_moon_fossil_event",
            ),
        },
    ),
    # ══════════════════════════════════════════════════════════════════════
    # ROCK TUNNEL  (2 floors)
    # ══════════════════════════════════════════════════════════════════════
    "rock_tunnel": DungeonDefinition(
        dungeon_id="rock_tunnel",
        name="Rock Tunnel",
        location_name="Rock Tunnel",
        entrance_floor="rock_tunnel_1f",
        escape_to="Lavender Town",
        completion_flag="rock_tunnel_completed",
        floors={
            "rock_tunnel_1f": DungeonFloor(
                floor_id="rock_tunnel_1f",
                name="Rock Tunnel 1F",
                description=(
                    "The entrance plunges you into near-total darkness. "
                    "Without Flash the Zubat swarms are impossible to see coming. "
                    "Hikers with headlamps patrol the upper passages. "
                    "Rough-hewn stairs lead down."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="down",
                        label="Rough stairs to B1F",
                        target_floor="rock_tunnel_b1f",
                    ),
                ],
                wild_pokemon=["ZUBAT", "GEODUDE", "MACHOP"],
                level_range=(15, 21),
                encounter_rate=0.65,
                encounter_weights={"ZUBAT": 45, "GEODUDE": 40, "MACHOP": 15},
                trainer_ids=["hiker_allen", "hiker_jake"],
                is_checkpoint=True,
                event_hook="rock_tunnel_darkness_warning",
            ),
            "rock_tunnel_b1f": DungeonFloor(
                floor_id="rock_tunnel_b1f",
                name="Rock Tunnel B1F",
                description=(
                    "The lower passages are even darker. Gravel crunches underfoot. "
                    "Graveler have made their home in the crevices. "
                    "A faint light glimmers at the southern exit toward Lavender Town."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="up",
                        label="Rough stairs to 1F",
                        target_floor="rock_tunnel_1f",
                    ),
                    DungeonFloorExit(
                        direction="south",
                        label="Exit to Lavender Town",
                        target_floor="EXIT",
                        target_location="Lavender Town",
                    ),
                ],
                wild_pokemon=["ZUBAT", "GEODUDE", "ONIX", "GRAVELER"],
                level_range=(17, 23),
                encounter_rate=0.65,
                encounter_weights={"ZUBAT": 35, "GEODUDE": 35, "ONIX": 20, "GRAVELER": 10},
                trainer_ids=["hiker_diana", "hiker_rugged", "youngster_josh_rt"],
                is_checkpoint=True,
            ),
        },
    ),
    # ══════════════════════════════════════════════════════════════════════
    # VICTORY ROAD  (3 floors)
    # ══════════════════════════════════════════════════════════════════════
    "victory_road": DungeonDefinition(
        dungeon_id="victory_road",
        name="Victory Road",
        location_name="Victory Road",
        entrance_floor="victory_road_1f",
        escape_to="Viridian City",
        completion_flag="victory_road_clear",
        floors={
            "victory_road_1f": DungeonFloor(
                floor_id="victory_road_1f",
                name="Victory Road 1F",
                description=(
                    "A vast stone corridor polished smooth by the footsteps of legendary trainers. "
                    "Boulder puzzles block the way forward. "
                    "Stairs lead up to the second floor."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="up",
                        label="Stone stairs to 2F",
                        target_floor="victory_road_2f",
                    ),
                ],
                wild_pokemon=["MACHOP", "GEODUDE", "ONIX", "MACHOKE"],
                level_range=(42, 46),
                encounter_rate=0.55,
                encounter_weights={"MACHOP": 40, "GEODUDE": 30, "ONIX": 20, "MACHOKE": 10},
                trainer_ids=["cooltrainer_f_naomi"],
                is_checkpoint=True,
                event_hook="victory_road_arrival",
            ),
            "victory_road_2f": DungeonFloor(
                floor_id="victory_road_2f",
                name="Victory Road 2F",
                description=(
                    "The air thins at this altitude. Boulders the size of cars litter the floor. "
                    "A veteran trainer blocks the path, testing only the worthy. "
                    "Stairs lead up and down."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="up",
                        label="Stone stairs to 3F",
                        target_floor="victory_road_3f",
                    ),
                    DungeonFloorExit(
                        direction="down",
                        label="Stone stairs to 1F",
                        target_floor="victory_road_1f",
                    ),
                ],
                wild_pokemon=["MACHOP", "GEODUDE", "ONIX", "MACHOKE", "MAROWAK"],
                level_range=(42, 49),
                encounter_rate=0.55,
                encounter_weights={
                    "MACHOP": 30,
                    "GEODUDE": 30,
                    "ONIX": 20,
                    "MACHOKE": 10,
                    "MAROWAK": 10,
                },
                trainer_ids=["black_belt_hitoshi", "cooltrainer_m_warren"],
                is_checkpoint=True,
            ),
            "victory_road_3f": DungeonFloor(
                floor_id="victory_road_3f",
                name="Victory Road 3F",
                description=(
                    "The final stretch. You can see the lights of the Pokemon League ahead. "
                    "One last group of elite trainers guard the passage. "
                    "A fiery presence emanates from a hidden alcove — Moltres roosts here. "
                    "Beyond them, the Pokemon League waits."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="down",
                        label="Stone stairs to 2F",
                        target_floor="victory_road_2f",
                    ),
                    DungeonFloorExit(
                        direction="north",
                        label="Gate to Pokemon League",
                        target_floor="EXIT",
                        target_location="Pokemon League",
                    ),
                ],
                wild_pokemon=["MACHOP", "GEODUDE", "ONIX", "MACHOKE", "MAROWAK", "MOLTRES"],
                level_range=(44, 50),
                encounter_rate=0.55,
                encounter_weights={
                    "MACHOP": 25,
                    "GEODUDE": 25,
                    "ONIX": 20,
                    "MACHOKE": 18,
                    "MAROWAK": 10,
                    "MOLTRES": 2,
                },
                trainer_ids=["veteran_trainer"],
                is_checkpoint=False,
                event_hook="victory_road_rival",
            ),
        },
    ),
    # ══════════════════════════════════════════════════════════════════════
    # POKEMON MANSION  (3 floors - B1F, 1F, 2F)
    # ══════════════════════════════════════════════════════════════════════
    "pokemon_mansion": DungeonDefinition(
        dungeon_id="pokemon_mansion",
        name="Pokemon Mansion",
        location_name="Pokemon Mansion",
        entrance_floor="mansion_1f",
        escape_to="Cinnabar Island",
        completion_flag="pokemon_mansion_explored",
        floors={
            "mansion_1f": DungeonFloor(
                floor_id="mansion_1f",
                name="Pokemon Mansion 1F",
                description=(
                    "The burnt-out remains of a research facility. Charred furniture and "
                    "scorched lab equipment litter the halls. Grimer ooze from broken pipes. "
                    "Stairs lead down to the basement and up to the second floor."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="down",
                        label="Stairs to B1F",
                        target_floor="mansion_b1f",
                    ),
                    DungeonFloorExit(
                        direction="up",
                        label="Stairs to 2F",
                        target_floor="mansion_2f",
                    ),
                ],
                wild_pokemon=["RATTATA", "RATICATE", "GRIMER", "PONYTA", "KOFFING", "GROWLITHE"],
                level_range=(30, 38),
                encounter_rate=0.60,
                encounter_weights={
                    "RATTATA": 30,
                    "RATICATE": 20,
                    "GRIMER": 20,
                    "PONYTA": 15,
                    "KOFFING": 10,
                    "GROWLITHE": 5,
                },
                trainer_ids=[],
                is_checkpoint=True,
            ),
            "mansion_b1f": DungeonFloor(
                floor_id="mansion_b1f",
                name="Pokemon Mansion B1F",
                description=(
                    "The underground laboratory. Broken cryo-pods line the walls. "
                    "Diary entries on burned scraps of paper hint at twisted genetic experiments. "
                    "Grimer and Muk infest the chemical storage rooms."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="up",
                        label="Stairs to 1F",
                        target_floor="mansion_1f",
                    ),
                ],
                wild_pokemon=["GRIMER", "MUK", "KOFFING", "WEEZING", "MAGMAR"],
                level_range=(32, 42),
                encounter_rate=0.65,
                encounter_weights={
                    "GRIMER": 30,
                    "MUK": 20,
                    "KOFFING": 20,
                    "WEEZING": 15,
                    "MAGMAR": 15,
                },
                trainer_ids=[],
                item_pickups=["Secret Key"],
                item_flag="received_secret_key",
                is_checkpoint=True,
                event_hook="mansion_secret_key",
            ),
            "mansion_2f": DungeonFloor(
                floor_id="mansion_2f",
                name="Pokemon Mansion 2F",
                description=(
                    "The upper floor. Collapsed ceilings expose the night sky. "
                    "Ponyta gallop through the rubble, and Fire Pokemon nest in the rafters. "
                    "You can see the ocean from the broken windows."
                ),
                exits=[
                    DungeonFloorExit(
                        direction="down",
                        label="Stairs to 1F",
                        target_floor="mansion_1f",
                    ),
                ],
                wild_pokemon=["PONYTA", "RAPIDASH", "MAGMAR", "GROWLITHE", "RATICATE"],
                level_range=(34, 40),
                encounter_rate=0.60,
                encounter_weights={
                    "PONYTA": 30,
                    "RAPIDASH": 20,
                    "MAGMAR": 20,
                    "GROWLITHE": 15,
                    "RATICATE": 15,
                },
                trainer_ids=[],
                is_checkpoint=False,
            ),
        },
    ),
}


# ---------------------------------------------------------------------------
# Registry helpers
# ---------------------------------------------------------------------------


def get_dungeon_for_location(location_name: str) -> Optional[DungeonDefinition]:
    """Return the :class:`DungeonDefinition` for *location_name*, or ``None``.

    Args:
        location_name: The ``Location.name`` value to look up.

    Returns:
        Matching ``DungeonDefinition``, or ``None`` if this location has no
        multi-floor dungeon definition.
    """
    for dungeon in DUNGEONS.values():
        if dungeon.location_name == location_name:
            return dungeon
    return None


def get_current_floor(game_state: GameState) -> Optional[DungeonFloor]:
    """Return the player's current :class:`DungeonFloor`, or ``None``.

    Args:
        game_state: Active game state.

    Returns:
        The active ``DungeonFloor``, or ``None`` if the player is not inside
        a tracked dungeon.
    """
    ds = game_state.game_data.get("dungeon_state", {})
    dungeon_id = ds.get("dungeon_id")
    floor_id = ds.get("current_floor")
    if not dungeon_id or not floor_id:
        return None
    dungeon = DUNGEONS.get(dungeon_id)
    if not dungeon:
        return None
    return dungeon.get_floor(floor_id)


# ---------------------------------------------------------------------------
# Entry / exit
# ---------------------------------------------------------------------------


def enter_dungeon(game_state: GameState, dungeon: DungeonDefinition, output: RichLog) -> None:
    """Initialise dungeon state when the player enters *dungeon*.

    Called automatically from ``move_to_location()`` whenever the destination
    has a :class:`DungeonDefinition`.

    Args:
        game_state: Active game state.
        dungeon: The dungeon being entered.
        output: Textual ``RichLog`` widget.
    """
    ds: Dict = game_state.game_data.setdefault("dungeon_state", {})
    ds["dungeon_id"] = dungeon.dungeon_id
    ds["current_floor"] = dungeon.entrance_floor

    # Track explored floors per dungeon
    explored: Dict[str, List[str]] = game_state.game_data.setdefault("dungeon_explored", {})
    floor_list = explored.setdefault(dungeon.dungeon_id, [])
    if dungeon.entrance_floor not in floor_list:
        floor_list.append(dungeon.entrance_floor)

    entrance = dungeon.get_floor(dungeon.entrance_floor)

    # Announce arrival at the entrance
    write_lines_fmt(
        output,
        T.DUNGEON_ENTER_HEADER,
        dungeon_name=dungeon.name,
        floor_name=entrance.name if entrance else dungeon.entrance_floor,
    )

    if entrance:
        write_lines_fmt(output, T.DUNGEON_FLOOR_DESCRIPTION, description=entrance.description)

        # Auto-save checkpoint on entrance (entrance is always a safe restart point)
        if entrance.is_checkpoint:
            _save_checkpoint(game_state, dungeon.dungeon_id, entrance.floor_id)
            write_lines(output, T.DUNGEON_CHECKPOINT_REACHED)

        # Fire arrival event hook
        if entrance.event_hook:
            _fire_event_hook(game_state, dungeon, entrance, output)

    write_lines(output, T.DUNGEON_ENTER_FOOTER)


def exit_dungeon(game_state: GameState) -> None:
    """Clear active dungeon state when the player leaves the dungeon location.

    Args:
        game_state: Active game state.
    """
    ds = game_state.game_data.get("dungeon_state", {})
    ds["dungeon_id"] = None
    ds["current_floor"] = None


# ---------------------------------------------------------------------------
# Navigation
# ---------------------------------------------------------------------------

_DIRECTION_ALIASES: Dict[str, List[str]] = {
    "up": ["up", "ascend", "climb up", "go up", "take stairs up", "take ladder up", "upstairs"],
    "down": [
        "down",
        "descend",
        "climb down",
        "go down",
        "take stairs down",
        "take ladder down",
        "downstairs",
    ],
    "north": ["north", "go north", "head north"],
    "south": ["south", "go south", "head south"],
    "east": ["east", "go east", "head east"],
    "west": ["west", "go west", "head west"],
    "ladder": ["ladder", "take ladder", "use ladder", "climb ladder"],
    "stairs": ["stairs", "take stairs", "use stairs", "climb stairs"],
    "warp": ["warp", "use warp", "step on warp"],
}


def _resolve_direction(raw: str) -> str:
    """Normalise a raw input string to a canonical direction token.

    Args:
        raw: Player's raw input (already stripped/lower-cased).

    Returns:
        A canonical direction string (e.g. ``"up"``, ``"north"``, …), or the
        original *raw* string if no alias matched.
    """
    for canonical, aliases in _DIRECTION_ALIASES.items():
        if raw in aliases:
            return canonical
    return raw


def dungeon_navigate(
    game_state: GameState,
    direction_raw: str,
    output: RichLog,
    trigger_wild_callback,
    trigger_trainer_callback,
) -> bool:
    """Attempt to move in *direction_raw* within the current dungeon.

    If the move succeeds the player is placed on the new floor and a wild or
    trainer encounter may be triggered at the new floor on arrival.

    Args:
        game_state: Active game state.
        direction_raw: Player's raw navigation input (e.g. ``"go down"``).
        output: Textual ``RichLog`` widget.
        trigger_wild_callback: ``callable(output)`` — starts a wild battle.
        trigger_trainer_callback: ``callable(output, trainer)`` — starts a
            trainer battle.

    Returns:
        ``True`` if navigation was handled (even if the exit was blocked),
        ``False`` if no matching exit was found (caller can try other actions).
    """
    ds = game_state.game_data.get("dungeon_state", {})
    dungeon_id = ds.get("dungeon_id")
    current_floor_id = ds.get("current_floor")

    if not dungeon_id or not current_floor_id:
        return False

    dungeon = DUNGEONS.get(dungeon_id)
    if not dungeon:
        return False

    current_floor = dungeon.get_floor(current_floor_id)
    if not current_floor:
        return False

    direction = _resolve_direction(direction_raw.strip().lower())

    # Find the matching exit
    matching_exit: Optional[DungeonFloorExit] = None
    for ex in current_floor.exits:
        if ex.direction == direction or direction in ex.label.lower():
            matching_exit = ex
            break

    # No exit in this direction at all — tell the caller
    if not matching_exit:
        return False

    # ── Gate checks ──────────────────────────────────────────────────────
    story_flags = game_state.game_data.get("story_flags", {})
    badges = game_state.game_data.get("badges", [])
    items = game_state.game_data.get("items", {})

    if matching_exit.requires_flag and not story_flags.get(matching_exit.requires_flag):
        write_lines_fmt(
            output,
            T.DUNGEON_EXIT_GATED_FLAG,
            label=matching_exit.label,
        )
        return True  # handled, but blocked

    if matching_exit.requires_item and not items.get(matching_exit.requires_item, 0):
        write_lines_fmt(
            output,
            T.DUNGEON_EXIT_GATED_ITEM,
            label=matching_exit.label,
            item=matching_exit.requires_item,
        )
        return True

    if matching_exit.requires_badge and matching_exit.requires_badge not in badges:
        write_lines_fmt(
            output,
            T.DUNGEON_EXIT_GATED_BADGE,
            label=matching_exit.label,
            badge=matching_exit.requires_badge.replace("_", " ").title(),
        )
        return True

    # ── Dungeon exit (leaves dungeon entirely) ────────────────────────────
    if matching_exit.target_floor == "EXIT":
        _do_dungeon_exit(game_state, dungeon, matching_exit, output)
        return True

    # ── Move to target floor ──────────────────────────────────────────────
    target_floor = dungeon.get_floor(matching_exit.target_floor)
    if not target_floor:
        write_lines_fmt(output, T.DUNGEON_FLOOR_NOT_FOUND, floor_id=matching_exit.target_floor)
        return True

    ds["current_floor"] = target_floor.floor_id

    # Track explored floors
    explored = game_state.game_data.setdefault("dungeon_explored", {})
    floor_list = explored.setdefault(dungeon.dungeon_id, [])
    first_visit = target_floor.floor_id not in floor_list
    if first_visit:
        floor_list.append(target_floor.floor_id)

    # Announce new floor
    write_lines_fmt(
        output,
        T.DUNGEON_FLOOR_ARRIVED,
        floor_name=target_floor.name,
    )
    write_lines_fmt(output, T.DUNGEON_FLOOR_DESCRIPTION, description=target_floor.description)

    # Checkpoint
    if target_floor.is_checkpoint:
        _save_checkpoint(game_state, dungeon.dungeon_id, target_floor.floor_id)
        write_lines(output, T.DUNGEON_CHECKPOINT_REACHED)

    # Item pickup on first visit
    if first_visit and target_floor.item_pickups and target_floor.item_flag:
        _award_floor_items(game_state, dungeon, target_floor, output)

    # Event hook on first visit
    if first_visit and target_floor.event_hook:
        _fire_event_hook(game_state, dungeon, target_floor, output)

    # Show available exits on the new floor
    _show_floor_exits(target_floor, output)

    return True


def _do_dungeon_exit(
    game_state: GameState,
    dungeon: DungeonDefinition,
    ex: DungeonFloorExit,
    output: RichLog,
) -> None:
    """Handle leaving a dungeon via an EXIT exit."""
    from .locations import get_location

    dest_name = ex.target_location or dungeon.escape_to
    dest = get_location(dest_name)
    if not dest:
        write_lines_fmt(output, T.DUNGEON_EXIT_LOCATION_NOT_FOUND, location=dest_name)
        return

    # Set completion flag
    if dungeon.completion_flag:
        game_state.game_data.setdefault("story_flags", {})[dungeon.completion_flag] = True

    # Move to destination
    game_state.game_data["previous_location"] = game_state.current_location.name
    game_state.current_location = dest
    game_state.game_data["location"] = dest.name
    game_state.game_data.setdefault("route_progress", {})[dest.name] = 0
    exit_dungeon(game_state)

    write_lines_fmt(output, T.DUNGEON_EXITED, dungeon_name=dungeon.name, location=dest.name)


# ---------------------------------------------------------------------------
# Where command
# ---------------------------------------------------------------------------


def dungeon_where(game_state: GameState, output: RichLog) -> bool:
    """Print a status panel for the current dungeon floor.

    Args:
        game_state: Active game state.
        output: Textual ``RichLog`` widget.

    Returns:
        ``True`` if inside a dungeon (panel was printed),
        ``False`` if the player is not currently in a dungeon.
    """
    ds = game_state.game_data.get("dungeon_state", {})
    dungeon_id = ds.get("dungeon_id")
    current_floor_id = ds.get("current_floor")

    if not dungeon_id or not current_floor_id:
        return False

    dungeon = DUNGEONS.get(dungeon_id)
    if not dungeon:
        return False

    current_floor = dungeon.get_floor(current_floor_id)
    if not current_floor:
        return False

    # Header
    write_lines_fmt(
        output,
        T.WHERE_HEADER,
        dungeon_name=dungeon.name,
        floor_name=current_floor.name,
    )

    # Description
    write_lines_fmt(output, T.WHERE_DESCRIPTION, description=current_floor.description)

    # Explored floors
    explored = game_state.game_data.get("dungeon_explored", {}).get(dungeon_id, [])
    total_floors = len(dungeon.floors)
    explored_count = len(explored)
    write_lines_fmt(
        output,
        T.WHERE_EXPLORED,
        explored_count=explored_count,
        total_floors=total_floors,
    )
    for fid in explored:
        fl = dungeon.get_floor(fid)
        fname = fl.name if fl else fid
        marker = "★" if fid == current_floor_id else "✓"
        tag = " [bold cyan](here)[/bold cyan]" if fid == current_floor_id else ""
        write_lines_fmt(output, T.WHERE_FLOOR_ENTRY, marker=marker, floor_name=fname, tag=tag)

    # Active checkpoint
    checkpoints = game_state.game_data.get("dungeon_checkpoints", {})
    cp_floor_id = checkpoints.get(dungeon_id)
    if cp_floor_id:
        cp_floor = dungeon.get_floor(cp_floor_id)
        cp_name = cp_floor.name if cp_floor else cp_floor_id
        write_lines_fmt(output, T.WHERE_CHECKPOINT, floor_name=cp_name)

    # Available exits from current floor
    _show_floor_exits(current_floor, output)

    write_lines(output, T.WHERE_FOOTER)
    return True


# ---------------------------------------------------------------------------
# Dungeon explore (per-floor encounter tables)
# ---------------------------------------------------------------------------


def dungeon_floor_encounter(
    game_state: GameState,
    floor: DungeonFloor,
    output: RichLog,
    trigger_wild_callback,
) -> bool:
    """Roll for a wild encounter using *floor*'s tables.

    Args:
        game_state: Active game state.
        floor: The active dungeon floor.
        output: Textual ``RichLog`` widget.
        trigger_wild_callback: ``callable(output)`` — starts a wild battle.

    Returns:
        ``True`` if a wild encounter was triggered.
    """
    if not floor.wild_pokemon:
        return False

    if random.random() >= floor.encounter_rate:
        return False

    # Repel check
    repel_steps = game_state.game_data.get("repel_steps", 0)
    if repel_steps > 0:
        game_state.game_data["repel_steps"] = repel_steps - 1
        if random.random() < 0.5:
            from .texts.en import exploration as ExT  # noqa: N812
            from .ui.formatters import write_lines, write_lines_fmt

            write_lines(output, ExT.REPEL_SUPPRESSED_ENCOUNTER)
            remaining = repel_steps - 1
            if remaining > 0:
                write_lines_fmt(output, ExT.REPEL_REMAINING, remaining=remaining)
            else:
                write_lines(output, ExT.REPEL_WORE_OFF)
            write_lines(output, ExT.REPEL_FOOTER)
            return False

    trigger_wild_callback(output)
    return True


def pick_floor_species(floor: DungeonFloor) -> str:
    """Pick a random wild species from *floor*'s weighted encounter table.

    Args:
        floor: The dungeon floor to pick from.

    Returns:
        An uppercase species key, or the first species if the floor is empty.
    """
    if not floor.wild_pokemon:
        return "ZUBAT"

    weights = floor.encounter_weights
    if weights:
        species_list = [s for s in floor.wild_pokemon if s in weights]
        weight_values = [weights[s] for s in species_list]
        if species_list:
            return random.choices(species_list, weights=weight_values, k=1)[0]

    return random.choice(floor.wild_pokemon)


def pick_floor_level(floor: DungeonFloor) -> int:
    """Pick a random wild level from *floor*'s ``level_range``.

    Args:
        floor: The dungeon floor to pick a level from.

    Returns:
        An integer level within ``floor.level_range``.
    """
    lo, hi = floor.level_range
    return random.randint(lo, hi)


# ---------------------------------------------------------------------------
# Blackout handling
# ---------------------------------------------------------------------------


def handle_dungeon_blackout(game_state: GameState, output: RichLog) -> None:
    """Handle a full party blackout while inside a dungeon.

    The player is moved to the last checkpoint (or dungeon entrance) and loses
    half their money.

    Args:
        game_state: Active game state.
        output: Textual ``RichLog`` widget.
    """
    ds = game_state.game_data.get("dungeon_state", {})
    dungeon_id = ds.get("dungeon_id")
    if not dungeon_id:
        return

    dungeon = DUNGEONS.get(dungeon_id)
    if not dungeon:
        return

    # Find respawn floor
    checkpoints = game_state.game_data.get("dungeon_checkpoints", {})
    respawn_floor_id = checkpoints.get(dungeon_id) or dungeon.respawn_floor()

    respawn_floor = dungeon.get_floor(respawn_floor_id)
    floor_name = respawn_floor.name if respawn_floor else respawn_floor_id

    # Half money penalty
    money = game_state.game_data.get("money", 0)
    penalty = money // 2
    game_state.game_data["money"] = money - penalty

    # Move to respawn floor
    ds["current_floor"] = respawn_floor_id
    explored = game_state.game_data.setdefault("dungeon_explored", {})
    floor_list = explored.setdefault(dungeon_id, [])
    if respawn_floor_id not in floor_list:
        floor_list.append(respawn_floor_id)

    write_lines_fmt(
        output,
        T.DUNGEON_BLACKOUT,
        dungeon_name=dungeon.name,
        floor_name=floor_name,
        penalty=penalty,
    )


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _save_checkpoint(game_state: GameState, dungeon_id: str, floor_id: str) -> None:
    """Persist *floor_id* as the active checkpoint for *dungeon_id*."""
    checkpoints = game_state.game_data.setdefault("dungeon_checkpoints", {})
    checkpoints[dungeon_id] = floor_id


def _award_floor_items(
    game_state: GameState,
    dungeon: DungeonDefinition,
    floor: DungeonFloor,
    output: RichLog,
) -> None:
    """Award one-time item pickups for a floor and set its item_flag.

    For the Mt. Moon B2F fossil floor, only one fossil (chosen randomly) is
    awarded rather than both.

    Args:
        game_state: Active game state.
        dungeon: Containing dungeon definition.
        floor: The floor whose items should be awarded.
        output: Textual ``RichLog`` widget.
    """
    if not floor.item_flag:
        return

    story_flags = game_state.game_data.setdefault("story_flags", {})
    if story_flags.get(floor.item_flag):
        return  # already awarded

    story_flags[floor.item_flag] = True
    items_bag = game_state.game_data.setdefault("items", {})

    # Special case: Mt. Moon B2F awards only ONE fossil at random
    if floor.floor_id == "mt_moon_b2f" and len(floor.item_pickups) == 2:
        chosen = random.choice(floor.item_pickups)
        items_bag[chosen] = items_bag.get(chosen, 0) + 1
        write_lines_fmt(output, T.DUNGEON_ITEM_PICKUP_FOSSIL, fossil=chosen)
        return

    for item in floor.item_pickups:
        items_bag[item] = items_bag.get(item, 0) + 1
        write_lines_fmt(output, T.DUNGEON_ITEM_PICKUP, item=item)


def _show_floor_exits(floor: DungeonFloor, output: RichLog) -> None:
    """Print the available exits from *floor*."""
    if not floor.exits:
        return
    write_lines(output, T.DUNGEON_EXITS_HEADER)
    for ex in floor.exits:
        if ex.target_floor == "EXIT":
            write_lines_fmt(
                output,
                T.DUNGEON_EXIT_ENTRY_LEAVE,
                direction=ex.direction,
                label=ex.label,
                location=ex.target_location,
            )
        else:
            write_lines_fmt(
                output,
                T.DUNGEON_EXIT_ENTRY,
                direction=ex.direction,
                label=ex.label,
            )
    write_lines(output, T.DUNGEON_EXITS_FOOTER)


def _fire_event_hook(
    game_state: GameState,
    dungeon: DungeonDefinition,
    floor: DungeonFloor,
    output: RichLog,
) -> None:
    """Fire a named event for first-arrival at *floor*.

    Events are only fired once per save (guarded by story flags).

    Args:
        game_state: Active game state.
        dungeon: Containing dungeon definition.
        floor: Floor whose ``event_hook`` should fire.
        output: Textual ``RichLog`` widget.
    """
    hook = floor.event_hook
    if not hook:
        return

    flags = game_state.game_data.setdefault("story_flags", {})
    fired_key = f"event_fired_{hook}"
    if flags.get(fired_key):
        return
    flags[fired_key] = True

    if hook == "mt_moon_b1f_arrival":
        write_lines(output, T.EVENT_MT_MOON_B1F)
    elif hook == "mt_moon_fossil_event":
        write_lines(output, T.EVENT_MT_MOON_FOSSIL)
    elif hook == "rock_tunnel_darkness_warning":
        write_lines(output, T.EVENT_ROCK_TUNNEL_DARK)
    elif hook == "victory_road_arrival":
        write_lines(output, T.EVENT_VICTORY_ROAD_ARRIVAL)
    elif hook == "victory_road_rival":
        write_lines(output, T.EVENT_VICTORY_ROAD_RIVAL)
