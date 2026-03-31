#!/usr/bin/env python
"""
Basic example: Launch the interactive Pokemon terminal.

This is the simplest way to run the game from Python.
Equivalent to running `poetry run python run_terminal.py`.
"""
from pytemon.terminal import launch_terminal


def main():
    """Launch the Pokemon terminal in interactive mode."""
    print("🎮 Starting Pokemon Terminal...")
    print("Type 'help' for available commands")
    print("Press 'q' or Ctrl+C to quit\n")

    # Launch the terminal - this blocks until the user quits
    launch_terminal()

    print("\n👋 Thanks for playing!")


if __name__ == "__main__":
    main()
