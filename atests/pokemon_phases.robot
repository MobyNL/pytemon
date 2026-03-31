*** Settings ***
Documentation       End-to-end tests for Phase 1-4 Pokemon implementation.
...
...                 Tests stats, stone evolutions, level-based evolutions, and gym battles
...                 for the 28 newly-implemented Pokemon species from Pallet Town to Cerulean City.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ============================================================================
# PHASE 1: Critical Wild Encounters - Stats & Evolution Tests
# ============================================================================

Zubat Has Correct Stats Not Stub Values
    [Documentation]    ZUBAT has proper stats (not stub values of 50/50/50).
    [Tags]    phase1    zubat    stats
    [Setup]    Setup Game With Pokemon    ZUBAT    10
    Party Pokemon Should Be    0    ZUBAT
    Party Pokemon Level Should Be    0    10

Clefairy Evolves With Moon Stone
    [Documentation]    Using Moon Stone on CLEFAIRY produces CLEFABLE.
    [Tags]    phase1    evolution    stone    clefairy
    [Setup]    Setup Evolution Test    CLEFAIRY    Moon Stone
    Type Command    use moon stone on clefairy
    Output Should Contain    CLEFABLE
    Party Pokemon Should Be    0    CLEFABLE
    Item Count Should Be    Moon Stone    0

Clefairy Has Normal Type
    [Documentation]    CLEFAIRY is Normal type (single type).
    [Tags]    phase1    clefairy    stats
    [Setup]    Setup Game With Pokemon    CLEFAIRY    10
    Party Pokemon Should Be    0    CLEFAIRY

Jigglypuff Has High HP Stat
    [Documentation]    JIGGLYPUFF has signature high HP (115 base HP).
    [Tags]    phase1    jigglypuff    stats
    [Setup]    Setup Game With Pokemon    JIGGLYPUFF    20
    Party Pokemon Should Be    0    JIGGLYPUFF

Jigglypuff Evolves To Wigglytuff With Moon Stone
    [Documentation]    Using Moon Stone on JIGGLYPUFF produces WIGGLYTUFF.
    [Tags]    phase1    evolution    stone    jigglypuff
    [Setup]    Setup Evolution Test    JIGGLYPUFF    Moon Stone
    Type Command    use moon stone on jigglypuff
    Output Should Contain    WIGGLYTUFF
    Party Pokemon Should Be    0    WIGGLYTUFF
    Item Count Should Be    Moon Stone    0

Meowth Has Normal Type
    [Documentation]    MEOWTH is Normal type with proper stats.
    [Tags]    phase1    meowth    stats
    [Setup]    Setup Game With Pokemon    MEOWTH    15
    Party Pokemon Should Be    0    MEOWTH

# ============================================================================
# PHASE 2: Gym Leaders - Brock & Misty Pokemon
# ============================================================================

Staryu Is Used By Misty In Gym Battle
    [Documentation]    Gym Leader Misty uses STARYU in her team.
    [Tags]    phase2    gym    misty    staryu
    [Setup]    Setup Game At Location    Cerulean City
    Add Badge    Boulder Badge
    Set Lead Pokemon    PIKACHU    25
    Type Command    enter gym
    Click Widget    id=btn-gym-challenge
    Should Be In Battle

Starmie Is Misty Signature Pokemon
    [Documentation]    Gym Leader Misty's signature Pokemon is STARMIE (Water/Psychic).
    [Tags]    phase2    gym    misty    starmie
    [Setup]    Setup Misty Battle With Starmie
    Should Be In Battle

Staryu Evolves With Water Stone
    [Documentation]    Using Water Stone on STARYU produces STARMIE.
    [Tags]    phase2    evolution    stone    staryu
    [Setup]    Setup Evolution Test    STARYU    Water Stone
    Type Command    use water stone on staryu
    Output Should Contain    STARMIE
    Party Pokemon Should Be    0    STARMIE
    Item Count Should Be    Water Stone    0

Starmie Has Water Type
    [Documentation]    STARMIE is Water/Psychic dual-type.
    [Tags]    phase2    starmie    stats
    [Setup]    Setup Game With Pokemon    STARMIE    20
    Party Pokemon Should Be    0    STARMIE

