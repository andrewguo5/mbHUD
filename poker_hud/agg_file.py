"""
Functions for reading and writing .txt.agg files.

The .txt.agg file stores aggregated statistics for a single session (hand history file).
Format: JSON with metadata and per-player statistics.
"""

import json
from pathlib import Path
from typing import Dict, Tuple
from datetime import datetime

from .stats import Stat


def get_agg_file_path(source_file: Path) -> Path:
    """
    Get the path to the .txt.agg file for a given source file.

    Args:
        source_file: Path to the original hand history .txt file

    Returns:
        Path to the .txt.agg file (may not exist yet)
    """
    return source_file.with_suffix(source_file.suffix + '.agg')


def agg_file_exists(source_file: Path) -> bool:
    """
    Check if a .txt.agg file exists for the given source file.

    Args:
        source_file: Path to the original hand history .txt file

    Returns:
        True if the .txt.agg file exists, False otherwise
    """
    agg_file = get_agg_file_path(source_file)
    return agg_file.exists()


def write_agg_file(
    source_file: Path,
    session_stats: Dict[str, Dict[Stat, Tuple[int, int]]],
    num_hands: int
) -> Path:
    """
    Write aggregated session statistics to a .txt.agg file.

    Args:
        source_file: Path to the original hand history .txt file
        session_stats: Dictionary mapping player -> (Stat -> (num, denom))
        num_hands: Total number of hands processed in the session

    Returns:
        Path to the created .txt.agg file

    Example:
        >>> stats = {"alice": {Stat.VPIP: (15, 20), Stat.PFR: (8, 20)}}
        >>> write_agg_file(Path("HH123.txt"), stats, 20)
        Path("HH123.txt.agg")
    """
    agg_file = get_agg_file_path(source_file)

    # Convert Stat enum to string for JSON serialization
    players_json = {}
    for player, stats in session_stats.items():
        players_json[player] = {}
        for stat, (num, denom) in stats.items():
            players_json[player][stat.value] = [num, denom]

    data = {
        "metadata": {
            "file": source_file.name,
            "processed_at": datetime.utcnow().isoformat() + "Z",
            "num_hands": num_hands
        },
        "players": players_json
    }

    with open(agg_file, 'w') as f:
        json.dump(data, f, indent=2)

    return agg_file


def read_agg_file(agg_file: Path) -> Dict[str, Dict[Stat, Tuple[int, int]]]:
    """
    Read aggregated session statistics from a .txt.agg file.

    Args:
        agg_file: Path to the .txt.agg file

    Returns:
        Dictionary mapping player -> (Stat -> (num, denom))

    Raises:
        FileNotFoundError: If the .txt.agg file doesn't exist
        json.JSONDecodeError: If the file is corrupted
    """
    if not agg_file.exists():
        raise FileNotFoundError(f"Aggregate file not found: {agg_file}")

    with open(agg_file, 'r') as f:
        data = json.load(f)

    # Convert string keys back to Stat enum
    session_stats = {}
    for player, stats_json in data["players"].items():
        session_stats[player] = {}
        for stat_name, (num, denom) in stats_json.items():
            stat = Stat(stat_name)  # Convert string to Stat enum
            session_stats[player][stat] = (num, denom)

    return session_stats
