*** Settings ***
Documentation       Badge-case and gym-related end-to-end tests.
...
...                 Covers the ``show badges`` command, badge display logic,
...                 and gym entry checks.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Badge case display
# ----------------------------------------------------------------------------

Show Badges Displays Badge Section Header
    [Documentation]    'show badges' renders a badge-case header in the output.
    [Tags]    badges    smoke
    [Setup]    Setup Game
    Type Command    show badges
    Output Should Contain    Badge    case_insensitive=True

Show Badges With No Badges Shows Zero Count
    [Documentation]    A newly bootstrapped game has no badges; the display reflects this.
    [Tags]    badges
    [Setup]    Setup Game
    Badge Count Should Be    0
    Type Command    show badges
    Output Should Contain    No badges    case_insensitive=True

Show Badges After Earning Boulder Badge Lists It
    [Documentation]    Adding the Boulder Badge causes 'show badges' to mention it.
    [Tags]    badges
    [Setup]    Setup Game With Badges    Boulder Badge
    Type Command    show badges
    Output Should Contain    Boulder Badge

Show Badges After Two Badges Lists Both
    [Documentation]    Adding two badges causes both to appear in the badge case.
    [Tags]    badges
    [Setup]    Setup Game With Badges    Boulder Badge    Cascade Badge
    Type Command    show badges
    Output Should Contain    Boulder Badge
    Output Should Contain    Cascade Badge

Badge Alias Works Same As Show Badges
    [Documentation]    The 'badge' alias is equivalent to 'show badges'.
    [Tags]    badges
    [Setup]    Setup Game With Badges    Boulder Badge
    Type Command    badge
    Output Should Contain    Boulder Badge

Status Shows Badge Count After Earning Badges
    [Documentation]    After earning a badge, 'status' shows the updated badge count.
    [Tags]    badges    status
    [Setup]    Setup Game With Badges    Boulder Badge    Cascade Badge
    Type Command    status
    Output Should Contain    2/8

# ----------------------------------------------------------------------------
# Gym entry
# ----------------------------------------------------------------------------

Entering Gym In Town Without Badge Requirement Shows Gym
    [Documentation]    Entering the Gym in Pewter City (needs 0 badges) should show the gym.
    [Tags]    badges    gym
    [Setup]    Setup Game At Location    Pewter City
    Type Command    enter gym
    Output Should Contain    PEWTER CITY GYM    case_insensitive=True

Entering Gym In Town With Badge Shows Already Earned
    [Documentation]    Entering a gym after already earning its badge shows a congratulatory note.
    [Tags]    badges    gym
    [Setup]    Setup Game At Location    Pewter City
    Add Badge    Boulder Badge
    Type Command    enter gym
    Output Should Contain    Boulder Badge
