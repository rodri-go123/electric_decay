# Centralizes application paths, display settings, and timing configuration.
from pathlib import Path

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
FPS = 30
IDLE_TIMEOUT = 120
CONFIRMATION_TIMEOUT = 45
CONFIRMATION_ALERT_DURATION = 6
CONFIRMATION_ALERT_INTERVAL = 15
SWITCH_PIN = 4
REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
DIALOGUE_PATH = REPOSITORY_ROOT / "data" / "updated_dialogue.json"
MESSAGE_PATH = REPOSITORY_ROOT / "data" / "user_messages.json"
FONT_PATH = REPOSITORY_ROOT / "assets" / "PPMondwest-Regular.otf"
INSTRUCTION_FONT_PATH = REPOSITORY_ROOT / "assets" / "PPNeueBit-Bold.otf"
if not INSTRUCTION_FONT_PATH.exists():
	INSTRUCTION_FONT_PATH = FONT_PATH
