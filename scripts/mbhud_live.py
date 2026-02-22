#!/usr/bin/env python3
"""
mbHUD Live - Real-time poker HUD display

Monitors active tables and displays player statistics in real-time.

Usage:
    python3 mbhud_live.py
"""

import time
import os
from poker_hud.config import USERNAME
from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.table_parser import get_latest_table_state
from poker_hud.live_tracker import LiveStatsTracker
from poker_hud.flush_manager import is_live_file, get_last_flush_time
from poker_hud.stats import Stat


def clear_screen():
    """Clear the terminal screen."""
    os.system('clear' if os.name != 'nt' else 'cls')


def format_stat(num, denom, is_percentage=True):
    """Format a stat as either percentage or raw value."""
    if denom == 0:
        return "N/A"

    if is_percentage:
        pct = (num / denom) * 100
        return f"{pct:5.1f}%"
    else:
        # For BB/100, calculate per 100 hands
        bb100 = (num / denom) * 100
        return f"{bb100:+7.1f}"


def display_hud(tracker: LiveStatsTracker, last_flush_time: float):
    """
    Display the HUD for all active tables.

    Args:
        tracker: LiveStatsTracker instance
        last_flush_time: Unix timestamp of last flush
    """
    clear_screen()

    print("=" * 120)
    print("mbHUD - Live Poker Statistics")
    print("=" * 120)
    print(f"Username: {USERNAME}")
    print(f"Last flush: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_flush_time))}")
    print(f"Update time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 120)
    print()

    # Find all live files
    all_files = find_hand_history_files()
    live_files = [f for f in all_files if is_live_file(f)]

    if not live_files:
        print("No active tables detected.")
        print("\nWaiting for you to join a table...")
        print("Join a table and finish at least one hand first to see stats.")
        print("\nPress Ctrl+C to quit")
        return

    # Display each table
    for file_path in live_files:
        try:
            # Read the file and parse hands
            content = read_hand_history_file(file_path)
            hands = split_into_hands(content)

            if not hands:
                print(f"\nTable: {file_path.name}")
                print("  No hands played yet. Waiting...")
                continue

            # Get table state from latest hand
            table_state = get_latest_table_state(hands, USERNAME)

            if not table_state:
                print(f"\nTable: {file_path.name}")
                print("  Could not parse table state. Waiting...")
                continue

            # Display table header
            print(f"\n{'─' * 120}")
            print(f"TABLE: {table_state.table_name} ({table_state.max_seats}-max)")
            print(f"Hands played: {len(hands)}")
            print(f"{'─' * 120}")

            # Display column headers
            print(f"{'Seat':<6} {'Player':<20} {'Hands':>8}  {'VPIP':>8}  {'PFR':>8}  {'3B':>8}  {'BB/100':>8}")
            print("─" * 120)

            # Get seats in clockwise order from hero
            seats = table_state.get_clockwise_seats_from_hero()

            for seat_num, player_name in seats:
                if player_name is None:
                    # Empty seat
                    print(f"{seat_num:<6} {'(empty)':<20}")
                else:
                    # Get stats for this player
                    stats = tracker.get_player_stats(player_name)

                    # Extract individual stats
                    n_hands = stats.get(Stat.N, (0, 0))[0]
                    vpip_num, vpip_denom = stats.get(Stat.VPIP, (0, 0))
                    pfr_num, pfr_denom = stats.get(Stat.PFR, (0, 0))
                    threeb_num, threeb_denom = stats.get(Stat.THREE_B, (0, 0))
                    bb100_total, bb100_hands = stats.get(Stat.BB100, (0, 0))

                    # Format stats
                    vpip_str = format_stat(vpip_num, vpip_denom, is_percentage=True)
                    pfr_str = format_stat(pfr_num, pfr_denom, is_percentage=True)
                    threeb_str = format_stat(threeb_num, threeb_denom, is_percentage=True)
                    bb100_str = format_stat(bb100_total, bb100_hands, is_percentage=False)

                    # Mark hero with asterisk
                    display_name = f"{player_name} *" if player_name == USERNAME else player_name

                    print(f"{seat_num:<6} {display_name:<20} {n_hands:>8}  {vpip_str:>8}  {pfr_str:>8}  {threeb_str:>8}  {bb100_str:>8}")

            print()

        except Exception as e:
            print(f"\nError processing {file_path.name}: {e}")

    print("─" * 120)
    print("Press Ctrl+C to stop")


def main():
    """Main HUD loop."""
    print("Starting mbHUD Live...")
    print("Initializing tracker...")

    # Initialize the live stats tracker
    tracker = LiveStatsTracker()

    # Initial update
    tracker.update()

    print("Ready!\n")
    time.sleep(1)

    last_flush_time = get_last_flush_time()
    flush_count = 0
    flush_detected_this_cycle = False

    try:
        while True:
            # Check if flush occurred
            current_flush_time = get_last_flush_time()
            if current_flush_time > last_flush_time:
                # Don't clear screen - show message at bottom
                print("\n")
                print("=" * 120)
                print("⚡ FLUSH DETECTED!")
                print("=" * 120)
                print(f"Previous flush: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(last_flush_time))}")
                print(f"New flush:      {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(current_flush_time))}")
                print("\nProcessing flush...")
                print("  - Resetting live tracker state...")
                print("  - Clearing in-memory hand tracking...")
                print("  - Reloading stats from .agg cache files...")

                last_flush_time = current_flush_time
                flush_count += 1
                flush_detected_this_cycle = True

                print(f"\n✓ Flush complete! (Total manual flushes this session: {flush_count})")
                print("\nWill update display in 5 seconds...")
                time.sleep(5)

            # Update tracker with new hands
            new_hands = tracker.update()
            if new_hands > 0:
                # New hands detected, update immediately
                pass

            # Display the HUD
            display_hud(tracker, last_flush_time)

            # Show flush info in status line if flush just happened
            if flush_detected_this_cycle:
                print(f"\n✓ Stats reloaded after flush (Manual flushes this session: {flush_count})")
                flush_detected_this_cycle = False

            # Wait before next update
            time.sleep(30)

    except KeyboardInterrupt:
        print("\n\nStopping mbHUD Live...")
        print("Goodbye!")


if __name__ == "__main__":
    main()
