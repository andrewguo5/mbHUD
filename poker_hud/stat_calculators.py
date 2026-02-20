"""
Stat calculator functions for poker statistics.

Each calculator takes a hand string and returns a dictionary mapping
player names to (numerator, denominator) tuples.
"""

from typing import Dict, Tuple
from .stats import Stat


def calculate_vpip(hand: str) -> Dict[str, Tuple[int, int]]:
    """
    Calculate VPIP (Voluntarily Put money In Pot) for all players in a hand.

    VPIP Definition:
    - Numerator: 1 if player's first action is call/raise, 0 if fold/check
    - Denominator: 1 (counted per hand dealt to player)

    Only tracks players who actually had an opportunity to act (appear in action lines).

    Args:
        hand: String content of a single hand

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
        Example: {"player1": (1, 1), "player2": (0, 1)}
    """
    result = {}
    lines = hand.split('\n')

    # Find the HOLE CARDS section and process actions
    in_hole_cards = False
    player_actions = {}  # Track first action per player

    for line in lines:
        line = line.strip()

        if line.startswith('*** HOLE CARDS ***'):
            in_hole_cards = True
            continue

        if line.startswith('*** FLOP ***') or line.startswith('*** SUMMARY ***'):
            # Stop processing when we hit FLOP
            break

        if in_hole_cards:
            # Parse actions like:
            # "junkyardwiz raises $0.10 to $0.10"
            # "Kolunio5 folds"
            # "aampersands calls $0.05"
            # "dreamwrecker checks"
            # "Fise posts the small blind $0.05"

            # Skip lines that aren't actions
            if not line or line.startswith('Dealt to') or line.startswith('Main pot') or line.startswith('Uncalled'):
                continue

            # Extract player name (first word) and action
            words = line.split()
            if len(words) >= 2:
                player = words[0]
                action = words[1]

                # Only count recognized actions
                # Recognized actions: raises, calls, folds, checks, bets
                recognized_actions = {'raises', 'calls', 'folds', 'checks', 'bets'}

                if action not in recognized_actions:
                    continue

                # Only track if this is the first action for this player
                if player not in player_actions:
                    # Determine if they voluntarily put money in
                    if action in ('raises', 'calls'):
                        player_actions[player] = 'VPIP'
                        result[player] = (1, 1)
                    elif action in ('folds', 'checks'):
                        player_actions[player] = 'NO_VPIP'
                        result[player] = (0, 1)
                    # Note: bets should not appear pre-flop, but if they do, count as VPIP
                    elif action == 'bets':
                        player_actions[player] = 'VPIP'
                        result[player] = (1, 1)

    return result


def calculate_pfr(hand: str) -> Dict[str, Tuple[int, int]]:
    """
    Calculate PFR (Pre-Flop Raise) for all players in a hand.

    PFR Definition:
    - Numerator: Number of times the player raises before FLOP
    - Denominator: Number of opportunities to raise (number of times player's name appears in actions before FLOP)

    Only tracks players who actually had an opportunity to act (appear in action lines).

    Args:
        hand: String content of a single hand

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
        Example: {"player1": (1, 2), "player2": (0, 1)}
    """
    result = {}
    lines = hand.split('\n')

    # Find the HOLE CARDS section and count raises + opportunities
    in_hole_cards = False
    player_raises = {}  # Track number of raises per player
    player_opportunities = {}  # Track number of opportunities per player

    for line in lines:
        line = line.strip()

        if line.startswith('*** HOLE CARDS ***'):
            in_hole_cards = True
            continue

        if line.startswith('*** FLOP ***') or line.startswith('*** SUMMARY ***'):
            # Stop processing when we hit FLOP
            break

        if in_hole_cards:
            # Skip lines that aren't actions
            if not line or line.startswith('Dealt to') or line.startswith('Main pot') or line.startswith('Uncalled'):
                continue

            # Extract player name (first word) and action
            words = line.split()
            if len(words) >= 2:
                player = words[0]
                action = words[1]

                # Only count recognized actions as opportunities
                # Recognized actions: raises, calls, folds, checks, bets
                # Skip: posts (not voluntary), does (descriptive), collected, etc.
                recognized_actions = {'raises', 'calls', 'folds', 'checks', 'bets'}

                if action not in recognized_actions:
                    continue

                # Count this as an opportunity for the player
                if player not in player_opportunities:
                    player_opportunities[player] = 0
                    player_raises[player] = 0
                player_opportunities[player] += 1

                # Check if this is a raise
                if action == 'raises':
                    player_raises[player] += 1

    # Build result from tracked data
    for player in player_opportunities:
        num_raises = player_raises[player]
        num_opportunities = player_opportunities[player]
        result[player] = (num_raises, num_opportunities)

    return result
