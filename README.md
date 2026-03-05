# mbHUD - Poker HUD for Americas Cardroom

Real-time poker statistics tracker for ACR cash games.

## Quick Start

You will need Python installed.

**1. Install from the latest release:**

```bash
pip3 install https://github.com/andrewguo5/mbHUD/releases/download/v0.3.0/mbhud-0.3.0-py3-none-any.whl
```

**2. Configure your settings:**
```bash
mbhud init
```

**3. Start tracking:**
```bash
mbhud start
```

Join a room on ACR and the display will begin tracking your stats. Note that stats only update after the current hand has been completed.

**Requirements:** Python 3.7+ and Americas Cardroom client with hand history saving enabled.

If mbhud isn't recognized as a command, then your Python setup may be incomplete. On Windows, make sure both your Python folder and 
Scripts folder are added to your PATH environment variable, then try again. 

If Python works but mbhud doesn't, then it's likely that you need to also add your Scripts folder to your PATH.

---

## Features

- Tracks common and useful stats (VPIP, PFR, 3B, 4B, ATS, F3B, CBET, FCBET, BB100)
- Position-aware breakdowns (BTN, SB, BB, CO, HJ, etc.)
- Real-time display in command line (overlay is WIP)
- Detailed stats view for all players you've ever encountered in your hand history
- Everything is done via the command line (easier for nerds)

## Installation

### Option 1: Install from GitHub Release (Recommended)

Install directly from the [latest release](https://github.com/andrewguo5/mbHUD/releases/latest):

```bash
pip3 install https://github.com/andrewguo5/mbHUD/releases/download/v0.3.0/mbhud-0.3.0-py3-none-any.whl
```

Double check the latest version on the release page. I might not remember to update this README but both Claude and I will make an effort to do so.

### Option 2: Install from Source (For Development)

1. **Clone the repository:**
```bash
git clone https://github.com/andrewguo5/mbHUD.git
cd mbHUD
```

2. **Install the package:**
```bash
pip3 install -e .
```

This installs mbHUD in editable mode and creates the `mbhud` command. You can do this if you really want to see the source code, I guess.

**Note:** If you see "command not found: pip", use `pip3` instead. See [INSTALL.md](INSTALL.md) for detailed troubleshooting.

## Setup

Always run the initialization if it's your first time:
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

The program makes a local copy of your ACR hand history folder and pre-processes it into aggregated files. Both of these types of files are stored in the /data/ directory. This pre-processing action is referred to as a "flush" by the program internals. If you see "last flush time" that means the last time hand histories were synced and processed, not the last time 5 cards came out with the same suit! 

You can run `mbhud start`, which will perform a flush and then start the live tracker (recommended), or you can manually run `mbhud flush` followed by `mbhud live` or `mbhud stats`. Always flush before starting the tracker or viewing stats if you want up-to-date information.

To update the stats, run `mbhud flush` to process any new hands. When using the live tracker, you do not have to flush. It will watch the ACR hand history directory, detect any new hands, and update the stats automatically. However, the live process holds any stats on hands it sees in its process memory. After you're done, make sure you flush so that it saves that data to file. Stats only update after a hand is finished, so there is always a 1-hand delay. 

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
Display overall stats across all sessions (paginated, 20 players per page).

Use `--page` or `-p` to view additional pages:
```bash
mbhud stats --page 2
```

**View detailed stats with position breakdown:**
```bash
mbhud detailed
```
Display your stats broken down by position (BTN, SB, BB, CO, HJ, etc.) alongside aggregate stats.

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

**Windows CMD goes blank randomly during live tracking**
- Press Enter to restore the live tracker
- Possibly caused by QuickEdit mode
- Right Click the title bar -> Properties -> Deselect QuickEdit mode

## Requirements

- Python 3.7+
- Americas Cardroom client
- Hand history saving enabled in ACR

## Limitations

- CLI-based (no graphical overlay yet)
- Cash games only
