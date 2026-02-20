# mbHUD - Poker HUD for Americas Cardroom

Real-time poker statistics tracker for ACR cash games.

## Features

- Tracks useful stats (VPIP, PFR, BB100)
- Real-time display in command line

## Setup

1. Set your ACR username in `poker_hud/config.py`:
   ```python
   USERNAME = "your_username_here"
   ```

2. Ensure ACR saves hand histories to default location:
   - Mac: `~/Downloads/AmericasCardroom/handHistory/<username>/`
   - Windows: `C:\ACR Poker\handHistory\<username>`

## Quick Start

### Initial flush (process all existing hands):
```bash
python3 mbhud_flush.py
```

### Run live HUD:
```bash
python3 mbhud_live.py
```

### View overall stats (all sessions):
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

## Troubleshooting

**"No active tables detected"**
- Play at least one hand (hand history file must update)
- Check that hand histories are saved to expected directory
- Verify username in `config.py` matches ACR username

**Stats look wrong**
- Run `python3 mbhud_flush.py` to refresh cache
- Delete `data/agg_files/` and re-flush to rebuild from scratch

**Live HUD not updating**
- Wait for hand to complete (stats update after each hand)

### Debug: Watch file updates
```bash
python3 watch_file.py
```
Shows latest hand as it's written to file.

### Force reprocess all files
```bash
# Delete cache
rm -rf data/agg_files/

# Rebuild
python3 mbhud_flush.py
```

## Requirements

- Python 3.7+
- Americas Cardroom client
- Hand history saving enabled in ACR

## Limitations

- CLI-based (no graphical overlay yet)
- Cash games only
