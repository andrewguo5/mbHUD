# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

mbHUD is a poker HUD (Heads-Up Display) for online poker that displays real-time statistics about opponents at the table. The system processes hand history files from Americas Cardroom (ACR) to compute and display player statistics.

## Architecture

### Data Flow Pipeline

1. **Hand History Ingestion**: ACR downloads hand histories to a local folder
2. **Diff Detection**: Compare new hand history files with `.txt.bak` files to identify unprocessed hands
3. **Hand Parsing**: Split files into individual hands and validate format
4. **Stat Calculation**: Process each hand to compute statistics (VPIP, PFR, etc.) for each player
5. **Aggregation**: Combine per-session `.txt.agg` files into in-memory view
6. **HUD Display**: Show statistics as percentages overlaid on poker table

### File Structure

- **Hand History Files**: Raw `.txt` files downloaded from ACR
- **Backup Files** (`.txt.bak`): Processed hand history files stored locally to track what's been processed
- **Aggregate Files** (`.txt.agg`): Per-session statistics in format: `player -> (STAT -> (numerator, denominator))`
- **In-Memory View**: Real-time aggregate of all `.txt.agg` files for HUD display

### Core Data Structures

**Hand Representation**:
- Sections: HOLE CARDS, FLOP, TURN, RIVER, SHOWDOWN (optional)
- Player list (excluding sitting out)
- Actions per betting round

**Stat Calculation**:
- Each stat is a function: `HAND -> (player -> (int, int))`
- Returns `(numerator, denominator)` for each player
- Some stats use "opportunities" as denominator instead of total hands seen
- Stats can be combined (e.g., VPIP+PFR calculated together for efficiency)

**Player Stats**:
- `player -> (STAT -> (numerator, denominator))`
- Display: `percentage = 100 * numerator / denominator`

### Stat Definitions

**VPIP (Voluntarily Put money In Pot)**:
- Numerator: 1 if player's first action is call/raise, 0 if fold/check
- Denominator: 1 (counted per hand dealt to player)
- Parse first action in HOLE CARDS section before FLOP

**PFR (Pre-Flop Raise)**:
- Numerator: Number of times the player raises before FLOP
- Denominator: Number of opportunities to raise (number of times player's name appears in actions before FLOP)
- Only count hands where player had opportunity to act pre-flop

## Processing Logic

### File Diff and Backup System

1. Check if `.txt.bak` exists for incoming hand history file
2. If exists, diff with current file
3. If no diff: file already processed, skip
4. If diff exists: delete `.txt.bak` and re-process entire file
5. After processing: write copy to `.txt.bak`

### Stat Aggregation

1. Parse hand history file into list of HAND objects
2. For each HAND:
   - Read players (exclude sitting out)
   - Initialize stats with `n -> 1` (hands seen)
   - Run stat functions to get `player -> (STAT -> (num, denom))`
3. Aggregate across all hands in file
4. Write session aggregates to `.txt.agg` file
5. Load all `.txt.agg` files into memory for HUD

## Hand History Format Notes

### Example Hand Structure
```
Hand #2674805038 - Holdem (No Limit) - $0.02/$0.05 - 2026/02/20 01:13:13 UTC
Cherry Hills 6-max Seat #3 is the button
Seat 1: Kolunio5 ($5.27)
Seat 2: Kiman11 ($7.74) is sitting out
...
*** HOLE CARDS ***
Dealt to aampersands [Qs 2s]
<actions>
*** FLOP *** [Kd Kh 6c]
<actions>
*** TURN *** [...]
<actions>
*** RIVER *** [...]
<actions>
*** SUMMARY ***
...
```

### Parsing Considerations

- **Cannot rely on SUMMARY section**: Doesn't include all action details (e.g., "folded on Pre-Flop" doesn't indicate if player raised first)
- **Must parse actions directly**: Iterate through action lines in each betting round
- **Player identification**: Track unique player IDs across hands
- **Sitting out players**: Exclude from stat calculations

## Development Priorities

1. Hand history parser (validate and split into hands)
2. VPIP/PFR stat calculators as proof of concept
3. File diff/backup system
4. Aggregation system for `.txt.agg` files
5. In-memory stats view
6. HUD overlay display (macOS menu bar or screen overlay)
