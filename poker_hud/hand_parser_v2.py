"""
Parser to convert raw hand history text to ParsedHand dataclass structure.
"""

import re
from typing import Optional
from .hand_structures import HandMetadata, Action, Street, ParsedHand
from .hand_parser import get_players_in_hand, extract_player_from_action


def parse_hand(hand: str) -> Optional[ParsedHand]:
    """
    Parse a raw hand history string into a ParsedHand dataclass.

    Args:
        hand: Raw hand history text

    Returns:
        ParsedHand object, or None if parsing fails
    """
    lines = hand.split('\n')

    if len(lines) < 2:
        return None

    # Parse metadata from header
    metadata = _parse_metadata(lines)
    if not metadata:
        return None

    # Calculate positions for all players
    metadata.calculate_positions()

    # Parse streets (preflop, flop, turn, river)
    streets = _parse_streets(hand, metadata.players)

    # Parse hole cards
    hole_cards = _parse_hole_cards(hand)

    # Parse pot and rake from summary
    total_pot, rake = _parse_pot_and_rake(hand)

    # Parse wins from summary and add to last street
    _parse_wins_to_last_street(hand, streets, list(metadata.players.values()))

    return ParsedHand(
        metadata=metadata,
        streets=streets,
        hole_cards=hole_cards,
        total_pot=total_pot,
        rake=rake
    )


def _parse_metadata(lines: list) -> Optional[HandMetadata]:
    """Parse hand metadata from header lines."""
    # Line 0: Hand #2658681643 - Holdem (No Limit) - $0.05/$0.10 - 2026/01/30 16:35:59 UTC
    header_line = lines[0].strip()
    match = re.match(r'Hand #(\d+) - .* - \$([\d.]+)/\$([\d.]+) - (.+)', header_line)
    if not match:
        return None

    hand_id = match.group(1)
    small_blind = float(match.group(2))
    big_blind = float(match.group(3))
    hand_datetime = match.group(4)

    # Line 1: South Beloit 6-max Seat #4 is the button
    table_line = lines[1].strip()
    match = re.match(r'(.+?)\s+(\d+)-max\s+Seat\s+#(\d+)\s+is the button', table_line)
    if not match:
        return None

    table_name = match.group(1).strip()
    max_seats = int(match.group(2))
    button_seat = int(match.group(3))

    # Lines 2+: Seat assignments and stacks
    # Seat 2: aampersands ($10.00)
    players = {}
    stacks = {}

    for line in lines[2:]:
        line = line.strip()

        # Stop at action section
        if line.startswith('***') or not line.startswith('Seat '):
            break

        # Skip sitting out and special conditions
        if 'is sitting out' in line or 'will be allowed to play' in line:
            continue

        # Parse seat and stack
        match = re.match(r'Seat (\d+): (.+?) \(\$([\d.]+)\)', line)
        if match:
            seat = int(match.group(1))
            player = match.group(2)
            stack = float(match.group(3))

            players[seat] = player
            stacks[player] = stack

    return HandMetadata(
        hand_id=hand_id,
        hand_datetime=hand_datetime,
        table_name=table_name,
        max_seats=max_seats,
        button_seat=button_seat,
        small_blind=small_blind,
        big_blind=big_blind,
        players=players,
        stacks=stacks
    )


