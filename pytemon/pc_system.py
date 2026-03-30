"""
PC Storage System for Pokemon Terminal.

Manages Bill's PC box system — storing, retrieving, and managing
Pokemon that aren't in the player's active party.
"""

from typing import TYPE_CHECKING, Dict, List, Optional

from textual.widgets import RichLog

if TYPE_CHECKING:
    from .game_state import GameState

from .texts.en import pc_system as T
from .ui.formatters import write_lines

# ── Constants ───────────────────────────────────────────────────────
BOXES_COUNT = 3
BOX_CAPACITY = 20


# ── Internal helpers ─────────────────────────────────────────────────


def get_pc_storage(game_state: "GameState") -> Dict[str, List]:
    """
    Get (or lazily create) the PC storage dict.

    The storage structure is:
        {
            "Box 1": [pokemon_or_None, ... (20 slots)],
            "Box 2": [...],
            "Box 3": [...],
        }

    Returns:
        The pc_storage dict from game_data (mutates in-place to create).
    """
    if "pc_storage" not in game_state.game_data:
        game_state.game_data["pc_storage"] = {}

    storage = game_state.game_data["pc_storage"]

    for i in range(1, BOXES_COUNT + 1):
        box_key = f"Box {i}"
        if box_key not in storage:
            storage[box_key] = [None] * BOX_CAPACITY
        elif len(storage[box_key]) < BOX_CAPACITY:
            # Pad shorter lists (backwards-compat)
            storage[box_key] += [None] * (BOX_CAPACITY - len(storage[box_key]))

    return storage


def get_total_in_pc(game_state: "GameState") -> int:
    """Return the total number of Pokemon stored across all PC boxes."""
    storage = get_pc_storage(game_state)
    return sum(1 for box in storage.values() for slot in box if slot is not None)


# ── Core operations ──────────────────────────────────────────────────


def send_to_pc(game_state: "GameState", pokemon: dict) -> Optional[str]:
    """
    Send a Pokemon to the first available PC slot.

    Args:
        game_state: The game state.
        pokemon: Pokemon dict to store.

    Returns:
        The box name on success ("Box 1" etc.), or None if the PC is full.
    """
    storage = get_pc_storage(game_state)

    for i in range(1, BOXES_COUNT + 1):
        box_key = f"Box {i}"
        box = storage[box_key]
        for j in range(BOX_CAPACITY):
            if box[j] is None:
                box[j] = pokemon
                return box_key

    return None  # PC is full


def withdraw_from_pc(game_state: "GameState", box_num: int, slot_num: int) -> Optional[dict]:
    """
    Withdraw a Pokemon from the PC and return it (slot removed from box).

    Args:
        box_num: 1-indexed box number.
        slot_num: 1-indexed slot number within the box.

    Returns:
        The Pokemon dict, or None if the slot was empty / out of range.
    """
    storage = get_pc_storage(game_state)
    box_key = f"Box {box_num}"

    if box_key not in storage:
        return None

    box = storage[box_key]
    if slot_num < 1 or slot_num > len(box):
        return None

    pokemon = box[slot_num - 1]
    if pokemon is None:
        return None

    box[slot_num - 1] = None
    return pokemon


# ── Display helpers ──────────────────────────────────────────────────


def _hp_color(hp: int, max_hp: int) -> str:
    pct = hp / max_hp if max_hp > 0 else 0
    if pct > 0.5:
        return "green"
    elif pct > 0.25:
        return "yellow"
    return "red"


def show_pc_menu(game_state: "GameState", output: RichLog) -> None:
    """Display the PC main menu with per-box summaries."""
    storage = get_pc_storage(game_state)
    total = get_total_in_pc(game_state)
    party_count = len(game_state.game_data.get("pokemon", []))

    write_lines(output, T.PC_MENU_HEADER)
    output.write(f"  [cyan]Party:[/cyan]   {party_count}/6 Pokemon")
    output.write(f"  [cyan]Stored:[/cyan]  {total} Pokemon in PC")
    write_lines(output, T.PC_BOX_OVERVIEW_HEADER)

    for i in range(1, BOXES_COUNT + 1):
        box_key = f"Box {i}"
        box = storage[box_key]
        count = sum(1 for slot in box if slot is not None)

        if count == 0:
            output.write(f"  {i}. [cyan]{box_key}[/cyan]  [dim]Empty[/dim]")
        else:
            names = [slot["name"] for slot in box if slot is not None]
            preview = ", ".join(names[:4])
            if count > 4:
                preview += f" +{count - 4} more"
            output.write(f"  {i}. [cyan]{box_key}[/cyan]  [{count}/{BOX_CAPACITY}]  {preview}")

    write_lines(output, T.PC_COMMANDS_BLOCK)


