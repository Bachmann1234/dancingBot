"""Tests for the dancing bot."""

import threading
import unittest
from unittest.mock import MagicMock, patch

from bot import FRAMES, BOB_SEQUENCE
from animator import Animator


class TestBot(unittest.TestCase):
    """Tests for bot.py ASCII frames."""

    def test_frames_exist(self):
        """All required frames should exist."""
        self.assertIn("neutral", FRAMES)
        self.assertIn("up", FRAMES)
        self.assertIn("down", FRAMES)

    def test_frames_are_strings(self):
        """All frames should be non-empty strings."""
        for name, frame in FRAMES.items():
            self.assertIsInstance(frame, str, f"Frame '{name}' should be a string")
            self.assertTrue(len(frame) > 0, f"Frame '{name}' should not be empty")

    def test_bob_sequence(self):
        """Bob sequence should contain valid frame names."""
        for frame_name in BOB_SEQUENCE:
            self.assertIn(frame_name, FRAMES, f"'{frame_name}' should be a valid frame")


class TestAnimator(unittest.TestCase):
    """Tests for animator.py."""

    def test_initial_state(self):
        """Animator should start in neutral state."""
        animator = Animator(fps=30)
        self.assertEqual(animator.current_frame, "neutral")
        self.assertEqual(animator.animation_queue, [])

    def test_trigger_bob_queues_animation(self):
        """Triggering bob should queue the animation sequence."""
        animator = Animator(fps=30)
        animator.trigger_bob()
        self.assertEqual(animator.animation_queue, list(BOB_SEQUENCE))

    def test_trigger_bob_replaces_queue(self):
        """New bob trigger should replace pending animation."""
        animator = Animator(fps=30)
        animator.animation_queue = ["up"]  # Partial animation in progress
        animator.trigger_bob()
        self.assertEqual(animator.animation_queue, list(BOB_SEQUENCE))

    def test_update_consumes_queue(self):
        """Update should consume animation queue."""
        animator = Animator(fps=30)
        animator._last_frame_content = FRAMES["neutral"]  # Prevent actual drawing

        animator.trigger_bob()
        initial_len = len(animator.animation_queue)

        # Mock _draw to prevent terminal output
        animator._draw = MagicMock()
        animator._update()

        self.assertEqual(len(animator.animation_queue), initial_len - 1)

    def test_update_returns_to_neutral(self):
        """After queue is empty, should return to neutral."""
        animator = Animator(fps=30)
        animator._draw = MagicMock()
        animator.animation_queue = []

        animator._update()

        self.assertEqual(animator.current_frame, "neutral")

    def test_frame_rate(self):
        """Animator should respect FPS setting."""
        animator = Animator(fps=10)
        self.assertEqual(animator.frame_duration, 0.1)

    def test_thread_safety(self):
        """Trigger bob should be thread-safe."""
        animator = Animator(fps=30)

        def trigger_many():
            for _ in range(100):
                animator.trigger_bob()

        threads = [threading.Thread(target=trigger_many) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should not raise any exceptions and queue should be valid
        self.assertEqual(animator.animation_queue, list(BOB_SEQUENCE))


class TestBeatDetector(unittest.TestCase):
    """Tests for beat_detector.py."""

    @patch("beat_detector.sd")
    @patch("beat_detector.aubio")
    def test_initialization(self, mock_aubio, mock_sd):
        """BeatDetector should initialize with callback."""
        from beat_detector import BeatDetector

        callback = MagicMock()
        detector = BeatDetector(callback=callback)

        self.assertEqual(detector.callback, callback)
        self.assertEqual(detector.sample_rate, 44100)
        self.assertEqual(detector.hop_size, 512)

    @patch("beat_detector.sd")
    @patch("beat_detector.aubio")
    def test_start_creates_stream(self, mock_aubio, mock_sd):
        """Start should create and start audio stream."""
        from beat_detector import BeatDetector

        callback = MagicMock()
        detector = BeatDetector(callback=callback)
        detector.start()

        mock_sd.InputStream.assert_called_once()
        mock_sd.InputStream.return_value.start.assert_called_once()

    @patch("beat_detector.sd")
    @patch("beat_detector.aubio")
    def test_stop_closes_stream(self, mock_aubio, mock_sd):
        """Stop should stop and close audio stream."""
        from beat_detector import BeatDetector

        callback = MagicMock()
        detector = BeatDetector(callback=callback)
        detector.start()
        detector.stop()

        mock_sd.InputStream.return_value.stop.assert_called_once()
        mock_sd.InputStream.return_value.close.assert_called_once()


if __name__ == "__main__":
    unittest.main()
