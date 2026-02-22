"""
Flush manager for converting hand history files to cached .agg files.

Handles:
- Flushing all hand histories to .agg files
- Detecting last flush time
- Determining which files are "live" (modified after last flush)
"""

from pathlib import Path
from typing import Optional

from .config import AGG_FILES_DIR
from .file_manager import find_hand_history_files
from .processor import process_session_file
from .agg_file import get_agg_file_path, agg_file_exists


def get_last_flush_time() -> float:
    """
    Get the timestamp of the last flush operation.

    This is determined by finding the most recent modification time
    of all .agg files in the AGG_FILES_DIR.

    Returns:
        Unix timestamp (seconds since epoch) of the last flush.
        Returns 0.0 if no .agg files exist (never flushed).

    Example:
        >>> last_flush = get_last_flush_time()
        >>> print(f"Last flush was at {last_flush}")
    """
    if not AGG_FILES_DIR.exists():
        return 0.0

    agg_files = list(AGG_FILES_DIR.glob('*.agg'))

    if not agg_files:
        return 0.0

    # Get the most recent modification time
    most_recent = max(f.stat().st_mtime for f in agg_files)
    return most_recent


def is_live_file(file_path: Path) -> bool:
    """
    Determine if a hand history file is "live" (modified after last flush).

    A file is considered live if its modification time is more recent
    than the last flush time.

    Args:
        file_path: Path to the hand history .txt file

    Returns:
        True if the file is live (modified after last flush), False otherwise

    Example:
        >>> if is_live_file(Path("HH20260220.txt")):
        ...     print("This is a live file")
    """
    last_flush = get_last_flush_time()
    file_mtime = file_path.stat().st_mtime
    return file_mtime > last_flush


def flush_all(verbose: bool = True) -> dict:
    """
    Flush all hand history files to .agg cache files.

    Pipeline:
    1. Backup (rsync) hand histories from ACR directory to data/handhistory
    2. Process files in data/handhistory and create .agg files

    For each file:
    - If .agg exists: skip (already processed)
    - If .agg missing: process the file and create .agg

    Args:
        verbose: If True, print detailed progress; if False, print summary only

    Returns:
        Dictionary with flush statistics:
        {
            'total_files': int,
            'skipped': int,  # Already had .agg files
            'processed': int,  # Newly processed
            'total_hands': int,  # Total hands processed
            'last_flush_time': float  # Timestamp after flush
        }

    Example:
        >>> result = flush_all()
        >>> print(f"Processed {result['processed']} new files")
    """
    from .hand_parser import split_into_hands

    # Step 1: Backup hand histories from ACR to data/handhistory
    print("Step 1: Backing up hand histories from ACR directory...")
    print("─" * 80)
    try:
        from scripts.backup_handhistory import backup_handhistory
        backup_handhistory()
    except Exception as e:
        print(f"Warning: Backup failed: {e}")
        print("Continuing with existing files in data/handhistory...")

    print()
    print("Step 2: Processing hand history files...")
    print("─" * 80)

    # Step 2: Find all hand history files (now from backup directory)
    files = find_hand_history_files()

    total_files = len(files)
    skipped = 0
    processed = 0
    total_hands = 0

    print(f"Found {total_files} hand history files")

    for i, file_path in enumerate(files, 1):
        if agg_file_exists(file_path):
            skipped += 1
        else:
            # Process the file and create .agg
            session_stats = process_session_file(file_path, force_reprocess=False, verbose=False)

            # Count hands from first player's N stat
            if session_stats:
                from .stats import Stat
                first_player = next(iter(session_stats.values()))
                hands_in_file = first_player.get(Stat.N, (0, 0))[0]
                total_hands += hands_in_file

                print(f"  [{i}/{total_files}] {file_path.name[:16]}..: Processed {hands_in_file} hands")

            processed += 1

    # Get the new last flush time
    last_flush = get_last_flush_time()

    print()
    print("─" * 80)
    print("Flush Summary:")
    print(f"  Files processed: {processed}")
    if skipped > 0:
        print(f"  Files skipped (cached): {skipped}")
    print(f"  Total hands: {total_hands}")
    print("─" * 80)

    return {
        'total_files': total_files,
        'skipped': skipped,
        'processed': processed,
        'total_hands': total_hands,
        'last_flush_time': last_flush
    }
