# Application Configuration

# Window Settings
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 700
MIN_WINDOW_WIDTH = 1000
MIN_WINDOW_HEIGHT = 600

# Colors - Modern Theme
PRIMARY_COLOR = "#1f538d"
SECONDARY_COLOR = "#14b8a6"
BACKGROUND_COLOR = "#f8fafc"
DARK_BACKGROUND = "#1e293b"
TEXT_COLOR = "#0f172a"
TEXT_LIGHT = "#64748b"
SUCCESS_COLOR = "#22c55e"
ERROR_COLOR = "#ef4444"
WARNING_COLOR = "#f59e0b"

# Dark Mode Colors
DARK_PRIMARY = "#3b82f6"
DARK_SECONDARY = "#14b8a6"
DARK_TEXT = "#f1f5f9"
DARK_CARD_BG = "#334155"

# Font Settings
FONT_FAMILY = "Segoe UI"
FONT_SIZE_LARGE = 24
FONT_SIZE_MEDIUM = 16
FONT_SIZE_SMALL = 12
FONT_SIZE_TITLE = 32

# Animation Settings
ANIMATION_SPEED = 0.5  # seconds per letter
TRANSITION_DURATION = 0.3  # seconds

# Database Settings
DATABASE_PATH = "database/app.db"

# Assets Paths
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SIGN_IMAGES_PATH = os.path.join(BASE_DIR, "assets", "sign_images")

# Speech Recognition Settings
SPEECH_TIMEOUT = 5
SPEECH_PHRASE_LIMIT = 15

# History Settings
MAX_HISTORY_ITEMS = 100
HISTORY_PER_PAGE = 20