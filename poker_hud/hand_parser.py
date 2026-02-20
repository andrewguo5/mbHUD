"""
Hand parsing utilities for ACR hand history files.
"""

import re
from typing import List, Optional


def split_into_hands(content: str) -> List[str]:
    """
    Split a hand history file into individual hands.

    Each hand starts with "Hand #" and continues until the next "Hand #" or EOF.

    Args:
        content: Full content of a hand history file

    Returns:
        List of hand strings, each representing one complete hand
    """
    lines = content.split('\n')
    hands = []
    current_hand = []

    for line in lines:
        if line.startswith('Hand #'):
            # Start of a new hand
            if current_hand:
                # Save the previous hand
                hands.append('\n'.join(current_hand))
            current_hand = [line]
        else:
            if current_hand:  # Only add if we're inside a hand
                current_hand.append(line)

    # Don't forget the last hand
    if current_hand:
        hands.append('\n'.join(current_hand))

    return hands


def get_players_in_hand(hand: str) -> List[str]:
    """
    Extract list of active players from a hand (excluding sitting out).

    Args:
        hand: String content of a single hand

    Returns:
        List of player names who are active in this hand
    """
    players = []
    lines = hand.split('\n')

    # Only look at lines before HOLE CARDS section to get the seat assignments
    for line in lines:
        # Stop once we hit HOLE CARDS - seats are defined before this
        if line.startswith('***'):
            break

        # Player seats look like: "Seat 1: Kolunio5 ($5.27)"
        # Skip those sitting out: "Seat 2: Kiman11 ($7.74) is sitting out"
        # May have conditions: "Seat 3: Specks4016 will be allowed to play after the button"
        if line.startswith('Seat ') and 'is sitting out' not in line:
            # Extract player name between "Seat N: " and first space or " ($"
            try:
                parts = line.split(': ', 1)
                if len(parts) == 2:
                    name_and_rest = parts[1]
                    # Player name is the first word (no spaces in player names)
                    player_name = name_and_rest.split()[0]
                    players.append(player_name)
            except (IndexError, ValueError):
                continue

    return players


def extract_hand_id(hand: str) -> Optional[str]:
    """
    Extract the hand ID from a hand string.

    The hand ID appears in the first line like:
    "Hand #1234567890 - Holdem (No Limit) - $0.05/$0.10 - 2026/01/30 ..."

    Args:
        hand: String content of a single hand

    Returns:
        Hand ID string (e.g., "1234567890"), or None if not found

    Example:
        >>> hand = "Hand #1234567890 - Holdem..."
        >>> extract_hand_id(hand)
        "1234567890"
    """
    # Get first line
    first_line = hand.split('\n')[0] if hand else ""

    # Extract hand ID using regex: "Hand #<digits>"
    match = re.match(r'Hand #(\d+)', first_line)
    if match:
        return match.group(1)

    return None
