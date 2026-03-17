# pytemon — Game Completion Roadmap

> Current state: **~35% of a complete Gen 1 Kanto experience**
> Target: A fully playable terminal Pokemon Red/Blue equivalent

---

## Where We Stand

| Area | Status | Completeness |
|---|---|---|
| Locations / Kanto map | 19 of ~60 areas | ~32% |
| Pokemon species (full data) | ~72 of 151 | ~48% |
| Gym leaders | 2 fully working, 6 stubbed | 25% |
| Battle mechanics | Core done, edge cases missing | ~70% |
| Move data | ~164 of ~165 Gen 1 moves | ~99% |
| Items | Full Gen 1 set | ~95% |
| Story / narrative | Pallet → Cerulean only | ~20% |
| Trainer roster | ~25 trainers | ~30% |
| Evolution chains | Level + item-based done | ~80% |
| PC storage | Fully working | 100% |
| Fishing | Fully working | 100% |
| HM/TM system | Fully working | 95% |

---

## Phase 1 — Solid Foundation (2–3 weeks) ✅ Completed
**Goal: Stabilise and polish what exists before expanding**

### 1.1 Battle System Polish
- [x] Fix two-turn moves (Fly, Dig, Solar Beam — charge turn skips player input)
- [x] Fix trapping moves (Wrap, Bind, Fire Spin — should lock opponent for 2–5 turns)
- [x] Fix Leech Seed (drain HP each turn, not just on apply)
- [x] Fix speed-priority moves (Quick Attack should always go first)
- [x] Validate stat stage resets correctly between battles
- [x] Fix recoil damage calculation (should be ¼ damage dealt, not flat)
- [x] Implement Disable (block one move for 3–8 turns)

### 1.2 Pokemon Data Upgrade
- [x] Fill in full stats + learnsets for the 80 stub-only species (priority: those on implemented routes)
- [x] Add evolution data for all Gen 1 trade-evolvers (Graveler→Golem, Haunter→Gengar, Machoke→Machamp, Kadabra→Alakazam) — since we can't trade, convert to item-based (Link Cable item)
- [x] Add happiness-based hints (Eevee evolution flavour text)

### 1.3 Item UI
- [x] Add in-field item use menu (use evolution stones from bag without being in battle)
- [x] Add Repel countdown display (show remaining steps)

### 1.4 Bug Fixes & QA
- [x] Verify all 19 current locations have correct wild Pokemon tables
- [x] Verify all current trainer teams are balanced vs. player progression point
- [x] Ensure badge-gated exits are consistent across all implemented routes

### 1.5 Core Dungeon System (Reusable for all story dungeons)
**Goal: One shared dungeon framework used by caves, ships, towers, hideouts, and buildings with floors**

- [x] Add a `DungeonDefinition` data model (dungeon id, floors, entrances/exits, completion flags)
- [x] Add floor graph support (named floors/rooms, directional links, ladders/warps, one-way tiles)
- [x] Add dungeon encounter tables per floor (species, level ranges, encounter weights)
- [x] Add trainer + NPC placement per floor with one-time defeat persistence
- [x] Add item pickup nodes with one-time story/item flags (e.g. `got_mt_moon_fossil`)
- [x] Add gated interactions (keys, switches, badge checks, story flags)
- [x] Add dungeon status command output (`where`, current floor, explored rooms, nearby exits)
- [x] Add dungeon escape rules (`Escape Rope`, blackout handling, optional restart checkpoint)
- [x] Add dungeon event hooks (boss trigger, rival event, item reward cutscene)
- [x] Add save/load compatibility for all dungeon progress fields
- [x] Add test utilities for scripted dungeon traversal (path, event, and gate assertions)

---

## Phase 2 — Complete the Western Map (3–4 weeks)
**Goal: Playable from Pallet Town to Vermillion City with full Lt. Surge gym**

### 2.1 Lt. Surge & Vermillion City
- [ ] Complete Lt. Surge trainer team (Voltorb, Pikachu, Raichu, Electrode)
- [ ] Add Vermillion City gym trainers (Sailors, etc.)
- [ ] Implement SS Anne as a structured mini-dungeon (decks/rooms + captain event, award HM01 Cut)
- [ ] Add Vermillion City Pokemart (Great Ball tier unlocked)

