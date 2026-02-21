"""
Stat calculator functions for poker statistics.

Each calculator takes a hand string and returns a dictionary mapping
player names to (numerator, denominator) tuples.
"""

import re
from typing import Dict, Tuple
from .stats import Stat
from .hand_parser import get_players_in_hand, extract_player_from_action


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

    # First, get the known player list from the hand roster
    known_players = get_players_in_hand(hand)

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
            # "Pointe After raises $0.30 to $0.30"

            # Skip lines that aren't actions
            if not line or line.startswith('Dealt to') or line.startswith('Main pot') or line.startswith('Uncalled'):
                continue

            # Extract player name using known player list
            player = extract_player_from_action(line, known_players)
            if not player:
                continue

            # Extract action (word immediately after player name)
            action_part = line[len(player):].strip()
            words = action_part.split()
            if len(words) < 1:
                continue

            action = words[0]

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

    # First, get the known player list from the hand roster
    known_players = get_players_in_hand(hand)

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

            # Extract player name using known player list
            player = extract_player_from_action(line, known_players)
            if not player:
                continue

            # Extract action (word immediately after player name)
            action_part = line[len(player):].strip()
            words = action_part.split()
            if len(words) < 1:
                continue

            action = words[0]

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


def calculate_bb100(hand: str) -> Dict[str, Tuple[float, int]]:
    """
    Calculate BB/100 (big blinds won per 100 hands) for all players in a hand.

    BB/100 Definition:
    - Numerator: Total big blinds won/lost in the hand (money in is negative, money won is positive)
    - Denominator: 1 (counted per hand participated in)

    Args:
        hand: String content of a single hand

    Returns:
        Dictionary mapping player names to (bb_won, 1) tuples
        Note: numerator is a float (big blinds), denominator is always 1

    Example:
        >>> calculate_bb100(hand)
        {"alice": (5.0, 1), "bob": (-5.0, 1)}  # alice won 5 BB, bob lost 5 BB
    """
    # Extract big blind amount from hand header
    # Format: "Hand #... - Holdem (No Limit) - $0.05/$0.10 - ..."
    #                                            SB   /  BB
    bb_amount = None
    lines = hand.split('\n')

    for line in lines[:3]:  # BB info is in first few lines
        match = re.search(r'\$[\d.]+/\$([\d.]+)', line)
        if match:
            bb_amount = float(match.group(1))
            break

    if bb_amount is None:
        # Can't calculate without BB amount
        return {}

    # First, get the known player list from the hand roster
    known_players = get_players_in_hand(hand)

    result = {}
    # Initialize all players who were dealt in with 0.0
    player_money = {player: 0.0 for player in known_players}

    # Track all players who participate
    for line in lines:
        line = line.strip()

        # Track money going in (posts, calls, raises, bets)
        # Format examples:
        #   "player posts the small blind $0.05"
        #   "Pointe After calls $0.30"
        #   "player bets $0.71"
        #   "player raises $0.65 to $0.70" - first $ is additional amount put in

        # Extract player name using known player list
        player = extract_player_from_action(line, known_players)
        if player:
            # Extract action (word immediately after player name)
            action_part = line[len(player):].strip()
            words = action_part.split()
            if len(words) >= 2:
                action = words[0]

                # Actions that put money in - extract first dollar amount
                if action in ('posts', 'calls', 'bets', 'raises'):
                    # Extract dollar amount (first $ after action)
                    for word in words[1:]:
                        if word.startswith('$'):
                            amount_str = word.replace('$', '').replace(',', '')
                            try:
                                amount = float(amount_str)
                                player_money[player] -= amount  # Money in is negative
                                break
                            except ValueError:
                                pass

        # Track money won (in SUMMARY section)
        # Format: "Seat N: player ... won $amount"
        # Need to handle multi-word names: "Seat 3: Pointe After ... won $1.23"
        if 'won $' in line:
            # Use regex to extract player name and amount
            # Pattern: Seat N: <player_name> ... won $<amount>
            match = re.search(r'Seat \d+: (.+?) .*won \$([\d.]+)', line)
            if match:
                player_name = match.group(1)
                amount = float(match.group(2))
                # Verify this is a known player
                if player_name in known_players:
                    player_money[player_name] += amount  # Money won is positive

        # Track uncalled bets returned
        # Format: "Uncalled bet ($X) returned to player"
        if line.startswith('Uncalled bet'):
            # Extract amount and player using known players
            match = re.search(r'Uncalled bet \(\$([\d.]+)\) returned to (.+)', line)
            if match:
                amount = float(match.group(1))
                player_part = match.group(2).strip()
                # Check which known player matches
                for known_player in known_players:
                    if player_part == known_player or player_part.startswith(known_player):
                        player_money[known_player] += amount  # Money returned is positive
                        break

    # Convert to big blinds
    for player, net_money in player_money.items():
        bb_won = net_money / bb_amount
        result[player] = (bb_won, 1)

    return result


def calculate_3bet(hand: str) -> Dict[str, Tuple[int, int]]:
    """
    Calculate 3-bet frequency for all players in a hand.

    3-bet Definition:
    - raise_count = 0: No raises yet (just blinds posted)
    - raise_count = 1: Someone has open-raised (the "2-bet")
    - raise_count = 2: Someone has 3-bet (re-raised the opener)

    When raise_count == 1 (facing an open):
    - If player raises: they 3-bet (numerator +1)
    - If player calls/folds: they had opportunity but didn't 3-bet (denominator only +1)

    This design allows future extension to 4-bet, 5-bet, fold-to-3bet, etc.

    Args:
        hand: String content of a single hand

    Returns:
        Dictionary mapping player names to (numerator, denominator) tuples
        Example: {"player1": (1, 2), "player2": (0, 3)}
    """
    known_players = get_players_in_hand(hand)
    result = {}
    lines = hand.split('\n')

    in_hole_cards = False
    raise_count = 0

    for line in lines:
        line = line.strip()

        if line.startswith('*** HOLE CARDS ***'):
            in_hole_cards = True
            continue

        if line.startswith('*** FLOP ***') or line.startswith('*** SUMMARY ***'):
            # Stop at flop - 3-bet is pre-flop only
            break

        if in_hole_cards:
            # Skip non-action lines
            if not line or line.startswith('Dealt to') or line.startswith('Main pot') or line.startswith('Uncalled'):
                continue

            # Extract player name
            player = extract_player_from_action(line, known_players)
            if not player:
                continue

            # Extract action
            action_part = line[len(player):].strip()
            words = action_part.split()
            if len(words) < 1:
                continue

            action = words[0]

            # Skip blind posts (not voluntary raises)
            if action == 'posts':
                continue

            # Process raises
            if action == 'raises':
                if raise_count == 1:
                    # This is a 3-bet!
                    result[player] = (1, 1)
                    raise_count = 2
                else:
                    # This is an open raise (or 4-bet, 5-bet, etc.)
                    raise_count += 1

            # Process other actions (calls, folds, checks)
            elif action in ('calls', 'folds', 'checks'):
                if raise_count == 1:
                    # Facing an open raise - this is a 3-bet opportunity
                    if player not in result:
                        result[player] = (0, 1)

    return result
