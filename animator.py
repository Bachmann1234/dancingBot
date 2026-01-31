"""Terminal rendering and animation state management."""

import sys
import time
import threading
from bot import FRAMES


class Animator:
    """Handles terminal rendering and animation state."""

    def __init__(self, fps: int = 30):
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.current_frame = "neutral"
        self.lock = threading.Lock()
        self.running = False
        self._last_frame_content = None
        self._pose_toggle = False  # Alternates between up/down on each beat

    def trigger_bob(self):
        """Trigger a pose change on beat."""
        with self.lock:
            # Simply toggle between up and down poses
            self._pose_toggle = not self._pose_toggle
            self.current_frame = "up" if self._pose_toggle else "down"
            self._draw()

    def _clear_and_draw(self, frame_name: str):
        """Clear terminal and draw the specified frame."""
        frame_content = FRAMES[frame_name]

        # Only redraw if frame changed
        if frame_content == self._last_frame_content:
            return

        self._last_frame_content = frame_content

        # Move cursor to home position and clear screen
        sys.stdout.write("\033[H\033[J")
        sys.stdout.write(frame_content)
        sys.stdout.write("\n[Press Ctrl+C to exit]\n")
        sys.stdout.flush()

    def _update(self):
        """Update animation state and render."""
        with self.lock:
            self._draw()

    def _draw(self):
        """Draw the current frame. Must be called with lock held."""
        self._clear_and_draw(self.current_frame)

    def run(self, stop_event: threading.Event):
        """Main animation loop."""
        self.running = True

        # Initial draw
        with self.lock:
            self._draw()

        while not stop_event.is_set():
            frame_start = time.time()

            self._update()

            # Maintain consistent frame rate
            elapsed = time.time() - frame_start
            sleep_time = self.frame_duration - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)

        self.running = False

    def cleanup(self):
        """Clean up terminal state."""
        # Show cursor and reset terminal
        sys.stdout.write("\033[?25h")  # Show cursor
        sys.stdout.write("\n")
        sys.stdout.flush()
