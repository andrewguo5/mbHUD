#!/usr/bin/env python3
"""
Test F3B calculation by finding examples and verifying them.

Uses the "search, calculate, and verify" method:
1. Search for hands with F3B opportunities
2. Calculate the stats
3. Display everything for manual verification
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand
from poker_hud.stat_calculators import calculate_f3b


def display_hand_analysis(hand_text, parsed, f3b_stats):
    """Display hand, parsed data, and F3B stats for verification."""
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

    print("F3B STATS:")
    print("-" * 80)
    if f3b_stats:
        for player, (num, denom) in f3b_stats.items():
            position = parsed.metadata.positions[player]
            folded = "FOLDED" if num == 1 else "CALLED/4BET"
            print(f"  {player:20s} ({position}): {folded}, (num={num}, denom={denom})")
    else:
        print("  No F3B opportunities in this hand")
    print()


def main():
    """Find and verify F3B examples."""
    print("F3B Verification Test")
    print("=" * 80)
    print()

    # Find hand history files
    files = find_hand_history_files()

    if not files:
        print("No hand history files found!")
        return

    print(f"Searching through {len(files)} files for F3B examples...\n")

    # Search for examples
    f3b_fold_examples = []
    f3b_call_or_4bet_examples = []
    no_f3b_opportunity_examples = []

    for file_path in files:
        content = read_hand_history_file(file_path)
        hands = split_into_hands(content)

        for hand_text in hands:
            parsed = parse_hand(hand_text)
            if not parsed:
                continue

            f3b_stats = calculate_f3b(parsed)

            # Categorize
            if f3b_stats:
                has_fold = any(num == 1 for num, denom in f3b_stats.values())
                if has_fold:
                    f3b_fold_examples.append((hand_text, parsed, f3b_stats))
                else:
                    f3b_call_or_4bet_examples.append((hand_text, parsed, f3b_stats))
            else:
                no_f3b_opportunity_examples.append((hand_text, parsed, f3b_stats))

            # Stop once we have enough examples
            if len(f3b_fold_examples) >= 2 and len(f3b_call_or_4bet_examples) >= 2 and len(no_f3b_opportunity_examples) >= 1:
                break

        if len(f3b_fold_examples) >= 2 and len(f3b_call_or_4bet_examples) >= 2 and len(no_f3b_opportunity_examples) >= 1:
            break

    # Display examples
    print("\n" + "=" * 80)
    print("EXAMPLES: FOLDED TO 3-BET (open raiser faced 3-bet and folded)")
    print("=" * 80)
    for hand_text, parsed, f3b_stats in f3b_fold_examples[:2]:
        display_hand_analysis(hand_text, parsed, f3b_stats)

    print("\n" + "=" * 80)
    print("EXAMPLES: CALLED OR 4-BET (open raiser faced 3-bet and called/4-bet)")
    print("=" * 80)
    for hand_text, parsed, f3b_stats in f3b_call_or_4bet_examples[:2]:
        display_hand_analysis(hand_text, parsed, f3b_stats)

    print("\n" + "=" * 80)
    print("EXAMPLES: NO F3B OPPORTUNITY")
    print("=" * 80)
    for hand_text, parsed, f3b_stats in no_f3b_opportunity_examples[:1]:
        display_hand_analysis(hand_text, parsed, f3b_stats)

    print("=" * 80)
    print("F3B Verification Complete!")
    print(f"Found {len(f3b_fold_examples)} folds to 3-bet")
    print(f"Found {len(f3b_call_or_4bet_examples)} calls/4-bets to 3-bet")
    print(f"Found {len(no_f3b_opportunity_examples)} hands with no F3B opportunity")
    print("=" * 80)


if __name__ == "__main__":
    main()
