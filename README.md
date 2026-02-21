# mbHUD - Poker HUD for Americas Cardroom

Real-time poker statistics tracker for ACR cash games.

## Features

- Tracks useful stats (VPIP, PFR, BB100)
- Real-time display in command line
- Simple setup and configuration

## Installation

1. **Clone the repository:**
```bash
git clone https://github.com/andrewguo5/mbHUD.git
cd mbHUD
```

2. **Install the package:**
```bash
pip install -e .
```

This installs mbHUD and creates the `mbhud` command.

**Note:** If you see "command not found: pip", use `pip3` instead. See [INSTALL.md](INSTALL.md) for detailed troubleshooting.

## Setup

Run the initialization:
```bash
mbhud init
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
mbhud start
```
Flushes cache then starts live HUD.

### View all commands:
```bash
mbhud --help
```

## Commands

**Initialize configuration:**
```bash
mbhud init
```

**Start HUD (with auto-flush):**
```bash
mbhud start
```

**Start HUD (without flush):**
```bash
mbhud live
```

**Flush cache:**
```bash
mbhud flush
```

**View stats:**
```bash
mbhud stats
```

**Clear cache:**
```bash
mbhud clear-cache
```

**Watch file updates (debug):**
```bash
mbhud watch
```

## How It Works

### Live HUD

Displays real-time stats for active tables.

- Updates every 30 seconds
- Shows players in clockwise order from your seat
- Combines cached + live stats
- Press `Ctrl+C` to stop

### Flush

Processes hand histories into cached `.agg` files.

- Skips already-processed files (fast)
- Only processes new/modified files
- Run after sessions to cache hands

### Stats Display

Shows aggregate statistics across all sessions.

- Reads from cached `.agg` files
- Includes live hands after flush
- Sorts players by hand count

## Troubleshooting

**"No active tables detected"**
- Play at least one hand (hand history must update)
- Check hand history directory in `config.json`
- Run `mbhud init` to reconfigure

**Stats look wrong**
- Run `mbhud flush` to refresh cache
- Run `mbhud clear-cache` then flush to rebuild

**Live HUD not updating**
- Wait for hand to complete (updates after each hand)

**Configuration issues**
- Check `config.json` in project root
- Run `mbhud init` to reconfigure

**Command not found**
- Make sure you ran `pip install -e .`
- Check that Python's bin directory is in PATH

## Requirements

- Python 3.7+
- Americas Cardroom client
- Hand history saving enabled in ACR

## Limitations

- CLI-based (no graphical overlay yet)
- Cash games only
