"""
Functions for reading and writing .txt.agg files.

The .txt.agg file stores aggregated statistics for a single session (hand history file).
Format: JSON with metadata and per-player position-bucketed statistics.

Format v2 (position-bucketed):
{
  "version": 2,
  "metadata": {...},
  "players": {
    "alice": {
      "VPIP": {"ALL": [11, 22], "BTN": [8, 10], "BB": [3, 12]},
      "PFR": {"ALL": [7, 22], "BTN": [6, 10], "BB": [1, 12]},
      ...
    }
  }
}

Format v1 (legacy, position-collapsed):
{
  "metadata": {...},
  "players": {
    "alice": {"VPIP": [15, 20], "PFR": [8, 20], ...}
  }
}
"""

import json
from pathlib import Path
from typing import Dict, Tuple, Optional
from datetime import datetime

from .stats import Stat
from .config import AGG_FILES_DIR


def get_agg_file_path(source_file: Path) -> Path:
    """
    Get the path to the .txt.agg file for a given source file.

    The .agg file is stored in our data directory, not alongside the source file.
    This keeps our generated files separate from ACR's download directory.

    Args:
        source_file: Path to the original hand history .txt file

    Returns:
        Path to the .txt.agg file in the data directory (may not exist yet)
    """
    # Use the source filename + .agg extension, stored in our data directory
    agg_filename = source_file.name + '.agg'
    return AGG_FILES_DIR / agg_filename


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
    session_stats: Dict[str, Dict[Stat, Dict[str, Tuple[float, int]]]],
    num_hands: int
) -> Path:
    """
    Write aggregated session statistics to a .txt.agg file (v2 format with positions).

    Args:
        source_file: Path to the original hand history .txt file
        session_stats: Dictionary mapping player -> stat -> position -> (num, denom)
        num_hands: Total number of hands processed in the session

    Returns:
        Path to the created .txt.agg file

    Example:
        >>> stats = {
        ...     "alice": {
        ...         Stat.VPIP: {"ALL": (11, 22), "BTN": (8, 10)},
        ...         Stat.PFR: {"ALL": (7, 22), "BTN": (6, 10)}
        ...     }
        ... }
        >>> write_agg_file(Path("HH123.txt"), stats, 22)
        Path("HH123.txt.agg")
    """
    agg_file = get_agg_file_path(source_file)

    # Convert Stat enum to string and positions dict for JSON serialization
    players_json = {}
    for player, stats in session_stats.items():
        players_json[player] = {}
        for stat, positions in stats.items():
            players_json[player][stat.value] = {}
            for position, (num, denom) in positions.items():
                players_json[player][stat.value][position] = [num, denom]

    data = {
        "version": 2,  # Mark as v2 format
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


def read_agg_file(agg_file: Path) -> Dict[str, Dict[Stat, Dict[str, Tuple[float, int]]]]:
    """
    Read aggregated session statistics from a .txt.agg file.

    Supports both v1 (position-collapsed) and v2 (position-bucketed) formats.
    V1 files are automatically converted to v2 format with an "ALL" position.

    Args:
        agg_file: Path to the .txt.agg file

    Returns:
        Dictionary mapping player -> stat -> position -> (num, denom)

    Raises:
        FileNotFoundError: If the .txt.agg file doesn't exist
        json.JSONDecodeError: If the file is corrupted
    """
    if not agg_file.exists():
        raise FileNotFoundError(f"Aggregate file not found: {agg_file}")

    with open(agg_file, 'r') as f:
        data = json.load(f)

    # Check version
    version = data.get("version", 1)  # Default to v1 if no version field

    session_stats = {}

    if version == 2:
        # V2 format: player -> stat -> position -> (num, denom)
        for player, stats_json in data["players"].items():
            session_stats[player] = {}
            for stat_name, positions_json in stats_json.items():
                stat = Stat(stat_name)
                session_stats[player][stat] = {}
                for position, (num, denom) in positions_json.items():
                    session_stats[player][stat][position] = (num, denom)

    else:
        # V1 format (legacy): player -> stat -> (num, denom)
        # Convert to v2 format with "ALL" position
        for player, stats_json in data["players"].items():
            session_stats[player] = {}
            for stat_name, (num, denom) in stats_json.items():
                stat = Stat(stat_name)
                session_stats[player][stat] = {
                    "ALL": (num, denom)  # Put everything in "ALL" position
                }

    return session_stats
