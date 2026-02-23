"""
Aggregation functions for combining hand statistics.
"""

from typing import Dict, List, Tuple, Callable
from .stats import Stat
from .hand_structures import ParsedHand


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


def aggregate_session_v2(
    parsed_hands: List[ParsedHand],
    stat_calculators: Dict[Stat, callable]
) -> Dict[str, Dict[Stat, Tuple[int, int]]]:
    """
    Aggregate statistics for a session using ParsedHand objects (position-collapsed).

    This function returns position-collapsed stats for backward compatibility.
    For position-bucketed stats, use aggregate_session_by_position() instead.

    Args:
        parsed_hands: List of ParsedHand objects
        stat_calculators: Dictionary mapping Stat -> v2 calculator function

    Returns:
        Dictionary mapping player -> (Stat -> (numerator, denominator))
        Position-collapsed format for backward compatibility
    """
    # Calculate per-hand results for each stat
    per_stat_results = {}
    for stat, calculator in stat_calculators.items():
        hand_results = []
        for parsed_hand in parsed_hands:
            hand_result = calculator(parsed_hand)
            hand_results.append(hand_result)

        # Aggregate across all hands for this stat
        per_stat_results[stat] = aggregate_hand_results(hand_results, stat)

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

        # Add N (number of hands) - sum of denominators for VPIP
        if Stat.VPIP in result[player]:
            _, vpip_denom = result[player][Stat.VPIP]
            result[player][Stat.N] = (vpip_denom, vpip_denom)
        else:
            result[player][Stat.N] = (0, 0)

    return result


def aggregate_session_by_position(
    parsed_hands: List[ParsedHand],
    stat_calculators: Dict[Stat, Callable]
) -> Dict[str, Dict[Stat, Dict[str, Tuple[float, int]]]]:
    """
    Aggregate statistics for a session with position bucketing.

    Args:
        parsed_hands: List of ParsedHand objects
        stat_calculators: Dictionary mapping Stat -> v2 calculator function

    Returns:
        Dictionary mapping player -> stat -> position -> (numerator, denominator)

        Example:
        {
            "alice": {
                Stat.VPIP: {"ALL": (11, 22), "BTN": (8, 10), "BB": (3, 12)},
                Stat.PFR: {"ALL": (7, 22), "BTN": (6, 10), "BB": (1, 12)},
                Stat.N: {"ALL": (22, 22), "BTN": (10, 10), "BB": (12, 12)}
            }
        }
    """
    # Structure: player -> position -> stat -> list of (num, denom) from each hand
    position_buckets: Dict[str, Dict[str, Dict[Stat, List[Tuple[float, int]]]]] = {}

    for parsed_hand in parsed_hands:
        # Calculate stats for this hand
        hand_stats = {}
        for stat, calculator in stat_calculators.items():
            hand_stats[stat] = calculator(parsed_hand)

        # Bucket by position
        for player in parsed_hand.metadata.positions.keys():
            position = parsed_hand.metadata.positions[player]

            # Initialize player if needed
            if player not in position_buckets:
                position_buckets[player] = {}

            # Initialize position bucket if needed
            if position not in position_buckets[player]:
                position_buckets[player][position] = {}

            # Add stats for this hand to this player's position bucket
            for stat, hand_result in hand_stats.items():
                if player in hand_result:
                    if stat not in position_buckets[player][position]:
                        position_buckets[player][position][stat] = []

                    position_buckets[player][position][stat].append(hand_result[player])

    # Aggregate the lists into totals
    # New structure: player -> stat -> position -> (num, denom)
    result: Dict[str, Dict[Stat, Dict[str, Tuple[float, int]]]] = {}

    for player, positions in position_buckets.items():
        result[player] = {}

        # First, collect all stats for this player
        all_stats_data: Dict[Stat, Dict[str, List[Tuple[float, int]]]] = {}

        # Aggregate each position bucket
        for position, stats in positions.items():
            for stat, values in stats.items():
                if stat not in all_stats_data:
                    all_stats_data[stat] = {}

                # Store values for this position
                if position not in all_stats_data[stat]:
                    all_stats_data[stat][position] = []
                all_stats_data[stat][position].extend(values)

        # Now reorganize as stat -> position -> (num, denom)
        for stat, position_values in all_stats_data.items():
            result[player][stat] = {}

            # Aggregate each position
            for position, values in position_values.items():
                total_num = sum(num for num, _ in values)
                total_denom = sum(denom for _, denom in values)
                result[player][stat][position] = (total_num, total_denom)

            # Add "ALL" position that aggregates across all positions
            all_values = []
            for values in position_values.values():
                all_values.extend(values)

            total_num = sum(num for num, _ in all_values)
            total_denom = sum(denom for _, denom in all_values)
            result[player][stat]["ALL"] = (total_num, total_denom)

        # Add N (number of hands) stat
        if Stat.VPIP in result[player]:
            result[player][Stat.N] = {}
            for position, (_, vpip_denom) in result[player][Stat.VPIP].items():
                result[player][Stat.N][position] = (vpip_denom, vpip_denom)

    return result
