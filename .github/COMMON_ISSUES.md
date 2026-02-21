# Common Installation Issues

Quick reference for common problems and solutions.

## pip command not found

Try these alternatives (in order):

```bash
# Try pip3
pip3 install -e .

# Use python module syntax
python3 -m pip install -e .

# On some systems
python -m pip install -e .
```

**All of these do the same thing!** Use whichever works on your system.

## mbhud command not found after install

**Cause:** Python's bin directory not in PATH.

**Quick fix:**
```bash
# Find where it was installed
python3 -m pip show mbhud

# Run directly with python
python3 -m mbhud_cli init

# Or add to PATH (Mac/Linux)
export PATH="$HOME/.local/bin:$PATH"
```

## Click not installed error

```bash
pip3 install click
# or
python3 -m pip install click
```

## Permission denied

```bash
# Install for current user only
pip3 install --user -e .

# Or use python module syntax
python3 -m pip install --user -e .
```

## Already installed but not working

```bash
# Reinstall
pip3 install -e . --force-reinstall

# Or uninstall first
pip3 uninstall mbhud
pip3 install -e .
```

## Python version too old

mbHUD requires Python 3.7+

```bash
# Check version
python3 --version

# If < 3.7, update Python:
# Mac: brew install python@3.11
# Windows: Download from python.org
```

## Quick Command Reference

| Task | Command |
|------|---------|
| Install | `pip install -e .` or `pip3 install -e .` |
| Install Click | `pip install click` or `pip3 install click` |
| Check installed | `pip show mbhud` or `pip3 show mbhud` |
| Uninstall | `pip uninstall mbhud` or `pip3 uninstall mbhud` |
| Run without install | `python3 mbhud_cli.py init` |
| Check Python | `python3 --version` |
| Check pip | `pip3 --version` |

## Still having issues?

1. Check [INSTALL.md](../INSTALL.md) for detailed guide
2. Try running scripts directly: `python3 mbhud_init.py`
3. Open an issue on GitHub with your error message
