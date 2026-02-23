#!/usr/bin/env python3
"""
Backup hand history files from ACR directory to persistent storage.

ACR only keeps the previous 30 days of hand history, so this script
backs up files to a persistent location with no TTL.
"""

import sys
import shutil
from pathlib import Path
import json


def load_config():
    """Load configuration from config.json."""
    config_path = Path(__file__).parent.parent / "config.json"

    if not config_path.exists():
        print(f"Error: config.json not found at {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        return json.load(f)


def backup_handhistory():
    """Copy hand history files to persistent storage (cross-platform)."""
    config = load_config()

    # Source: ACR hand history directory
    source_dir = Path(config["hand_history_dir"])

    # Destination: mbHUD/data/handhistory
    dest_dir = Path(__file__).parent.parent / "data" / "handhistory"

    # Ensure source exists
    if not source_dir.exists():
        print(f"Error: Source directory not found: {source_dir}")
        sys.exit(1)

    # Ensure destination exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    print(f"Backing up hand history files...")
    print(f"  From: {source_dir}")
    print(f"  To:   {dest_dir}")

    # Find all .txt files in source directory
    txt_files = list(source_dir.glob("*.txt"))

    if not txt_files:
        print("\nNo .txt files found in source directory")
        return

    copied = 0
    skipped = 0
    errors = 0

    for source_file in txt_files:
        dest_file = dest_dir / source_file.name

        try:
            # Skip if file already exists in destination
            if dest_file.exists():
                skipped += 1
                continue

            # Copy file, preserving metadata
            shutil.copy2(source_file, dest_file)
            copied += 1

        except Exception as e:
            print(f"  Error copying {source_file.name}: {e}")
            errors += 1

    print("\nBackup complete!")
    print(f"\nSummary:")
    print(f"  Files copied: {copied}")
    print(f"  Files skipped (already exist): {skipped}")
    print(f"  Total files in source: {len(txt_files)}")
    if errors > 0:
        print(f"  Errors: {errors}")


if __name__ == "__main__":
    backup_handhistory()
