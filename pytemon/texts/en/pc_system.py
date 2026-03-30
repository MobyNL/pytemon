"""
Text constants for pytemon/pc_system.py.
"""

# ── show_pc_menu ──────────────────────────────────────────────────────────────

PC_MENU_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]          💾 BILL'S PC SYSTEM 💾            [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
    "  [dim]Storage System v2.0[/dim]",
]

PC_BOX_OVERVIEW_HEADER: list[str] = [
    "",
    "[bold green]📦 Box Overview:[/bold green]",
]

PC_COMMANDS_BLOCK: list[str] = [
    "",
    "[bold green]Commands:[/bold green]",
    "  [cyan]box <n>[/cyan]                - View box contents (e.g. 'box 1')",
    "  [cyan]deposit <party slot>[/cyan]   - Store a party Pokemon (e.g. 'deposit 2')",
    "  [cyan]withdraw <box> <slot>[/cyan]  - Retrieve from PC   (e.g. 'withdraw 1 3')",
    "  [cyan]leave[/cyan]                  - Log out of PC",
    "",
]

# ── show_box ──────────────────────────────────────────────────────────────────

PC_BOX_EMPTY: list[str] = [
    "[dim]This box is empty.[/dim]",
    "",
]

# ── deposit / withdraw messages ───────────────────────────────────────────────

PC_DEPOSIT_FULL: list[str] = [
    "",
    "[red]❌ The PC is full! All boxes are at capacity.[/red]",
    "",
]

PC_PARTY_TOO_SMALL: list[str] = [
    "",
    "[red]❌ Can't deposit — you'd have no Pokemon left in your party![/red]",
    "",
]

PC_WITHDRAW_PARTY_FULL: list[str] = [
    "",
    "[red]❌ Your party is full! (Max 6 Pokemon)[/red]",
    "[dim]Deposit a Pokemon first before withdrawing.[/dim]",
    "",
]
