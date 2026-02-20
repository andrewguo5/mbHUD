"""
Stat definitions and calculators for poker statistics.
"""

from enum import Enum


class Stat(Enum):
    """Enumeration of all poker statistics tracked by the HUD."""

    VPIP = "VPIP"      # Voluntarily Put money In Pot
    PFR = "PFR"        # Pre-Flop Raise
    BB100 = "BB100"    # Big blinds won per 100 hands
    N = "N"            # Number of hands seen