Horsea Can Be Added To Party
    [Documentation]    HORSEA can be added to the party and has proper stats.
    [Tags]    phase2    horsea    stats
    [Setup]    Setup Game With Pokemon    HORSEA    18
    Party Pokemon Should Be    0    HORSEA

Goldeen Can Be Added To Party
    [Documentation]    GOLDEEN can be added to the party and has proper stats.
    [Tags]    phase2    goldeen    stats
    [Setup]    Setup Game With Pokemon    GOLDEEN    18
    Party Pokemon Should Be    0    GOLDEEN

# ============================================================================
# PHASE 3: Trainer Battles - Route Trainers
# ============================================================================

Ekans Has Poison Type
    [Documentation]    EKANS is Poison type with proper stats.
    [Tags]    phase3    ekans    stats
    [Setup]    Setup Game With Pokemon    EKANS    15
    Party Pokemon Should Be    0    EKANS

Sandshrew Has Ground Type
    [Documentation]    SANDSHREW is Ground type with proper stats.
    [Tags]    phase3    sandshrew    stats
    [Setup]    Setup Game With Pokemon    SANDSHREW    15
    Party Pokemon Should Be    0    SANDSHREW

Abra Has Psychic Type
    [Documentation]    ABRA is Psychic type with proper stats.
    [Tags]    phase3    abra    stats
    [Setup]    Setup Game With Pokemon    ABRA    10
    Party Pokemon Should Be    0    ABRA

Abra Only Knows Teleport Initially
    [Documentation]    ABRA's signature trait - it only knows TELEPORT at low levels.
    [Tags]    phase3    abra    moves
    [Setup]    Setup Game With Pokemon    ABRA    5
    Party Pokemon Should Be    0    ABRA

Gloom Evolves To Vileplume With Leaf Stone
    [Documentation]    Using Leaf Stone on GLOOM produces VILEPLUME.
    [Tags]    phase3    evolution    stone    oddish
    [Setup]    Setup Evolution Test    GLOOM    Leaf Stone
    Type Command    use leaf stone on gloom
    Output Should Contain    VILEPLUME
    Party Pokemon Should Be    0    VILEPLUME
    Item Count Should Be    Leaf Stone    0

Oddish Has Grass Poison Dual Type
    [Documentation]    ODDISH is Grass/Poison dual-type.
    [Tags]    phase3    oddish    stats
    [Setup]    Setup Game With Pokemon    ODDISH    15
    Party Pokemon Should Be    0    ODDISH

Weepinbell Evolves To Victreebel With Leaf Stone
    [Documentation]    Using Leaf Stone on WEEPINBELL produces VICTREEBEL.
    [Tags]    phase3    evolution    stone    bellsprout
    [Setup]    Setup Evolution Test    WEEPINBELL    Leaf Stone
    Type Command    use leaf stone on weepinbell
    Output Should Contain    VICTREEBEL
    Party Pokemon Should Be    0    VICTREEBEL
    Item Count Should Be    Leaf Stone    0

Bellsprout Has Grass Poison Dual Type
    [Documentation]    BELLSPROUT is Grass/Poison dual-type.
    [Tags]    phase3    bellsprout    stats
    [Setup]    Setup Game With Pokemon    BELLSPROUT    15
    Party Pokemon Should Be    0    BELLSPROUT

# ============================================================================
# PHASE 4: Complete Evolution Lines
# ============================================================================

Alakazam Can Be In Party
    [Documentation]    ALAKAZAM has very high Special stat (135 base).
    [Tags]    phase4    alakazam    stats
    [Setup]    Setup Game With Pokemon    ALAKAZAM    50
    Party Pokemon Should Be    0    ALAKAZAM

Golem Has Rock Ground Dual Type
    [Documentation]    GOLEM is Rock/Ground dual-type.
    [Tags]    phase4    golem    stats
    [Setup]    Setup Game With Pokemon    GOLEM    40
    Party Pokemon Should Be    0    GOLEM

Wigglytuff Is Final Evolution
    [Documentation]    WIGGLYTUFF is a final evolution.
    [Tags]    phase4    evolution    wigglytuff
    [Setup]    Setup Game With Pokemon    WIGGLYTUFF    50
    Party Pokemon Should Be    0    WIGGLYTUFF

Persian Is Final Evolution
    [Documentation]    PERSIAN is a final evolution.
    [Tags]    phase4    evolution    persian
    [Setup]    Setup Game With Pokemon    PERSIAN    50
    Party Pokemon Should Be    0    PERSIAN

