"""
Live stats tracker for monitoring active poker sessions.

Tracks stats in-memory for files modified after the last flush,
without using .agg cache files.
"""

from pathlib import Path
from typing import Dict, Set, Tuple, Optional
import time

from .stats import Stat
from .file_manager import find_acr_hand_history_files, read_hand_history_file
from .hand_parser import split_into_hands, extract_hand_id
from .hand_parser_v2 import parse_hand
from .aggregator import aggregate_session_v2
from .processor import DEFAULT_STAT_CALCULATORS
from .flush_manager import get_last_flush_time, is_live_file
from .agg_file import get_agg_file_path, read_agg_file, agg_file_exists


class LiveStatsTracker:
    """
    Tracks statistics for live (actively updating) hand history files.

    This class monitors files that have been modified after the last flush
    and maintains an in-memory aggregation of statistics from new hands.

    Usage:
        tracker = LiveStatsTracker()
        tracker.update()  # Call periodically to check for new hands
        stats = tracker.get_player_stats("aampersands")
    """

    def __init__(self):
        """
        Initialize the live stats tracker.
        """
        self.last_flush_time = get_last_flush_time()
        self.processed_hand_ids: Set[str] = set()  # Track which hands we've seen
        self.live_stats: Dict[str, Dict[Stat, Tuple[float, int]]] = {}  # In-memory stats
        self.live_files: Set[Path] = set()  # Track which files are live

    def _check_flush_reset(self):
        """
        Check if a flush occurred and reset in-memory state if needed.

        This is called at the start of each update() to detect if someone
        ran a flush command.
        """
        current_flush_time = get_last_flush_time()
        if current_flush_time > self.last_flush_time:
            # Flush occurred, reset everything
            self.last_flush_time = current_flush_time
            self.processed_hand_ids.clear()
            self.live_stats.clear()
            self.live_files.clear()

    def _delete_agg_for_live_file(self, file_path: Path):
        """
        Delete .agg file for a live file if it exists.

        Only deletes if the file is confirmed to be live (safety check).

        Args:
            file_path: Path to the live hand history file
        """
        # Safety check: only delete if file is actually live
        if not is_live_file(file_path):
            return

        agg_file = get_agg_file_path(file_path)
        if agg_file.exists():
            agg_file.unlink()

    def _process_live_file(self, file_path: Path):
        """
        Process a single live file, adding new hands to in-memory stats.

        Args:
            file_path: Path to the live hand history file
        """
        # Read the file
        content = read_hand_history_file(file_path)
        hands = split_into_hands(content)

        # Filter to only new hands (not yet processed) and parse them
        new_hand_texts = []
        for hand_text in hands:
            hand_id = extract_hand_id(hand_text)
            if hand_id and hand_id not in self.processed_hand_ids:
                new_hand_texts.append(hand_text)
                self.processed_hand_ids.add(hand_id)

        if not new_hand_texts:
            return  # No new hands

        # Parse new hands to ParsedHand objects
        parsed_hands = []
        for hand_text in new_hand_texts:
            parsed = parse_hand(hand_text)
            if parsed:
                parsed_hands.append(parsed)

        if not parsed_hands:
            return  # Failed to parse any hands

        # Aggregate the new hands
        new_stats = aggregate_session_v2(parsed_hands, DEFAULT_STAT_CALCULATORS)

        # Merge into live_stats
        for player, stats in new_stats.items():
            if player not in self.live_stats:
                self.live_stats[player] = {}

            for stat, (num, denom) in stats.items():
                if stat not in self.live_stats[player]:
                    self.live_stats[player][stat] = (0, 0)

                current_num, current_denom = self.live_stats[player][stat]
                self.live_stats[player][stat] = (current_num + num, current_denom + denom)

    def update(self):
        """
        Update the live stats tracker by checking for new hands.

        This should be called periodically (e.g., every few seconds) to
        monitor for new hands in live files.

        Returns:
            Number of new hands processed
        """
        # Check if a flush occurred
        self._check_flush_reset()

        # Find all hand history files
        all_files = find_acr_hand_history_files()

        # Identify live files (modified after last flush)
        current_live_files = {f for f in all_files if is_live_file(f)}

        # For newly detected live files, delete their .agg files
        newly_live = current_live_files - self.live_files
        for file_path in newly_live:
            self._delete_agg_for_live_file(file_path)

        # Update tracked live files
        self.live_files = current_live_files

        # Process each live file
        hands_before = len(self.processed_hand_ids)
        for file_path in self.live_files:
            self._process_live_file(file_path)

        hands_processed = len(self.processed_hand_ids) - hands_before
        return hands_processed

    def get_player_stats(self, player: str) -> Dict[Stat, Tuple[float, int]]:
        """
        Get combined stats (cached + live) for a player.

        Args:
            player: Player name

        Returns:
            Dictionary mapping Stat -> (numerator, denominator)
            Combines cached stats from .agg files with live in-memory stats

        Example:
            >>> tracker = LiveStatsTracker()
            >>> tracker.update()
            >>> stats = tracker.get_player_stats("alice")
            >>> vpip_num, vpip_denom = stats.get(Stat.VPIP, (0, 0))
        """
        # Start with cached stats from all historical (non-live) files
        all_files = find_acr_hand_history_files()
        historical_files = [f for f in all_files if not is_live_file(f)]

        cached_stats: Dict[Stat, Tuple[float, int]] = {}

        for file_path in historical_files:
            if agg_file_exists(file_path):
                agg_file = get_agg_file_path(file_path)
                session_stats = read_agg_file(agg_file)

                if player in session_stats:
                    for stat, (num, denom) in session_stats[player].items():
                        if stat not in cached_stats:
                            cached_stats[stat] = (0, 0)

                        current_num, current_denom = cached_stats[stat]
                        cached_stats[stat] = (current_num + num, current_denom + denom)

        # Merge with live stats
        combined_stats = cached_stats.copy()

        if player in self.live_stats:
            for stat, (num, denom) in self.live_stats[player].items():
                if stat not in combined_stats:
                    combined_stats[stat] = (0, 0)

                current_num, current_denom = combined_stats[stat]
                combined_stats[stat] = (current_num + num, current_denom + denom)

        return combined_stats

    def get_all_players(self) -> Set[str]:
        """
        Get set of all players seen in live sessions.

        Returns:
            Set of player names seen in live hands
        """
        return set(self.live_stats.keys())
