"""Audio input and beat detection using sounddevice and librosa."""

from typing import Callable

import numpy as np
import sounddevice as sd
import librosa


class BeatDetector:
    """Detects beats from microphone input using onset detection."""

    def __init__(
        self,
        callback: Callable[[], None],
        sample_rate: int = 44100,
        hop_size: int = 512,
    ):
        """
        Initialize beat detector.

        Args:
            callback: Function to call when a beat is detected
            sample_rate: Audio sample rate in Hz
            hop_size: Number of samples between successive analysis frames
        """
        self.callback = callback
        self.sample_rate = sample_rate
        self.hop_size = hop_size

        # Onset detection parameters
        self.threshold = 0.3
        self.prev_onset_strength = 0.0

        # Buffer for accumulating audio for onset analysis
        self.buffer_size = hop_size * 4
        self.audio_buffer = np.zeros(self.buffer_size, dtype=np.float32)

        self.stream = None

    def _audio_callback(self, indata, frames, _time_info, status):
        """Process incoming audio data."""
        if status:
            # Audio overrun/underrun, skip this buffer
            return

        # Convert to mono float32 and ensure 1D shape
        audio = indata.astype(np.float32).flatten()

        # Shift buffer and add new audio
        self.audio_buffer = np.roll(self.audio_buffer, -len(audio))
        self.audio_buffer[-len(audio) :] = audio

        # Compute onset strength using librosa
        try:
            onset_env = librosa.onset.onset_strength(
                y=self.audio_buffer,
                sr=self.sample_rate,
                hop_length=self.hop_size,
            )

            # Get the latest onset strength value
            if len(onset_env) > 0:
                current_strength = onset_env[-1]

                # Detect onset: current strength exceeds threshold and is a local peak
                if (
                    current_strength > self.threshold
                    and current_strength > self.prev_onset_strength
                ):
                    self.callback()

                self.prev_onset_strength = current_strength
        except Exception:
            # Don't let analysis errors crash the audio stream
            pass

    def start(self):
        """Start listening to microphone."""
        self.stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype=np.float32,
            blocksize=self.hop_size * 4,
            callback=self._audio_callback,
        )
        self.stream.start()

    def stop(self):
        """Stop listening to microphone."""
        if self.stream:
            self.stream.stop()
            self.stream.close()
            self.stream = None
