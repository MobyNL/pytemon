"""
English locale package.

Each module mirrors its source counterpart:

    texts/en/cheat_commands.py  ← pytemon/cheat_commands.py
    texts/en/buildings.py       ← pytemon/buildings.py
    texts/en/pokedex.py         ← pytemon/pokedex.py
    texts/en/exploration.py     ← pytemon/exploration.py
    texts/en/gym_system.py      ← pytemon/gym_system.py
    texts/en/evolution.py       ← pytemon/evolution.py
    texts/en/pc_system.py       ← pytemon/pc_system.py
    texts/en/fishing.py         ← pytemon/fishing.py
    texts/en/items.py           ← pytemon/items.py
    texts/en/displays.py        ← pytemon/ui/displays.py
    texts/en/menus.py           ← pytemon/ui/menus.py
    texts/en/battle_ui.py       ← pytemon/battle/battle_ui.py

Each constant is a list[str] that can be passed directly to write_lines().
Lines containing {placeholders} are used with write_dynamic_lines(data_dict)
or write_lines_fmt(**kwargs).
"""
