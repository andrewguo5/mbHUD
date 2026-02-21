"""
Parse table state from hand history data.

Extracts information about:
- Table name and configuration (6-max, 9-max)
- Seat assignments and players
- Hero's seat position
- Empty seats
"""

import re
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass
class TableState:
    """Represents the current state of a poker table."""
    table_name: str
    max_seats: int  # 6 for 6-max, 9 for 9-max
    hero: str  # The player we're tracking (usually from config.USERNAME)
    hero_seat: int  # Seat number where hero is sitting
    seats: Dict[int, Optional[str]]  # Seat number -> player name (None for empty)

    def get_clockwise_seats_from_hero(self) -> List[tuple[int, Optional[str]]]:
        """
        Get seats in clockwise order starting from hero.

        Returns:
            List of (seat_number, player_name) tuples, starting with hero
            and going clockwise around the table. Empty seats have player_name=None.
        """
        result = []

        # Start from hero's seat and go clockwise
        for i in range(self.max_seats):
            seat_num = ((self.hero_seat - 1 + i) % self.max_seats) + 1
            player_name = self.seats.get(seat_num)
            result.append((seat_num, player_name))

        return result


def parse_table_state(hand: str, hero: str) -> Optional[TableState]:
    """
    Parse table state from a hand string.

    Args:
        hand: String content of a single hand
        hero: Username of the hero player (usually config.USERNAME)

    Returns:
        TableState object, or None if parsing fails

    Example:
        >>> hand = "Hand #123...\\nCherry Hills 6-max Seat #3 is the button\\nSeat 1: Alice..."
        >>> state = parse_table_state(hand, "Alice")
        >>> state.table_name
        "Cherry Hills"
        >>> state.max_seats
        6
    """
    lines = hand.split('\n')

    if len(lines) < 2:
        return None

    # Parse the header line
    # Format: "Cherry Hills 6-max Seat #3 is the button"
    # or:     "South Beloit 9-max Seat #5 is the button"
    header_line = lines[1].strip()

    # Extract table name and max seats
    # Pattern: "<table name> <N>-max Seat #<button> is the button"
    match = re.match(r'(.+?)\s+(\d+)-max\s+Seat\s+#\d+\s+is the button', header_line)
    if not match:
        return None

    table_name = match.group(1).strip()
    max_seats = int(match.group(2))

    # Parse seat assignments
    # Format: "Seat 1: Kolunio5 ($5.27)"
    #         "Seat 2: Kiman11 ($7.74) is sitting out"
    seats: Dict[int, Optional[str]] = {}
    hero_seat = None

    for line in lines[2:]:
        line = line.strip()

        # Stop when we hit the action section
        if line.startswith('***') or line.startswith('Dealt to'):
            break

        # Match seat lines
        # Pattern: "Seat N: PlayerName ($X.XX)" or "Seat N: Player Name ($X.XX)"
        # Use same robust pattern as hand_parser.get_players_in_hand()
        if line.startswith('Seat ') and 'is sitting out' not in line:
            # Extract player name: everything between ": " and " ($"
            seat_match = re.match(r'Seat (\d+): (.+?) \(\$[\d.]+\)', line)
            if seat_match:
                seat_num = int(seat_match.group(1))
                player_name = seat_match.group(2)

                seats[seat_num] = player_name

                # Check if this is the hero
                if player_name == hero:
                    hero_seat = seat_num
        elif line.startswith('Seat ') and 'is sitting out' in line:
            # Handle sitting out players
            seat_match = re.match(r'Seat (\d+):', line)
            if seat_match:
                seat_num = int(seat_match.group(1))
                seats[seat_num] = None

    # Make sure we found the hero
    if hero_seat is None:
        return None

    # Fill in empty seats (seats that weren't listed at all)
    for seat_num in range(1, max_seats + 1):
        if seat_num not in seats:
            seats[seat_num] = None

    return TableState(
        table_name=table_name,
        max_seats=max_seats,
        hero=hero,
        hero_seat=hero_seat,
        seats=seats
    )


def get_latest_table_state(hands: List[str], hero: str) -> Optional[TableState]:
    """
    Get the table state from the most recent hand.

    Args:
        hands: List of hand strings (from split_into_hands)
        hero: Username of the hero player

    Returns:
        TableState from the most recent hand, or None if no valid hands
    """
    if not hands:
        return None

    # Parse from most recent to oldest until we find a valid state
    for hand in reversed(hands):
        state = parse_table_state(hand, hero)
        if state is not None:
            return state

    return None
