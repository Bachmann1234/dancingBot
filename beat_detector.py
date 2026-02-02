"""Audio input and beat detection using sounddevice and spectral flux."""

from typing import Callable

import numpy as np
import sounddevice as sd


class BeatDetector:
    """Detects beats from microphone input using spectral flux onset detection."""

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

        # Onset detection threshold for normalized spectral flux.
        # This is a heuristic default that may need tuning depending on
        # audio source and desired sensitivity.
        self.threshold = 0.3

        # Pre-compute Hann window for spectral analysis
        self.window = np.hanning(hop_size)

        # Previous spectrum magnitude for spectral flux calculation
        self.prev_spectrum = None

        # For peak detection: track recent flux values
        self.prev_flux = 0.0
        self.prev_prev_flux = 0.0

        self.stream = None

    def _compute_spectral_flux(self, audio_chunk: np.ndarray) -> float:
        """
        Compute spectral flux between current and previous frame.

        Spectral flux measures the change in spectrum magnitude between frames,
        which correlates with onsets/beats.
        """
        # Apply Hann window to reduce spectral leakage
        windowed = audio_chunk * self.window

        # Compute FFT magnitude spectrum
        spectrum = np.abs(np.fft.rfft(windowed))

        if self.prev_spectrum is None:
            self.prev_spectrum = spectrum
            return 0.0

        # Spectral flux: sum of positive differences (half-wave rectified)
        diff = spectrum - self.prev_spectrum
        flux = np.sum(np.maximum(0, diff))

        # Normalize by spectrum size
        flux = flux / len(spectrum)

        self.prev_spectrum = spectrum
        return flux

    def _audio_callback(self, indata, frames, _time_info, status):
        """Process incoming audio data."""
        if status:
            # Audio overrun/underrun, skip this buffer
            return

        # Convert to mono float32 and ensure 1D shape
        audio = indata.astype(np.float32).flatten()

        # Process in hop_size chunks
        for i in range(0, len(audio), self.hop_size):
            chunk = audio[i : i + self.hop_size]
            if len(chunk) == self.hop_size:
                try:
                    flux = self._compute_spectral_flux(chunk)

                    # Peak detection: previous flux must be a local maximum
                    # (greater than both neighbors) and above threshold
                    if (
                        self.prev_flux > self.threshold
                        and self.prev_flux > self.prev_prev_flux
                        and self.prev_flux >= flux
                    ):
                        self.callback()

                    # Shift flux history
                    self.prev_prev_flux = self.prev_flux
                    self.prev_flux = flux
                except (ValueError, IndexError):
                    # Reset state to avoid stale data on next iteration
                    self.prev_spectrum = None
                    self.prev_flux = 0.0
                    self.prev_prev_flux = 0.0

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
