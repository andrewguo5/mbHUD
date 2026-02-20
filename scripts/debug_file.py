#!/usr/bin/env python3
"""Debug script to test specific file."""

from poker_hud.file_manager import find_hand_history_files, read_hand_history_file
from poker_hud.hand_parser import split_into_hands
from poker_hud.stat_calculators import calculate_bb100
import time

files = find_hand_history_files()
target = [f for f in files if 'Safety Harbor' in f.name and '20260209' in f.name][0]
print(f'Processing {target.name}...')

start = time.time()
content = read_hand_history_file(target)
print(f'Read file in {time.time() - start:.2f}s')

start = time.time()
hands = split_into_hands(content)
print(f'Split into {len(hands)} hands in {time.time() - start:.2f}s')

print('\nTesting BB/100 calculation on each hand:')
for i, hand in enumerate(hands):
    start = time.time()
    result = calculate_bb100(hand)
    elapsed = time.time() - start
    if elapsed > 0.1:
        print(f'Hand {i+1}: {elapsed:.3f}s - {len(result)} players')
    if elapsed > 1.0:
        print(f'  WARNING: Hand {i+1} took too long!')
        print(f'  First 500 chars: {hand[:500]}')
        break

print('\nDone')
