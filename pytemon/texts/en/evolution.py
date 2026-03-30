"""
Text constants for pytemon/evolution.py.
"""

# ── force_evolve / apply_evolution ───────────────────────────────────────────

# Dynamic: use write_lines_fmt(output, EVOLVING_LINE, old_name=...)
EVOLVING_LINE: list[str] = [
    "",
    "[bold yellow]✨ What? {old_name} is evolving![/bold yellow]",
]

EVOLUTION_PREAMBLE: list[str] = [
    "",
    "[dim]  ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇[/dim]",
    "[bold cyan]  ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆[/bold cyan]",
    "",
]

# Dynamic: use write_lines_fmt(output, EVOLUTION_SUCCESS, old_name=..., evolved_form=...,
#                              current_level=..., hp=..., max_hp=...)
EVOLUTION_SUCCESS: list[str] = [
    "[bold green]🎉 Congratulations! {old_name} evolved into {evolved_form}! 🎉[/bold green]",
    "  [dim]Level {current_level} | HP: {hp}/{max_hp}[/dim]",
    "",
]
