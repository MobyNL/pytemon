"""
Text constants for pytemon/gym_system.py.
"""

# ── enter_gym_lobby ───────────────────────────────────────────────────────────

# Dynamic header — use write_lines_fmt(output, GYM_LOBBY_HEADER, gym_name="PEWTER CITY GYM")
# Note: [bold cyan] with a dynamic name can't be fully pre-baked; only the
# surrounding border lines are in the list — the name line stays inline.

GYM_LOBBY_BORDER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    # dynamic: f"[bold cyan]     ⚔️  {gym_name} ⚔️      [/bold cyan]"
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

GYM_LOBBY_NO_GYM: list[str] = [
    "",
    "[yellow]⚠ There is no Pokemon Gym here[/yellow]",
    "",
]

GYM_LOBBY_LEAVE: list[str] = [
    "",
    "[dim]You leave the Gym[/dim]",
    "",
]

GYM_LOBBY_VIRIDIAN_CLOSED: list[str] = [
    "[bold]Gym Assistant:[/bold] [yellow]The Gym Leader isn't in right now.[/yellow]",
    "[yellow]               He seems to be away on... business.[/yellow]",
    "",
    "[dim]Rumour has it he won't return until you've proven your worth[/dim]",
    "[dim]with all 7 other badges.[/dim]",
]

GYM_TRAINERS_CLEARED: list[str] = [
    "[green]You've cleared all the gym trainers![/green]",
]

GYM_TRAINERS_HINT: list[str] = [
    "[dim]Defeat the gym trainers or skip straight to the leader![/dim]",
]

GYM_NO_TRAINERS_HINT: list[str] = [
    "[dim]No trainers block the path. Head straight to the leader![/dim]",
]

# ── award_badge ───────────────────────────────────────────────────────────────

BADGE_EARNED_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold yellow]★ ★ ★  BADGE EARNED!  ★ ★ ★[/bold yellow]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

# ── show_badge_case ───────────────────────────────────────────────────────────

BADGE_CASE_HEADER: list[str] = [
    "",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "[bold cyan]             🏆 BADGE CASE 🏆              [/bold cyan]",
    "[bold cyan]═══════════════════════════════════════════[/bold cyan]",
    "",
]

BADGE_CASE_EMPTY: list[str] = [
    "[dim]No badges yet. Challenge Pokemon Gyms to earn badges![/dim]",
    "",
]

BADGE_CASE_ALL_BADGES: list[str] = [
    "",
    "[bold green]🏆 You have all 8 badges! The Pokemon League awaits![/bold green]",
    "",
]
