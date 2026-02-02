"""Tests for the dancing bot."""

import threading
import unittest
from unittest.mock import MagicMock, patch

from bot import FRAMES
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

    def test_up_and_down_frames_exist(self):
        """Up and down frames should exist for beat animation."""
        self.assertIn("up", FRAMES)
        self.assertIn("down", FRAMES)


class TestAnimator(unittest.TestCase):
    """Tests for animator.py."""

    def test_initial_state(self):
        """Animator should start in neutral state."""
        animator = Animator(fps=30)
        self.assertEqual(animator.current_frame, "neutral")
        self.assertFalse(animator._pose_toggle)

    def test_trigger_bob_toggles_pose(self):
        """Triggering bob should toggle between up and down."""
        animator = Animator(fps=30)
        animator._draw = MagicMock()

        animator.trigger_bob()
        self.assertEqual(animator.current_frame, "up")

        animator.trigger_bob()
        self.assertEqual(animator.current_frame, "down")

        animator.trigger_bob()
        self.assertEqual(animator.current_frame, "up")

    def test_frame_rate(self):
        """Animator should respect FPS setting."""
        animator = Animator(fps=10)
        self.assertEqual(animator.frame_duration, 0.1)

    def test_thread_safety(self):
        """Trigger bob should be thread-safe."""
        animator = Animator(fps=30)
        animator._draw = MagicMock()
        exceptions = []

        def trigger_many():
            try:
                for _ in range(100):
                    animator.trigger_bob()
                    # Verify frame is always in valid state
                    with animator.lock:
                        if animator.current_frame not in FRAMES:
                            raise ValueError(f"Invalid frame: {animator.current_frame}")
            except Exception as e:
                exceptions.append(e)

        threads = [threading.Thread(target=trigger_many) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Should not raise any exceptions
        self.assertEqual(exceptions, [])
        # Current frame should be valid
        self.assertIn(animator.current_frame, FRAMES)


class TestBeatDetector(unittest.TestCase):
    """Tests for beat_detector.py."""

    @patch("beat_detector.sd")
    @patch("beat_detector.librosa")
    def test_initialization(self, mock_librosa, mock_sd):
        """BeatDetector should initialize with callback."""
        from beat_detector import BeatDetector

        callback = MagicMock()
        detector = BeatDetector(callback=callback)

        self.assertEqual(detector.callback, callback)
        self.assertEqual(detector.sample_rate, 44100)
        self.assertEqual(detector.hop_size, 512)

    @patch("beat_detector.sd")
    @patch("beat_detector.librosa")
    def test_start_creates_stream(self, mock_librosa, mock_sd):
        """Start should create and start audio stream."""
        from beat_detector import BeatDetector

        callback = MagicMock()
        detector = BeatDetector(callback=callback)
        detector.start()

        mock_sd.InputStream.assert_called_once()
        mock_sd.InputStream.return_value.start.assert_called_once()

    @patch("beat_detector.sd")
    @patch("beat_detector.librosa")
    def test_stop_closes_stream(self, mock_librosa, mock_sd):
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
