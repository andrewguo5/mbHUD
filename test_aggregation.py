#!/usr/bin/env python3
"""
Test script to validate session aggregation.
"""

from poker_hud.utils import get_sample_hands
from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.stat_calculators import calculate_vpip, calculate_pfr
from poker_hud.aggregator import aggregate_session
from poker_hud.stats import Stat


def main():
    print("Reading first hand history file...")
    files = find_hand_history_files()
    if not files:
        print("No files found!")
        return

    first_file = files[0]
    print(f"File: {first_file.name}\n")

    content = read_hand_history_file(first_file)
    hands = split_into_hands(content)
    print(f"Total hands in file: {len(hands)}\n")

    # Define stat calculators
    stat_calculators = {
        Stat.VPIP: calculate_vpip,
        Stat.PFR: calculate_pfr,
    }

    # Aggregate the session
    print("Aggregating session statistics...")
    session_stats = aggregate_session(hands, stat_calculators)

    # Display results
    print(f"\nSession Statistics ({len(session_stats)} players):")
    print("=" * 80)

    # Sort players by number of hands (descending)
    sorted_players = sorted(
        session_stats.items(),
        key=lambda x: x[1][Stat.N][0],
        reverse=True
    )

    for player, stats in sorted_players:
        n_hands = stats[Stat.N][0]

        vpip_num, vpip_denom = stats[Stat.VPIP]
        vpip_pct = (vpip_num / vpip_denom * 100) if vpip_denom > 0 else 0

        pfr_num, pfr_denom = stats[Stat.PFR]
        pfr_pct = (pfr_num / pfr_denom * 100) if pfr_denom > 0 else 0

        print(f"\n{player}:")
        print(f"  Hands: {n_hands}")
        print(f"  VPIP:  {vpip_num}/{vpip_denom} ({vpip_pct:.1f}%)")
        print(f"  PFR:   {pfr_num}/{pfr_denom} ({pfr_pct:.1f}%)")


if __name__ == "__main__":
    main()
