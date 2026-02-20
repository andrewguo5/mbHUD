"""
Utility functions for testing and development.
"""

from pathlib import Path
from typing import Optional

from .file_manager import find_hand_history_files, read_hand_history_file
from .hand_parser import split_into_hands


def get_sample_hand(file_index: int = 0, hand_index: int = 0, username: Optional[str] = None) -> str:
    """
    Get a sample hand for testing purposes.

    Args:
        file_index: Index of the file to read (0-based, default: 0 for first file)
        hand_index: Index of the hand within the file (0-based, default: 0 for first hand)
        username: ACR username (default: uses config.USERNAME)

    Returns:
        String content of the specified hand

    Raises:
        IndexError: If file_index or hand_index is out of range
        FileNotFoundError: If no hand history files are found
    """
    files = find_hand_history_files(username)

    if not files:
        raise FileNotFoundError("No hand history files found")

    if file_index >= len(files):
        raise IndexError(f"File index {file_index} out of range (found {len(files)} files)")

    file_path = files[file_index]
    content = read_hand_history_file(file_path)
    hands = split_into_hands(content)

    if not hands:
        raise ValueError(f"No hands found in file: {file_path.name}")

    if hand_index >= len(hands):
        raise IndexError(f"Hand index {hand_index} out of range (found {len(hands)} hands in file)")

    return hands[hand_index]


def get_sample_hands(file_index: int = 0, num_hands: int = 5, username: Optional[str] = None) -> list[str]:
    """
    Get multiple sample hands from a file for testing.

    Args:
        file_index: Index of the file to read (0-based, default: 0 for first file)
        num_hands: Number of hands to retrieve (default: 5)
        username: ACR username (default: uses config.USERNAME)

    Returns:
        List of hand strings

    Raises:
        IndexError: If file_index is out of range
        FileNotFoundError: If no hand history files are found
    """
    files = find_hand_history_files(username)

    if not files:
        raise FileNotFoundError("No hand history files found")

    if file_index >= len(files):
        raise IndexError(f"File index {file_index} out of range (found {len(files)} files)")

    file_path = files[file_index]
    content = read_hand_history_file(file_path)
    hands = split_into_hands(content)

    return hands[:num_hands]
