# Installation Guide

## Quick Install

```bash
# Clone the repository
git clone https://github.com/andrewguo5/mbHUD.git
cd mbHUD

# Install the package (use pip3 if pip doesn't work)
pip install -e .

# Run setup
mbhud init
```

That's it! You now have the `mbhud` command available.

**Note:** If you see "command not found: pip", try `pip3` instead, or see [Troubleshooting](#troubleshooting) below.

## Detailed Steps

### 1. Install Python

Make sure you have Python 3.7 or later installed:

```bash
python3 --version
```

If not installed:
- **Mac**: Install via [python.org](https://www.python.org/downloads/) or Homebrew: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)

### 2. Clone the Repository

```bash
git clone https://github.com/andrewguo5/mbHUD.git
cd mbHUD
```

### 3. Install the Package

**Option A: Editable Install (Recommended for Development)**
```bash
pip install -e .
```
Changes to the code take effect immediately.

**Option B: Regular Install**
```bash
pip install .
```
Need to reinstall after making changes.

### 4. Verify Installation

```bash
mbhud --help
```

You should see the command list.

### 5. Run Setup

```bash
mbhud init
```

Follow the prompts to configure your username and hand history directory.

## Troubleshooting

### "command not found: pip"

**Cause:** pip is not installed or not in PATH.

**Solution:**

**Check if pip3 works instead:**
```bash
pip3 --version
```

If `pip3` works, use it instead of `pip`:
```bash
pip3 install -e .
```

**If pip3 also doesn't work:**

**Mac:**
```bash
# Install pip using Python
python3 -m ensurepip --upgrade

# Or reinstall Python with Homebrew
brew install python3
```

**Windows:**
```bash
# Reinstall Python from python.org, make sure to check "Add to PATH"
# Or use:
python -m ensurepip --upgrade
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt install python3-pip

# Fedora
sudo dnf install python3-pip
```

**Alternative - use python -m pip:**
```bash
# This always works if Python is installed
python3 -m pip install -e .
```

### "command not found: mbhud"

**Cause:** Python's bin directory is not in your PATH.

**Solution:**

**Mac/Linux:**
```bash
# Find where pip installed it
which mbhud

# If empty, add Python's bin to PATH
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc
```

**Windows:**

First, find where Python installed the Scripts folder:
```cmd
python -c "import site; print(site.USER_BASE + '\\Scripts')"
```

This will output something like:
```
C:\Users\YourName\AppData\Roaming\Python\Python311\Scripts
```

Now add this path to your PATH environment variable:

1. Press Windows key and search for "Environment Variables"
2. Click "Edit the system environment variables"
3. Click the "Environment Variables" button at the bottom
4. Under "User variables" (top section), find and select "Path"
5. Click "Edit"
6. Click "New"
7. Paste the Scripts path from above (e.g., `C:\Users\YourName\AppData\Roaming\Python\Python311\Scripts`)
8. Click "OK" on all dialogs
9. **Close and reopen your terminal/command prompt** (required for changes to take effect)
10. Test: `mbhud --help`

**Alternative (if you don't want to modify PATH):**

You can always run mbhud using:
```cmd
python -m cli <command>
```

For example:
```cmd
python -m cli init
python -m cli start
python -m cli stats
```

### "No module named 'click'"

**Cause:** Click dependency not installed.

**Solution:**
```bash
pip install click
```

Or reinstall:
```bash
pip install -e .
```

### Permission Denied

**Cause:** Missing write permissions.

**Solution:**

**Mac/Linux:**
```bash
pip install --user -e .
```

**Windows:**
Run terminal as Administrator.

## Uninstall

```bash
pip uninstall mbhud
```

## Update

```bash
cd mbHUD
git pull
pip install -e . --upgrade
```
