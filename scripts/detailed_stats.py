#!/usr/bin/env python3
"""
Display detailed stats for hero with position breakdown.

Shows both aggregate stats (across all positions) and position-bucketed stats
to help analyze positional tendencies.
"""

from pathlib import Path
from poker_hud.config import USERNAME
from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand
from poker_hud.aggregator import aggregate_session_by_position
from poker_hud.processor import DEFAULT_STAT_CALCULATORS
from poker_hud.stats import Stat


def format_stat(num: float, denom: int) -> str:
    """Format a stat as percentage with sample size."""
    if denom == 0:
        return "  -  (0)"

    percentage = 100 * num / denom

    # Special handling for BB/100 (numerator is already in BB)
    if isinstance(num, float) and num != int(num):
        # This is BB/100 - don't convert to percentage
        return f"{num:6.1f} ({denom})"

    return f"{percentage:5.1f}% ({denom})"


def display_detailed_stats(hero: str):
    """
    Display detailed stats for hero with position breakdown.

    Args:
        hero: Player name to analyze
    """
    print(f"Detailed Stats for {hero}")
    print("=" * 80)

    # Find and process all hand history files
    files = find_hand_history_files()

    if not files:
        print("No hand history files found!")
        return

    print(f"Processing {len(files)} hand history files...\n")

    # Parse all hands
    all_parsed_hands = []
    for file_path in files:
        content = read_hand_history_file(file_path)
        hands = split_into_hands(content)

        for hand_text in hands:
            parsed = parse_hand(hand_text)
            if parsed and hero in parsed.metadata.positions:
                all_parsed_hands.append(parsed)

    if not all_parsed_hands:
        print(f"No hands found for {hero}!")
        return

    print(f"Found {len(all_parsed_hands)} hands for {hero}\n")

    # Aggregate by position
    position_stats = aggregate_session_by_position(all_parsed_hands, DEFAULT_STAT_CALCULATORS)

    if hero not in position_stats:
        print(f"No stats found for {hero}!")
        return

    hero_stats = position_stats[hero]

    # Display overall hands first
    if "ALL" in hero_stats:
        all_stats = hero_stats["ALL"]
        n_stat = all_stats.get(Stat.N, (0, 0))
        print(f"Total Hands: {n_stat[0]}")
        print()

    # Define position ordering for display (most common positions first)
    position_order = ["BTN", "SB", "BB", "BTN-1", "BTN-2", "BTN-3", "BTN-4", "BTN-5"]

    # Get positions that hero actually played (exclude "ALL")
    positions_played = [pos for pos in position_order if pos in hero_stats and pos != "ALL"]

    # Add any other positions not in our predefined list
    other_positions = sorted([pos for pos in hero_stats.keys() if pos not in position_order and pos != "ALL"])
    positions_played.extend(other_positions)

    if not positions_played:
        print("No position data available.")
        return

    # Display each stat with position breakdown
    stat_order = [Stat.VPIP, Stat.PFR, Stat.THREE_B, Stat.BB100]

    for stat in stat_order:
        print(f"{stat.value}")
        print("-" * 80)

        # Show aggregate first
        if "ALL" in hero_stats and stat in hero_stats["ALL"]:
            num, denom = hero_stats["ALL"][stat]
            formatted = format_stat(num, denom)
            print(f"  {'ALL':8s}: {formatted}")

        # Show each position
        for position in positions_played:
            pos_stats = hero_stats[position]
            if stat in pos_stats:
                num, denom = pos_stats[stat]
                formatted = format_stat(num, denom)
                print(f"  {position:8s}: {formatted}")

        print()

    print("=" * 80)


def main():
    """Run the detailed stats display."""
    if not USERNAME:
        print("Error: Username not configured!")
        print("Run 'mbhud init' to set up configuration.")
        return

    display_detailed_stats(USERNAME)


if __name__ == "__main__":
    main()
