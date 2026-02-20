"""
Session processing pipeline: process hand history files and create .txt.agg files.
"""

from pathlib import Path
from typing import Dict, Tuple, Optional

from .stats import Stat
from .file_manager import read_hand_history_file
from .hand_parser import split_into_hands
from .stat_calculators import calculate_vpip, calculate_pfr, calculate_bb100
from .aggregator import aggregate_session
from .agg_file import agg_file_exists, write_agg_file, read_agg_file, get_agg_file_path


# Default stat calculators
DEFAULT_STAT_CALCULATORS = {
    Stat.VPIP: calculate_vpip,
    Stat.PFR: calculate_pfr,
    Stat.BB100: calculate_bb100,
}


def process_session_file(
    file_path: Path,
    stat_calculators: Optional[Dict[Stat, callable]] = None,
    force_reprocess: bool = False
) -> Dict[str, Dict[Stat, Tuple[int, int]]]:
    """
    Process a single hand history file and return aggregated statistics.

    If a .txt.agg file exists and force_reprocess is False, loads from cache.
    Otherwise, processes the file and creates/updates the .txt.agg file.

    Args:
        file_path: Path to the hand history .txt file
        stat_calculators: Dictionary mapping Stat -> calculator function
                         (default: VPIP and PFR)
        force_reprocess: If True, ignore existing .txt.agg and reprocess

    Returns:
        Dictionary mapping player -> (Stat -> (num, denom))

    Example:
        >>> stats = process_session_file(Path("HH20260130.txt"))
        >>> print(stats["alice"][Stat.VPIP])
        (15, 20)
    """
    if stat_calculators is None:
        stat_calculators = DEFAULT_STAT_CALCULATORS

    agg_file = get_agg_file_path(file_path)

    # Check if .txt.agg exists and we're not forcing reprocess
    if agg_file_exists(file_path) and not force_reprocess:
        print(f"Loading cached stats from {agg_file.name}")
        return read_agg_file(agg_file)

    # Process the file
    print(f"Processing {file_path.name}...")
    content = read_hand_history_file(file_path)
    hands = split_into_hands(content)

    if not hands:
        print(f"  Warning: No hands found in {file_path.name}")
        return {}

    # Aggregate statistics
    session_stats = aggregate_session(hands, stat_calculators)

    # Write to .txt.agg file
    write_agg_file(file_path, session_stats, len(hands))
    print(f"  Processed {len(hands)} hands, wrote to {agg_file.name}")

    return session_stats


def aggregate_all_sessions(
    session_stats_list: list[Dict[str, Dict[Stat, Tuple[int, int]]]]
) -> Dict[str, Dict[Stat, Tuple[int, int]]]:
    """
    Aggregate statistics across multiple sessions.

    Combines session-level stats into overall stats for each player.

    Args:
        session_stats_list: List of session stat dictionaries

    Returns:
        Dictionary mapping player -> (Stat -> (total_num, total_denom))

    Example:
        >>> session1 = {"alice": {Stat.VPIP: (10, 20)}}
        >>> session2 = {"alice": {Stat.VPIP: (5, 10)}}
        >>> aggregate_all_sessions([session1, session2])
        {"alice": {Stat.VPIP: (15, 30)}}
    """
    overall_stats = {}

    for session_stats in session_stats_list:
        for player, stats in session_stats.items():
            if player not in overall_stats:
                overall_stats[player] = {}

            for stat, (num, denom) in stats.items():
                if stat not in overall_stats[player]:
                    overall_stats[player][stat] = (0, 0)

                current_num, current_denom = overall_stats[player][stat]
                overall_stats[player][stat] = (current_num + num, current_denom + denom)

    return overall_stats