### 2.2 Diglett's Cave & Rock Tunnel
- [ ] Implement Rock Tunnel as a multi-floor dungeon (darkness mechanic with HM05 Flash)
- [ ] Add Rock Tunnel trainers (Hikers, Picnickers)
- [ ] Add Diglett's Cave wild Pokemon (Diglett, Dugtrio)

### 2.3 Routes 7–12 (Eastern Kanto)
- [ ] Route 7 (Celadon ↔ Saffron)
- [ ] Route 8 (Saffron ↔ Lavender)
- [ ] Route 9 (Cerulean ↔ Rock Tunnel) — exists, needs trainers
- [ ] Route 10 (Rock Tunnel ↔ Lavender) — exists, needs trainers
- [ ] Route 11 (Vermillion ↔ Route 12) — exists, needs full trainer roster
- [ ] Route 12 (north–south connector, Fishing spot)

### 2.4 Lavender Town
- [ ] Implement Lavender Town (Pokémon Tower story arc)
- [ ] Add Mr. Fuji / ghost storyline (narrative-only, no silph co. required)
- [ ] Add Pokémon Tower as a multi-floor dungeon

### 2.5 Dungeon Rollout (First Wave)
**Goal: Use the shared dungeon system for all early/midgame set-piece areas**

- [ ] Mt. Moon: 3 floors, fossils choice event, Team Rocket trainer pockets, ladder shortcuts
- [ ] SS Anne: multi-room ship layout, optional trainer rooms, captain cutscene + HM01 reward
- [ ] Rock Tunnel: dark-room navigation, Flash interaction, trainer gauntlet route
- [ ] Pokémon Tower: ghost encounter gating, Silph Scope reveal flow, Mr. Fuji rescue trigger
- [ ] Team Rocket Hideout (Celadon): basement floors, switch/warp tile puzzle, Giovanni boss room

---

## Phase 3 — Celadon, Fuchsia & Central Kanto (3–4 weeks)
**Goal: Complete gyms 4 & 5, unlock Surf**

### 3.1 Celadon City
- [x] Implement Celadon City
- [x] Erika (Gym 4) — Grass-type, Rainbow Badge
  - [x] Gym trainers: Beauty, Lass
  - [x] Team: Tangela, Weepinbell, Gloom, Vileplume
- [x] Celadon Department Store (full 6-floor shop with unique items)
- [x] Game Corner (simple slot machine / coin exchange for TM prizes)
- [x] Routes 16, 17, 18 (Cycling Road)

### 3.2 Fuchsia City
- [x] Implement Fuchsia City
- [x] Koga (Gym 5) — Poison-type, Soul Badge (unlocks Surf)
  - [x] Gym trainers: Juggler, Lass
  - [x] Team: Koffing, Muk, Koffing, Weezing
- [x] Safari Zone (simplified — set encounter pool, catch with bait/rock)
- [x] Routes 13, 14, 15 (south coast)
- [x] Routes 19, 20 (sea routes enabling Cinnabar access)

---

## Phase 4 — Saffron, Cinnabar & Eastern Kanto (3–4 weeks)
**Goal: Complete gyms 6 & 7, open Victory Road**

### 4.1 Saffron City
- [ ] Implement Saffron City
- [ ] Silph Co. (3–4 floor simplified version) — rescue Mr. Fuji, earn Master Ball
- [ ] Sabrina (Gym 6) — Psychic-type, Marsh Badge
  - [ ] Team: Abra, Kadabra, Mr. Mime, Alakazam
- [ ] Route 7 connector

### 4.2 Cinnabar Island
- [ ] Implement Cinnabar Island
- [ ] Blaine (Gym 7) — Fire-type, Volcano Badge
  - [ ] Team: Growlithe, Ponyta, Rapidash, Arcanine
