#!/usr/bin/env python3
"""
mbHUD Initialization Script

First-time setup for new users.
"""

import json
import sys
from pathlib import Path


def get_default_hand_history_dir(username):
    """Get platform-specific default hand history directory."""
    if sys.platform == 'darwin':  # Mac
        return Path.home() / "Downloads" / "AmericasCardroom" / "handHistory" / username
    elif sys.platform == 'win32':  # Windows
        return Path("C:/ACR Poker/handHistory") / username
    else:  # Linux (assume similar to Mac)
        return Path.home() / "Downloads" / "AmericasCardroom" / "handHistory" / username


def main():
    print("=" * 80)
    print("mbHUD - First Time Setup")
    print("=" * 80)
    print()

    # Step 1: Get username
    print("Step 1: Configure ACR Username")
    print("-" * 80)
    username = input("Enter your Americas Cardroom username: ").strip()

    if not username:
        print("Error: Username cannot be empty")
        sys.exit(1)

    # Step 2: Get hand history directory
    print("\nStep 2: Configure Hand History Directory")
    print("-" * 80)

    default_dir = get_default_hand_history_dir(username)
    print(f"Default location: {default_dir}")
    print()

    custom_path = input("Enter hand history directory path (or press Enter for default): ").strip()

    if custom_path:
        hh_dir = Path(custom_path)
    else:
        hh_dir = default_dir

    # Verify directory exists
    if hh_dir.exists():
        print(f"✓ Directory found: {hh_dir}")
        txt_files = list(hh_dir.glob("*.txt"))
        print(f"✓ Found {len(txt_files)} hand history files")
    else:
        print(f"⚠ Directory not found: {hh_dir}")
        print("\nMake sure:")
        print("  1. ACR client is installed")
        print("  2. Hand history saving is enabled in ACR settings")
        print("  3. You've played at least one hand")
        print("\nContinuing setup anyway. You can fix this later.")
        txt_files = []

    # Step 3: Update config.json
    print("\nStep 3: Saving configuration...")
    # Use poker_hud.config to get correct paths
    from poker_hud.config import CONFIG_FILE, AGG_FILES_DIR

    config_data = {
        "username": username,
        "hand_history_dir": str(hh_dir)
    }

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)

        print(f"✓ Username: {username}")
        print(f"✓ Hand history directory: {hh_dir}")
        print(f"✓ Config saved to: {CONFIG_FILE}")

    except Exception as e:
        print(f"Error saving config: {e}")
        sys.exit(1)

    # Step 4: Create data directories
    print("\nStep 4: Creating data directories...")
    AGG_FILES_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Created: {AGG_FILES_DIR}")

    # Step 5: Initial flush
    print("\nStep 5: Processing existing hand histories...")
    print("-" * 80)

    if hh_dir.exists() and txt_files:
        from poker_hud.flush_manager import flush_all
        result = flush_all(verbose=True)

        print()
        print(f"✓ Processed {result['total_hands']} hands from {result['processed']} files")
    else:
        print("⚠ Skipping flush (no hand history files found)")
        print("Run 'python3 mbhud_flush.py' after playing your first session")

    # Done
    print()
    print("=" * 80)
    print("Setup Complete!")
    print("=" * 80)
    print()
    print("Next steps:")
    print("  1. Start playing on ACR")
    print("  2. Run: python3 mbhud_start.py")
    print()
    print("For help, see README.md")
    print()


if __name__ == "__main__":
    main()
