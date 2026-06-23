#!/usr/bin/env python3
"""
Export parsed hand histories as ParsedHand JSON for downstream projects.

mbHUD's pipeline parses raw ACR text into ParsedHand objects, aggregates stats,
then discards the ParsedHand. This script re-runs the parse and PERSISTS each
ParsedHand to a shared location as JSON Lines (one hand per line), so other
projects (e.g. the Poker Leak Detection System) can consume a clean, parsed,
source-agnostic representation instead of re-parsing raw text.

Output layout (mirrors source sessions):
    <out_dir>/hands/<session>.jsonl   # one ParsedHand JSON object per line
    <out_dir>/SCHEMA.md               # the interchange-format spec
    <out_dir>/manifest.json           # export summary (counts, source, time)

Each exported record is ParsedHand.to_dict() plus two self-contained extras:
    hero       -> hero username
    hero_seat  -> hero's seat number (int), or null if hero not dealt in

Amounts are raw chips/dollars exactly as parsed; metadata carries small_blind
and big_blind so any consumer can normalize to BB itself.
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from poker_hud import config
from poker_hud.hand_parser import split_into_hands
from poker_hud.hand_parser_v2 import parse_hand

DEFAULT_OUT_DIR = Path.home() / "PokerData"


def find_hero_seat(parsed, hero: str):
    """Return hero's seat number, or None if hero is not in the hand."""
    for seat, name in parsed.metadata.players.items():
        if name == hero:
            return seat
    return None


def run_export(out=None, hh_dir=None, hero=None, verbose=True):
    """Resolve defaults from mbHUD config and run the export. Returns manifest.

    Shared entry point for both the standalone CLI and `mbhud export`.
    """
    out = Path(out) if out else DEFAULT_OUT_DIR
    hh_dir = Path(hh_dir) if hh_dir else config.BACKUP_HANDHISTORY_DIR
    hero = hero or config.USERNAME

    if not hero:
        raise ValueError("hero username not set; pass hero or configure mbHUD config.json")
    if not hh_dir.is_dir():
        raise FileNotFoundError(f"hand history dir not found: {hh_dir}")

    if verbose:
        print("Exporting parsed hands")
        print(f"  source: {hh_dir}")
        print(f"  output: {out}")
        print(f"  hero:   {hero}")
        print("-" * 60)
    m = export(hh_dir, out, hero, verbose=verbose)
    if verbose:
        print("-" * 60)
        print(f"Done: {m['total_hands']} hands across {m['sessions']} sessions "
              f"({m['hands_with_hero']} with hero, {m['parse_failures']} parse failures)")
        print(f"Wrote {out}/hands/*.jsonl, manifest.json")
    return m


def export(hh_dir: Path, out_dir: Path, hero: str, verbose: bool = True):
    hands_dir = out_dir / "hands"
    hands_dir.mkdir(parents=True, exist_ok=True)

    txt_files = sorted(f for f in os.listdir(hh_dir) if f.endswith(".txt"))
    total_hands = 0
    total_with_hero = 0
    parse_fail = 0
    sessions = []

    for fname in txt_files:
        src = hh_dir / fname
        content = src.read_text(encoding="utf-8", errors="ignore")
        hand_texts = split_into_hands(content)

        out_name = fname[:-4] + ".jsonl"  # drop ".txt"
        out_path = hands_dir / out_name
        n_in_session = 0

        with open(out_path, "w", encoding="utf-8") as out:
            for hand_text in hand_texts:
                parsed = parse_hand(hand_text)
                if parsed is None:
                    parse_fail += 1
                    continue
                record = parsed.to_dict()
                hero_seat = find_hero_seat(parsed, hero)
                record["hero"] = hero
                record["hero_seat"] = hero_seat
                out.write(json.dumps(record, ensure_ascii=False) + "\n")
                n_in_session += 1
                total_hands += 1
                if hero_seat is not None:
                    total_with_hero += 1

        sessions.append({"source": fname, "output": out_name, "hands": n_in_session})
        if verbose:
            print(f"  {fname}: {n_in_session} hands -> {out_name}")

    manifest = {
        "format": "ParsedHand JSONL v2",
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "source_dir": str(hh_dir),
        "hero": hero,
        "sessions": len(sessions),
        "total_hands": total_hands,
        "hands_with_hero": total_with_hero,
        "parse_failures": parse_fail,
        "files": sessions,
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2))
    return manifest


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--out", type=Path, default=DEFAULT_OUT_DIR,
        help=f"Shared output directory (default: {DEFAULT_OUT_DIR})",
    )
    ap.add_argument(
        "--hh-dir", type=Path, default=config.BACKUP_HANDHISTORY_DIR,
        help="Source hand history dir (default: mbHUD's data/handhistory)",
    )
    ap.add_argument(
        "--hero", default=config.USERNAME,
        help="Hero username (default: from mbHUD config.json)",
    )
    args = ap.parse_args()

    try:
        run_export(out=args.out, hh_dir=args.hh_dir, hero=args.hero)
    except (ValueError, FileNotFoundError) as e:
        ap.error(str(e))


if __name__ == "__main__":
    main()
