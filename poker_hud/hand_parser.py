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
    sitting_out = []
    lines = hand.split('\n')

    # Only look at lines before HOLE CARDS section to get the seat assignments
    for line in lines:
        # Stop once we hit HOLE CARDS - seats are defined before this
        if line.startswith('***'):
            break

        # Player seats look like: "Seat 1: Kolunio5 ($5.27)"
        # Or with spaces in name: "Seat 3: Pointe After ($5.00)"
        # Skip those sitting out: "Seat 2: Kiman11 ($7.74) is sitting out"
        # Skip special conditions: "Seat 3: Specks4016 will be allowed to play after the button"
        if line.startswith('Seat ') and 'is sitting out' not in line:
            # Extract player name using regex: everything between ": " and " ($"
            # Pattern: Seat N: <player_name> ($X.XX)
            # The player name can contain spaces (e.g., "Pointe After")
            match = re.match(r'Seat \d+: (.+?) \(\$[\d.]+\)', line)
            if match:
                player_name = match.group(1)
                players.append(player_name)

        # Also check for "player sits out" lines (appear after seat assignments)
        # Format: "fish223 sits out"
        if ' sits out' in line:
            # Extract player name (everything before " sits out")
            player_sitting = line.split(' sits out')[0].strip()
            if player_sitting:
                sitting_out.append(player_sitting)

    # Remove sitting out players from active list
    players = [p for p in players if p not in sitting_out]

    return players


def extract_player_from_action(line: str, known_players: List[str]) -> Optional[str]:
    """
    Extract player name from an action line, using known player list for matching.

    Uses a greedy/longest-match strategy to handle player names with spaces.
    For example, if known_players contains "Pointe After" and the line starts with
    "Pointe After raises", we'll match "Pointe After" not just "Pointe".

    Args:
        line: Action line like "Pointe After raises $0.30 to $0.30"
        known_players: List of player names from get_players_in_hand()

    Returns:
        Matched player name, or None if no match found

    Example:
        >>> known = ["aampersands", "Pointe After", "Fise"]
        >>> extract_player_from_action("Pointe After raises $0.30", known)
        "Pointe After"
        >>> extract_player_from_action("Fise folds", known)
        "Fise"
    """
    line = line.strip()

    # Try to match each known player, preferring longer names first
    # This ensures "Pointe After" matches before "Pointe" would
    sorted_players = sorted(known_players, key=len, reverse=True)

    for player in sorted_players:
        if line.startswith(player + ' '):
            return player
        # Also handle case where player name is the entire line (edge case)
        if line == player:
            return player

    return None


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
