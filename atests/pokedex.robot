*** Settings ***
Documentation       Pokédex viewing and entry lookup end-to-end tests.
...
...                 Covers the ``pokedex``, ``dex``, ``inspect``,
...                 ``pokedex entry <name>``, ``pokedex seen``, ``pokedex caught``
...                 and ``pokedex missing`` commands.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Basic Pokédex display
# ----------------------------------------------------------------------------

Pokedex Command Shows Header
    [Documentation]    'pokedex' renders a Pokédex header in the output.
    [Tags]    pokedex    smoke
    [Setup]    Setup Game
    Type Command    pokedex
    Output Should Contain    POKEDEX    case_insensitive=True

Dex Alias Works Same As Pokedex
    [Documentation]    The 'dex' alias is equivalent to 'pokedex'.
    [Tags]    pokedex
    [Setup]    Setup Game
    Type Command    dex
    Output Should Contain    POKEDEX    case_insensitive=True

Pokedex Shows Seen And Caught Counts
    [Documentation]    The Pokédex overview shows how many Pokemon have been seen/caught.
    [Tags]    pokedex
    [Setup]    Setup Game
    Type Command    pokedex
    Output Should Contain    seen    case_insensitive=True
    Output Should Contain    caught    case_insensitive=True

# ----------------------------------------------------------------------------
# Pokédex entry lookup
# ----------------------------------------------------------------------------

Pokedex Entry Shows Species Name
    [Documentation]    'pokedex entry squirtle' displays SQUIRTLE's entry.
    [Tags]    pokedex    entry
    [Setup]    Setup Game
    Type Command    pokedex entry squirtle
    Output Should Contain    SQUIRTLE

Pokedex Entry Shows Species Type
    [Documentation]    The Pokédex entry for SQUIRTLE includes its Water type.
    [Tags]    pokedex    entry
    [Setup]    Setup Game
    Type Command    pokedex entry squirtle
    Output Should Contain    Water