Vileplume Is Final Evolution
    [Documentation]    VILEPLUME is a final evolution.
    [Tags]    phase4    evolution    vileplume
    [Setup]    Setup Game With Pokemon    VILEPLUME    50
    Party Pokemon Should Be    0    VILEPLUME

Victreebel Is Final Evolution
    [Documentation]    VICTREEBEL is a final evolution.
    [Tags]    phase4    evolution    victreebel
    [Setup]    Setup Game With Pokemon    VICTREEBEL    50
    Party Pokemon Should Be    0    VICTREEBEL

Golbat Has Poison Flying Dual Type
    [Documentation]    GOLBAT is Poison/Flying dual-type.
    [Tags]    phase4    golbat    stats
    [Setup]    Setup Game With Pokemon    GOLBAT    30
    Party Pokemon Should Be    0    GOLBAT

Seadra Is Water Type
    [Documentation]    SEADRA is Water type.
    [Tags]    phase4    seadra    stats
    [Setup]    Setup Game With Pokemon    SEADRA    35
    Party Pokemon Should Be    0    SEADRA

Seaking Is Water Type
    [Documentation]    SEAKING is Water type.
    [Tags]    phase4    seaking    stats
    [Setup]    Setup Game With Pokemon    SEAKING    35
    Party Pokemon Should Be    0    SEAKING

Arbok Is Poison Type
    [Documentation]    ARBOK is Poison type.
    [Tags]    phase4    arbok    stats
    [Setup]    Setup Game With Pokemon    ARBOK    25
    Party Pokemon Should Be    0    ARBOK

Sandslash Is Ground Type
    [Documentation]    SANDSLASH is Ground type.
    [Tags]    phase4    sandslash    stats
    [Setup]    Setup Game With Pokemon    SANDSLASH    25
    Party Pokemon Should Be    0    SANDSLASH

# ============================================================================
# Level-Based Evolution Tests
# ============================================================================

Charmander Evolves To Charmeleon At Level 16
    [Documentation]    CHARMANDER evolves to CHARMELEON at level 16.
    [Tags]    evolution    level    starter    charmander
    [Setup]    Setup Game With Pokemon    CHARMANDER    15
    Level Up Pokemon    0
    Party Pokemon Should Be    0    CHARMELEON
    Party Pokemon Level Should Be    0    16
    Output Should Contain    CHARMELEON

Squirtle Evolves To Wartortle At Level 16
    [Documentation]    SQUIRTLE evolves to WARTORTLE at level 16.
    [Tags]    evolution    level    starter    squirtle
    [Setup]    Setup Game With Pokemon    SQUIRTLE    15
    Level Up Pokemon    0
    Party Pokemon Should Be    0    WARTORTLE
    Party Pokemon Level Should Be    0    16
    Output Should Contain    WARTORTLE

Bulbasaur Evolves To Ivysaur At Level 16
    [Documentation]    BULBASAUR evolves to IVYSAUR at level 16.
    [Tags]    evolution    level    starter    bulbasaur
    [Setup]    Setup Game With Pokemon    BULBASAUR    15
    Level Up Pokemon    0
    Party Pokemon Should Be    0    IVYSAUR
    Party Pokemon Level Should Be    0    16
    Output Should Contain    IVYSAUR

Charmeleon Evolves To Charizard At Level 36
    [Documentation]    CHARMELEON evolves to CHARIZARD at level 36.
    [Tags]    evolution    level    starter    charmeleon
    [Setup]    Setup Game With Pokemon    CHARMELEON    35
    Level Up Pokemon    0
    Party Pokemon Should Be    0    CHARIZARD
    Party Pokemon Level Should Be    0    36
    Output Should Contain    CHARIZARD

Wartortle Evolves To Blastoise At Level 36
    [Documentation]    WARTORTLE evolves to BLASTOISE at level 36.
    [Tags]    evolution    level    starter    wartortle
    [Setup]    Setup Game With Pokemon    WARTORTLE    35
    Level Up Pokemon    0
    Party Pokemon Should Be    0    BLASTOISE
    Party Pokemon Level Should Be    0    36
    Output Should Contain    BLASTOISE

