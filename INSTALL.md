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
- Add `C:\Python3X\Scripts\` to your PATH environment variable
- Restart your terminal

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
