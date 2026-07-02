"""
Configuration settings for the poker HUD.

Persistent state lives under a fixed data root in the user's home directory,
NOT inside the package, so the installed copy and a repo checkout always
resolve to the same data.

The data root holds handhistory/, agg_files/, and the app config.json
(username + ACR hand-history dir). `mbhud init` writes config.json and
performs the one-time migration of any legacy data. Nothing migrates at
import time.
"""

import json
from pathlib import Path

# Fixed data root. Everything mbHUD persists lives under here.
DATA_ROOT = Path.home() / ".mbHUD"

# Resolved paths. Symbol names are stable so consumers need no changes.
CONFIG_FILE = DATA_ROOT / "config.json"
DATA_DIR = DATA_ROOT / "data"
AGG_FILES_DIR = DATA_DIR / "agg_files"
BACKUP_HANDHISTORY_DIR = DATA_DIR / "handhistory"


def ensure_data_dirs() -> None:
    """Create the storage subdirectories under the current data root."""
    AGG_FILES_DIR.mkdir(parents=True, exist_ok=True)
    BACKUP_HANDHISTORY_DIR.mkdir(parents=True, exist_ok=True)


def is_initialized() -> bool:
    """True once `mbhud init` has written config."""
    return CONFIG_FILE.exists()


def load_config():
    """Load configuration from config.json."""
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(
            f"Config file not found: {CONFIG_FILE}\n"
            "Run 'mbhud init' to set up configuration."
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
            "Run 'mbhud init' to set up configuration."
        )

    return username


def get_hand_history_dir():
    """Get the ACR hand history directory from config."""
    config = load_config()
    hh_dir = config.get('hand_history_dir')

    if not hh_dir:
        raise ValueError(
            "Hand history directory not configured in config.json\n"
            "Run 'mbhud init' to set up configuration."
        )

    return Path(hh_dir)


# Load configuration on module import
try:
    USERNAME = get_username()
    ACR_HAND_HISTORY_DIR = get_hand_history_dir()  # ACR's download directory (for live view)
    HAND_HISTORY_DIR = BACKUP_HANDHISTORY_DIR  # Default to backup directory (for processing)
except (FileNotFoundError, ValueError) as e:
    # Allow import to succeed but config will be None
    # Scripts will fail with clear error message when they try to use it
    USERNAME = None
    ACR_HAND_HISTORY_DIR = None
    HAND_HISTORY_DIR = None
    _config_error = str(e)
