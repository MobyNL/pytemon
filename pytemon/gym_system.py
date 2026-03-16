"""
Pokemon Gym System.

This module handles Pokemon Gym battles, badge awards, and gym progression.
It includes badge definitions, gym leader data references, and gym challenge mechanics.
"""

from typing import TYPE_CHECKING, Any, Dict, List, Optional

from textual.widgets import RichLog

if TYPE_CHECKING:
    from .game_state import GameState


# Badge definitions
BADGES = {
    "Boulder Badge": {
        "id": "boulder_badge",
        "name": "Boulder Badge",
        "emoji": "🪨",
        "gym": "Pewter City Gym",
        "leader": "Brock",
        "type": "Rock",
        "color": "orange3",
        "description": "Proves victory over Brock, the Rock-hard trainer",
        "order": 1,
    },
    "Cascade Badge": {
        "id": "cascade_badge",
        "name": "Cascade Badge",
        "emoji": "💧",
        "gym": "Cerulean City Gym",
        "leader": "Misty",
        "type": "Water",
        "color": "blue",
        "description": "Proves victory over Misty, the Tomboyish Mermaid",
        "order": 2,
    },
    "Thunder Badge": {
        "id": "thunder_badge",
        "name": "Thunder Badge",
        "emoji": "⚡",
        "gym": "Vermillion City Gym",
        "leader": "Lt. Surge",
        "type": "Electric",
        "color": "yellow",
        "description": "Proves victory over Lt. Surge, the Lightning Lieutenant",
        "order": 3,
    },
    "Rainbow Badge": {
        "id": "rainbow_badge",
        "name": "Rainbow Badge",
        "emoji": "🌈",
        "gym": "Celadon City Gym",
        "leader": "Erika",
        "type": "Grass",
        "color": "green",
        "description": "Proves victory over Erika, the Nature-Loving Princess",
        "order": 4,
    },
    "Soul Badge": {
        "id": "soul_badge",
        "name": "Soul Badge",
        "emoji": "👻",
        "gym": "Fuchsia City Gym",
        "leader": "Koga",
        "type": "Poison",
        "color": "purple",
        "description": "Proves victory over Koga, the Poisonous Ninja Master",
        "order": 5,
    },
    "Marsh Badge": {
        "id": "marsh_badge",
        "name": "Marsh Badge",
        "emoji": "🧠",
        "gym": "Saffron City Gym",
        "leader": "Sabrina",
        "type": "Psychic",
        "color": "magenta",
        "description": "Proves victory over Sabrina, the Master of Psychic Pokemon",
        "order": 6,
    },
    "Volcano Badge": {
        "id": "volcano_badge",
        "name": "Volcano Badge",
        "emoji": "🔥",
        "gym": "Cinnabar Island Gym",
        "leader": "Blaine",
        "type": "Fire",
        "color": "red",
        "description": "Proves victory over Blaine, the Hotheaded Quiz Master",
        "order": 7,
    },
    "Earth Badge": {
        "id": "earth_badge",
        "name": "Earth Badge",
        "emoji": "🌍",
        "gym": "Viridian City Gym",
        "leader": "Giovanni",
        "type": "Ground",
        "color": "brown",
        "description": "Proves victory over Giovanni, the Self-Proclaimed Strongest Trainer",
        "order": 8,
    },
}


