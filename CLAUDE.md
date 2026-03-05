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
- **Aggregate Files** (`.txt.agg`): Per-session statistics in v2 format: `player -> (STAT -> position -> (numerator, denominator))`
  - Position-bucketed: BTN, SB, BB, BTN-1 (CO), BTN-2 (HJ), etc.
  - "ALL" position contains aggregate across all positions
  - v1 format (legacy): position-collapsed, automatically converted to v2 on read
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

**Player Stats** (v2 format):
- Storage: `player -> (STAT -> position -> (numerator, denominator))`
- Stat-first ordering throughout the codebase (not position-first)
- Display: `percentage = 100 * numerator / denominator`
- Position labels: BTN (button), SB (small blind), BB (big blind), BTN-1 (cutoff/CO), BTN-2 (hijack/HJ), BTN-3 (UTG in 6-max), etc.

### Stat Definitions

**VPIP (Voluntarily Put money In Pot)**:
- Numerator: 1 if player's first action is call/raise, 0 if fold/check
- Denominator: 1 (counted per hand dealt to player)
- Parse first action in HOLE CARDS section before FLOP

**PFR (Pre-Flop Raise)**:
- Numerator: Number of times the player raises before FLOP
- Denominator: Number of opportunities to raise (number of times player's name appears in actions before FLOP)
- Only count hands where player had opportunity to act pre-flop

**3B (3-Bet)**:
- Numerator: Number of times the player 3-bets (re-raises) preflop
- Denominator: Number of opportunities to 3-bet (times facing a raise preflop)

**ATS (Attempt To Steal)**:
- Numerator: Number of times the player raises from steal positions when folded to
- Denominator: Number of opportunities (times in steal positions with action folded to player)
- Steal positions: CO (BTN-1), BTN, SB
- Only counts if no one has called or raised before player acts

**F3B (Fold to 3-Bet)**:
- Numerator: Number of times the player folds to a 3-bet after opening
- Denominator: Number of opportunities (times facing a 3-bet after opening)
- Only applies to the original raiser when facing a re-raise

**BB/100**:
- Numerator: Total big blinds won
- Denominator: Number of hands played
- Display: `(numerator / denominator) * 100`

## Processing Logic

### File Diff and Backup System

1. Check if `.txt.bak` exists for incoming hand history file
2. If exists, diff with current file
3. If no diff: file already processed, skip
4. If diff exists: delete `.txt.bak` and re-process entire file
5. After processing: write copy to `.txt.bak`

### Stat Aggregation (Position-Bucketed)

1. Parse hand history file into list of ParsedHand objects
2. For each ParsedHand:
   - Read players (exclude sitting out)
   - Calculate table positions (BTN, SB, BB, BTN-1, etc.)
   - Run stat calculators to get `player -> (STAT -> (num, denom))`
3. Aggregate by position:
   - Bucket stats by player position in each hand
   - Create stat -> position -> (num, denom) structure
   - Add "ALL" position with aggregate across all positions
4. Write session aggregates to `.txt.agg` file (v2 format)
5. Load all `.txt.agg` files into memory for HUD
6. Support backward compatibility for v1 files (auto-convert to v2 on read)

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

## Completed Features

1. ✅ Hand history parser (validate and split into hands)
2. ✅ Comprehensive stat calculators (VPIP, PFR, 3B, ATS, F3B, BB/100)
3. ✅ File diff/backup system
4. ✅ Position-bucketed aggregation system for `.txt.agg` files (v2 format)
5. ✅ In-memory stats view with pagination
6. ✅ Live HUD tracker
7. ✅ Detailed position breakdown display

## Future Development

1. HUD overlay display (macOS menu bar or screen overlay)
2. Additional stats (WTSD, W$SD, Agg%, etc.)
3. Tournament support
4. Database backend (currently file-based)
- Please keep comments and descriptions short, simple and terse.
- When creating a new release, please refer to the local ./release.sh script (not tracked by git) to perform the entire release in one step.