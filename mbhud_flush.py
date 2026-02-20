#!/usr/bin/env python3
"""
CLI command to flush all hand history files to .agg cache files.

Usage:
    python mbhud_flush.py
    or
    ./mbhud_flush.py
"""

from poker_hud.flush_manager import flush_all


def main():
    print("mbHUD Flush Utility")
    print("=" * 80)
    print()

    result = flush_all(verbose=True)

    print()
    print("=" * 80)
    print("Flush completed successfully!")


if __name__ == "__main__":
    main()
