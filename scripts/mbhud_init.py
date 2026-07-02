#!/usr/bin/env python3
"""
mbHUD Initialization Script

First-time setup for new users, and the one-command fix for existing users
upgrading from a version that stored data elsewhere (in the package/clone tree
or under ~/PokerData): migrates any legacy data into the fixed ~/.mbHUD data
root, then configures username + hand-history directory.
"""

import importlib
import json
import sys
from pathlib import Path

from poker_hud import config as config_module


def get_default_hand_history_dir(username):
    """Get platform-specific default hand history directory."""
    if sys.platform == 'darwin':  # Mac
        return Path.home() / "Downloads" / "AmericasCardroom" / "handHistory" / username
    elif sys.platform == 'win32':  # Windows
        return Path("C:/ACR Poker/handHistory") / username
    else:  # Linux (assume similar to Mac)
        return Path.home() / "Downloads" / "AmericasCardroom" / "handHistory" / username


def migrate_legacy_if_present(cfg):
    """Detect a legacy store and offer a one-time migration into the data root."""
    from poker_hud import migration

    store = migration.find_legacy_store()
    if store is None:
        return

    print("Migrate existing data")
    print("-" * 80)
    hint = f" (~{store.hand_count_hint} hand-history files)" if store.hand_count_hint else ""
    print(f"Found data from a previous install at: {store.root}{hint}")
    answer = input("Migrate it into your data root? [Y/n]: ").strip().lower()

    if answer in ("", "y", "yes"):
        moved = migration.migrate(store)
        if moved:
            for line in moved:
                print(f"  ✓ moved {line}")
        else:
            print("  Nothing to move (destination already populated).")
    else:
        print("  Skipped. You can migrate manually later.")


def configure_account(cfg):
    """Prompt for username + hand-history dir and write the app config.json."""
    print("\nConfigure ACR Account")
    print("-" * 80)
    username = input("Enter your Americas Cardroom username: ").strip()
    if not username:
        print("Error: Username cannot be empty")
        sys.exit(1)

    default_dir = get_default_hand_history_dir(username)
    print(f"\nDefault hand history location: {default_dir}")
    custom_path = input("Enter hand history directory (or press Enter for default): ").strip()
    hh_dir = Path(custom_path) if custom_path else default_dir

    if hh_dir.exists():
        txt_files = list(hh_dir.glob("*.txt"))
        print(f"✓ Directory found: {hh_dir} ({len(txt_files)} hand history files)")
    else:
        print(f"⚠ Directory not found: {hh_dir}")
        print("  Make sure ACR is installed with hand-history saving enabled.")
        print("  Continuing anyway; you can fix this later.")
        txt_files = []

    cfg.ensure_data_dirs()
    config_data = {"username": username, "hand_history_dir": str(hh_dir)}
    try:
        with open(cfg.CONFIG_FILE, 'w') as f:
            json.dump(config_data, f, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")
        sys.exit(1)
    print(f"✓ Config saved to: {cfg.CONFIG_FILE}")

    # config.py resolves ACR_HAND_HISTORY_DIR/USERNAME at import, when config.json
    # did not yet exist -- so those are stale (None) now. Reload config, then the
    # modules that bound those values by import, so the flush sees the fresh ACR
    # dir. (Paths derived purely from the fixed DATA_ROOT are never stale.)
    importlib.reload(cfg)
    import scripts.backup_handhistory as backup_module
    importlib.reload(backup_module)
    return hh_dir, txt_files


def run_initial_flush(hh_dir, txt_files):
    """Process any existing hand histories into aggregates."""
    print("\nProcessing existing hand histories")
    print("-" * 80)
    if hh_dir.exists() and txt_files:
        from poker_hud.flush_manager import flush_all
        result = flush_all(verbose=True)
        print(f"\n✓ Processed {result['total_hands']} hands from {result['processed']} files")
    else:
        print("⚠ Skipping flush (no hand history files found).")
        print("  Run 'mbhud flush' after playing your first session.")


def main():
    print("=" * 80)
    print("mbHUD - Setup")
    print("=" * 80)
    print()

    print(f"Data location: {config_module.DATA_ROOT}\n")
    migrate_legacy_if_present(config_module)
    hh_dir, txt_files = configure_account(config_module)
    run_initial_flush(hh_dir, txt_files)

    print()
    print("=" * 80)
    print("Setup Complete!")
    print("=" * 80)
    print("\nNext steps:")
    print("  1. Start playing on ACR")
    print("  2. Run: mbhud start")
    print("\nFor help, run: mbhud --help")
    print()


if __name__ == "__main__":
    main()
