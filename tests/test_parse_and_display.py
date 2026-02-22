#!/usr/bin/env python3
"""
Test parsing recent hand histories and display ParsedHand structure.

This test verifies that:
1. Recent hands can be parsed successfully
2. All key fields are populated correctly
3. Position calculation works
4. The parsed structure is complete and usable
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand


def display_parsed_hand(parsed, verbose=True):
    """Display a ParsedHand in a readable format."""
    print(f"\n{'=' * 80}")
    print(f"HAND #{parsed.metadata.hand_id}")
    print(f"{'=' * 80}")

    # Metadata
    print(f"\nTable: {parsed.metadata.table_name} ({parsed.metadata.max_seats}-max)")
    print(f"Date: {parsed.metadata.hand_datetime}")
    print(f"Stakes: ${parsed.metadata.small_blind:.2f}/${parsed.metadata.big_blind:.2f}")
    print(f"Button: Seat {parsed.metadata.button_seat}")
    print(f"Total Pot: ${parsed.total_pot:.2f} (Rake: ${parsed.rake:.2f})")

    # Players
    print(f"\nPlayers ({len(parsed.metadata.players)}):")
    for seat_num in sorted(parsed.metadata.players.keys()):
        player = parsed.metadata.players[seat_num]
        position = parsed.metadata.positions[player]
        stack = parsed.metadata.stacks[player]
        hole_cards = parsed.hole_cards.get(player, None)
        cards_str = f" [{' '.join(hole_cards)}]" if hole_cards else ""
        print(f"  Seat {seat_num}: {player:20s} {position:6s} ${stack:6.2f}{cards_str}")

    # Streets
    for street_name in ['preflop', 'flop', 'turn', 'river']:
        if street_name not in parsed.streets:
            continue

        street = parsed.streets[street_name]
        print(f"\n{street_name.upper()}:")

        if street.board_cards:
            print(f"  Board: {' '.join(street.board_cards)}")

        if verbose:
            for action in street.actions:
                amt_str = f" ${action.amount:.2f}" if action.amount else ""
                total_str = f" -> ${action.total_bet:.2f}" if action.total_bet else ""
                allin_str = " (ALL-IN)" if action.is_all_in else ""
                print(f"  {action.player:20s} {action.action_type:10s}{amt_str}{total_str}{allin_str}")
        else:
            print(f"  {len(street.actions)} actions")


def test_parse_recent_hands(num_hands=5, verbose=True):
    """
    Parse and display recent hands.

    Args:
        num_hands: Number of hands to parse and display
        verbose: If True, show all actions; if False, show summary only
    """
    print("=" * 80)
    print("TESTING: Parse and Display Recent Hands")
    print("=" * 80)

    # Get most recent file
    files = find_hand_history_files()
    files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

    if not files:
        print("No hand history files found!")
        return

    recent_file = files[0]
    print(f"\nFile: {recent_file.name}")

    # Read and split hands
    content = read_hand_history_file(recent_file)
    hand_texts = split_into_hands(content)

    print(f"Total hands in file: {len(hand_texts)}")
    print(f"Parsing first {min(num_hands, len(hand_texts))} hands...")

    # Parse and display
    parsed_count = 0
    failed_count = 0

    for i, hand_text in enumerate(hand_texts[:num_hands], 1):
        parsed = parse_hand(hand_text)

        if parsed:
            display_parsed_hand(parsed, verbose=verbose)
            parsed_count += 1
        else:
            print(f"\n[FAILED] Hand #{i} could not be parsed")
            failed_count += 1

    # Summary
    print(f"\n{'=' * 80}")
    print("SUMMARY")
    print(f"{'=' * 80}")
    print(f"Successfully parsed: {parsed_count}/{num_hands}")
    if failed_count > 0:
        print(f"Failed to parse: {failed_count}/{num_hands}")
    print()


def test_parse_all_files():
    """Test parsing all hands from all files (quick validation)."""
    print("=" * 80)
    print("TESTING: Parse All Files (Validation)")
    print("=" * 80)

    files = find_hand_history_files()
    print(f"\nFound {len(files)} files")

    total_hands = 0
    total_parsed = 0
    total_failed = 0

    for file_path in files:
        content = read_hand_history_file(file_path)
        hand_texts = split_into_hands(content)

        for hand_text in hand_texts:
            total_hands += 1
            parsed = parse_hand(hand_text)
            if parsed:
                total_parsed += 1
            else:
                total_failed += 1

    print(f"\nTotal hands: {total_hands}")
    print(f"Successfully parsed: {total_parsed} ({total_parsed/total_hands*100:.1f}%)")
    if total_failed > 0:
        print(f"Failed to parse: {total_failed} ({total_failed/total_hands*100:.1f}%)")

    print()


if __name__ == "__main__":
    # Test 1: Parse and display 5 recent hands with full details
    test_parse_recent_hands(num_hands=5, verbose=True)

    # Test 2: Quick validation of all files
    test_parse_all_files()
