"""
Configuration settings for the poker HUD.

Reads settings from config.json in the project root.
"""

import json
from pathlib import Path

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_FILE = PROJECT_ROOT / "config.json"
DATA_DIR = PROJECT_ROOT / "data"
AGG_FILES_DIR = DATA_DIR / "agg_files"

# Ensure directories exist
AGG_FILES_DIR.mkdir(parents=True, exist_ok=True)


def load_config():
    """Load configuration from config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}\n"
            "Run 'python3 mbhud_init.py' to set up configuration."
        )

    with open(CONFIG_FILE, 'r') as f:
        return json.load(f)


def get_username():
    """Get the ACR username from config."""
    config = load_config()
    username = config.get('username')

    if not username:
        raise ValueError(
            "Username not configured in config.json\n"
            "Run 'python3 mbhud_init.py' to set up configuration."
        )

    return username


def get_hand_history_dir():
    """Get the hand history directory from config."""
    config = load_config()
    hh_dir = config.get('hand_history_dir')

    if not hh_dir:
        raise ValueError(
            "Hand history directory not configured in config.json\n"
            "Run 'python3 mbhud_init.py' to set up configuration."
        )

    return Path(hh_dir)


# Load configuration on module import
try:
    USERNAME = get_username()
    HAND_HISTORY_DIR = get_hand_history_dir()
except (FileNotFoundError, ValueError) as e:
    # Allow import to succeed but config will be None
    # Scripts will fail with clear error message when they try to use it
    USERNAME = None
    HAND_HISTORY_DIR = None
    _config_error = str(e)