def _parse_streets(hand: str, players_dict: dict) -> dict:
    """Parse all streets (preflop, flop, turn, river) with actions."""
    lines = hand.split('\n')
    known_players = list(players_dict.values())

    streets = {}
    current_street = None
    current_actions = []
    current_board = None
    preflop_started = False  # Track if we've started collecting preflop actions

    for line in lines:
        line = line.strip()

        # Detect street markers
        if line.startswith('*** HOLE CARDS ***'):
            current_street = 'preflop'
            preflop_started = True
            # Keep existing actions (blind posts) if any
            current_board = None
            continue
        elif line.startswith('*** FLOP ***'):
            # Save previous street
            if current_street:
                streets[current_street] = Street(current_street, current_actions, current_board)

            # Extract board cards: *** FLOP *** [9c 9d Jh]
            match = re.search(r'\[(.*?)\]', line)
            current_board = match.group(1).split() if match else None
            current_street = 'flop'
            current_actions = []
            continue
        elif line.startswith('*** TURN ***'):
            if current_street:
                streets[current_street] = Street(current_street, current_actions, current_board)

            # Extract turn card: *** TURN *** [9c 9d Jh] [5s]
            match = re.search(r'\[.*?\]\s+\[(.*?)\]', line)
            turn_card = match.group(1) if match else None
            if current_board and turn_card:
                current_board = current_board + [turn_card]
            current_street = 'turn'
            current_actions = []
            continue
        elif line.startswith('*** RIVER ***'):
            if current_street:
                streets[current_street] = Street(current_street, current_actions, current_board)

            # Extract river card: *** RIVER *** [9c 9d Jh 5s] [8d]
            match = re.search(r'\[.*?\]\s+\[(.*?)\]', line)
            river_card = match.group(1) if match else None
            if current_board and river_card:
                current_board = current_board + [river_card]
            current_street = 'river'
            current_actions = []
            continue
        elif line.startswith('*** SUMMARY ***'):
            # Save last street
            if current_street:
                streets[current_street] = Street(current_street, current_actions, current_board)
            break

        # Parse blind/ante posts before HOLE CARDS
        if not preflop_started and not line.startswith('Seat '):
            action = _parse_action_line(line, known_players)
            if action and action.action_type in ('post_sb', 'post_bb', 'post_ante'):
                current_actions.append(action)

        # Parse actions within a street
        if current_street:
            action = _parse_action_line(line, known_players)
            if action:
                current_actions.append(action)

    return streets


def _parse_action_line(line: str, known_players: list) -> Optional[Action]:
    """Parse a single action line."""
    # Skip non-action lines
    if not line or line.startswith('Dealt to') or line.startswith('Main pot') or line.startswith('Board'):
        return None

    # Handle uncalled bets first (player name is at the end, not beginning)
    if line.startswith('Uncalled bet'):
        # Format: "Uncalled bet ($1.46) returned to aampersands"
        match = re.search(r'Uncalled bet \(\$([\d.]+)\) returned to (.+)', line)
        if match:
            amount = float(match.group(1))
            return_player = match.group(2).strip()
            # Verify player is known
            for known in known_players:
                if return_player == known or return_player.startswith(known):
                    return Action(known, 'receive', amount)
        return None

    # Extract player name
    player = extract_player_from_action(line, known_players)
    if not player:
        return None

    # Extract action and details
    action_part = line[len(player):].strip()
    words = action_part.split()

    if len(words) < 1:
        return None

    action_verb = words[0]

    # Posts (small blind, big blind, ante)
    if action_verb == 'posts':
        if 'small blind' in line:
            match = re.search(r'\$([\d.]+)', action_part)
            amount = float(match.group(1)) if match else None
            return Action(player, 'post_sb', amount)
        elif 'big blind' in line:
            match = re.search(r'\$([\d.]+)', action_part)
            amount = float(match.group(1)) if match else None
            return Action(player, 'post_bb', amount)
        elif 'ante' in line:
            match = re.search(r'\$([\d.]+)', action_part)
            amount = float(match.group(1)) if match else None
            return Action(player, 'post_ante', amount)

    # Folds
    elif action_verb == 'folds':
        return Action(player, 'fold')

    # Checks
    elif action_verb == 'checks':
        return Action(player, 'check')

    # Calls
    elif action_verb == 'calls':
        # Format: "calls $0.30" or "calls $0.30 and is all-in"
        match = re.search(r'calls \$([\d.]+)', action_part)
        amount = float(match.group(1)) if match else None
        is_all_in = 'all-in' in line
        return Action(player, 'call', amount, is_all_in=is_all_in)

    # Raises
    elif action_verb == 'raises':
        # Format: "raises $0.30 to $0.30" or "raises $0.65 to $0.70"
        match = re.search(r'raises \$([\d.]+) to \$([\d.]+)', action_part)
        if match:
            amount = float(match.group(1))
            total_bet = float(match.group(2))
            is_all_in = 'all-in' in line
            return Action(player, 'raise', amount, total_bet, is_all_in)

    # Bets
    elif action_verb == 'bets':
        # Format: "bets $0.71" or "bets $1.46 and is all-in"
        match = re.search(r'bets \$([\d.]+)', action_part)
        amount = float(match.group(1)) if match else None
        is_all_in = 'all-in' in line
        return Action(player, 'bet', amount, is_all_in=is_all_in)

    return None


