"""
File management for ACR hand history files.

This module provides functions to discover and read hand history files
from the Americas Cardroom download directory.
"""

import os
from pathlib import Path
from typing import List, Optional

from .config import USERNAME


def get_hand_history_directory(username: Optional[str] = None) -> Path:
    """
    Get the path to the ACR hand history directory for a user.

    Args:
        username: ACR username (default: uses config.USERNAME)

    Returns:
        Path to the hand history directory

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    if username is None:
        username = USERNAME

    home = Path.home()
    hh_dir = home / "Downloads" / "AmericasCardroom" / "handHistory" / username

    if not hh_dir.exists():
        raise FileNotFoundError(
            f"Hand history directory not found: {hh_dir}\n"
            f"Expected location: ~/Downloads/AmericasCardroom/handHistory/{username}/"
        )

    return hh_dir


def find_hand_history_files(
    username: Optional[str] = None,
    pattern: str = "*.txt"
) -> List[Path]:
    """
    Find all hand history files in the user's directory.

    Args:
        username: ACR username (default: uses config.USERNAME)
        pattern: File pattern to match (default: "*.txt")

    Returns:
        List of Path objects for hand history files, sorted by name

    Raises:
        FileNotFoundError: If the directory doesn't exist
    """
    hh_dir = get_hand_history_directory(username)
    files = sorted(hh_dir.glob(pattern))
    return files


def read_hand_history_file(file_path: Path) -> str:
    """
    Read the contents of a hand history file.

    Args:
        file_path: Path to the hand history file

    Returns:
        File contents as a string

    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If there's an error reading the file
    """
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Try with different encoding if UTF-8 fails
        with open(file_path, 'r', encoding='latin-1') as f:
            return f.read()


def get_file_info(file_path: Path) -> dict:
    """
    Extract metadata from a hand history filename.

    Filename format:
    HH20260131 CASHID-G34287939T1333 TN-Westmont GAMETYPE-Hold'em LIMIT-no CUR-REAL OND-F BUYIN-0 MIN-2 MAX-5.txt

    Args:
        file_path: Path to the hand history file

    Returns:
        Dictionary with parsed metadata (date, table_name, game_type, stakes, etc.)
    """
    filename = file_path.stem  # filename without .txt

    info = {
        "filename": file_path.name,
        "full_path": str(file_path),
    }

    # Use regex to extract components, since table names can have spaces
    import re

    # Extract date (HH20260131)
    date_match = re.search(r'HH(\d{8})', filename)
    if date_match:
        date_str = date_match.group(1)
        info["date"] = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"

    # Extract cash ID
    cashid_match = re.search(r'CASHID-([^\s]+)', filename)
    if cashid_match:
        info["cash_id"] = cashid_match.group(1)

    # Extract table name (TN-... up to GAMETYPE)
    # Table name can contain spaces, so we match until the next keyword
    table_match = re.search(r'TN-(.+?)\s+GAMETYPE', filename)
    if table_match:
        info["table_name"] = table_match.group(1)

    # Extract game type
    gametype_match = re.search(r"GAMETYPE-([^\s]+(?:\s+[^\s]+)?)", filename)
    if gametype_match:
        info["game_type"] = gametype_match.group(1)

    # Extract limit
    limit_match = re.search(r'LIMIT-([^\s]+)', filename)
    if limit_match:
        info["limit"] = limit_match.group(1)

    # Extract min/max buyins
    min_match = re.search(r'MIN-([^\s]+)', filename)
    if min_match:
        info["min_buyin"] = min_match.group(1)

    max_match = re.search(r'MAX-([^\s]+)', filename)
    if max_match:
        info["max_buyin"] = max_match.group(1)

    return info


def process_all_files(
    username: Optional[str] = None,
    callback=None
) -> List[dict]:
    """
    Process all hand history files for a user.

    Args:
        username: ACR username (default: uses config.USERNAME)
        callback: Optional function to call for each file, receives (file_path, content)

    Returns:
        List of file info dictionaries

    Example:
        >>> def print_file(path, content):
        ...     print(f"Processing {path.name}: {len(content)} bytes")
        >>> files = process_all_files(callback=print_file)
    """
    files = find_hand_history_files(username)
    results = []

    for file_path in files:
        info = get_file_info(file_path)

        if callback:
            content = read_hand_history_file(file_path)
            callback(file_path, content)

        results.append(info)

    return results
