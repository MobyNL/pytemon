*** Settings ***
Documentation       Settings and autosave end-to-end tests.
...
...                 Covers the ``show settings``, ``enable autosave``,
...                 ``disable autosave``, and ``autosave <frequency>`` commands.

Library             PokemonLibraryTest
Resource            resources/common.resource

Suite Setup         Open Pokemon Terminal
Suite Teardown      Close Pokemon Terminal


*** Test Cases ***

# ----------------------------------------------------------------------------
# Settings display
# ----------------------------------------------------------------------------

Show Settings Displays Settings Header
    [Documentation]    'show settings' outputs a settings section header.
    [Tags]    settings    smoke
    [Setup]    Setup Game
    Type Command    show settings
    Output Should Contain    Settings    case_insensitive=True

Settings Alias Works Same As Show Settings
    [Documentation]    'settings' is an alias for 'show settings'.
    [Tags]    settings
    [Setup]    Setup Game
    Type Command    settings
    Output Should Contain    Settings    case_insensitive=True

Show Settings Mentions Autosave
    [Documentation]    The settings screen mentions the autosave configuration.
    [Tags]    settings
    [Setup]    Setup Game
    Type Command    show settings
    Output Should Contain    autosave    case_insensitive=True

# ----------------------------------------------------------------------------
# Enable / disable autosave
# ----------------------------------------------------------------------------

Enable Autosave Shows Confirmation
    [Documentation]    'enable autosave' outputs a confirmation message.
    [Tags]    settings    autosave
    [Setup]    Setup Game
    Type Command    enable autosave
    Output Should Contain    Autosave enabled    case_insensitive=True

Disable Autosave Shows Confirmation
    [Documentation]    'disable autosave' outputs a confirmation message.
    [Tags]    settings    autosave
    [Setup]    Setup Game
    Type Command    disable autosave
    Output Should Contain    Autosave disabled    case_insensitive=True

Enable Then Disable Autosave Works
    [Documentation]    Autosave can be toggled on and then off without error.
    [Tags]    settings    autosave
    [Setup]    Setup Game
    Type Command    enable autosave
    Output Should Contain    enabled    case_insensitive=True
    Type Command    disable autosave
    Output Should Contain    disabled    case_insensitive=True

# ----------------------------------------------------------------------------
# Autosave frequency
# ----------------------------------------------------------------------------

Set Autosave Frequency To Valid Value
    [Documentation]    'autosave 10' sets the autosave frequency to 10 commands.
    [Tags]    settings    autosave    frequency
    [Setup]    Setup Game
    Type Command    autosave 10
    Output Should Contain    10    case_insensitive=True

Set Autosave Frequency Out Of Range Shows Error
    [Documentation]    A frequency outside 5–100 should produce an error.
    [Tags]    settings    autosave    frequency    error
    [Setup]    Setup Game
    Type Command    autosave 3
    Output Should Contain    must be between    case_insensitive=True

# ----------------------------------------------------------------------------
# Misc info commands
# ----------------------------------------------------------------------------

Hello Command Shows Greeting
    [Documentation]    The 'hello' easter-egg command shows a greeting.
    [Tags]    settings    misc
    [Setup]    Setup Game
    Type Command    hello
    Output Should Contain    Hello    case_insensitive=True

About Command Shows Version Info
    [Documentation]    'about' outputs version and project information.
    [Tags]    settings    misc
    [Setup]    Setup Game
    Type Command    about
    Output Should Contain    Robot Framework    case_insensitive=True

Adventure Stats Shows Statistics
    [Documentation]    'stats' shows adventure statistics.
    [Tags]    settings    stats
    [Setup]    Setup Game
    Type Command    stats
    Output Should Contain    stats    case_insensitive=True
