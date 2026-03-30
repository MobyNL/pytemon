"""
Battle UI display functions for Pokemon Terminal.

This module handles all battle-related display logic including battle start screens,
move selection menus, battle options, and victory/defeat messages.
"""

from typing import TYPE_CHECKING, List

from textual.widgets import RichLog

from ..data import get_move
from ..texts.en import battle_ui as T  # noqa: N812
from ..ui.formatters import format_hp_bar, write_lines, write_lines_fmt

if TYPE_CHECKING:
    from ..game_state import GameState


def get_battle_start_lines(game_state: "GameState") -> List[str]:
    """
    Return the wild Pokemon encounter introduction as a list of text lines.

    Args:
        game_state: The game state (must have an active ``battle_state``; behaviour
            is undefined if ``battle_state`` is ``None``).

    Returns:
        List of Rich-markup strings representing the battle intro.
    """
    battle = game_state.battle_state
    wild = battle.wild_pokemon
    player = battle.player_pokemon

    if battle.is_safari:
        return [
            line.format(
                wild_name=wild["name"], wild_level=wild["level"], player_name=player["name"]
            )
            for line in T.SAFARI_BATTLE_START
        ]

    return [
        line.format(wild_name=wild["name"], wild_level=wild["level"], player_name=player["name"])
        for line in T.WILD_BATTLE_START
    ]


def show_battle_start(game_state: "GameState", output: RichLog) -> None:
    """Display the wild Pokemon encounter introduction."""
    for line in get_battle_start_lines(game_state):
        output.write(line)


def get_trainer_battle_start_lines(game_state: "GameState") -> List[str]:
    """
    Return the trainer battle introduction as a list of text lines.

    Args:
        game_state: The game state (must have an active ``battle_state``; behaviour
            is undefined if ``battle_state`` is ``None``).

    Returns:
        List of Rich-markup strings representing the trainer battle intro.
    """
    battle = game_state.battle_state
    trainer = battle.trainer_data
    trainer_pokemon = battle.wild_pokemon
    player = battle.player_pokemon
    player_name = game_state.game_data.get("player_name", "Trainer")

    lines = list(T.TRAINER_BATTLE_HEADER)

    for intro_line in trainer.get("intro_text", []):
        lines.append(f"[yellow]{intro_line.replace('{player_name}', player_name)}[/yellow]")

    lines.append("")
    lines.append(f"[bold]{trainer['trainer_class']} {trainer['name']} wants to battle![/bold]")
    lines.append("")

    num_pokemon = len(battle.trainer_pokemon_team)
    if num_pokemon > 1:
        lines.extend(
            [
                line.format(trainer_name=trainer["name"], pokemon_name=trainer_pokemon["name"])
                for line in T.TRAINER_BATTLE_SENT_OUT
            ]
        )
        lines.extend([line.format(num_pokemon=num_pokemon) for line in T.TRAINER_BATTLE_TEAM_SIZE])
    else:
        lines.extend(
            [
                line.format(trainer_name=trainer["name"], pokemon_name=trainer_pokemon["name"])
                for line in T.TRAINER_BATTLE_SENT_OUT
            ]
        )

    lines.extend([line.format(player_name=player["name"]) for line in T.TRAINER_BATTLE_GO])
    return lines


def show_trainer_battle_start(game_state: "GameState", output: RichLog) -> None:
    """Display the trainer battle introduction."""
    for line in get_trainer_battle_start_lines(game_state):
        output.write(line)


