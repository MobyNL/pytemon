"""
Text animation utilities for Pokemon Terminal.

Provides functions to display text with animation effects like typewriter.
"""

from typing import Callable, List, Optional

from textual.widgets import RichLog


class AnimatedTextWriter:
    """Helper class to manage animated text writing."""

    def __init__(self, app):
        """
        Initialize the text writer.

        Args:
            app: The Textual app instance (needed for set_interval)
        """
        self.app = app
        self.current_timer = None
        self.last_delay: float = 0.0

    def write_lines_with_delay(
        self,
        output: RichLog,
        lines: List[str],
        delay: float = 0.4,
        on_complete: Optional[Callable] = None,
    ):
        """
        Write multiple lines with a delay between each line.

        Perfect for dialogue, battle narration, etc.

        Args:
            output: The RichLog widget to write to
            lines: List of text lines (can include Rich markup)
            delay: Seconds between lines (0.2=fast, 0.4=medium, 0.8=slow)
            on_complete: Optional callback to run when animation completes
        """
        self.last_delay = delay

        if self.current_timer:
            self.current_timer.stop()

        lines_copy = lines.copy()

        def write_next_line():
            if lines_copy:
                line = lines_copy.pop(0)
                output.write(line)
            else:
                if self.current_timer:
                    self.current_timer.stop()
                    self.current_timer = None
                if on_complete:
                    on_complete()

        # Write first line immediately
        if lines_copy:
            output.write(lines_copy.pop(0))

        # Set timer for remaining lines
        if lines_copy:
            self.current_timer = self.app.set_interval(delay, write_next_line)

    def write_fast(self, output: RichLog, lines: List[str], on_complete: Optional[Callable] = None):
        """Write lines with fast animation (0.2s delay)."""
        self.write_lines_with_delay(output, lines, delay=0.2, on_complete=on_complete)

    def write_medium(
        self, output: RichLog, lines: List[str], on_complete: Optional[Callable] = None
    ):
        """Write lines with medium animation (0.3s delay)."""
        self.write_lines_with_delay(output, lines, delay=0.3, on_complete=on_complete)

    def write_slow(self, output: RichLog, lines: List[str], on_complete: Optional[Callable] = None):
        """Write lines with slow animation (0.5s delay)."""
        self.write_lines_with_delay(output, lines, delay=0.5, on_complete=on_complete)

    def write_instant(self, output: RichLog, lines: List[str]):
        """Write all lines immediately (no animation)."""
        for line in lines:
            output.write(line)

    def cancel(self):
        """Cancel any ongoing animation."""
        if self.current_timer:
            self.current_timer.stop()
            self.current_timer = None