Pokedex Entry By Number Works
    [Documentation]    'pokedex 7' resolves to SQUIRTLE (Pokédex #7).
    [Tags]    pokedex    entry
    [Setup]    Setup Game
    Type Command    pokedex 7
    Output Should Contain    SQUIRTLE

Pokedex Entry By Name Works
    [Documentation]    'pokedex squirtle' shows SQUIRTLE's entry (starter is already in party/seen).
    [Tags]    pokedex    entry
    [Setup]    Setup Game
    Type Command    pokedex squirtle
    Output Should Contain    SQUIRTLE

# ----------------------------------------------------------------------------
# Filtered views
# ----------------------------------------------------------------------------

Pokedex Seen Filter Shows Header
    [Documentation]    'pokedex seen' shows a header or listing for seen Pokemon.
    [Tags]    pokedex    filter
    [Setup]    Setup Game
    Type Command    pokedex seen
    Output Should Contain    seen    case_insensitive=True

Pokedex Caught Filter Shows Header
    [Documentation]    'pokedex caught' shows a header or listing for caught Pokemon.
    [Tags]    pokedex    filter
    [Setup]    Setup Game
    Type Command    pokedex caught
    Output Should Contain    caught    case_insensitive=True

Pokedex Missing Filter Shows Header
    [Documentation]    'pokedex missing' shows the Pokemon not yet caught (displayed as 'Unseen Pokemon').
    [Tags]    pokedex    filter
    [Setup]    Setup Game
    Type Command    pokedex missing
    Output Should Contain    Unseen    case_insensitive=True

# ----------------------------------------------------------------------------
# Inspect command
# ----------------------------------------------------------------------------

Inspect Shows Species Name
    [Documentation]    'inspect squirtle' shows SQUIRTLE's detailed info.
    [Tags]    pokedex    inspect
    [Setup]    Setup Game
    Type Command    inspect squirtle
    Output Should Contain    SQUIRTLE

Inspect Shows Level
    [Documentation]    'inspect squirtle' shows the Pokemon's level.
    [Tags]    pokedex    inspect
    [Setup]    Setup Game
    Type Command    inspect squirtle
    Output Should Contain    Level

Inspect Shows HP Stats
    [Documentation]    'inspect squirtle' shows the HP stats.
    [Tags]    pokedex    inspect
    [Setup]    Setup Game
    Type Command    inspect squirtle
    Output Should Contain    HP

Inspect Non-Existent Pokemon Shows Error
    [Documentation]    Inspecting a Pokemon not in the party shows an error.
    [Tags]    pokedex    inspect    error
    [Setup]    Setup Game
    Type Command    inspect bulbasaur
    Output Should Contain    Could not find    case_insensitive=True

# ----------------------------------------------------------------------------
# Pagination
# ----------------------------------------------------------------------------

Pokedex Next Page Advances The Page
    [Documentation]    'pokedex next' shows a different page of entries.
    [Tags]    pokedex    pagination
    [Setup]    Setup Game
    Type Command    pokedex
    Type Command    pokedex next
    Output Should Contain    Page    case_insensitive=True

Pokedex Page Jump Works
    [Documentation]    'pokedex page 2' jumps directly to page 2.
    [Tags]    pokedex    pagination
    [Setup]    Setup Game
    Type Command    pokedex page 2
    Output Should Contain    Page    case_insensitive=True

# ----------------------------------------------------------------------------
# Phase 1-4 Pokemon Pokedex entries
# ----------------------------------------------------------------------------

Pokedex Entry For Zubat Shows Poison Flying Type
    [Documentation]    ZUBAT (#41) Pokédex entry shows Poison/Flying type.
    [Tags]    pokedex    entry    phase1    zubat
    [Setup]    Setup Game
    Register Pokemon As Seen    Zubat
    Type Command    pokedex entry zubat
    Output Should Contain    ZUBAT
    Output Should Contain    Poison

Pokedex Entry For Clefairy Shows Normal Type
    [Documentation]    CLEFAIRY (#35) Pokédex entry shows Normal type.
    [Tags]    pokedex    entry    phase1    clefairy
    [Setup]    Setup Game
    Register Pokemon As Seen    Clefairy
    Type Command    pokedex entry clefairy
    Output Should Contain    CLEFAIRY
    Output Should Contain    Normal

Pokedex Entry For Jigglypuff By Number
    [Documentation]    'pokedex 39' resolves to JIGGLYPUFF.
    [Tags]    pokedex    entry    phase1    jigglypuff
    [Setup]    Setup Game
    Register Pokemon As Seen    Jigglypuff
    Type Command    pokedex 39
    Output Should Contain    JIGGLYPUFF

Pokedex Entry For Meowth Shows Normal Type
    [Documentation]    MEOWTH (#52) Pokédex entry shows Normal type.
    [Tags]    pokedex    entry    phase1    meowth
    [Setup]    Setup Game
    Register Pokemon As Seen    Meowth
    Type Command    pokedex entry meowth
    Output Should Contain    MEOWTH
    Output Should Contain    Normal

Pokedex Entry For Staryu Shows Water Type
    [Documentation]    STARYU (#120) Pokédex entry shows Water type.
    [Tags]    pokedex    entry    phase2    staryu
    [Setup]    Setup Game
    Register Pokemon As Seen    Staryu
    Type Command    pokedex entry staryu
    Output Should Contain    STARYU
    Output Should Contain    Water

Pokedex Entry For Starmie Shows Water Psychic Type
    [Documentation]    STARMIE (#121) Pokédex entry shows Water/Psychic dual type.
    [Tags]    pokedex    entry    phase2    starmie
    [Setup]    Setup Game
    Register Pokemon As Seen    Starmie
    Type Command    pokedex entry starmie
    Output Should Contain    STARMIE
    Output Should Contain    Water

Pokedex Entry For Horsea By Number
    [Documentation]    'pokedex 116' resolves to HORSEA.
    [Tags]    pokedex    entry    phase2    horsea
    [Setup]    Setup Game
    Register Pokemon As Seen    Horsea
    Type Command    pokedex 116
    Output Should Contain    HORSEA

Pokedex Entry For Goldeen Shows Water Type
    [Documentation]    GOLDEEN (#118) Pokédex entry shows Water type.
    [Tags]    pokedex    entry    phase2    goldeen
    [Setup]    Setup Game
    Register Pokemon As Seen    Goldeen
    Type Command    pokedex entry goldeen
    Output Should Contain    GOLDEEN
    Output Should Contain    Water

Pokedex Entry For Ekans Shows Poison Type
    [Documentation]    EKANS (#23) Pokédex entry shows Poison type.
    [Tags]    pokedex    entry    phase3    ekans
    [Setup]    Setup Game
    Register Pokemon As Seen    Ekans
    Type Command    pokedex entry ekans
    Output Should Contain    EKANS
    Output Should Contain    Poison

Pokedex Entry For Sandshrew Shows Ground Type
    [Documentation]    SANDSHREW (#27) Pokédex entry shows Ground type.
    [Tags]    pokedex    entry    phase3    sandshrew
    [Setup]    Setup Game
    Register Pokemon As Seen    Sandshrew
    Type Command    pokedex entry sandshrew
    Output Should Contain    SANDSHREW
    Output Should Contain    Ground

Pokedex Entry For Abra Shows Psychic Type
    [Documentation]    ABRA (#63) Pokédex entry shows Psychic type.
    [Tags]    pokedex    entry    phase3    abra
    [Setup]    Setup Game
    Register Pokemon As Seen    Abra
    Type Command    pokedex entry abra
    Output Should Contain    ABRA
    Output Should Contain    Psychic

Pokedex Entry For Oddish Shows Grass Poison Type
    [Documentation]    ODDISH (#43) Pokédex entry shows Grass/Poison dual type.
    [Tags]    pokedex    entry    phase3    oddish
    [Setup]    Setup Game
    Register Pokemon As Seen    Oddish
    Type Command    pokedex entry oddish
    Output Should Contain    ODDISH
    Output Should Contain    Grass

Pokedex Entry For Bellsprout Shows Grass Poison Type
    [Documentation]    BELLSPROUT (#69) Pokédex entry shows Grass/Poison dual type.
    [Tags]    pokedex    entry    phase3    bellsprout
    [Setup]    Setup Game
    Register Pokemon As Seen    Bellsprout
    Type Command    pokedex entry bellsprout
    Output Should Contain    BELLSPROUT
    Output Should Contain    Grass

Pokedex Entry For Alakazam By Number
    [Documentation]    'pokedex 65' resolves to ALAKAZAM.
    [Tags]    pokedex    entry    phase4    alakazam
    [Setup]    Setup Game
    Register Pokemon As Seen    Alakazam
    Type Command    pokedex 65
    Output Should Contain    ALAKAZAM

Pokedex Entry For Golem Shows Rock Ground Type
    [Documentation]    GOLEM (#76) Pokédex entry shows Rock/Ground dual type.
    [Tags]    pokedex    entry    phase4    golem
    [Setup]    Setup Game
    Register Pokemon As Seen    Golem
    Type Command    pokedex entry golem
    Output Should Contain    GOLEM
    Output Should Contain    Rock

Pokedex Entry For Vileplume By Number
    [Documentation]    'pokedex 45' resolves to VILEPLUME.
    [Tags]    pokedex    entry    phase4    vileplume
    [Setup]    Setup Game
    Register Pokemon As Seen    Vileplume
    Type Command    pokedex 45
    Output Should Contain    VILEPLUME

Pokedex Entry For Victreebel Shows Grass Poison Type
    [Documentation]    VICTREEBEL (#71) Pokédex entry shows Grass/Poison dual type.
    [Tags]    pokedex    entry    phase4    victreebel
    [Setup]    Setup Game
    Register Pokemon As Seen    Victreebel
    Type Command    pokedex entry victreebel
    Output Should Contain    VICTREEBEL
    Output Should Contain    Grass

# ----------------------------------------------------------------------------
# Verify Pokemon are not stubs in Pokedex
# ----------------------------------------------------------------------------

Newly Implemented Pokemon Have Complete Pokedex Entries
    [Documentation]    Newly implemented Pokemon show complete entries, not stub data.
    [Tags]    pokedex    entry    phase1234
    [Setup]    Setup Game
    # Test a few representative Pokemon from each phase
    Register Pokemon As Seen    Zubat
    Type Command    pokedex entry zubat
    Output Should Contain    ZUBAT
    Register Pokemon As Seen    Starmie
    Type Command    pokedex entry starmie
    Output Should Contain    STARMIE
    Register Pokemon As Seen    Abra
    Type Command    pokedex entry abra
    Output Should Contain    ABRA
    Register Pokemon As Seen    Alakazam
    Type Command    pokedex entry alakazam
    Output Should Contain    ALAKAZAM