def _parse_hole_cards(hand: str) -> dict:
    """Parse hole cards for all players."""
    hole_cards = {}
    lines = hand.split('\n')

    for line in lines:
        line = line.strip()

        # Dealt to hero: Dealt to aampersands [Ts Js]
        if line.startswith('Dealt to'):
            match = re.match(r'Dealt to (.+?) \[(.+?)\]', line)
            if match:
                player = match.group(1)
                cards = match.group(2).split()
                hole_cards[player] = cards

        # Showdown cards in summary: Seat 2: aampersands showed [9c 9d] and won ...
        # or: Seat 2: aampersands (small blind) showed [9c 9d] and won ...
        elif 'showed [' in line:
            match = re.search(r'Seat \d+: (.+?) (?:\(.+?\) )?showed \[(.+?)\]', line)
            if match:
                player = match.group(1).strip()
                cards = match.group(2).split()
                hole_cards[player] = cards

    return hole_cards


def _parse_pot_and_rake(hand: str) -> tuple:
    """Parse total pot and rake from summary."""
    lines = hand.split('\n')

    for line in lines:
        line = line.strip()

        # Total pot $2.78 | Rake $0.10 | JP Fee $0.04
        # or: Total pot $0.15
        if line.startswith('Total pot'):
            pot_match = re.search(r'Total pot \$([\d.]+)', line)
            rake_match = re.search(r'Rake \$([\d.]+)', line)

            total_pot = float(pot_match.group(1)) if pot_match else 0.0
            rake = float(rake_match.group(1)) if rake_match else 0.0

            return total_pot, rake

    return 0.0, 0.0


def _parse_wins_to_last_street(hand: str, streets: dict, known_players: list):
    """
    Parse wins from SUMMARY section and add them as 'win' actions to the last street.

    Args:
        hand: Raw hand text
        streets: Dictionary of parsed streets (modified in place)
        known_players: List of known player names
    """
    lines = hand.split('\n')
    in_summary = False

    # Determine the last street that occurred
    street_order = ['preflop', 'flop', 'turn', 'river']
    last_street_name = None
    for street_name in street_order:
        if street_name in streets:
            last_street_name = street_name

    if not last_street_name:
        return  # No streets to add wins to

    last_street = streets[last_street_name]

    for line in lines:
        line = line.strip()

        if line.startswith('*** SUMMARY ***'):
            in_summary = True
            continue

        if not in_summary:
            continue

        # Parse win lines
        # Format: "Seat 2: aampersands did not show and won $0.15"
        # Or: "Seat 2: aampersands showed [Ad Kd] and won $1.23 with..."
        # Or: "Seat 2: aampersands (small blind) did not show and won $2.78"
        if 'won $' in line:
            match = re.search(r'Seat \d+: (.+?) (?:\(.+?\) )?(?:showed .+? and )?(?:did not show and )?won \$([\d.]+)', line)
            if match:
                player_name = match.group(1).strip()
                amount = float(match.group(2))

                # Verify this is a known player
                if player_name in known_players:
                    # Add win action to last street
                    last_street.actions.append(Action(player_name, 'win', amount))
