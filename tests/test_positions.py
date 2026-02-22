#!/usr/bin/env python3
"""
Test position calculation on real hand histories.
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand
from poker_hud.hand_structures import calculate_position


def test_position_calculation():
    """Test the calculate_position function with known inputs."""
    print("Testing position calculation function...")
    print("=" * 80)

    # 6-max table, button on seat 4
    test_cases = [
        (4, 4, 6, "BTN"),    # Button
        (5, 4, 6, "SB"),     # Small blind
        (6, 4, 6, "BB"),     # Big blind
        (3, 4, 6, "BTN-1"),  # Cutoff (1 before button)
        (2, 4, 6, "BTN-2"),  # Hijack (2 before button)
        (1, 4, 6, "BTN-3"),  # UTG (3 before button)
    ]

    all_passed = True
    for seat, btn, max_seats, expected in test_cases:
        result = calculate_position(seat, btn, max_seats)
        status = "OK" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"  Seat {seat}, BTN {btn}, {max_seats}-max: {result:6s} (expected {expected:6s}) [{status}]")

    print()
    if all_passed:
        print("All position calculation tests PASSED!")
    else:
        print("Some position calculation tests FAILED!")
    print()


def test_parsed_hands():
    """Test position calculation on real parsed hands."""
    print("=" * 80)
    print("Testing position calculation on real hands...")
    print("=" * 80)

    # Get most recent hand history file
    files = find_hand_history_files()
    files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)

    if not files:
        print("No hand history files found!")
        return

    # Read first file
    file_path = files[0]
    print(f"\nReading: {file_path.name}")
    content = read_hand_history_file(file_path)
    hands = split_into_hands(content)

    # Test first 5 hands
    num_hands = min(5, len(hands))
    print(f"Testing first {num_hands} hands...")
    print()

    for i, hand_text in enumerate(hands[:num_hands], 1):
        parsed = parse_hand(hand_text)
        if not parsed:
            print(f"Hand #{i}: Failed to parse")
            continue

        print(f"Hand #{i} - {parsed.metadata.hand_id}")
        print(f"  Table: {parsed.metadata.table_name} ({parsed.metadata.max_seats}-max)")
        print(f"  Button: Seat {parsed.metadata.button_seat}")
        print(f"  Players and positions:")

        # Show players in seat order
        for seat_num in sorted(parsed.metadata.players.keys()):
            player = parsed.metadata.players[seat_num]
            position = parsed.metadata.positions[player]
            stack = parsed.metadata.stacks[player]
            print(f"    Seat {seat_num}: {player:20s} {position:6s} (${stack:.2f})")

        print()


def main():
    """Run all position tests."""
    test_position_calculation()
    test_parsed_hands()


if __name__ == "__main__":
    main()