# Gym data (maps locations to gym information)
GYMS = {
    "Pewter City": {
        "name": "Pewter City Gym",
        "leader_id": "gym_leader_brock",
        "badge": "Boulder Badge",
        "required_badges": 0,
        "specialty": "Rock-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Cerulean City": {
        "name": "Cerulean City Gym",
        "leader_id": "gym_leader_misty",
        "badge": "Cascade Badge",
        "required_badges": 1,
        "specialty": "Water-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Vermillion City": {
        "name": "Vermillion City Gym",
        "leader_id": "gym_leader_lt_surge",
        "badge": "Thunder Badge",
        "required_badges": 2,
        "specialty": "Electric-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Celadon City": {
        "name": "Celadon City Gym",
        "leader_id": "gym_leader_erika",
        "badge": "Rainbow Badge",
        "required_badges": 3,
        "specialty": "Grass-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Fuchsia City": {
        "name": "Fuchsia City Gym",
        "leader_id": "gym_leader_koga",
        "badge": "Soul Badge",
        "required_badges": 4,
        "specialty": "Poison-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Saffron City": {
        "name": "Saffron City Gym",
        "leader_id": "gym_leader_sabrina",
        "badge": "Marsh Badge",
        "required_badges": 5,
        "specialty": "Psychic-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Cinnabar Island": {
        "name": "Cinnabar Island Gym",
        "leader_id": "gym_leader_blaine",
        "badge": "Volcano Badge",
        "required_badges": 6,
        "specialty": "Fire-type Pokemon",
        "description": "Official Pokemon Gym",
    },
    "Viridian City": {
        "name": "Viridian City Gym",
        "leader_id": "gym_leader_giovanni",
        "badge": "Earth Badge",
        "required_badges": 7,
        "specialty": "Ground-type Pokemon",
        "description": "Official Pokemon Gym",
    },
}


# Ordered list of gym trainers that must be fought before the leader.
# Each list is in encounter order (first to last before the leader).
GYM_TRAINERS: Dict[str, List[str]] = {
    "Pewter City": [
        "gym_trainer_pewter_hiker",
        "gym_trainer_pewter_youngster",
    ],
    "Cerulean City": [
        "gym_trainer_cerulean_swimmer",
    ],
    # Future gyms can be populated here
}


def get_gym_trainers(location_name: str) -> List[str]:
    """
    Get ordered list of gym trainer IDs for a location.

    Args:
        location_name: Name of the location

    Returns:
        Ordered list of trainer IDs (may be empty)
    """
    return GYM_TRAINERS.get(location_name, [])


def get_next_gym_trainer(game_state: "GameState", location_name: str) -> Optional[str]:
    """
    Get the next undefeated gym trainer ID for a location.

    Args:
        game_state: The game state
        location_name: Name of the location

    Returns:
        Trainer ID of the next gym trainer, or None if all defeated
    """
    trainers = get_gym_trainers(location_name)
    defeated = set(game_state.game_data.get("defeated_trainers", []))
    for tid in trainers:
        if tid not in defeated:
            return tid
    return None


def enter_gym_lobby(game_state: "GameState", output: RichLog, show_gym_panel_callback) -> None:
    """
    Enter a Pokemon Gym and show the lobby overview with trainer/leader options.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        show_gym_panel_callback: Callback to display the gym action panel
    """
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    location_name = game_state.current_location.name
    gym_data = get_gym_data(location_name)

    if not gym_data:
        output.write("")
        output.write("[yellow]⚠ There is no Pokemon Gym here[/yellow]")
        output.write("")
        return

    badge_name = gym_data["badge"]
    badge_data = get_badge_data(badge_name)
    badge_color = badge_data["color"] if badge_data else "orange3"
    leader_name = badge_data["leader"] if badge_data else "Gym Leader"

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write(f"[bold cyan]     ⚔️  {gym_data['name'].upper()} ⚔️      [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write(f"[bold]Official Pokemon Gym[/bold]  [dim]{gym_data['specialty']}[/dim]")
    output.write("")

    # Already have the badge?
    if has_badge(game_state, badge_name):
        output.write(f"[{badge_color}]✓ You have already earned the {badge_name}![/{badge_color}]")
        output.write(f"[dim]Gym Leader {leader_name} nods at you respectfully.[/dim]")
        output.write("")
        show_gym_panel_callback()
        return

    # Special Viridian City flavour
    can_challenge, reason = can_challenge_gym(game_state, location_name)
    if not can_challenge:
        if location_name == "Viridian City":
            output.write(
                "[bold]Gym Assistant:[/bold] [yellow]The Gym Leader isn't in right now.[/yellow]"
            )
            output.write("[yellow]               He seems to be away on... business.[/yellow]")
            output.write("")
            output.write("[dim]Rumour has it he won't return until you've proven your worth[/dim]")
            output.write("[dim]with all 7 other badges.[/dim]")
        else:
            output.write(f"[yellow]⚠ {reason}[/yellow]")
        output.write("")
        output.write("[dim]You leave the Gym[/dim]")
        output.write("")
        return

    # Show gym trainer overview
    from .data import get_trainer

    gym_trainers = get_gym_trainers(location_name)
    defeated = set(game_state.game_data.get("defeated_trainers", []))

    if gym_trainers:
        remaining = [t for t in gym_trainers if t not in defeated]
        beaten = [t for t in gym_trainers if t in defeated]

        output.write(f"[bold]Gym Trainers:[/bold] {len(beaten)}/{len(gym_trainers)} defeated")
        output.write("")

        for tid in gym_trainers:
            trainer = get_trainer(tid)
            if trainer:
                if tid in defeated:
                    output.write(
                        f"  [green]✓ {trainer.trainer_class} {trainer.name}[/green]  [dim](defeated)[/dim]"
                    )
                else:
                    output.write(
                        f"  [yellow]○ {trainer.trainer_class} {trainer.name}[/yellow]  [dim](awaiting)[/dim]"
                    )
        output.write("")

        if remaining:
            output.write("[dim]Defeat the gym trainers or skip straight to the leader![/dim]")
        else:
            output.write("[green]You've cleared all the gym trainers![/green]")
    else:
        output.write("[dim]No trainers block the path. Head straight to the leader![/dim]")

    output.write("")
    output.write(
        f"[{badge_color}]⭐ Gym Leader {leader_name} is waiting at the back...[/{badge_color}]"
    )
    output.write(f"[dim]Defeat {leader_name} to earn the {badge_name}![/dim]")
    output.write("")

    show_gym_panel_callback()


def get_gym_data(location_name: str) -> Optional[Dict[str, Any]]:
    """
    Get gym data for a location.

    Args:
        location_name: Name of the location

    Returns:
        Gym data dict or None if no gym at this location
    """
    return GYMS.get(location_name)


def get_badge_data(badge_name: str) -> Optional[Dict[str, Any]]:
    """
    Get badge data by name.

    Args:
        badge_name: Name of the badge

    Returns:
        Badge data dict or None if not found
    """
    return BADGES.get(badge_name)


def has_badge(game_state: "GameState", badge_name: str) -> bool:
    """
    Check if the player has earned a specific badge.

    Args:
        game_state: The game state
        badge_name: Name of the badge to check

    Returns:
        True if player has the badge, False otherwise
    """
    badges = game_state.game_data.get("badges", [])
    if not isinstance(badges, list):
        badges = []
    badge_data = get_badge_data(badge_name)
    if not badge_data:
        return False
    return badge_data["id"] in badges


def get_badge_count(game_state: "GameState") -> int:
    """
    Get the number of badges the player has earned.

    Args:
        game_state: The game state

    Returns:
        Number of badges
    """
    badges = game_state.game_data.get("badges", [])
    if not isinstance(badges, list):
        return 0
    return len(badges)


def award_badge(game_state: "GameState", badge_name: str, output: RichLog) -> None:
    """
    Award a badge to the player.

    Args:
        game_state: The game state
        badge_name: Name of the badge to award
        output: The RichLog widget to write to
    """
    badge_data = get_badge_data(badge_name)
    if not badge_data:
        output.write(f"[red]❌ Error: Unknown badge '{badge_name}'[/red]")
        return

    # Initialize badges list if needed
    if "badges" not in game_state.game_data:
        game_state.game_data["badges"] = []

    badges = game_state.game_data["badges"]
    badge_id = badge_data["id"]

    # Check if already has badge
    if badge_id in badges:
        output.write(f"[yellow]⚠ You already have the {badge_name}![/yellow]")
        return

    # Award the badge
    badges.append(badge_id)

    # Display badge award ceremony
    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold yellow]★ ★ ★  BADGE EARNED!  ★ ★ ★[/bold yellow]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write(
        f"[bold {badge_data['color']}]{badge_data['emoji']} {badge_name} {badge_data['emoji']}[/bold {badge_data['color']}]"
    )
    output.write("")
    output.write(f"[{badge_data['color']}]{badge_data['description']}[/{badge_data['color']}]")
    output.write("")
    output.write(f"[bold]Badges: {len(badges)}/8[/bold]")
    output.write("")


def can_challenge_gym(game_state: "GameState", location_name: str) -> tuple[bool, str]:
    """
    Check if the player can challenge a gym at the given location.

    Args:
        game_state: The game state
        location_name: Name of the location

    Returns:
        Tuple of (can_challenge, reason_if_not)
    """
    gym_data = get_gym_data(location_name)

    if not gym_data:
        return False, "There is no gym at this location"

    # Check if already defeated
    badge_name = gym_data["badge"]
    if has_badge(game_state, badge_name):
        return False, f"You've already defeated this gym and earned the {badge_name}!"

    # Check badge requirements
    required = gym_data.get("required_badges", 0)
    current = get_badge_count(game_state)

    if current < required:
        return False, f"You need at least {required} badge(s) to challenge this gym"

    # Check if player has any Pokemon
    pokemon = game_state.game_data.get("pokemon", [])
    if not pokemon:
        return False, "You need Pokemon to challenge a gym!"

    # Check if player has any Pokemon that can battle
    if not game_state.get_active_pokemon():
        return False, "All your Pokemon have fainted! Visit a Pokemon Center first!"

    return True, ""


def show_badge_case(game_state: "GameState", output: RichLog) -> None:
    """
    Display the player's badge case.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
    """
    badges = game_state.game_data.get("badges", [])

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("[bold cyan]             🏆 BADGE CASE 🏆              [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")

    if not badges:
        output.write("[dim]No badges yet. Challenge Pokemon Gyms to earn badges![/dim]")
        output.write("")
        return

    output.write(f"[bold]Badges Collected: {len(badges)}/8[/bold]")
    output.write("")

    # Show badges in order
    for badge_name, badge_data in BADGES.items():
        badge_id = badge_data["id"]
        if badge_id in badges:
            output.write(
                f"  [{badge_data['color']}]✓ {badge_data['emoji']} {badge_name}[/{badge_data['color']}]  [dim]({badge_data['leader']} - {badge_data['type']} type)[/dim]"
            )
        else:
            output.write("  [dim]○ ? ? ?  (Not yet earned)[/dim]")

    output.write("")

    # Special message for completing the badge challenge
    if len(badges) == 8:
        output.write("[bold yellow]🎉 CONGRATULATIONS! 🎉[/bold yellow]")
        output.write("[yellow]You've collected all 8 Gym Badges![/yellow]")
        output.write("[yellow]You're ready to challenge the Pokemon League![/yellow]")
        output.write("")


def enter_gym(game_state: "GameState", output: RichLog, trigger_trainer_battle_callback) -> None:
    """
    Enter a Pokemon Gym and initiate gym battle.

    Args:
        game_state: The game state
        output: The RichLog widget to write to
        trigger_trainer_battle_callback: Callback to start trainer battle
    """
    if not game_state.current_location:
        output.write("[red]❌ Error: No current location set[/red]")
        return

    location_name = game_state.current_location.name
    gym_data = get_gym_data(location_name)

    if not gym_data:
        output.write("")
        output.write("[yellow]⚠ There is no Pokemon Gym here[/yellow]")
        output.write("")
        return

    output.write("")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write(f"[bold cyan]     ⚔️  {gym_data['name'].upper()} ⚔️      [/bold cyan]")
    output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
    output.write("")
    output.write("[bold]Official Pokemon Gym[/bold]")
    output.write(f"[dim]Specialty: {gym_data['specialty']}[/dim]")
    output.write("")

    # Check if can challenge
    can_challenge, reason = can_challenge_gym(game_state, location_name)

    if not can_challenge:
        # Viridian City Gym has special flavour — Giovanni is absent until late game
        if location_name == "Viridian City":
            output.write(
                "[bold]Gym Assistant:[/bold] [yellow]The Gym Leader isn't in right now.[/yellow]"
            )
            output.write("[yellow]               He seems to be away on... business.[/yellow]")
            output.write("")
            output.write("[dim]Rumour has it he won't return until you've proven your worth[/dim]")
            output.write("[dim]with all 7 other badges.[/dim]")
        else:
            output.write(f"[yellow]⚠ {reason}[/yellow]")
        output.write("")
        output.write("[dim]You leave the Gym[/dim]")
        output.write("")
        return

    # Start gym battle
    leader_id = gym_data["leader_id"]
    badge_name = gym_data["badge"]
    badge_data = get_badge_data(badge_name)

    if not badge_data:
        output.write("[red]❌ Error: Badge data not found[/red]")
        return

    # Display gym leader introduction
    output.write("[bold]This is a Pokemon Gym![/bold]")
    output.write(
        f"[bold]Gym Leader:[/bold] [{badge_data['color']}]{badge_data['leader']}[/{badge_data['color']}]"
    )
    output.write("")
    output.write(f"[dim]Defeat the Gym Leader to earn the {badge_name}![/dim]")
    output.write("")

    # Trigger gym leader battle with special flag
    trigger_trainer_battle_callback(leader_id, output, is_gym_battle=True)


def handle_gym_victory(game_state: "GameState", trainer_id: str, output: RichLog) -> None:
    """
    Handle victory over a gym leader - award badge.

    Args:
        game_state: The game state
        trainer_id: ID of the gym leader defeated
        output: The RichLog widget to write to
    """
    # Find which gym this leader belongs to
    for location_name, gym_data in GYMS.items():
        if gym_data["leader_id"] == trainer_id:
            badge_name = gym_data["badge"]
            award_badge(game_state, badge_name, output)

            # Add TM/prize money bonus message
            output.write("[bold cyan]═══════════════════════════════════════════[/bold cyan]")
            output.write("")
            output.write(f"[dim]The {badge_name} will make your Pokemon stronger![/dim]")
            output.write("")
            return

    # If we get here, trainer wasn't a gym leader
    output.write("[yellow]⚠ Warning: Trainer battle completed but no badge found[/yellow]")
