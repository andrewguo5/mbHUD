#!/usr/bin/env python3
"""
Test script to validate BB/100 calculation on sample hands.
"""

from poker_hud.utils import get_sample_hands
from poker_hud.stat_calculators import calculate_bb100


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

        # Calculate BB/100
        bb100_results = calculate_bb100(hand)

        print("\nBB/100 Results:")
        if not bb100_results:
            print("  (No BB/100 data - couldn't extract BB amount or no players participated)")
        else:
            for player, (bb_won, hands_count) in bb100_results.items():
                print(f"  {player:20s} - {bb_won:+.2f} BB")


if __name__ == "__main__":
    main()
