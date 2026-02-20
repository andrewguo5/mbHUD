#!/usr/bin/env python3
"""
Test script to validate VPIP calculation on sample hands.
"""

from poker_hud.utils import get_sample_hands
from poker_hud.stat_calculators import calculate_vpip


def main():
    print("Getting first 5 hands from first file...")
    hands = get_sample_hands(file_index=0, num_hands=5)

    for i, hand in enumerate(hands):
        print(f"\n{'='*80}")
        print(f"HAND #{i+1}")
        print('='*80)

        # Show the hand content
        print("\nHand content:")
        print("-" * 80)
        print(hand)
        print("-" * 80)

        # Calculate VPIP
        vpip_results = calculate_vpip(hand)

        print("\nVPIP Results:")
        for player, (num, denom) in vpip_results.items():
            vpip_pct = (num / denom * 100) if denom > 0 else 0
            status = "VPIP" if num == 1 else "NO VPIP"
            print(f"  {player:20s} - {num}/{denom} ({vpip_pct:.0f}%) - {status}")


if __name__ == "__main__":
    main()
