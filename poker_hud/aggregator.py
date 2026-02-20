"""
Aggregation functions for combining hand statistics.
"""

from typing import Dict, List, Tuple
from .stats import Stat


def aggregate_hand_results(
    hand_results: List[Dict[str, Tuple[int, int]]],
    stat: Stat
) -> Dict[str, Tuple[int, int]]:
    """
    Aggregate results from multiple hands for a single stat.

    Takes a list of per-hand results and combines them into aggregate statistics.

    Args:
        hand_results: List of dictionaries, each mapping player -> (numerator, denominator)
        stat: The stat being aggregated (for metadata/logging purposes)

    Returns:
        Dictionary mapping player -> (total_numerator, total_denominator)

    Example:
        >>> hand1 = {"alice": (1, 1), "bob": (0, 1)}
        >>> hand2 = {"alice": (0, 1), "bob": (1, 1)}
        >>> aggregate_hand_results([hand1, hand2], Stat.VPIP)
        {"alice": (1, 2), "bob": (1, 2)}
    """
    aggregated = {}

    for hand_result in hand_results:
        for player, (num, denom) in hand_result.items():
            if player not in aggregated:
                aggregated[player] = (0, 0)

            current_num, current_denom = aggregated[player]
            aggregated[player] = (current_num + num, current_denom + denom)

    return aggregated


def aggregate_session(
    hands: List[str],
    stat_calculators: Dict[Stat, callable]
) -> Dict[str, Dict[Stat, Tuple[int, int]]]:
    """
    Aggregate all statistics for a session (single file).

    Processes all hands and calculates aggregate statistics for each player.

    Args:
        hands: List of hand strings
        stat_calculators: Dictionary mapping Stat -> calculator function
                         e.g., {Stat.VPIP: calculate_vpip, Stat.PFR: calculate_pfr}

    Returns:
        Dictionary mapping player -> (Stat -> (numerator, denominator))

    Example output:
        {
            "alice": {
                Stat.VPIP: (15, 20),
                Stat.PFR: (8, 20),
                Stat.N: (20, 20)
            },
            "bob": {
                Stat.VPIP: (10, 18),
                Stat.PFR: (5, 18),
                Stat.N: (18, 18)
            }
        }
    """
    # Calculate per-hand results for each stat
    per_stat_results = {}
    for stat, calculator in stat_calculators.items():
        hand_results = []
        for hand in hands:
            hand_result = calculator(hand)
            hand_results.append(hand_result)

        # Aggregate across all hands for this stat
        per_stat_results[stat] = aggregate_hand_results(hand_results, stat)

    # Track number of hands each player participated in
    player_hand_counts = {}
    for stat_result in per_stat_results.values():
        for player in stat_result.keys():
            if player not in player_hand_counts:
                player_hand_counts[player] = set()
            # We use the presence in any stat to count hands
            # (could be refined to track actual hand participation)

    # Reorganize: player -> (Stat -> (num, denom))
    result = {}

    # Get all unique players across all stats
    all_players = set()
    for stat_result in per_stat_results.values():
        all_players.update(stat_result.keys())

    for player in all_players:
        result[player] = {}

        for stat, stat_result in per_stat_results.items():
            if player in stat_result:
                result[player][stat] = stat_result[player]
            else:
                # Player didn't have this stat (no opportunities)
                result[player][stat] = (0, 0)

        # Add N (number of hands) - sum of denominators for VPIP (most inclusive stat)
        if Stat.VPIP in result[player]:
            _, vpip_denom = result[player][Stat.VPIP]
            result[player][Stat.N] = (vpip_denom, vpip_denom)
        else:
            result[player][Stat.N] = (0, 0)

    return result
