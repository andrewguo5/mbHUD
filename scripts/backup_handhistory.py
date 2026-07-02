#!/usr/bin/env python3
"""
Backup hand history files from ACR directory to persistent storage.

ACR only keeps the previous 30 days of hand history, so this script
backs up files to a persistent location with no TTL.
"""

import sys
import shutil
from pathlib import Path

from poker_hud.config import ACR_HAND_HISTORY_DIR, BACKUP_HANDHISTORY_DIR


def backup_handhistory():
    """Copy hand history files to persistent storage (cross-platform)."""
    # Source: ACR hand history directory (from config).
    source_dir = ACR_HAND_HISTORY_DIR
    if source_dir is None:
        print("Error: hand_history_dir not configured. Run 'mbhud init'.")
        sys.exit(1)

    # Destination: the canonical backup dir under the user data root.
    dest_dir = BACKUP_HANDHISTORY_DIR

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
