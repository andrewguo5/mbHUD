"""
Verification script for 3-bet detection.

Parses real hand history files and displays hands where 3-bets were detected,
so they can be manually verified for correctness.
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.stat_calculators import calculate_3bet


def display_hand_with_3bet_info(hand: str, stats: dict):
    """Display a hand with 3-bet information highlighted."""
    lines = hand.split('\n')

    # Print header
    print("=" * 80)
    print(lines[0] if lines else "")  # Hand ID line
    print(lines[1] if len(lines) > 1 else "")  # Table info
    print("-" * 80)

    # Print pre-flop action only
    in_preflop = False
    for line in lines:
        if line.startswith('*** HOLE CARDS ***'):
            in_preflop = True
            print(line)
            continue

        if line.startswith('*** FLOP ***') or line.startswith('*** SUMMARY ***'):
            break

        if in_preflop:
            print(line)

    print("-" * 80)
    print("3-bet Statistics:")
    for player, (three_bets, opportunities) in stats.items():
        if three_bets > 0:
            print(f"  ✓ {player}: 3-BET ({three_bets}/{opportunities})")
        else:
            print(f"    {player}: No 3-bet ({three_bets}/{opportunities})")
    print()


def main():
    """Find and display hands with detected 3-bets."""
    print("Searching for hands with 3-bets in recent hand history files...\n")

    # Get all hand history files
    all_files = find_hand_history_files()

    # Sort by modification time (most recent first)
    all_files = sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True)

    # Limit to most recent 3 files to keep output manageable
    recent_files = all_files[:3]

    hands_with_3bets = []
    total_hands_checked = 0

    for file_path in recent_files:
        print(f"Checking file: {file_path.name}")
        content = read_hand_history_file(file_path)
        hands = split_into_hands(content)

        for hand in hands:
            total_hands_checked += 1
            stats = calculate_3bet(hand)

            # Check if any player 3-bet in this hand
            if any(three_bets > 0 for three_bets, _ in stats.values()):
                hands_with_3bets.append((hand, stats))

    print(f"\nTotal hands checked: {total_hands_checked}")
    print(f"Hands with 3-bets found: {len(hands_with_3bets)}\n")

    if not hands_with_3bets:
        print("No 3-bets detected in recent files.")
        print("\nShowing a few random hands with opportunities for reference:")

        # Show some hands with 3-bet opportunities (but no actual 3-bets)
        hands_with_opportunities = []
        for file_path in recent_files:
            content = read_hand_history_file(file_path)
            hands = split_into_hands(content)

            for hand in hands[:5]:  # Check first 5 hands per file
                stats = calculate_3bet(hand)
                if stats:  # Has opportunities
                    hands_with_opportunities.append((hand, stats))
                    if len(hands_with_opportunities) >= 3:
                        break
            if len(hands_with_opportunities) >= 3:
                break

        for hand, stats in hands_with_opportunities[:3]:
            display_hand_with_3bet_info(hand, stats)
    else:
        print("Displaying hands with detected 3-bets:\n")

        # Display up to 5 hands with 3-bets
        for hand, stats in hands_with_3bets[:5]:
            display_hand_with_3bet_info(hand, stats)

        if len(hands_with_3bets) > 5:
            print(f"... and {len(hands_with_3bets) - 5} more hands with 3-bets")

    print("\n" + "=" * 80)
    print("Please review the above hands to verify 3-bet detection is correct.")
    print("=" * 80)


if __name__ == "__main__":
    main()
