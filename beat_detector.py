"""Audio input and beat detection using sounddevice and aubio."""

import numpy as np
import sounddevice as sd
import aubio


class BeatDetector:
    """Detects beats from microphone input."""

    def __init__(self, callback, sample_rate: int = 44100, hop_size: int = 512):
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

        # Initialize aubio onset detector
        # 'default' method works well for general beat detection
        self.onset = aubio.onset(
            method="default",
            buf_size=hop_size * 2,
            hop_size=hop_size,
            samplerate=sample_rate,
        )

        # Adjust sensitivity (lower = more sensitive)
        self.onset.set_threshold(0.3)

        self.stream = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Process incoming audio data."""
        if status:
            # Audio overrun/underrun, skip this buffer
            return

        # Convert to mono float32 if needed
        audio = indata[:, 0].astype(np.float32)

        # Process in hop_size chunks
        for i in range(0, len(audio), self.hop_size):
            chunk = audio[i : i + self.hop_size]
            if len(chunk) == self.hop_size:
                # Check for onset/beat
                if self.onset(chunk):
                    self.callback()

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
