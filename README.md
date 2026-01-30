# Dancing Bot

An ASCII terminal bot that listens to music and dances to the beat, inspired by [Keepon](https://en.wikipedia.org/wiki/Keepon).

```
   ◕ ◕
  ( ● )
   /|\
   / \
```

## Requirements

- Python 3.12+
- PortAudio library (for microphone input)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt install python3.12-venv libportaudio2
```

**macOS:**
```bash
brew install portaudio
```

## Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Demo Mode (no microphone needed)

```bash
python main.py --demo
```

The bot will bob to simulated beats at 120 BPM.

### Live Mode (listens to music)

```bash
python main.py
```

Play music near your microphone and watch the bot dance to the beat!

Press `Ctrl+C` to exit.

## How It Works

1. **Microphone Input**: Captures audio using `sounddevice`
2. **Beat Detection**: Uses `aubio` for real-time onset detection
3. **Animation**: Renders ASCII frames to terminal at 30 FPS

## Project Structure

```
dancingBot/
├── main.py           # Entry point
├── bot.py            # ASCII art frames
├── animator.py       # Terminal rendering
├── beat_detector.py  # Audio input and beat detection
└── requirements.txt  # Python dependencies
```