def show_battle_options(game_state: "GameState", output: RichLog) -> None:
    """Display the main battle menu with HP bars."""
    battle = game_state.battle_state
    if not battle:
        return

    wild = battle.wild_pokemon
    player = battle.player_pokemon

    wild_bar = format_hp_bar(wild["hp"], wild["max_hp"])
    player_bar = format_hp_bar(player["hp"], player["max_hp"])

    # Status condition icons (shown prominently in the HUD)
    status_icons = {
        "BURN": "[bold red] 🔥BRN[/bold red]",
        "POISON": "[bold magenta] ☠PSN[/bold magenta]",
        "BAD_POISON": "[bold magenta] ☠☠TOX[/bold magenta]",
        "PARALYSIS": "[bold yellow] ⚡PAR[/bold yellow]",
        "SLEEP": "[dim] 💤SLP[/dim]",
        "FREEZE": "[bold cyan] ❄FRZ[/bold cyan]",
    }

    wild_status = status_icons.get(wild.get("status", "") or "", "")
    player_status = status_icons.get(player.get("status", "") or "", "")

    # Show opponent label differently for trainers
    if battle.is_trainer_battle:
        trainer = battle.trainer_data
        output.write(
            f"  [bold red]{trainer['name']}'s {wild['name']}[/bold red]"
            f" [dim]Lv.{wild['level']}[/dim]{wild_status}"
        )
    else:
        output.write(
            f"  [bold red]{wild['name']}[/bold red] [dim]Lv.{wild['level']}[/dim]{wild_status}"
        )

    output.write(f"  HP {wild_bar} {wild['hp']}/{wild['max_hp']}")
    output.write("")
    output.write(
        f"  [bold cyan]{player['name']}[/bold cyan] [dim]Lv.{player['level']}[/dim]{player_status}"
    )
    output.write(f"  HP {player_bar} {player['hp']}/{player['max_hp']}")
    output.write("")
    write_lines(output, T.BATTLE_WHAT_TO_DO)
    items = game_state.game_data.get("items", {})

    # Safari Zone: show Bait/Rock/Safari Ball/Run instead of normal options
    if battle.is_safari:
        safari_balls = items.get("Safari Ball", 0)
        status_parts = []
        if battle.safari_bait_turns > 0:
            status_parts.append(f"[green]🥩 Bait ({battle.safari_bait_turns}t)[/green]")
        if battle.safari_rock_turns > 0:
            status_parts.append(f"[red]🪨 Rock ({battle.safari_rock_turns}t)[/red]")
        if status_parts:
            write_lines_fmt(output, T.SAFARI_STATUS_LINE, status_text="  |  ".join(status_parts))
        if safari_balls > 0:
            write_lines_fmt(output, T.SAFARI_OPTIONS_WITH_BALLS, safari_balls=safari_balls)
        else:
            write_lines(output, T.SAFARI_OPTIONS_NO_BALLS)
    # Show different options for trainer battles
    elif battle.is_trainer_battle:
        write_lines(output, T.BATTLE_OPTIONS_CORE)
        write_lines(output, T.BATTLE_OPTIONS_TRAINER_HINT)
    else:
        pokeballs = items.get("Pokeball", 0)
        write_lines(output, T.BATTLE_OPTIONS_CORE)
        if pokeballs > 0:
            write_lines_fmt(output, T.BATTLE_OPTIONS_CATCH_AVAILABLE, pokeballs=pokeballs)
        else:
            write_lines(output, T.BATTLE_OPTIONS_CATCH_NONE)
    write_lines(output, T.MENU_TRAILING_BLANK)


def show_move_selection(game_state: "GameState", output: RichLog) -> None:
    """Display the move selection menu."""
    battle = game_state.battle_state
    if not battle:
        return

    player = battle.player_pokemon

    write_lines(output, T.MOVE_SELECTION_HEADER)

    move_type_colors = {
        "Normal": "white",
        "Fire": "red",
        "Water": "blue",
        "Grass": "green",
        "Electric": "yellow",
        "Ice": "cyan",
        "Fighting": "orange1",
        "Poison": "magenta",
        "Ground": "yellow3",
        "Flying": "sky_blue1",
        "Psychic": "pink1",
        "Bug": "green_yellow",
        "Rock": "tan",
        "Ghost": "purple",
        "Dragon": "blue_violet",
    }

    for move in player["moves"]:
        move_data = get_move(move["name"])
        is_disabled = battle.player_disabled_move == move["name"]
        if move_data:
            move_type = move_data.get("type", "Normal")
            color = move_type_colors.get(move_type, "white")
            pp_text = f"PP: {move['pp']}/{move.get('max_pp', move['pp'])}"
            if is_disabled:
                output.write(
                    f"  • [dim strike]{move['name']}[/dim strike]"
                    f"  {pp_text}  [yellow](DISABLED)[/yellow]"
                )
            else:
                output.write(f"  • [{color}]{move['name']}[/{color}]  {pp_text}")
        else:
            if is_disabled:
                output.write(
                    f"  • [dim strike]{move['name']}[/dim strike]  [yellow](DISABLED)[/yellow]"
                )
            else:
                output.write(f"  • {move['name']}")

    write_lines(output, T.MOVE_SELECTION_PROMPT)


