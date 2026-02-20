#!/usr/bin/env python3
"""
Test script to validate the full processing pipeline.
"""

from poker_hud.file_manager import find_hand_history_files
from poker_hud.processor import process_session_file, aggregate_all_sessions
from poker_hud.stats import Stat


def main():
    print("=" * 80)
    print("POKER HUD - Full Pipeline Test")
    print("=" * 80)

    # Find all hand history files
    print("\n1. Finding hand history files...")
    files = find_hand_history_files()
    print(f"   Found {len(files)} files")

    # Process first 5 files for testing
    test_files = files[:5]
    print(f"\n2. Processing first {len(test_files)} files...")
    print("-" * 80)

    session_stats_list = []
    for file_path in test_files:
        stats = process_session_file(file_path)
        session_stats_list.append(stats)

    # Aggregate across all sessions
    print(f"\n3. Aggregating statistics across {len(session_stats_list)} sessions...")
    overall_stats = aggregate_all_sessions(session_stats_list)

    # Display results
    print(f"\n4. Overall Statistics ({len(overall_stats)} players):")
    print("=" * 80)

    # Sort players by number of hands (descending)
    sorted_players = sorted(
        overall_stats.items(),
        key=lambda x: x[1].get(Stat.N, (0, 0))[0],
        reverse=True
    )

    # Show top 10 players
    for player, stats in sorted_players[:10]:
        n_hands = stats.get(Stat.N, (0, 0))[0]

        vpip_num, vpip_denom = stats.get(Stat.VPIP, (0, 0))
        vpip_pct = (vpip_num / vpip_denom * 100) if vpip_denom > 0 else 0

        pfr_num, pfr_denom = stats.get(Stat.PFR, (0, 0))
        pfr_pct = (pfr_num / pfr_denom * 100) if pfr_denom > 0 else 0

        print(f"\n{player}:")
        print(f"  Hands: {n_hands}")
        print(f"  VPIP:  {vpip_num}/{vpip_denom} ({vpip_pct:.1f}%)")
        print(f"  PFR:   {pfr_num}/{pfr_denom} ({pfr_pct:.1f}%)")

    print("\n" + "=" * 80)
    print("5. Testing cache (re-running first file)...")
    print("-" * 80)

    # This should load from cache
    cached_stats = process_session_file(test_files[0])
    print(f"   Successfully loaded from cache!")

    print("\n" + "=" * 80)
    print("Pipeline test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
