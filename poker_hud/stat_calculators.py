"""
Stat calculator functions using ParsedHand structure.

These calculators work with the pre-parsed ParsedHand dataclass,
making them cleaner and easier to maintain than the original string-based calculators.
"""

from typing import Dict, Tuple
from .hand_structures import ParsedHand


def calculate_vpip(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate VPIP (Voluntarily Put money In Pot) from ParsedHand.

    VPIP Definition:
    - Numerator: 1 if player's first action is call/raise, 0 if fold/check
    - Denominator: 1 (counted per hand dealt to player)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    player_first_action = {}  # Track first voluntary action per player

    for action in parsed.preflop.actions:
        # Skip blind/ante posts (not voluntary)
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue

        # Only track first voluntary action
        if action.player not in player_first_action:
            if action.action_type in ('raise', 'call'):
                player_first_action[action.player] = 'VPIP'
                result[action.player] = (1, 1)
            elif action.action_type in ('fold', 'check'):
                player_first_action[action.player] = 'NO_VPIP'
                result[action.player] = (0, 1)
            elif action.action_type == 'bet':
                # Bets pre-flop count as VPIP
                player_first_action[action.player] = 'VPIP'
                result[action.player] = (1, 1)

    return result


def calculate_pfr(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate PFR (Pre-Flop Raise) from ParsedHand.

    PFR Definition:
    - Numerator: Number of times the player raises pre-flop
    - Denominator: Number of opportunities to raise (number of actions pre-flop)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    player_raises = {}
    player_opportunities = {}

    for action in parsed.preflop.actions:
        # Skip blind/ante posts
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue

        player = action.player

        # Only count recognized voluntary actions
        if action.action_type in ('raise', 'call', 'fold', 'check', 'bet'):
            # Initialize if first opportunity
            if player not in player_opportunities:
                player_opportunities[player] = 0
                player_raises[player] = 0

            player_opportunities[player] += 1

            # Check if this is a raise
            if action.action_type == 'raise':
                player_raises[player] += 1

    # Build result
    for player in player_opportunities:
        num_raises = player_raises[player]
        num_opportunities = player_opportunities[player]
        result[player] = (num_raises, num_opportunities)

    return result


def calculate_3bet(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate 3-bet frequency from ParsedHand.

    3-bet Definition:
    - raise_count = 0: No raises yet (just blinds posted)
    - raise_count = 1: Someone has open-raised
    - raise_count = 2: Someone has 3-bet

    When raise_count == 1 (facing an open):
    - If player raises: they 3-bet (numerator +1)
    - If player calls/folds: they had opportunity but didn't 3-bet (denominator only +1)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    raise_count = 0

    for action in parsed.preflop.actions:
        # Skip blind/ante posts
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue

        player = action.player

        if action.action_type == 'raise':
            if raise_count == 1:
                # This is a 3-bet!
                result[player] = (1, 1)
                raise_count = 2
            else:
                # This is an open raise (or 4-bet, 5-bet, etc.)
                raise_count += 1

        elif action.action_type in ('call', 'fold', 'check'):
            if raise_count == 1:
                # Facing an open raise - this is a 3-bet opportunity
                if player not in result:
                    result[player] = (0, 1)

    return result


def calculate_bb100(parsed: ParsedHand) -> Dict[str, Tuple[float, int]]:
    """
    Calculate BB/100 (big blinds won per 100 hands) from ParsedHand.

    BB/100 Definition:
    - Numerator: Total big blinds won/lost in the hand
    - Denominator: 1 (counted per hand participated in)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (bb_won, 1) tuples
    """
    bb_amount = parsed.metadata.big_blind
    player_money = {}  # Track net money for each player

    # Process all streets
    for street in parsed.streets.values():
        for action in street.actions:
            player = action.player

            # Initialize if needed
            if player not in player_money:
                player_money[player] = 0.0

            # Money out (posts, calls, raises, bets)
            if action.action_type in ('post_sb', 'post_bb', 'post_ante', 'call', 'raise', 'bet'):
                if action.amount is not None:
                    player_money[player] -= action.amount

            # Money in (receives, wins)
            elif action.action_type in ('receive', 'win'):
                if action.amount is not None:
                    player_money[player] += action.amount

    # Convert to big blinds
    result = {}
    for player, net_money in player_money.items():
        bb_won = net_money / bb_amount
        result[player] = (bb_won, 1)

    return result
