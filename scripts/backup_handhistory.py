#!/usr/bin/env python3
"""
Backup hand history files from ACR directory to persistent storage.

ACR only keeps the previous 30 days of hand history, so this script
backs up files to a persistent location with no TTL.
"""

import subprocess
import sys
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
    """Rsync hand history files to persistent storage."""
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

    # Add trailing slashes for rsync
    # rsync behavior: source/ means "contents of source", source means "source directory itself"
    source = str(source_dir) + "/"
    dest = str(dest_dir) + "/"

    print(f"Backing up hand history files...")
    print(f"  From: {source_dir}")
    print(f"  To:   {dest_dir}")

    # rsync options:
    # -a: archive mode (preserves timestamps, permissions, etc.)
    # -v: verbose
    # --progress: show progress during transfer
    # --ignore-existing: skip files that already exist in destination (faster)
    try:
        result = subprocess.run(
            ["rsync", "-av", "--progress", "--ignore-existing", source, dest],
            check=True,
            capture_output=True,
            text=True
        )

        print("\nBackup complete!")

        # Show summary
        output_lines = result.stdout.strip().split('\n')
        # Last few lines typically contain the summary
        if len(output_lines) > 3:
            print("\nSummary:")
            for line in output_lines[-3:]:
                print(f"  {line}")

    except subprocess.CalledProcessError as e:
        print(f"Error during rsync: {e}")
        print(f"stderr: {e.stderr}")
        sys.exit(1)
    except FileNotFoundError:
        print("Error: rsync command not found. Please ensure rsync is installed.")
        sys.exit(1)


if __name__ == "__main__":
    backup_handhistory()
