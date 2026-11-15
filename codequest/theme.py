"""Colors shared by every screen."""
from kivy.utils import get_color_from_hex as hx

BG = hx('#0e1128')
PANEL = hx('#1a1f45')
PANEL2 = hx('#262d63')
CODE_BG = hx('#0a0d20')
TEXT = hx('#f4f6ff')
MUTED = hx('#9aa3d6')
GOOD = hx('#34d399')
BAD = hx('#fb7185')
GOLD = hx('#fbbf24')
ACCENT = hx('#7c5cff')
DIM = hx('#3a4180')

TRACK_COLOR = {
    'ds': hx('#2dd4bf'),     # teal
    'py': hx('#fbbf24'),     # amber
    'c': hx('#818cf8'),      # periwinkle
    'daily': hx('#fb7185'),  # coral
}

DIFF_COLOR = {1: hx('#34d399'), 2: hx('#fbbf24'), 3: hx('#fb7185')}

FONT_MONO = None  # filled in by widgets.py once Kivy has located its fonts
