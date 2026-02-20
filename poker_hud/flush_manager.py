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


def flush_all(username: Optional[str] = None, verbose: bool = True) -> dict:
    """
    Flush all hand history files to .agg cache files.

    This processes all hand history files in the hand history directory.
    For each file:
    - If .agg exists: skip (already processed)
    - If .agg missing: process the file and create .agg

    Args:
        username: Username to process files for (uses config.USERNAME if None)
        verbose: If True, print progress messages

    Returns:
        Dictionary with flush statistics:
        {
            'total_files': int,
            'skipped': int,  # Already had .agg files
            'processed': int,  # Newly processed
            'last_flush_time': float  # Timestamp after flush
        }

    Example:
        >>> result = flush_all()
        >>> print(f"Processed {result['processed']} new files")
    """
    # Find all hand history files
    files = find_hand_history_files(username)

    total_files = len(files)
    skipped = 0
    processed = 0

    if verbose:
        print(f"Found {total_files} hand history files")
        print(f"{'='*80}")

    for i, file_path in enumerate(files, 1):
        if agg_file_exists(file_path):
            if verbose:
                agg_file = get_agg_file_path(file_path)
                print(f"[{i}/{total_files}] Skipping {file_path.name} (cached in {agg_file.name})")
            skipped += 1
        else:
            if verbose:
                print(f"[{i}/{total_files}] Processing {file_path.name}...")

            # Process the file and create .agg
            process_session_file(file_path, force_reprocess=False)
            processed += 1

    # Get the new last flush time
    last_flush = get_last_flush_time()

    if verbose:
        print(f"\n{'='*80}")
        print(f"Flush complete:")
        print(f"  Total files: {total_files}")
        print(f"  Skipped (already cached): {skipped}")
        print(f"  Newly processed: {processed}")
        print(f"  Last flush time: {last_flush}")

    return {
        'total_files': total_files,
        'skipped': skipped,
        'processed': processed,
        'last_flush_time': last_flush
    }
