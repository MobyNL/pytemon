"""
Battle UI display functions for Pokemon Terminal.

This module handles all battle-related display logic including battle start screens,
move selection menus, battle options, and victory/defeat messages.
"""

from typing import TYPE_CHECKING, List

from textual.widgets import RichLog

from ..data import get_move
from ..ui.formatters import format_hp_bar

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
    return [
        "",
        "[bold red]═══════════════════════════════════════════[/bold red]",
        f"[bold red]⚔️  A wild {wild['name']} appeared! (Lv. {wild['level']})  ⚔️[/bold red]",
        "[bold red]═══════════════════════════════════════════[/bold red]",
        "",
        f"[bold]Go! {player['name']}![/bold]",
        "",
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

    lines = [
        "",
        "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
        "[bold yellow]⚔️  TRAINER BATTLE!  ⚔️[/bold yellow]",
        "[bold yellow]═══════════════════════════════════════════[/bold yellow]",
        "",
    ]

    for intro_line in trainer.get("intro_text", []):
        lines.append(f"[yellow]{intro_line.replace('{player_name}', player_name)}[/yellow]")

    lines.append("")
    lines.append(f"[bold]{trainer['trainer_class']} {trainer['name']} wants to battle![/bold]")
    lines.append("")

    num_pokemon = len(battle.trainer_pokemon_team)
    if num_pokemon > 1:
        lines.append(f"[dim]{trainer['name']} sent out {trainer_pokemon['name']}![/dim]")
        lines.append(f"[dim]They have {num_pokemon} Pokemon total[/dim]")
    else:
        lines.append(f"[dim]{trainer['name']} sent out {trainer_pokemon['name']}![/dim]")

    lines.extend(["", f"[bold]Go! {player['name']}![/bold]", ""])
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
    STATUS_ICONS = {
        "BURN": "[bold red] 🔥BRN[/bold red]",
        "POISON": "[bold magenta] ☠PSN[/bold magenta]",
        "BAD_POISON": "[bold magenta] ☠☠TOX[/bold magenta]",
        "PARALYSIS": "[bold yellow] ⚡PAR[/bold yellow]",
        "SLEEP": "[dim] 💤SLP[/dim]",
        "FREEZE": "[bold cyan] ❄FRZ[/bold cyan]",
    }

    wild_status = STATUS_ICONS.get(wild.get("status", "") or "", "")
    player_status = STATUS_ICONS.get(player.get("status", "") or "", "")

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
    output.write("[bold yellow]What will you do?[/bold yellow]")
    items = game_state.game_data.get("items", {})
    pokeballs = items.get("Pokeball", 0)

    # Show different options for trainer battles
    if battle.is_trainer_battle:
        output.write("  [cyan]Fight[/cyan]  |  [cyan]Switch[/cyan]  |  [cyan]Item[/cyan]")
        output.write("[dim]  (Can't flee or catch in trainer battles)[/dim]")
    else:
        output.write("  [cyan]Fight[/cyan]  |  [cyan]Switch[/cyan]  |  [cyan]Item[/cyan]")
        if pokeballs > 0:
            output.write(
                f"  [green]Catch[/green] ({pokeballs} Pokeballs)  |  [yellow]Flee[/yellow]"
            )
        else:
            output.write("  [dim]Catch (No Pokeballs)[/dim]  |  [yellow]Flee[/yellow]")
    output.write("")


def show_move_selection(game_state: "GameState", output: RichLog) -> None:
    """Display the move selection menu."""
    battle = game_state.battle_state
    if not battle:
        return

    player = battle.player_pokemon

    output.write("")
    output.write("[bold yellow]Select a move:[/bold yellow]")
    output.write("")

    MOVE_TYPE_COLORS = {
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

    for i, move in enumerate(player["moves"], 1):
        move_data = get_move(move["name"])
        is_disabled = battle.player_disabled_move == move["name"]
        if move_data:
            move_type = move_data.get("type", "Normal")
            color = MOVE_TYPE_COLORS.get(move_type, "white")
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

    output.write("")
    output.write("[dim]Type the move name or 'Back' to go back[/dim]")
    output.write("")


def show_pokemon_switch_menu(game_state: "GameState", output: RichLog) -> None:
    """Display the Pokemon switch menu."""
    battle = game_state.battle_state
    active = battle.player_pokemon
    pokemon_list = game_state.game_data.get("pokemon", [])

    output.write("")
    output.write("[bold cyan]Choose a Pokemon to switch in:[/bold cyan]")
    output.write("")

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

    output.write("")
    output.write("[yellow]Type the number or name of the Pokemon, or 'Back':[/yellow]")
    output.write("")


def show_battle_help(output: RichLog) -> None:
    """Display battle help information."""
    output.write("")
    output.write("[bold cyan]⚔️  BATTLE HELP ⚔️[/bold cyan]")
    output.write("")
    output.write("[bold yellow]Commands:[/bold yellow]")
    output.write("  [cyan]Fight[/cyan]   - Choose a move to attack")
    output.write("  [cyan]Switch[/cyan]  - Switch to another Pokemon")
    output.write("  [cyan]Item[/cyan]    - Use an item (Potion, Pokeball, etc.)")
    output.write("  [cyan]Catch[/cyan]   - Try to catch the wild Pokemon (needs Pokeball)")
    output.write("  [cyan]Flee[/cyan]    - Try to escape from battle")
    output.write("")
    output.write("[bold yellow]Items you can use in battle:[/bold yellow]")
    output.write("  [green]Potion[/green]        - Restores 20 HP")
    output.write("  [green]Super Potion[/green]  - Restores 50 HP")
    output.write("  [green]Antidote[/green]      - Cures poison")
    output.write("  [green]Paralyze Heal[/green] - Cures paralysis")
    output.write("  [green]Awakening[/green]     - Wakes sleeping Pokemon")
    output.write("")
    output.write("[dim]Trainer battles: Can't catch or flee[/dim]")
    output.write("")


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

    output.write("")
    output.write("[bold cyan]🎒 Battle Bag[/bold cyan]")

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
        output.write("  [dim]Your bag has no usable items![/dim]")
        output.write("")
        output.write("[dim]Buy items at the Pokemart. Type 'fight' or 'run'[/dim]")
    else:
        output.write("")
        output.write("[dim]Or type 'fight'/'run' to cancel[/dim]")
    output.write("")