def show_pc_box(game_state: "GameState", box_num: int, output: RichLog) -> None:
    """Display the contents of a single PC box."""
    storage = get_pc_storage(game_state)
    box_key = f"Box {box_num}"

    if box_key not in storage:
        output.write(f"[red]❌ Box {box_num} doesn't exist. Available boxes: 1–{BOXES_COUNT}[/red]")
        output.write("")
        return

    box = storage[box_key]
    party_count = len(game_state.game_data.get("pokemon", []))

    output.write("")
    output.write(f"[bold cyan]─── 📦 {box_key} ───────────────────────────[/bold cyan]")
    output.write("")

    has_pokemon = False
    for i, pokemon in enumerate(box):
        slot_num = i + 1
        if pokemon is not None:
            has_pokemon = True
            types_str = "/".join(pokemon.get("types", ["???"]))
            hp = pokemon.get("hp", 0)
            max_hp = pokemon.get("max_hp", 1)
            color = _hp_color(hp, max_hp)
            status = pokemon.get("status")
            status_tag = f" [red]({status})[/red]" if status else ""
            output.write(
                f"  [bold]{slot_num:>2}.[/bold] [bold]{pokemon['name']}[/bold]"
                f"  Lv.[cyan]{pokemon['level']}[/cyan]"
                f"  [dim]{types_str}[/dim]"
                f"  HP:[{color}]{hp}/{max_hp}[/{color}]{status_tag}"
            )

    if not has_pokemon:
        output.write("  [dim](This box is empty)[/dim]")

    output.write("")
    output.write(f"  [dim]Party: {party_count}/6[/dim]")
    output.write(
        f"  [dim]'withdraw {box_num} <slot>'  'deposit <party slot>'  'box <n>'  'leave'[/dim]"
    )
    output.write("")


# ── Command processor ────────────────────────────────────────────────


def process_pc_command(
    game_state: "GameState",
    command: str,
    output: RichLog,
    set_pending_callback,
) -> None:
    """
    Process a command while the player is at the PC (pending_command == "pc").

    Sub-commands: box <n> | deposit <n> | withdraw <box> <slot> | leave
    """
    cmd = command.lower().strip()

    # ── Leave PC ────────────────────────────────────────────────────
    if cmd in ("leave", "exit", "done", "back", "bye", "close", "log out"):
        output.write("")
        output.write("[dim]You log out of the PC.[/dim]")
        output.write("")
        # Don't call set_pending — exits the PC mode
        return

    # ── View box ────────────────────────────────────────────────────
    if cmd.startswith("box ") or cmd.startswith("box"):
        parts = cmd.split()
        if len(parts) >= 2 and parts[1].isdigit():
            box_num = int(parts[1])
            if 1 <= box_num <= BOXES_COUNT:
                show_pc_box(game_state, box_num, output)
            else:
                output.write(f"[red]❌ Box must be between 1 and {BOXES_COUNT}[/red]")
                output.write("")
        else:
            output.write("[red]❌ Usage: box <number>  (e.g. 'box 1')[/red]")
            output.write("")
        set_pending_callback("pc")
        return

    # ── Deposit from party ──────────────────────────────────────────
    if cmd.startswith("deposit ") or cmd == "deposit":
        parts = cmd.split()
        if len(parts) >= 2 and parts[1].isdigit():
            slot = int(parts[1])
            party = game_state.game_data.get("pokemon", [])

            if slot < 1 or slot > len(party):
                output.write(
                    f"[red]❌ Invalid party slot: {slot}. "
                    f"You have {len(party)} Pokemon in your party.[/red]"
                )
                output.write("")
                set_pending_callback("pc")
                return

            if len(party) <= 1:
                output.write("[red]❌ You can't deposit your last Pokemon![/red]")
                output.write("")
                set_pending_callback("pc")
                return

            pokemon = party[slot - 1]
            placed_box = send_to_pc(game_state, pokemon)

            if placed_box is None:
                output.write(
                    "[red]❌ The PC is completely full! "
                    f"({BOXES_COUNT * BOX_CAPACITY} Pokemon stored)[/red]"
                )
                output.write("")
                set_pending_callback("pc")
                return

            party.pop(slot - 1)
            output.write(f"[green]✓ {pokemon['name']} was sent to {placed_box}.[/green]")
            remaining = len(party)
            output.write(f"[dim]Party now has {remaining} Pokemon.[/dim]")
            output.write("")
        else:
            output.write("[red]❌ Usage: deposit <party slot>  (e.g. 'deposit 3')[/red]")
            output.write("[dim]Type 'party' to see your party, then 'deposit <slot number>'[/dim]")
            output.write("")
        set_pending_callback("pc")
        return

    # ── Withdraw from PC ────────────────────────────────────────────
    if cmd.startswith("withdraw ") or cmd == "withdraw":
        parts = cmd.split()
        if len(parts) >= 3 and parts[1].isdigit() and parts[2].isdigit():
            box_num = int(parts[1])
            slot_num = int(parts[2])
            party = game_state.game_data.get("pokemon", [])

            if len(party) >= 6:
                output.write("[red]❌ Your party is full (6/6)! Deposit a Pokemon first.[/red]")
                output.write("")
                set_pending_callback("pc")
                return

            pokemon = withdraw_from_pc(game_state, box_num, slot_num)

            if pokemon is None:
                output.write(f"[red]❌ No Pokemon in Box {box_num}, slot {slot_num}.[/red]")
                output.write(f"[dim]Use 'box {box_num}' to see what's in that box.[/dim]")
                output.write("")
                set_pending_callback("pc")
                return

            party.append(pokemon)
            output.write(
                f"[green]✓ {pokemon['name']} (Lv.{pokemon['level']}) "
                f"was added to your party![/green]"
            )
            output.write(f"[dim]Party now has {len(party)} Pokemon.[/dim]")
            output.write("")
        else:
            output.write("[red]❌ Usage: withdraw <box> <slot>  (e.g. 'withdraw 1 3')[/red]")
            output.write("[dim]Use 'box <n>' to see slot numbers.[/dim]")
            output.write("")
        set_pending_callback("pc")
        return

    # ── Unknown ─────────────────────────────────────────────────────
    output.write(f"[yellow]?[/yellow] [dim]Unknown PC command: '{command}'[/dim]")
    output.write("[dim]Try: 'box 1'  'deposit 2'  'withdraw 1 3'  'leave'[/dim]")
    output.write("")
    set_pending_callback("pc")
