#!/usr/bin/env python3
"""
mbHUD Start Script

Flushes all hand histories then starts the live HUD.
"""

from poker_hud.flush_manager import flush_all
from scripts.mbhud_live import main as live_main


def main():
    print("=" * 80)
    print("Starting mbHUD...")
    print("=" * 80)
    print()

    # Step 1: Flush all hand histories
    print("Step 1: Flushing hand histories to cache...")
    print("-" * 80)
    print()

    result = flush_all(verbose=True)

    print()

    # Step 2: Start live HUD
    print("=" * 80)
    print("Step 2: Starting live HUD...")
    print("=" * 80)
    print()

    live_main()


if __name__ == "__main__":
    main()
