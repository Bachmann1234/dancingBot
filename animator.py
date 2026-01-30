"""Terminal rendering and animation state management."""

import sys
import time
import threading
from bot import FRAMES, BOB_SEQUENCE


class Animator:
    """Handles terminal rendering and animation state."""

    def __init__(self, fps: int = 30):
        self.fps = fps
        self.frame_duration = 1.0 / fps
        self.current_frame = "neutral"
        self.animation_queue = []
        self.lock = threading.Lock()
        self.running = False
        self._last_frame_content = None

    def trigger_bob(self):
        """Trigger a bob animation sequence."""
        with self.lock:
            # Add bob sequence to queue (replaces any pending animation)
            self.animation_queue = list(BOB_SEQUENCE)

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
            if self.animation_queue:
                self.current_frame = self.animation_queue.pop(0)
            else:
                self.current_frame = "neutral"

        self._draw()

    def _draw(self):
        """Draw the current frame."""
        self._clear_and_draw(self.current_frame)

    def run(self, stop_event: threading.Event):
        """Main animation loop."""
        self.running = True

        # Initial draw
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
