# mbHUD - Poker HUD for Americas Cardroom

Real-time poker statistics tracker for ACR cash games.

## Features

- Tracks useful stats (VPIP, PFR, 3B, BB100)
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

## How it Works

The program makes a local copy of your ACR hand history folder and pre-processes it into aggregated files. Both of these files are stored in the /data/ directory. This pre-processing action is referred to as a "flush" by the program internals.

You can run `mbhud start`, which will perform a flush and then start the live tracker, or you can manually run `mbhud flush` followed by `mbhud live` or `mbhud stats`. 

To update the stats, run `mbhud flush` to process any new hands. When using the live tracker, you do not have to flush. It will watch the ACR hand history directory, detect any new hands, and update the stats automatically. Stats only update after a hand is finished, so there is always a 1-hand delay.

## Quick Start

### Start HUD (recommended):
```bash
mbhud start
```
Quick-start option. Run this after `mbhud init` and then you can start playing on ACR.

### View all commands:
```bash
mbhud --help
```

## Commands

**Initialize configuration:**
```bash
mbhud init
```
Run this once at the beginning or if you want to change your username or hand history directory location.

**Start HUD (with auto-flush):**
```bash
mbhud start
```
Essentially just `mbhud flush` followed by `mbhud live`.

**Start HUD (without flush):**
```bash
mbhud live
```

**Flush cache:**
```bash
mbhud flush
```
Finds any new hands and pre-processes them into aggregated files.

**View stats:**
```bash
mbhud stats
```
Display stats. 

**Clear cache:**
```bash
mbhud clear-cache
```
Delete the aggregated file cache. Use for debugging or maintenance purposes if you know what you're doing.

**Watch file updates (debug):**
```bash
mbhud watch
```
For debugger/dev use.

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
