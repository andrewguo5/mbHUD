# mbHUD - Poker HUD for Americas Cardroom

Real-time poker statistics tracker for ACR cash games.

## Features

- Tracks useful stats (VPIP, PFR, BB100)
- Real-time display in command line
- Fast caching system
- Simple setup and configuration

## Setup

Run the setup script:
```bash
python3 mbhud_init.py
```

This will:
- Prompt for your ACR username
- Prompt for your hand history directory
- Process existing hand histories
- Create configuration file

Default hand history locations:
- Mac: `~/Downloads/AmericasCardroom/handHistory/<username>/`
- Windows: `C:\ACR Poker\handHistory\<username>`

## Quick Start

### Start HUD (recommended):
```bash
python3 mbhud_start.py
```
Flushes cache then starts live HUD.

### Or run components separately:

**Flush cache (process hands):**
```bash
python3 mbhud_flush.py
```

**Start live HUD:**
```bash
python3 mbhud_live.py
```

**View overall stats:**
```bash
python3 display_stats.py
```

## Usage

### Live HUD (`mbhud_live.py`)

Displays real-time stats for active tables.

- Updates every 30 seconds
- Shows players in clockwise order from your seat
- Combines cached + live stats

**Stop:** Press `Ctrl+C`

### Flush (`mbhud_flush.py`)

Processes all hand histories into cached `.agg` files.

- Run before starting live HUD for first time
- Run periodically to update cache with completed sessions
- Skips already-processed files (fast)

**When to flush:**
- First time using mbHUD
- After finishing a session (to cache those hands)
- Before analyzing stats with `display_stats.py`

### Display Stats (`display_stats.py`)

Shows aggregate statistics across all sessions.

- Reads from cached `.agg` files only
- Does NOT include live (uncached) hands
- Sorts players by hand count

**Tip:** Run `mbhud_flush.py` first to include recent sessions

## Maintenance

### Clear cache:
```bash
python3 mbhud_clear_cache.py
```
Safely removes all cached files. Prompts for confirmation.

### Debug: Watch file updates
```bash
python3 watch_file.py
```
Shows latest hand as it's written to file.

## Troubleshooting

**"No active tables detected"**
- Play at least one hand (hand history file must update)
- Check hand history directory in `config.json`
- Run `python3 mbhud_init.py` to reconfigure

**Stats look wrong**
- Run `python3 mbhud_flush.py` to refresh cache
- Run `python3 mbhud_clear_cache.py` then flush to rebuild

**Live HUD not updating**
- Wait for hand to complete (stats update after each hand)

**Configuration issues**
- Check `config.json` in project root
- Run `python3 mbhud_init.py` to reconfigure

## Requirements

- Python 3.7+
- Americas Cardroom client
- Hand history saving enabled in ACR

## Limitations

- CLI-based (no graphical overlay yet)
- Cash games only
