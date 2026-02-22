"""
Dataclass structures for representing parsed poker hands.

Provides a complete, serializable representation of poker hands that can be
stored and retrieved from a hand history database.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional
import json


def calculate_position(seat_num: int, button_seat: int, max_seats: int) -> str:
    """
    Calculate position relative to button.

    Position naming:
    - BTN: Button
    - SB: Small blind (1 seat after button)
    - BB: Big blind (2 seats after button)
    - BTN-N: N seats before button (e.g., BTN-1 = cutoff, BTN-2 = hijack in 6-max)

    Args:
        seat_num: Player's seat number
        button_seat: Button seat number
        max_seats: Maximum seats at table

    Returns:
        Position string (e.g., "BTN", "SB", "BB", "BTN-3")

    Examples:
        >>> calculate_position(4, 4, 6)  # Button
        'BTN'
        >>> calculate_position(5, 4, 6)  # Small blind
        'SB'
        >>> calculate_position(6, 4, 6)  # Big blind
        'BB'
        >>> calculate_position(3, 4, 6)  # Cutoff (1 before button)
        'BTN-1'
        >>> calculate_position(1, 4, 6)  # UTG in 6-max (3 before button)
        'BTN-3'
    """
    # Calculate distance from button (clockwise)
    distance = (seat_num - button_seat) % max_seats

    if distance == 0:
        return "BTN"
    elif distance == 1:
        return "SB"
    elif distance == 2:
        return "BB"
    else:
        # Seats before the button (counting backwards)
        seats_before_btn = max_seats - distance
        return f"BTN-{seats_before_btn}"


@dataclass
class HandMetadata:
    """Metadata about the hand setup."""
    hand_id: str
    hand_datetime: str  # ISO format: "2026/02/21 00:55:56 UTC"
    table_name: str
    max_seats: int  # 6 for 6-max, 9 for 9-max
    button_seat: int
    small_blind: float
    big_blind: float
    players: Dict[int, str]  # seat_number -> player_name
    stacks: Dict[str, float]  # player_name -> starting_stack
    positions: Dict[str, str] = field(default_factory=dict)  # player_name -> position (BTN, SB, BB, BTN-N)

    def calculate_positions(self) -> None:
        """Calculate and populate positions for all players."""
        self.positions = {}
        for seat_num, player_name in self.players.items():
            position = calculate_position(seat_num, self.button_seat, self.max_seats)
            self.positions[player_name] = position


@dataclass
class Action:
    """A single action taken by a player."""
    player: str
    action_type: str  # 'post_sb', 'post_bb', 'call', 'fold', 'raise', 'bet', 'check', 'receive', 'win'
    amount: Optional[float] = None  # For posts, calls, raises, bets, receives, wins
    total_bet: Optional[float] = None  # For raises (the "to" amount)
    is_all_in: bool = False


@dataclass
class Street:
    """Actions for a single betting round."""
    name: str  # 'preflop', 'flop', 'turn', 'river'
    actions: List[Action]
    board_cards: Optional[List[str]] = None  # e.g., ['Ah', 'Kd', '7s'] for flop


@dataclass
class ParsedHand:
    """Fully parsed hand with metadata and action sequences."""
    metadata: HandMetadata
    streets: Dict[str, Street]  # 'preflop' -> Street, 'flop' -> Street, etc.
    hole_cards: Dict[str, List[str]]  # player_name -> ['Ah', 'Kh']
    total_pot: float
    rake: float

    # Convenience accessors
    @property
    def preflop(self) -> Street:
        return self.streets.get('preflop', Street('preflop', []))

    @property
    def flop(self) -> Optional[Street]:
        return self.streets.get('flop')

    @property
    def turn(self) -> Optional[Street]:
        return self.streets.get('turn')

    @property
    def river(self) -> Optional[Street]:
        return self.streets.get('river')

    def to_dict(self) -> dict:
        """Serialize to dictionary for JSON storage."""
        return asdict(self)

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), indent=2)

    @classmethod
    def from_dict(cls, data: dict) -> 'ParsedHand':
        """Deserialize from dictionary."""
        # Reconstruct nested dataclasses
        metadata = HandMetadata(**data['metadata'])

        streets = {}
        for name, street_data in data['streets'].items():
            actions = [Action(**a) for a in street_data['actions']]
            streets[name] = Street(
                name=street_data['name'],
                actions=actions,
                board_cards=street_data.get('board_cards')
            )

        return cls(
            metadata=metadata,
            streets=streets,
            hole_cards=data['hole_cards'],
            total_pot=data['total_pot'],
            rake=data['rake']
        )

    @classmethod
    def from_json(cls, json_str: str) -> 'ParsedHand':
        """Deserialize from JSON string."""
        return cls.from_dict(json.loads(json_str))
