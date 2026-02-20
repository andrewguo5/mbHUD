#!/usr/bin/env python3
"""
Test script to validate PFR calculation on sample hands.
"""

from poker_hud.utils import get_sample_hands
from poker_hud.stat_calculators import calculate_pfr


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

        # Calculate PFR
        pfr_results = calculate_pfr(hand)

        print("\nPFR Results:")
        for player, (num, denom) in pfr_results.items():
            pfr_pct = (num / denom * 100) if denom > 0 else 0
            print(f"  {player:20s} - {num}/{denom} ({pfr_pct:.0f}%) - Raised {num} times in {denom} opportunities")


if __name__ == "__main__":
    main()