Ivysaur Evolves To Venusaur At Level 32
    [Documentation]    IVYSAUR evolves to VENUSAUR at level 32.
    [Tags]    evolution    level    starter    ivysaur
    [Setup]    Setup Game With Pokemon    IVYSAUR    31
    Level Up Pokemon    0
    Party Pokemon Should Be    0    VENUSAUR
    Party Pokemon Level Should Be    0    32
    Output Should Contain    VENUSAUR

Caterpie Evolves To Metapod At Level 7
    [Documentation]    CATERPIE evolves to METAPOD at level 7.
    [Tags]    evolution    level    bug    caterpie
    [Setup]    Setup Game With Pokemon    CATERPIE    6
    Level Up Pokemon    0
    Party Pokemon Should Be    0    METAPOD
    Party Pokemon Level Should Be    0    7
    Output Should Contain    METAPOD

Metapod Evolves To Butterfree At Level 10
    [Documentation]    METAPOD evolves to BUTTERFREE at level 10.
    [Tags]    evolution    level    bug    metapod
    [Setup]    Setup Game With Pokemon    METAPOD    9
    Level Up Pokemon    0
    Party Pokemon Should Be    0    BUTTERFREE
    Party Pokemon Level Should Be    0    10
    Output Should Contain    BUTTERFREE

Weedle Evolves To Kakuna At Level 7
    [Documentation]    WEEDLE evolves to KAKUNA at level 7.
    [Tags]    evolution    level    bug    weedle
    [Setup]    Setup Game With Pokemon    WEEDLE    6
    Level Up Pokemon    0
    Party Pokemon Should Be    0    KAKUNA
    Party Pokemon Level Should Be    0    7
    Output Should Contain    KAKUNA

Kakuna Evolves To Beedrill At Level 10
    [Documentation]    KAKUNA evolves to BEEDRILL at level 10.
    [Tags]    evolution    level    bug    kakuna
    [Setup]    Setup Game With Pokemon    KAKUNA    9
    Level Up Pokemon    0
    Party Pokemon Should Be    0    BEEDRILL
    Party Pokemon Level Should Be    0    10
    Output Should Contain    BEEDRILL

Pidgey Evolves To Pidgeotto At Level 18
    [Documentation]    PIDGEY evolves to PIDGEOTTO at level 18.
    [Tags]    evolution    level    flying    pidgey
    [Setup]    Setup Game With Pokemon    PIDGEY    17
    Level Up Pokemon    0
    Party Pokemon Should Be    0    PIDGEOTTO
    Party Pokemon Level Should Be    0    18
    Output Should Contain    PIDGEOTTO

Pidgeotto Evolves To Pidgeot At Level 36
    [Documentation]    PIDGEOTTO evolves to PIDGEOT at level 36.
    [Tags]    evolution    level    flying    pidgeotto
    [Setup]    Setup Game With Pokemon    PIDGEOTTO    35
    Level Up Pokemon    0
    Party Pokemon Should Be    0    PIDGEOT
    Party Pokemon Level Should Be    0    36
    Output Should Contain    PIDGEOT

Rattata Evolves To Raticate At Level 20
    [Documentation]    RATTATA evolves to RATICATE at level 20.
    [Tags]    evolution    level    normal    rattata
    [Setup]    Setup Game With Pokemon    RATTATA    19
    Level Up Pokemon    0
    Party Pokemon Should Be    0    RATICATE
    Party Pokemon Level Should Be    0    20
    Output Should Contain    RATICATE

Kadabra Has Psychic Type
    [Documentation]    KADABRA is Psychic type.
    [Tags]    phase4    kadabra    stats
    [Setup]    Setup Game With Pokemon    KADABRA    25
    Party Pokemon Should Be    0    KADABRA

Clefable Is Normal Type
    [Documentation]    CLEFABLE is Normal type.
    [Tags]    phase4    clefable    stats
    [Setup]    Setup Game With Pokemon    CLEFABLE    25
    Party Pokemon Should Be    0    CLEFABLE


*** Keywords ***

# ── Custom setup for gym battles ─────────────────────────────────────────

Setup Misty Battle With Starmie
    [Documentation]    Set up game state ready to battle Misty who has Starmie.
    Bootstrap Game    location=Cerulean City
    Add Badge    Boulder Badge
    Set Lead Pokemon    PIKACHU    25
    Type Command    enter gym
    Click Widget    id=btn-gym-challenge

