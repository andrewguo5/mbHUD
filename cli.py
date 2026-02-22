#!/usr/bin/env python3
"""
mbHUD CLI - Main command-line interface

Provides a unified entry point for all mbHUD commands.
"""

import click


@click.group()
@click.version_option(version='0.1.0')
def cli():
    """mbHUD - Poker statistics tracker for Americas Cardroom"""
    pass


@cli.command()
def init():
    """Initialize mbHUD configuration (first-time setup)"""
    from scripts.mbhud_init import main
    main()


@cli.command()
def start():
    """Start the live HUD (flushes cache first, then runs HUD)"""
    from scripts.mbhud_start import main
    main()


@cli.command()
def live():
    """Start the live HUD without flushing"""
    from scripts.mbhud_live import main
    main()


@cli.command()
def flush():
    """Flush hand histories to cache"""
    from scripts.mbhud_flush import main
    main()


@cli.command()
def stats():
    """Display overall statistics across all sessions"""
    from scripts.display_stats import main
    main()


@cli.command()
def detailed():
    """Display detailed stats with position breakdown for hero"""
    from scripts.detailed_stats import main
    main()


@cli.command()
def clear_cache():
    """Clear all cached .agg files"""
    from scripts.mbhud_clear_cache import main
    main()


@cli.command()
def watch():
    """Watch hand history files for updates (debug utility)"""
    from scripts.watch_file import main
    main()


@cli.command()
def backup():
    """Backup hand history files to persistent storage"""
    from scripts.backup_handhistory import backup_handhistory
    backup_handhistory()


if __name__ == '__main__':
    cli()
