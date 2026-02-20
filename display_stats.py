#!/usr/bin/env python3
"""
Display overall statistics across all sessions in a readable format.
"""

from poker_hud.file_manager import find_hand_history_files
from poker_hud.processor import process_session_file, aggregate_all_sessions
from poker_hud.stats import Stat


def main():
    print("=" * 120)
    print("POKER HUD - Overall Statistics Across All Sessions")
    print("=" * 120)

    # Find and process all hand history files
    print("\nFinding and processing hand history files...")
    files = find_hand_history_files()
    print(f"Found {len(files)} files")
    print("-" * 120)

    # Process all files (will use cache if .agg exists)
    session_stats_list = []
    total_hands = 0

    for i, file_path in enumerate(files, 1):
        print(f"[{i}/{len(files)}] Processing {file_path.name}...")
        stats = process_session_file(file_path)
        session_stats_list.append(stats)

        # Count hands from first player's N stat
        if stats:
            first_player = next(iter(stats.values()))
            hands_in_session = first_player.get(Stat.N, (0, 0))[0]
            total_hands += hands_in_session

    # Aggregate across all sessions
    print(f"\n{'=' * 120}")
    print(f"Aggregating statistics across {len(session_stats_list)} sessions ({total_hands} total hands)...")
    overall_stats = aggregate_all_sessions(session_stats_list)

    # Display results
    print(f"\n{'=' * 120}")
    print(f"OVERALL STATISTICS - {len(overall_stats)} UNIQUE PLAYERS")
    print("=" * 120)
    print()

    # Sort players by number of hands (descending)
    sorted_players = sorted(
        overall_stats.items(),
        key=lambda x: x[1].get(Stat.N, (0, 0))[0],
        reverse=True
    )

    # Print header
    print(f"{'Player':<25} {'Hands':>8}  {'VPIP %':>8} {'VPIP':>12}  {'PFR %':>8} {'PFR':>12}  {'BB/100':>10}")
    print("-" * 120)

    # Print each player
    for player, stats in sorted_players:
        n_hands = stats.get(Stat.N, (0, 0))[0]

        vpip_num, vpip_denom = stats.get(Stat.VPIP, (0, 0))
        vpip_pct = (vpip_num / vpip_denom * 100) if vpip_denom > 0 else 0
        vpip_str = f"{vpip_num}/{vpip_denom}"

        pfr_num, pfr_denom = stats.get(Stat.PFR, (0, 0))
        pfr_pct = (pfr_num / pfr_denom * 100) if pfr_denom > 0 else 0
        pfr_str = f"{pfr_num}/{pfr_denom}"

        bb100_total, bb100_hands = stats.get(Stat.BB100, (0, 0))
        bb100 = (bb100_total / bb100_hands * 100) if bb100_hands > 0 else 0

        print(f"{player:<25} {n_hands:>8}  {vpip_pct:>7.1f}% {vpip_str:>12}  {pfr_pct:>7.1f}% {pfr_str:>12}  {bb100:>9.1f}")

    # Summary statistics
    print()
    print("=" * 120)
    print("SUMMARY")
    print("=" * 120)
    print(f"Total players tracked:  {len(overall_stats)}")
    print(f"Total sessions:         {len(session_stats_list)}")
    print(f"Total hands processed:  {total_hands}")

    # Find players with most hands
    if sorted_players:
        top_player, top_stats = sorted_players[0]
        top_hands = top_stats.get(Stat.N, (0, 0))[0]
        print(f"Most hands (player):    {top_player} ({top_hands} hands)")

    print()


if __name__ == "__main__":
    main()