def show_pokemon_switch_menu(game_state: "GameState", output: RichLog) -> None:
    """Display the Pokemon switch menu."""
    battle = game_state.battle_state
    active = battle.player_pokemon
    pokemon_list = game_state.game_data.get("pokemon", [])

    write_lines(output, T.SWITCH_MENU_HEADER)

    for i, p in enumerate(pokemon_list, 1):
        if isinstance(p, str):
            continue
        # Ensure pokemon has battle stats
        from . import battle_actions

        battle_actions.ensure_battle_ready(p)
        is_active = p is active
        hp_bar = format_hp_bar(p["hp"], p["max_hp"], width=10)
        status = p.get("status") or ""
        status_str = f" [yellow][{status}][/yellow]" if status else ""
        active_str = " [bold yellow]← Active[/bold yellow]" if is_active else ""
        fainted_str = " [dim](Fainted)[/dim]" if p["hp"] <= 0 else ""
        output.write(
            f"  {i}. [bold]{p['name']}[/bold] Lv.{p['level']}{status_str}{active_str}{fainted_str}"
        )
        output.write(f"     {hp_bar} {p['hp']}/{p['max_hp']} HP")

    write_lines(output, T.SWITCH_MENU_PROMPT)


def show_battle_help(output: RichLog) -> None:
    """Display battle help information."""
    write_lines(output, T.BATTLE_HELP_BLOCK)


def show_bag_menu(game_state: "GameState", output: RichLog) -> None:
    """
    Display the battle bag menu with available items.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    items = game_state.game_data.get("items", {})
    potions = items.get("Potion", 0)
    super_potions = items.get("Super Potion", 0)
    pokeballs = items.get("Pokeball", 0)
    antidotes = items.get("Antidote", 0)
    par_heals = items.get("Paralyze Heal", 0)
    awakenings = items.get("Awakening", 0)

    player_status = (
        game_state.battle_state.player_pokemon.get("status") if game_state.battle_state else None
    )

    write_lines(output, T.BATTLE_BAG_HEADER)

    has_items = False
    if pokeballs > 0:
        output.write(
            f"  • [red]Pokeball[/red] x{pokeballs} - Catch wild Pokemon  [dim](type 'throw pokeball')[/dim]"
        )
        has_items = True
    if potions > 0:
        output.write(
            f"  • [green]Potion[/green] x{potions} - Restores 20 HP  [dim](type 'use potion')[/dim]"
        )
        has_items = True
    if super_potions > 0:
        output.write(
            f"  • [green]Super Potion[/green] x{super_potions} - Restores 50 HP  [dim](type 'use super potion')[/dim]"
        )
        has_items = True
    if antidotes > 0 and player_status == "POISON":
        output.write(
            f"  • [magenta]Antidote[/magenta] x{antidotes} - Cures poison  [dim](type 'use antidote')[/dim]"
        )
        has_items = True
    if par_heals > 0 and player_status == "PARALYSIS":
        output.write(
            f"  • [yellow]Paralyze Heal[/yellow] x{par_heals} - Cures paralysis  [dim](type 'use paralyze heal')[/dim]"
        )
        has_items = True
    if awakenings > 0 and player_status == "SLEEP":
        output.write(
            f"  • [cyan]Awakening[/cyan] x{awakenings} - Wakes your Pokemon  [dim](type 'use awakening')[/dim]"
        )
        has_items = True

    if not has_items:
        write_lines(output, T.BATTLE_BAG_NO_ITEMS)
    else:
        write_lines(output, T.BATTLE_BAG_CANCEL_HINT)
    write_lines(output, T.BATTLE_BAG_FOOTER)
