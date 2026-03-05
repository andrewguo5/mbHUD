"""
Stat definitions and calculators for poker statistics.
"""

from enum import Enum


class Stat(Enum):
    """Enumeration of all poker statistics tracked by the HUD."""

    VPIP = "VPIP"      # Voluntarily Put money In Pot
    PFR = "PFR"        # Pre-Flop Raise
    THREE_B = "3B"     # 3-bet frequency
    FOUR_B = "4B"      # 4-bet frequency
    ATS = "ATS"        # Attempt To Steal (raise from CO/BTN/SB when folded to)
    F3B = "F3B"        # Fold to 3-bet
    CBET = "CBET"      # Continuation bet frequency
    FCBET = "FCBET"    # Fold to continuation bet
    BB100 = "BB100"    # Big blinds won per 100 hands
    N = "N"            # Number of hands seen
