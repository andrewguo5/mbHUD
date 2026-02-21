"""
Compare old (string-based) and new (ParsedHand-based) stat calculators.

This test verifies that both implementations produce identical results
on real hand history data.
"""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand

# Old calculators (string-based)
from poker_hud.stat_calculators import (
    calculate_vpip,
    calculate_pfr,
    calculate_3bet,
    calculate_bb100
)

# New calculators (ParsedHand-based)
from poker_hud.stat_calculators_v2 import (
    calculate_vpip_v2,
    calculate_pfr_v2,
    calculate_3bet_v2,
    calculate_bb100_v2
)


def compare_stats(stat_name, old_result, new_result):
    """Compare two stat result dictionaries."""
    mismatches = []

    # Check all players in old result
    for player in old_result:
        if player not in new_result:
            mismatches.append(f"  Player '{player}' missing in new result")
        elif old_result[player] != new_result[player]:
            mismatches.append(
                f"  Player '{player}': old={old_result[player]}, new={new_result[player]}"
            )

    # Check for players only in new result
    for player in new_result:
        if player not in old_result:
            mismatches.append(f"  Player '{player}' only in new result: {new_result[player]}")

    if mismatches:
        print(f"[MISMATCH] {stat_name}:")
        for m in mismatches:
            print(m)
        return False
    else:
        print(f"[OK] {stat_name}: All results match")
        return True


def test_hand(hand_text, hand_num):
    """Test a single hand with all stat calculators."""
    print(f"\nHand #{hand_num}")
    print("-" * 80)

    # Parse the hand
    parsed = parse_hand(hand_text)
    if not parsed:
        print("[ERROR] Failed to parse hand")
        return False

    print(f"Hand ID: {parsed.metadata.hand_id}")

    all_match = True

    # Test VPIP
    vpip_old = calculate_vpip(hand_text)
    vpip_new = calculate_vpip_v2(parsed)
    if not compare_stats("VPIP", vpip_old, vpip_new):
        all_match = False

    # Test PFR
    pfr_old = calculate_pfr(hand_text)
    pfr_new = calculate_pfr_v2(parsed)
    if not compare_stats("PFR", pfr_old, pfr_new):
        all_match = False

    # Test 3-bet
    threeb_old = calculate_3bet(hand_text)
    threeb_new = calculate_3bet_v2(parsed)
    if not compare_stats("3-BET", threeb_old, threeb_new):
        all_match = False

    # Test BB/100
    bb100_old = calculate_bb100(hand_text)
    bb100_new = calculate_bb100_v2(parsed)
    if not compare_stats("BB/100", bb100_old, bb100_new):
        all_match = False

    return all_match


def main():
    """Compare old and new stat calculators on real hands."""
    print("=" * 80)
    print("Comparing Old vs New Stat Calculators")
    print("=" * 80)

    # Get most recent file
    all_files = find_hand_history_files()
    all_files = sorted(all_files, key=lambda f: f.stat().st_mtime, reverse=True)

    if not all_files:
        print("No hand history files found!")
        return

    # Test first 10 hands from most recent file
    recent_file = all_files[0]
    print(f"\nTesting file: {recent_file.name}")

    content = read_hand_history_file(recent_file)
    hands = split_into_hands(content)

    num_hands = min(10, len(hands))
    print(f"Testing {num_hands} hands...")

    all_passed = True
    for i, hand in enumerate(hands[:num_hands], 1):
        if not test_hand(hand, i):
            all_passed = False

    print("\n" + "=" * 80)
    if all_passed:
        print("SUCCESS: All stat calculators produce identical results!")
    else:
        print("FAILURE: Some mismatches found between old and new calculators")
    print("=" * 80)


if __name__ == "__main__":
    main()
