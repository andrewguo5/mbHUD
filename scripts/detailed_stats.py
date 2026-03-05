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


def format_stat(num: float, denom: int, stat: Stat, include_denom: bool = True) -> str:
    """Format a stat as percentage with optional sample size."""
    if denom == 0:
        return "  -  " if not include_denom else "  -  (0)"

    # Special handling for BB/100
    if stat == Stat.BB100:
        # BB/100 = (total_bb / hands) * 100
        bb100 = (num / denom) * 100 if denom > 0 else 0
        if include_denom:
            return f"{bb100:6.1f} ({denom})"
        return f"{bb100:6.1f}"

    # Regular percentage stats
    percentage = 100 * num / denom
    if include_denom:
        return f"{percentage:5.1f}% ({denom})"
    return f"{percentage:5.1f}%"


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
    if Stat.N in hero_stats and "ALL" in hero_stats[Stat.N]:
        n_hands = hero_stats[Stat.N]["ALL"][0]
        print(f"Total Hands: {n_hands}")
        print()

    # Define position ordering for display: ALL first, then BTN-X (highest to lowest), then BTN, SB, BB
    # Get all positions that hero actually played
    all_positions = set()
    for stat, position_data in hero_stats.items():
        all_positions.update(position_data.keys())
    all_positions.discard("ALL")  # We'll add ALL first

    # Separate BTN-X positions from named positions
    btn_x_positions = []
    named_positions = []

    for pos in all_positions:
        if pos.startswith("BTN-"):
            try:
                # Extract the number after BTN-
                num = int(pos.split("-")[1])
                btn_x_positions.append((num, pos))
            except (ValueError, IndexError):
                named_positions.append(pos)
        else:
            named_positions.append(pos)

    # Sort BTN-X positions from highest to lowest (BTN-6 before BTN-5 before ... BTN-1)
    btn_x_positions.sort(reverse=True)
    btn_x_sorted = [pos for _, pos in btn_x_positions]

    # Define order for named positions
    named_order = ["BTN", "SB", "BB"]
    named_sorted = [pos for pos in named_order if pos in named_positions]

    # Build final position list: ALL, BTN-X (high to low), BTN, SB, BB
    positions_to_display = ["ALL"] + btn_x_sorted + named_sorted

    if len(positions_to_display) <= 1:  # Only "ALL"
        print("No position data available.")
        return

    # Display stats as a table: rows = stats, columns = positions
    stat_order = [Stat.VPIP, Stat.PFR, Stat.THREE_B, Stat.FOUR_B, Stat.ATS, Stat.F3B, Stat.CBET, Stat.FCBET, Stat.BB100]

    # Column widths
    col_width = 10  # Width for each position column
    stat_col_width = 8

    # Print header
    header = f"{'Stat':<{stat_col_width}}"
    for pos in positions_to_display:
        header += f"{pos:>{col_width}}"
    print(header)
    print("-" * (stat_col_width + col_width * len(positions_to_display)))

    # Print each stat as two rows: percentages, then sample sizes
    for stat in stat_order:
        if stat not in hero_stats:
            continue

        stat_positions = hero_stats[stat]

        # Row 1: Stat name and percentages
        row_pct = f"{stat.value:<{stat_col_width}}"
        for position in positions_to_display:
            if position in stat_positions:
                num, denom = stat_positions[position]
                formatted = format_stat(num, denom, stat, include_denom=False)
                row_pct += f"{formatted:>{col_width}}"
            else:
                row_pct += f"{'  -':>{col_width}}"

        # Row 2: Sample sizes (indented)
        row_n = f"{'':>{stat_col_width}}"
        for position in positions_to_display:
            if position in stat_positions:
                num, denom = stat_positions[position]
                row_n += f"{'(' + str(denom) + ')':>{col_width}}"
            else:
                row_n += f"{'':>{col_width}}"

        print(row_pct)
        print(row_n)
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
