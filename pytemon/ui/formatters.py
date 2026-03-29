"""
UI formatting utilities for Pokemon Terminal.

This module provides helper functions for formatting HP bars, experience bars,
and other UI elements, plus write_lines helpers for text-constant blocks.
"""

from typing import Any, List

from textual.widgets import RichLog

from ..locations import Location


def write_lines(output: RichLog, lines: list[str]) -> None:
    """Write a list of pre-formatted Rich-markup lines to a RichLog.

    Use with text constants from ``pytemon.texts.en.*``:

        from ..texts.en import menus as T
        write_lines(output, T.MAIN_MENU)
    """
    for line in lines:
        output.write(line)


def write_lines_fmt(output: RichLog, lines: list[str], **kwargs: Any) -> None:
    """Write lines to a RichLog, substituting ``{placeholder}`` values.

    Any line containing ``{`` is formatted with *kwargs* using
    ``str.format_map``; lines without placeholders are written as-is.

    Example::

        write_lines_fmt(output, T.WARP_SUCCESS, location="Cerulean City")
    """
    for line in lines:
        output.write(line.format_map(kwargs) if "{" in line else line)


def format_hp_bar(current: int, max_hp: int, width: int = 18) -> str:
    """
    Format an HP bar as a Rich-markup string.

    Args:
        current: Current HP
        max_hp: Maximum HP
        width: Width of the bar in characters

    Returns:
        str: Rich markup HP bar
    """
    if max_hp <= 0:
        return "░" * width
    ratio = max(0.0, current / max_hp)
    filled = int(width * ratio)
    empty = width - filled
    color = "green" if ratio > 0.5 else ("yellow" if ratio > 0.25 else "red")
    return f"[{color}]{'█' * filled}[/{color}]{'░' * empty}"


def format_experience_text(exp: int, next_level_exp: int) -> str:
    """
    Format experience text for display.

    Args:
        exp: Current experience points
        next_level_exp: Experience needed for next level

    Returns:
        str: Formatted experience text
    """
    if next_level_exp > 0:
        return f"Exp: {exp}/{next_level_exp} to next level"
    else:
        return f"Exp: {exp}"


def format_experience_bar(
    exp: int, next_level_exp: int, level: int, width: int = 20
) -> tuple[str, str]:
    """
    Format experience progress bar with text.

    Args:
        exp: Current experience points
        next_level_exp: Experience needed for next level
        level: Current level
        width: Width of the bar in characters

    Returns:
        tuple: (bar_string, text_string)
    """
    if next_level_exp > 0:
        exp_progress = int((exp / next_level_exp) * width)
        exp_bar = "█" * exp_progress + "░" * (width - exp_progress)
        exp_text = f"{exp} / {next_level_exp} Exp to Level {level + 1}"
    else:
        exp_bar = "█" * width
        exp_text = f"{exp} Exp (Max Level)"
    return exp_bar, exp_text


def format_list(items: List[str], article: str = "") -> str:
    """
    Format a list of items into a natural language string.

    Args:
        items: List of items to format
        article: Article to use before each item (e.g., "the")

    Returns:
        Formatted string
    """
    if not items:
        return ""

    if article:
        items = [f"{article} {item}" for item in items]

    if len(items) == 1:
        return items[0]
    elif len(items) == 2:
        return f"{items[0]} and {items[1]}"
    else:
        return ", ".join(items[:-1]) + f", and {items[-1]}"


def get_travel_description(exit_name: str, dest_location: Location) -> str:
    """
    Get a descriptive text for traveling to a destination.

    Args:
        exit_name: Name of the exit
        dest_location: Destination location object

    Returns:
        Description string
    """
    # Special descriptions for known routes
    descriptions = {
        "Pallet Town": "Back to your hometown",
        "Route 1": "A simple route with wild Pokemon",
        "Viridian City": "A city with a Pokemon Center and Pokemart",
        "Route 22": "A side path towards the Pokemon League",
        "Route 2": "Towards Pewter City through Viridian Forest",
        "Viridian Forest": "A dense forest full of Bug Pokemon",
        "Pewter City": "Home of Brock, the first Gym Leader",
    }

    return descriptions.get(exit_name, dest_location.description)
