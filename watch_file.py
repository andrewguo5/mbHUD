#!/usr/bin/env python3
"""
Utility to watch hand history file(s) for updates and display the latest hand.

Usage:
    python3 watch_file.py
"""

import time
from pathlib import Path
from poker_hud.file_manager import find_hand_history_files
from poker_hud.hand_parser import split_into_hands, extract_hand_id
from poker_hud.flush_manager import is_live_file


def get_latest_live_file():
    """Find the most recently modified live file."""
    all_files = find_hand_history_files()
    live_files = [f for f in all_files if is_live_file(f)]

    if not live_files:
        return None

    # Return the most recently modified
    return max(live_files, key=lambda f: f.stat().st_mtime)


def watch_and_display():
    """Watch for file updates and display the latest hand."""
    print("=" * 120)
    print("HAND HISTORY FILE WATCHER")
    print("=" * 120)
    print("\nWatching for live hand history files...")
    print("Press Ctrl+C to stop\n")

    last_hand_id = None
    last_file = None

    try:
        while True:
            # Find the latest live file
            current_file = get_latest_live_file()

            if current_file is None:
                print("No live files detected. Waiting...")
                time.sleep(5)
                continue

            # Notify if we're tracking a new file
            if current_file != last_file:
                print(f"\n{'=' * 120}")
                print(f"Now tracking: {current_file.name}")
                print(f"{'=' * 120}\n")
                last_file = current_file

            # Read the file and get the latest hand
            try:
                with open(current_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                hands = split_into_hands(content)

                if not hands:
                    print("No hands found in file yet. Waiting...")
                    time.sleep(5)
                    continue

                latest_hand = hands[-1]
                hand_id = extract_hand_id(latest_hand)

                # Only display if this is a new hand
                if hand_id != last_hand_id:
                    print(f"\n{'=' * 120}")
                    print(f"NEW HAND DETECTED - Hand ID: {hand_id}")
                    print(f"Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    print(f"{'=' * 120}")
                    print(latest_hand)
                    print(f"{'=' * 120}\n")

                    last_hand_id = hand_id

            except Exception as e:
                print(f"Error reading file: {e}")

            # Wait before checking again
            time.sleep(2)

    except KeyboardInterrupt:
        print("\n\nStopped watching.")


if __name__ == "__main__":
    watch_and_display()
