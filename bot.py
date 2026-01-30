"""ASCII art frames for the dancing bot."""

# Neutral pose - relaxed standing position
NEUTRAL = r"""
   ◕ ◕
  ( ● )
   /|\
   / \
"""

# Bob up - squished/compressed (like bouncing up)
BOB_UP = r"""
   ◕ ◕
 (( ● ))
   \|/
   ___
"""

# Bob down - stretched/extended (like bouncing down)
BOB_DOWN = r"""
   ◕ ◕
  ( ● )
   /|\
  /| |\
"""

# All frames in order for easy access
FRAMES = {
    "neutral": NEUTRAL,
    "up": BOB_UP,
    "down": BOB_DOWN,
}

# Animation sequence for a single bob
BOB_SEQUENCE = ["up", "down", "neutral"]
