#!/usr/bin/env python3
"""Dancing Bot - ASCII terminal bot that dances to the beat."""

import argparse
import signal
import sys
import threading
import time

from animator import Animator


def run_demo_mode(animator: Animator, stop_event: threading.Event):
    """Run demo mode with simulated beats at regular intervals."""
    beat_interval = 0.5  # 120 BPM

    while not stop_event.is_set():
        animator.trigger_bob()
        # Wait for next beat, but wake up early if stop_event is set
        if stop_event.wait(beat_interval):
            break


def run_live_mode(animator: Animator, stop_event: threading.Event):
    """Run live mode with microphone beat detection."""
    from beat_detector import BeatDetector

    detector = BeatDetector(callback=animator.trigger_bob)

    try:
        detector.start()
        # Wait for stop signal
        while not stop_event.is_set():
            time.sleep(0.1)
    finally:
        detector.stop()


def main():
    parser = argparse.ArgumentParser(
        description="Dancing Bot - ASCII bot that dances to the beat"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with simulated beats (no microphone needed)",
    )
    args = parser.parse_args()

    # Create animator
    animator = Animator(fps=30)

    # Event to signal shutdown
    stop_event = threading.Event()

    # Handle Ctrl+C gracefully
    def signal_handler(sig, _frame):
        stop_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, "SIGTERM"):
        signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Hide cursor
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()
        # Start beat source in background thread
        if args.demo:
            beat_thread = threading.Thread(
                target=run_demo_mode, args=(animator, stop_event)
            )
        else:
            beat_thread = threading.Thread(
                target=run_live_mode, args=(animator, stop_event)
            )

        beat_thread.start()

        # Run animator in main thread
        animator.run(stop_event)

        # Wait for beat thread to finish
        beat_thread.join()

    finally:
        animator.cleanup()
        print("Goodbye!")


if __name__ == "__main__":
    main()