- [ ] Pokémon Mansion (fossil Pokémon lore, find Secret Key)
- [ ] Fossil revival — Dome/Helix Fossil → Kabuto/Omanyte
- [ ] Routes 20, 21 (ocean)

### 4.3 Final Viridian Gym
- [ ] Giovanni (Gym 8) — Ground-type, Earth Badge (requires 7 badges)
  - [ ] Team: Rhyhorn, Dugtrio, Nidoqueen, Nidoking, Rhydon
- [ ] Victory Road (cave with strong trainers)

### 4.4 Dungeon Rollout (Late Game)
- [ ] Silph Co.: office-building dungeon with floor warps + keycard-gated rooms
- [ ] Pokémon Mansion: switch-locked doors, journal lore nodes, Secret Key progression
- [ ] Victory Road: strength/boulder gates + high-level trainer checkpoints

---

## Phase 5 — Endgame & Elite Four (2–3 weeks)
**Goal: Complete the story — become Pokémon Champion**

### 5.1 Pokémon League
- [ ] Implement Pokémon League building / reception
- [ ] Lorelei (Ice-type) — Team: Dewgong, Cloyster, Slowbro, Jynx, Lapras
- [ ] Bruno (Fighting-type) — Team: Onix, Hitmonchan, Hitmonlee, Onix, Machamp
- [ ] Agatha (Ghost-type) — Team: Gengar, Haunter, Gengar, Arbok, Gengar
- [ ] Lance (Dragon-type) — Team: Gyarados, Dragonair ×2, Aerodactyl, Dragonite
- [ ] Champion Gary (rival final battle — team depends on player's starter)

### 5.2 Rival Final Battle Scaling
- [ ] Gary's team should evolve based on player starter choice (implemented stubs, needs finalisation)
- [ ] Post-game "Hall of Fame" display with party snapshot

---

## Phase 6 — Post-game & Polish (2 weeks)
**Goal: Replayability and completionist content**

### 6.1 Legendaries
- [ ] Articuno (Seafoam Islands — optional dungeon)
- [ ] Zapdos (Power Plant — accessible via Surf)
- [ ] Moltres (Victory Road — rare encounter)
- [ ] Mewtwo (Cerulean Cave — post-E4 only)
- [ ] Mew (cheat code / secret trigger only)

### 6.2 Post-game Content
- [ ] Cerulean Cave (new area, post-Champion only)
- [ ] Pokédex completion reward (Oak's certificate)
- [ ] Rematch system (rebattle gym leaders at higher levels)

### 6.3 Pokémon Data Completion
- [ ] Fill in all 151 species with complete learnsets
- [ ] Verify all evolution chains are accurate

### 6.4 TUI & UX Polish
- [ ] Typewriter animation for NPC dialogue
- [ ] Consistent colour scheme review (Rich markup audit)
- [ ] Smoother battle flow (reduce blank lines, tighten pacing)
- [ ] `pokedex` command improvements (search by type, show evolution chain)
- [ ] Party-screen HP bar improvements (show status conditions inline)

---

## Ongoing / Cross-cutting

| Task | Notes |
|---|---|
| Keep test coverage ≥ 80% | Add tests alongside every new module |
| Lint/format clean | Run `ruff format` + `ruff check` before every push |
| PyPI releases | Bump version + publish after each Phase completes |
| CHANGELOG.md | Maintain a changelog starting Phase 2 |
| GitHub Issues | Log each Phase section as a tracked issue |

---

## Estimated Timeline Summary

| Phase | Description | Duration |
|---|---|---|
| **1** | Foundation stabilisation | 2–3 weeks |
| **2** | Western map + Lt. Surge | 3–4 weeks |
| **3** | Celadon + Fuchsia (Gyms 4–5) | 3–4 weeks |
| **4** | Saffron + Cinnabar (Gyms 6–7) | 3–4 weeks |
| **5** | Elite Four + Champion | 2–3 weeks |
| **6** | Post-game + polish | 2 weeks |
| **Total** | | **~15–20 weeks** |

> At a comfortable pace of a few hours per week this puts a v1.0 "complete" release around **mid-to-late 2026**.
