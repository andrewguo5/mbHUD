#!/usr/bin/env python3
"""
Test ATS calculation by finding examples and verifying them.

Uses the "search, calculate, and verify" method:
1. Search for hands with ATS attempts and non-attempts
2. Calculate the stats
3. Display everything for manual verification
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand
from poker_hud.stat_calculators import calculate_ats


def display_hand_analysis(hand_text, parsed, ats_stats):
    """Display hand, parsed data, and ATS stats for verification."""
    print("=" * 80)
    print("RAW HAND HISTORY:")
    print("-" * 80)
    print(hand_text)
    print()

    print("PARSED DATA:")
    print("-" * 80)
    print(f"Hand ID: {parsed.metadata.hand_id}")
    print(f"Button: Seat {parsed.metadata.button_seat}")
    print()
    print("Players and Positions:")
    for seat_num in sorted(parsed.metadata.players.keys()):
        player = parsed.metadata.players[seat_num]
        position = parsed.metadata.positions[player]
        print(f"  Seat {seat_num}: {player:20s} {position}")
    print()

    print("Preflop Actions:")
    for action in parsed.preflop.actions:
        position = parsed.metadata.positions.get(action.player, "?")
        print(f"  {action.player:20s} ({position:6s}): {action.action_type:10s} ${action.amount if action.amount else ''}")
    print()

    print("ATS STATS:")
    print("-" * 80)
    if ats_stats:
        for player, (num, denom) in ats_stats.items():
            position = parsed.metadata.positions[player]
            attempted = "YES" if num == 1 else "NO"
            print(f"  {player:20s} ({position}): Attempted steal = {attempted}, (num={num}, denom={denom})")
    else:
        print("  No ATS opportunities in this hand")
    print()


def main():
    """Find and verify ATS examples."""
    print("ATS Verification Test")
    print("=" * 80)
    print()

    # Find hand history files
    files = find_hand_history_files()

    if not files:
        print("No hand history files found!")
        return

    print(f"Searching through {len(files)} files for ATS examples...\n")

    # Search for examples
    ats_attempt_examples = []
    ats_no_attempt_examples = []
    no_ats_opportunity_examples = []

    for file_path in files:
        content = read_hand_history_file(file_path)
        hands = split_into_hands(content)

        for hand_text in hands:
            parsed = parse_hand(hand_text)
            if not parsed:
                continue

            ats_stats = calculate_ats(parsed)

            # Categorize
            if ats_stats:
                has_attempt = any(num == 1 for num, denom in ats_stats.values())
                if has_attempt:
                    ats_attempt_examples.append((hand_text, parsed, ats_stats))
                else:
                    ats_no_attempt_examples.append((hand_text, parsed, ats_stats))
            else:
                no_ats_opportunity_examples.append((hand_text, parsed, ats_stats))

            # Stop once we have enough examples
            if len(ats_attempt_examples) >= 2 and len(ats_no_attempt_examples) >= 2 and len(no_ats_opportunity_examples) >= 1:
                break

        if len(ats_attempt_examples) >= 2 and len(ats_no_attempt_examples) >= 2 and len(no_ats_opportunity_examples) >= 1:
            break

    # Display examples
    print("\n" + "=" * 80)
    print("EXAMPLES: ATS ATTEMPT (player raised when folded to in steal position)")
    print("=" * 80)
    for hand_text, parsed, ats_stats in ats_attempt_examples[:2]:
        display_hand_analysis(hand_text, parsed, ats_stats)

    print("\n" + "=" * 80)
    print("EXAMPLES: NO ATS ATTEMPT (player in steal position but didn't raise)")
    print("=" * 80)
    for hand_text, parsed, ats_stats in ats_no_attempt_examples[:2]:
        display_hand_analysis(hand_text, parsed, ats_stats)

    print("\n" + "=" * 80)
    print("EXAMPLES: NO ATS OPPORTUNITY (no one in steal position with opportunity)")
    print("=" * 80)
    for hand_text, parsed, ats_stats in no_ats_opportunity_examples[:1]:
        display_hand_analysis(hand_text, parsed, ats_stats)

    print("=" * 80)
    print("ATS Verification Complete!")
    print(f"Found {len(ats_attempt_examples)} ATS attempts")
    print(f"Found {len(ats_no_attempt_examples)} non-attempts")
    print(f"Found {len(no_ats_opportunity_examples)} hands with no ATS opportunity")
    print("=" * 80)


if __name__ == "__main__":
    main()
