#!/usr/bin/env python3
"""
Simple test script to verify file manager functionality.
"""

from poker_hud.file_manager import (
    find_hand_history_files,
    get_file_info,
    read_hand_history_file,
)


def main():
    print("Finding hand history files...")
    files = find_hand_history_files()
    print(f"Found {len(files)} files\n")

    if files:
        # Show info for first few files
        print("File metadata (first 5):")
        for file_path in files[:5]:
            info = get_file_info(file_path)
            print(f"  {info['filename']}")
            print(f"    Date: {info.get('date', 'N/A')}")
            print(f"    Table: {info.get('table_name', 'N/A')}")
            print(f"    Stakes: {info.get('min_buyin', '?')}-{info.get('max_buyin', '?')}")
            print()

        # Read first file as example
        print("\nReading first file...")
        first_file = files[0]
        content = read_hand_history_file(first_file)
        lines = content.split('\n')
        print(f"File: {first_file.name}")
        print(f"Total lines: {len(lines)}")
        print(f"Total characters: {len(content)}")
        print("\nFirst 20 lines:")
        print("-" * 80)
        for line in lines[:20]:
            print(line)


if __name__ == "__main__":
    main()
