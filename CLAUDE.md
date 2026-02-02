# Dancing Bot

ASCII terminal bot that dances to music beats.

## Quick Start

```bash
source venv/bin/activate
python main.py --demo    # Demo mode (no mic)
python main.py           # Live mode (mic input)
```

## Architecture

```
Microphone → BeatDetector (spectral flux) → Animator → Terminal
```

- `bot.py`: ASCII art frames (neutral, bob up, bob down)
- `animator.py`: Terminal rendering at 30 FPS, animation state
- `beat_detector.py`: Audio capture via sounddevice, onset detection via spectral flux
- `main.py`: Entry point, threading, signal handling

## Before Committing

```bash
ruff format *.py        # Format code
ruff check *.py         # Lint code
python -m pytest -v              # Run tests
```

## Key Details

- Beat detection uses spectral flux with threshold 0.3
- Animation runs in main thread, beat source in background thread
- Demo mode simulates beats at 120 BPM (0.5s interval)
- Uses ANSI escape codes for terminal control
