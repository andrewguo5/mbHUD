#!/usr/bin/env python3
"""
mbHUD Clear Cache Script

Safely removes all cached .agg files to force reprocessing.
"""

import shutil
from pathlib import Path
from poker_hud.config import AGG_FILES_DIR


def main():
    print("=" * 80)
    print("mbHUD - Clear Cache")
    print("=" * 80)
    print()

    # Check if cache directory exists
    if not AGG_FILES_DIR.exists():
        print("No cache found.")
        print(f"Cache directory does not exist: {AGG_FILES_DIR}")
        return

    # Count cache files
    agg_files = list(AGG_FILES_DIR.glob("*.agg"))
    num_files = len(agg_files)

    if num_files == 0:
        print("No cache files found.")
        print(f"Cache directory is empty: {AGG_FILES_DIR}")
        return

    print(f"Found {num_files} cached files in:")
    print(f"  {AGG_FILES_DIR}")
    print()

    # Confirm with user
    response = input(f"Delete all {num_files} cached files? (yes/no): ").strip().lower()

    if response not in ('yes', 'y'):
        print("\nCancelled. No files were deleted.")
        return

    # Delete all .agg files
    print("\nDeleting cache files...")
    for agg_file in agg_files:
        agg_file.unlink()

    print(f"✓ Deleted {num_files} files")
    print()
    print("Cache cleared successfully!")
    print()
    print("Next steps:")
    print("  Run 'mbhud flush' to rebuild cache")
    print()


if __name__ == "__main__":
    main()
