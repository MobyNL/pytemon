#!/usr/bin/env python
"""
Direct launcher for the pytemon Pokemon Terminal.

Usage:
    poetry run python run_terminal.py

Or from the pytemon/ subdirectory:
    poetry run python run_terminal.py
"""
from pytemon.terminal import launch_terminal


def main():
    """Main entry point."""
    print("🎮 Launching Pokemon Terminal...")
    print()
    print("TIPS:")
    print("  • Type 'help' to see available commands")
    print("  • Press 'q' or Ctrl+C to quit")
    print("  • Use a native terminal (not VS Code) for best experience")
    print()
    launch_terminal()


if __name__ == "__main__":
    main()
