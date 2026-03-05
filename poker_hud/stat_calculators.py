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


def calculate_ats(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate ATS (Attempt To Steal) from ParsedHand.

    ATS Definition:
    - Steal attempt = raise from CO/BTN/SB when action is folded to player
    - Only counts if player is in late position (CO/BTN/SB in 6-max)
    - Numerator: 1 if player raises when folded to, 0 otherwise
    - Denominator: 1 if player had opportunity to steal (folded to in steal position)

    Steal positions in 6-max:
    - BTN (button)
    - SB (small blind)
    - BTN-1 (cutoff)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}

    # Define steal positions for 6-max
    # In future, could adjust based on table size
    steal_positions = {"BTN", "SB", "BTN-1"}

    # Track if action was folded to current player
    folded_to_player = True

    for action in parsed.preflop.actions:
        # Skip blind/ante posts
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue

        player = action.player
        position = parsed.metadata.positions.get(player)

        # Check if this player is in a steal position
        if position in steal_positions:
            # Only count as steal opportunity if action was folded to them
            if folded_to_player and player not in result:
                # This is a steal opportunity (action folded to player in steal position)
                if action.action_type == 'raise':
                    # Player attempted steal
                    result[player] = (1, 1)
                elif action.action_type in ('call', 'fold', 'check'):
                    # Player had opportunity but didn't steal
                    result[player] = (0, 1)

        # Update folded_to_player: set to False if someone calls or raises
        if action.action_type in ('call', 'raise'):
            folded_to_player = False

    return result


def calculate_f3b(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate F3B (Fold to 3-bet) from ParsedHand.

    F3B Definition:
    - Player open-raises, faces a 3-bet, then folds
    - Numerator: 1 if player folds to 3-bet, 0 if they call/4-bet
    - Denominator: 1 if player faced a 3-bet (had opportunity)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    raise_count = 0
    open_raiser = None  # Track who made the first raise

    for action in parsed.preflop.actions:
        # Skip blind/ante posts
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue

        player = action.player

        # Check if open raiser is acting after facing a 3-bet (raise_count == 2)
        if raise_count == 2 and player == open_raiser:
            # The open raiser is acting after facing a 3-bet
            if action.action_type == 'fold':
                # Folded to 3-bet
                result[player] = (1, 1)
            elif action.action_type in ('call', 'raise'):
                # Called or 4-bet the 3-bet
                result[player] = (0, 1)

        # Track raises
        if action.action_type == 'raise':
            if raise_count == 0:
                # This is the open raise - track who did it
                open_raiser = player
            raise_count += 1

    return result


def calculate_4bet(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate 4-bet (or higher) frequency from ParsedHand.

    4-bet Definition:
    - Only players who have already raised in the hand can have a 4-bet opportunity
    - If action comes back to a player who has raised, they have a 4-bet opportunity
    - By virtue of action coming back, someone must have raised (re-opening action)
    - Numerator: 1 if player raises (4-bet/5-bet/etc), 0 if fold/call
    - Denominator: 1 for each time action comes back to a player who has raised

    Note: We ignore the rare case where someone goes all-in but doesn't re-open action
    (insufficient raise). In that case, action comes back but player cannot 4-bet, only call.
    This is exceedingly rare and not tracked.

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    player_has_raised = set()  # Track who has raised in this hand

    for action in parsed.preflop.actions:
        # Skip blind/ante posts
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue

        player = action.player

        # Check if this player has already raised
        if player in player_has_raised:
            # Action came back to them - this is a 4-bet opportunity
            if action.action_type == 'raise':
                result[player] = (1, 1)  # They 4-bet
            elif action.action_type in ('call', 'fold'):
                result[player] = (0, 1)  # They didn't 4-bet
        else:
            # Player hasn't raised yet - check if they raise now
            if action.action_type == 'raise':
                player_has_raised.add(player)

    return result


def calculate_cbet(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate continuation bet (cbet) frequency from ParsedHand.

    Cbet Definition:
    - The preflop aggressor (last raiser preflop) continues aggression on the flop
    - Only counts if action is checked to the aggressor (first to bet on flop)
    - If someone donk bets into the aggressor, this is NOT a cbet opportunity
    - Check-raises do NOT count as cbets
    - Numerator: 1 if aggressor bet when checked to, 0 if checked
    - Denominator: 1 if aggressor was checked to (bet/check), 0 if bet into (fold/call/raise)

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    preflop_aggressor = None

    # Determine preflop aggressor (last raiser preflop)
    for action in parsed.preflop.actions:
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue
        if action.action_type == 'raise':
            preflop_aggressor = action.player

    # If no preflop aggressor or no flop, return empty
    if not preflop_aggressor or 'flop' not in parsed.streets:
        return result

    # Find the preflop aggressor's first action on the flop
    for action in parsed.streets['flop'].actions:
        if action.player == preflop_aggressor:
            # Map action to numerator/denominator
            if action.action_type == 'bet':
                result[preflop_aggressor] = (1, 1)  # Made a cbet
            elif action.action_type == 'check':
                result[preflop_aggressor] = (0, 1)  # Had opportunity, didn't cbet
            # fold/call/raise means they were bet into - no cbet opportunity
            break

    return result


def calculate_fold_to_cbet(parsed: ParsedHand) -> Dict[str, Tuple[int, int]]:
    """
    Calculate fold to continuation bet (fold to cbet) frequency from ParsedHand.

    Fold to Cbet Definition:
    - Measures how often a player folds when facing a cbet
    - A cbet is when the preflop aggressor bets after being checked to on the flop
    - Numerator: 1 if player folded to cbet, 0 if call/raise
    - Denominator: 1 if player faced a cbet
    - State tracking: cbet is "active" until someone raises it

    Args:
        parsed: ParsedHand object

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
    """
    result = {}
    preflop_aggressor = None

    # Determine preflop aggressor (last raiser preflop)
    for action in parsed.preflop.actions:
        if action.action_type in ('post_sb', 'post_bb', 'post_ante'):
            continue
        if action.action_type == 'raise':
            preflop_aggressor = action.player

    # If no preflop aggressor or no flop, return empty
    if not preflop_aggressor or 'flop' not in parsed.streets:
        return result

    # State tracking
    cbet_active = False  # Is there currently a cbet that players are facing?

    for action in parsed.streets['flop'].actions:
        player = action.player

        if player == preflop_aggressor:
            # Preflop aggressor's action
            if action.action_type == 'bet':
                cbet_active = True  # Cbet made, now active
            # Any other action (check/fold/call/raise) - no cbet or cbet no longer original

        else:
            # Other player's action
            if cbet_active:
                # This player is facing the cbet
                if action.action_type == 'fold':
                    result[player] = (1, 1)
                elif action.action_type == 'call':
                    result[player] = (0, 1)
                elif action.action_type == 'raise':
                    result[player] = (0, 1)
                    cbet_active = False  # Cbet raised, no longer facing original cbet

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
