"""
Configuration settings for the poker HUD.
"""

from pathlib import Path

# ACR username for hand history processing
USERNAME = "aampersands"

# Data directory for storing processed files
# This keeps our generated files separate from ACR's download directory
DATA_DIR = Path(__file__).parent.parent / "data"
AGG_FILES_DIR = DATA_DIR / "agg_files"

# Ensure directories exist
AGG_FILES_DIR.mkdir(parents=True, exist_ok=True)
