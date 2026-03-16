"""
Battle and exploration statistics for Pokemon Terminal.

All mutable stats live inside ``game_state.game_data["stats"]`` so they are
persisted automatically with every save / autosave.

Public API
----------
record_wild_encounter(game_state, location_name)
record_trainer_encounter(game_state)
record_wild_victory(game_state, player_pokemon_name)
record_trainer_victory(game_state, trainer_class, trainer_name)
record_fled(game_state)
record_faint(game_state, player_pokemon_name)
record_catch(game_state, species_name)
record_explore(game_state, location_name)
show_stats(game_state, output)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from textual.widgets import RichLog

if TYPE_CHECKING:
    from .game_state import GameState


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _empty_stats() -> dict:
    """Return the default stats sub-dict for a new save."""
    return {
        "total_explores": 0,
        "explores_by_location": {},  # {location_name: count}
        "wild_encounters": 0,
        "wild_victories": 0,
        "wild_fled": 0,
        "trainer_battles": 0,
        "trainer_victories": 0,
        "trainer_losses": 0,  # incremented when player faints vs trainer
        "catches": 0,
        "pokemon_stats": {},  # {pokemon_name: {battles, kos_dealt, faints}}
    }


def _s(game_state: GameState) -> dict:
    """Return (and lazily initialise) the stats sub-dict from game_data."""
    gd = game_state.game_data
    if "stats" not in gd or not isinstance(gd["stats"], dict):
        gd["stats"] = _empty_stats()
    return gd["stats"]


def _pokemon_entry(stats: dict, name: str) -> dict:
    """Return (and lazily create) the per-Pokemon stats entry."""
    ps = stats.setdefault("pokemon_stats", {})
    if name not in ps:
        ps[name] = {"battles": 0, "kos_dealt": 0, "faints": 0}
    return ps[name]


# ---------------------------------------------------------------------------
# Record helpers — called from battle_actions.py and exploration.py
# ---------------------------------------------------------------------------


def record_wild_encounter(game_state: GameState, location_name: str) -> None:
    """Increment wild encounter counter at *location_name*."""
    st = _s(game_state)
    st["wild_encounters"] = st.get("wild_encounters", 0) + 1

    # Also track active player Pokémon battles count
    player_pokemon = game_state.get_active_pokemon()
    if player_pokemon:
        entry = _pokemon_entry(st, player_pokemon["name"])
        entry["battles"] = entry.get("battles", 0) + 1


def record_trainer_encounter(game_state: GameState) -> None:
    """Increment trainer battle counter."""
    st = _s(game_state)
    st["trainer_battles"] = st.get("trainer_battles", 0) + 1

    player_pokemon = game_state.get_active_pokemon()
    if player_pokemon:
        entry = _pokemon_entry(st, player_pokemon["name"])
        entry["battles"] = entry.get("battles", 0) + 1


def record_ko_dealt(game_state: GameState, player_pokemon_name: str) -> None:
    """Increment KO counter for *player_pokemon_name* (every enemy faint, wild or trainer)."""
    st = _s(game_state)
    entry = _pokemon_entry(st, player_pokemon_name)
    entry["kos_dealt"] = entry.get("kos_dealt", 0) + 1


def record_wild_battle_won(game_state: GameState) -> None:
    """Increment the wild-battle victory counter (call once per completed wild battle)."""
    st = _s(game_state)
    st["wild_victories"] = st.get("wild_victories", 0) + 1


def record_trainer_battle_won(
    game_state: GameState,
) -> None:
    """Increment the trainer-battle victory counter (call when the final trainer Pokémon faints)."""
    st = _s(game_state)
    st["trainer_victories"] = st.get("trainer_victories", 0) + 1


def record_fled(game_state: GameState) -> None:
    """Increment successful-flee counter."""
    st = _s(game_state)
    st["wild_fled"] = st.get("wild_fled", 0) + 1


def record_faint(game_state: GameState, player_pokemon_name: str) -> None:
    """Increment faint counter for *player_pokemon_name* and trainer-losses if in trainer battle."""
    st = _s(game_state)
    entry = _pokemon_entry(st, player_pokemon_name)
    entry["faints"] = entry.get("faints", 0) + 1

    battle = game_state.battle_state
    if battle and battle.is_trainer_battle:
        st["trainer_losses"] = st.get("trainer_losses", 0) + 1


def record_catch(game_state: GameState, species_name: str) -> None:
    """Increment the total catches counter."""
    st = _s(game_state)
    st["catches"] = st.get("catches", 0) + 1


def record_explore(game_state: GameState, location_name: str) -> None:
    """Increment lifetime explore counters for *location_name*."""
    st = _s(game_state)
    st["total_explores"] = st.get("total_explores", 0) + 1
    by_loc = st.setdefault("explores_by_location", {})
    by_loc[location_name] = by_loc.get(location_name, 0) + 1


# ---------------------------------------------------------------------------
# Display
# ---------------------------------------------------------------------------


def show_stats(game_state: GameState, output: RichLog) -> None:
    """Render the full statistics panel to *output*."""
    st = _s(game_state)

    output.write("")
    output.write("[bold cyan]📊 Adventure Statistics[/bold cyan]")
    output.write("")

    # ── Exploration ──────────────────────────────────────────────────────────
    total_ex = st.get("total_explores", 0)
    by_loc = st.get("explores_by_location", {})
    fav_loc = max(by_loc, key=by_loc.get) if by_loc else None

    output.write("[bold]🗺  Exploration[/bold]")
    output.write(f"   Total explores            [cyan]{total_ex}[/cyan]")
    if fav_loc:
        output.write(
            f"   Favourite location        [cyan]{fav_loc}[/cyan] ({by_loc[fav_loc]} explores)"
        )
    if by_loc:
        output.write("   [dim]Explores per location:[/dim]")
        for loc, cnt in sorted(by_loc.items(), key=lambda x: -x[1]):
            bar = "█" * min(cnt, 20)
            output.write(f"     [dim]{loc:<22}[/dim] [green]{bar}[/green] [dim]{cnt}[/dim]")
    output.write("")

    # ── Battles ──────────────────────────────────────────────────────────────
    wild_enc = st.get("wild_encounters", 0)
    wild_win = st.get("wild_victories", 0)
    wild_fled = st.get("wild_fled", 0)
    tr_battles = st.get("trainer_battles", 0)
    tr_win = st.get("trainer_victories", 0)
    tr_loss = st.get("trainer_losses", 0)
    catches = st.get("catches", 0)

    output.write("[bold]⚔️  Battles[/bold]")
    output.write(f"   Wild encounters           [cyan]{wild_enc}[/cyan]")
    if wild_enc > 0:
        rate = int(wild_win / wild_enc * 100)
        output.write(f"   Wild victories            [green]{wild_win}[/green]  ({rate}% win rate)")
        output.write(f"   Fled successfully         [yellow]{wild_fled}[/yellow]")
    output.write(f"   Trainer battles           [cyan]{tr_battles}[/cyan]")
    if tr_battles > 0:
        output.write(f"   Trainer victories         [green]{tr_win}[/green]")
        if tr_loss > 0:
            output.write(f"   Trainer losses            [red]{tr_loss}[/red]")
    output.write(f"   Pokemon caught            [cyan]{catches}[/cyan]")
    output.write("")

    # ── Per-Pokémon ───────────────────────────────────────────────────────────
    pokemon_stats: dict = st.get("pokemon_stats", {})
    if pokemon_stats:
        output.write("[bold]🐾 Per-Pokémon[/bold]")
        # Sort by most battles
        for name, ps in sorted(pokemon_stats.items(), key=lambda x: -x[1].get("battles", 0)):
            battles = ps.get("battles", 0)
            kos = ps.get("kos_dealt", 0)
            faints = ps.get("faints", 0)
            faint_s = f"  [dim]({faints} faint{'s' if faints != 1 else ''})[/dim]" if faints else ""
            output.write(
                f"   [green]{name:<14}[/green]  "
                f"[cyan]{battles}[/cyan] battle{'s' if battles != 1 else ''}  "
                f"[yellow]{kos}[/yellow] KO{'s' if kos != 1 else ''}"
                f"{faint_s}"
            )
            if battles > 0:
                # Best-Pokemon highlight: most KOs dealt
                pass
        output.write("")

        # Highlight: MVP
        mvp = max(pokemon_stats.items(), key=lambda x: x[1].get("kos_dealt", 0))
        if mvp[1].get("kos_dealt", 0) > 0:
            output.write(
                f"   🏆 [bold]MVP:[/bold] [bold green]{mvp[0]}[/bold green] with {mvp[1]['kos_dealt']} KOs"
            )
            output.write("")
    else:
        output.write("[dim]No battle stats yet. Go find some Pokemon![/dim]")
        output.write("")
