"""
Text content package for Pokemon Terminal Game.

All user-visible strings live under texts/en/ (one module per source module).
Import them like:

    from .texts.en import cheat_commands as T
    write_lines(output, T.CHEAT_ACTIVATED)

For dynamic lines use write_dynamic_lines() with a dict, or write_lines_fmt()
with keyword arguments, and {placeholder} format strings in the constants.
"""
