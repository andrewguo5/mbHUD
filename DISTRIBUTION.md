# Distribution Guide for mbHUD

## For You (The Distributor)

### Building the Package

The wheel file has already been built and is located at:
```
dist/mbhud-0.1.0-py3-none-any.whl
```

To rebuild the package after making changes:
```bash
python3 -m build
```

This will create/update:
- `dist/mbhud-0.1.0-py3-none-any.whl` (wheel file - give this to your friends)
- `dist/mbhud-0.1.0.tar.gz` (source distribution - optional)

### Sharing with Friends

Send them the **wheel file** (`mbhud-0.1.0-py3-none-any.whl`) along with the installation instructions below.

You can share via:
- Email attachment
- Dropbox/Google Drive link
- USB drive
- Any file sharing method

---

## For Your Friends (Installation Instructions)

### Prerequisites

1. **Python 3.7 or later** must be installed
   - Mac: Check with `python3 --version`
   - If not installed: Download from [python.org](https://www.python.org/downloads/)

2. **Americas Cardroom** must be installed with hand history saving enabled

### Installation Steps

1. **Download the wheel file** (`mbhud-0.1.0-py3-none-any.whl`) to your computer

2. **Open Terminal** (Mac) or **Command Prompt** (Windows)

3. **Navigate to the download location:**
   ```bash
   cd ~/Downloads
   ```

4. **Install the package:**
   ```bash
   pip3 install mbhud-0.1.0-py3-none-any.whl
   ```

   Or if `pip3` doesn't work:
   ```bash
   python3 -m pip install mbhud-0.1.0-py3-none-any.whl
   ```

5. **Verify installation:**
   ```bash
   mbhud --help
   ```

   You should see the list of available commands.

6. **Run initial setup:**
   ```bash
   mbhud init
   ```

   This will prompt you for:
   - Your ACR username
   - Your hand history directory path

7. **Start using mbHUD:**
   ```bash
   mbhud start
   ```

### Default Hand History Locations

- **Mac:** `~/Downloads/AmericasCardroom/handHistory/<username>/`
- **Windows:** `C:\ACR Poker\handHistory\<username>`

### Troubleshooting

**"Command not found: pip3"**
- Try: `python3 -m pip install mbhud-0.1.0-py3-none-any.whl`

**"Command not found: mbhud"**
- Add Python's bin directory to PATH (see below)
- Mac/Linux: Add to `~/.bashrc` or `~/.zshrc`:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```
- Restart terminal after adding

**"No module named 'click'"**
- The dependency should install automatically
- If not, run: `pip3 install click`

### Updating to a New Version

If you receive a newer version of the wheel file:

1. Uninstall the old version:
   ```bash
   pip3 uninstall mbhud
   ```

2. Install the new version:
   ```bash
   pip3 install mbhud-0.X.X-py3-none-any.whl
   ```

### Getting Help

For full documentation, see the README.md file or run:
```bash
mbhud --help
```

Available commands:
- `mbhud init` - Initial setup
- `mbhud start` - Start HUD with auto-update
- `mbhud live` - Start live tracker
- `mbhud stats` - View all player stats
- `mbhud detailed` - View your detailed position stats
- `mbhud flush` - Process new hand histories
- `mbhud clear-cache` - Clear aggregated cache
