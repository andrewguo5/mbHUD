"""
Test the new hand parser on real hand history files.
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand


def display_parsed_hand(parsed):
    """Display a parsed hand in a readable format."""
    print("=" * 80)
    print(f"Hand ID: {parsed.metadata.hand_id}")
    print(f"Table: {parsed.metadata.table_name} ({parsed.metadata.max_seats}-max)")
    print(f"Blinds: ${parsed.metadata.small_blind}/${parsed.metadata.big_blind}")
    print(f"Button: Seat #{parsed.metadata.button_seat}")
    print(f"Total Pot: ${parsed.total_pot} | Rake: ${parsed.rake}")
    print("-" * 80)

    print("Players:")
    for seat, player in sorted(parsed.metadata.players.items()):
        stack = parsed.metadata.stacks[player]
        button_marker = " (BTN)" if seat == parsed.metadata.button_seat else ""
        print(f"  Seat {seat}: {player} (${stack:.2f}){button_marker}")

    print("-" * 80)
    print("Hole Cards:")
    for player, cards in parsed.hole_cards.items():
        print(f"  {player}: {' '.join(cards)}")

    print("-" * 80)
    for street_name in ['preflop', 'flop', 'turn', 'river']:
        street = parsed.streets.get(street_name)
        if street:
            board = f" [{' '.join(street.board_cards)}]" if street.board_cards else ""
            print(f"{street_name.upper()}{board}:")
            for action in street.actions:
                amount_str = f" ${action.amount:.2f}" if action.amount else ""
                total_str = f" to ${action.total_bet:.2f}" if action.total_bet else ""
                allin_str = " (ALL-IN)" if action.is_all_in else ""
                print(f"  {action.player} {action.action_type}{amount_str}{total_str}{allin_str}")
            print()


def main():
    """Test the parser on a few real hands."""
    print("Testing hand parser on real hand history files...\n")

    # Get most recent file
    all_files = find_hand_history_files()
    all_files = sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True)

    if not all_files:
        print("No hand history files found!")
        return

    # Parse first 3 hands from most recent file
    recent_file = all_files[0]
    print(f"Reading from: {recent_file.name}\n")

    content = read_hand_history_file(recent_file)
    hands = split_into_hands(content)

    for i, hand in enumerate(hands[:3], 1):
        print(f"\n{'='*80}")
        print(f"HAND {i}")
        print(f"{'='*80}\n")

        parsed = parse_hand(hand)

        if parsed:
            display_parsed_hand(parsed)

            # Test serialization
            print("-" * 80)
            print("Serialization test:")
            json_str = parsed.to_json()
            print(f"JSON length: {len(json_str)} characters")

            # Test deserialization
            reparsed = parsed.from_json(json_str)
            print(f"[OK] Successfully serialized and deserialized")
            print(f"[OK] Hand ID matches: {reparsed.metadata.hand_id == parsed.metadata.hand_id}")
        else:
            print("[ERROR] Failed to parse hand")
            print("\nRaw hand text:")
            print(hand[:500])

    print("\n" + "=" * 80)
    print("Parser test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
