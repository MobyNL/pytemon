"""
Text constants for pytemon/evolution.py.
"""

# ── force_evolve / apply_evolution ───────────────────────────────────────────

# Written after the dynamic "What? X is evolving!" line
EVOLUTION_PREAMBLE: list[str] = [
    "",
    "[dim]  ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇ ◇[/dim]",
    "[bold cyan]  ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆ ◆[/bold cyan]",
    "",
]

# Dynamic: "[bold green]🎉 Congratulations! {old_name} evolved into {evolved_form}! 🎉[/bold green]"
EVOLUTION_SUCCESS_POST: list[str] = [
    # dynamic level/HP line follows
    "",
]
