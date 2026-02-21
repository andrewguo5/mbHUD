"""
Test that player names with spaces are handled correctly.

This tests the fix for handling player names like "Pointe After" which contain spaces.
"""

from poker_hud.hand_parser import get_players_in_hand, extract_player_from_action
from poker_hud.stat_calculators import calculate_vpip, calculate_pfr, calculate_bb100
from poker_hud.table_parser import parse_table_state


# Sample hand with a player named "Pointe After"
SAMPLE_HAND = """Hand #1234567890 - Holdem (No Limit) - $0.02/$0.05 - 2026/02/20 12:00:00 UTC
Blandinsville 6-max Seat #2 is the button
Seat 1: aampersands ($5.00)
Seat 3: Pointe After ($5.00)
Seat 5: Fise ($10.00)
Pointe After posts the big blind $0.05
aampersands posts the small blind $0.02
*** HOLE CARDS ***
Dealt to aampersands [Ah Kh]
Fise folds
aampersands raises $0.13 to $0.15
Pointe After calls $0.10
*** FLOP *** [2h 3d 7c]
aampersands bets $0.20
Pointe After folds
Uncalled bet ($0.20) returned to aampersands
*** SUMMARY ***
Total pot $0.30
Seat 1: aampersands (small blind) did not show and won $0.30
Seat 3: Pointe After (big blind) folded on the Flop
Seat 5: Fise folded on the Pre-Flop and did not bet
"""


def test_get_players_in_hand_with_spaces():
    """Test that get_players_in_hand correctly extracts names with spaces."""
    players = get_players_in_hand(SAMPLE_HAND)

    assert "aampersands" in players
    assert "Pointe After" in players
    assert "Fise" in players
    assert len(players) == 3


def test_extract_player_from_action_with_spaces():
    """Test that extract_player_from_action correctly matches names with spaces."""
    known_players = ["aampersands", "Pointe After", "Fise"]

    # Test single-word name
    assert extract_player_from_action("aampersands raises $0.15 to $0.15", known_players) == "aampersands"
    assert extract_player_from_action("Fise folds", known_players) == "Fise"

    # Test multi-word name
    assert extract_player_from_action("Pointe After posts the big blind $0.05", known_players) == "Pointe After"
    assert extract_player_from_action("Pointe After calls $0.10", known_players) == "Pointe After"
    assert extract_player_from_action("Pointe After folds", known_players) == "Pointe After"


def test_calculate_vpip_with_spaces():
    """Test that VPIP calculation works with names containing spaces."""
    vpip_stats = calculate_vpip(SAMPLE_HAND)

    # aampersands raised (VPIP)
    assert "aampersands" in vpip_stats
    assert vpip_stats["aampersands"] == (1, 1)

    # Pointe After called (VPIP)
    assert "Pointe After" in vpip_stats
    assert vpip_stats["Pointe After"] == (1, 1)

    # Fise folded (no VPIP)
    assert "Fise" in vpip_stats
    assert vpip_stats["Fise"] == (0, 1)


def test_calculate_pfr_with_spaces():
    """Test that PFR calculation works with names containing spaces."""
    pfr_stats = calculate_pfr(SAMPLE_HAND)

    # aampersands raised
    assert "aampersands" in pfr_stats
    assert pfr_stats["aampersands"] == (1, 1)

    # Pointe After called (no raise)
    assert "Pointe After" in pfr_stats
    assert pfr_stats["Pointe After"] == (0, 1)

    # Fise folded
    assert "Fise" in pfr_stats
    assert pfr_stats["Fise"] == (0, 1)


def test_calculate_bb100_with_spaces():
    """Test that BB/100 calculation works with names containing spaces."""
    bb100_stats = calculate_bb100(SAMPLE_HAND)

    # Debug: print actual values
    print(f"\nBB/100 stats: {bb100_stats}")

    # aampersands won (posted $0.02, raised to $0.15 total, won $0.30, got $0.20 uncalled back)
    # Money in: -0.15, Money won: 0.30, Net: +0.15 = +3 BB
    assert "aampersands" in bb100_stats
    bb_won, hands = bb100_stats["aampersands"]
    assert hands == 1
    print(f"aampersands BB/100: {bb_won} (expected 3.0)")
    assert abs(bb_won - 3.0) < 0.01  # Handle floating point precision

    # Pointe After lost (posted $0.05, called additional $0.10, total -$0.15)
    # Net: -0.15 = -3 BB
    assert "Pointe After" in bb100_stats
    bb_won, hands = bb100_stats["Pointe After"]
    assert hands == 1
    print(f"Pointe After BB/100: {bb_won} (expected -3.0)")
    assert abs(bb_won - (-3.0)) < 0.01  # Handle floating point precision

    # Fise didn't play (no money)
    if "Fise" in bb100_stats:
        print(f"Fise BB/100: {bb100_stats['Fise']}")
    assert "Fise" not in bb100_stats or bb100_stats["Fise"] == (0.0, 1)


def test_parse_table_state_with_spaces():
    """Test that table state parsing works with names containing spaces."""
    state = parse_table_state(SAMPLE_HAND, "aampersands")

    assert state is not None
    assert state.table_name == "Blandinsville"
    assert state.max_seats == 6
    assert state.hero == "aampersands"
    assert state.hero_seat == 1

    # Check seat assignments
    assert state.seats[1] == "aampersands"
    assert state.seats[3] == "Pointe After"  # This is the key test!
    assert state.seats[5] == "Fise"

    # Empty seats should be None
    assert state.seats[2] is None
    assert state.seats[4] is None
    assert state.seats[6] is None


if __name__ == "__main__":
    # Run all tests
    test_get_players_in_hand_with_spaces()
    print("✓ test_get_players_in_hand_with_spaces passed")

    test_extract_player_from_action_with_spaces()
    print("✓ test_extract_player_from_action_with_spaces passed")

    test_calculate_vpip_with_spaces()
    print("✓ test_calculate_vpip_with_spaces passed")

    test_calculate_pfr_with_spaces()
    print("✓ test_calculate_pfr_with_spaces passed")

    test_calculate_bb100_with_spaces()
    print("✓ test_calculate_bb100_with_spaces passed")

    test_parse_table_state_with_spaces()
    print("✓ test_parse_table_state_with_spaces passed")

    print("\nAll tests passed! ✓")
