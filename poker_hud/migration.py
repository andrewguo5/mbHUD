"""
One-time migration of legacy state into the fixed data root.

Older versions stored config.json + data/ either inside the package/clone tree
(location varied by install mode) or under ~/PokerData (a former default root).
This finds any such legacy store and moves it into the current data root.

Driven explicitly by `mbhud init`, never at import time.
"""

import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

from . import config


# The export summary written alongside hands/. Regenerated on the next export,
# but carried over so the old root is left empty rather than half-migrated.
EXPORT_MANIFEST = "manifest.json"


@dataclass
class LegacyStore:
    """A discovered legacy location holding data/, config.json and/or hands/."""
    root: Path
    data_dir: Optional[Path]      # legacy <root>/data if present
    config_file: Optional[Path]   # legacy <root>/config.json if present
    hands_dir: Optional[Path]     # legacy <root>/hands (exported JSONL) if present

    @property
    def hand_count_hint(self) -> int:
        """Rough count of hand-history files, for a human-readable prompt."""
        hh = self.data_dir / "handhistory" if self.data_dir else None
        return len(list(hh.glob("*.txt"))) if hh and hh.exists() else 0


def _candidate_roots() -> List[Path]:
    """Likely legacy roots, most-specific first.

    - package tree (editable install points here at the user's clone)
    - current working directory (user running from their clone)
    - ~/PokerData (former default data root before the fixed ~/.mbHUD root)
    """
    package_root = Path(__file__).resolve().parent.parent
    cwd = Path.cwd()
    former_default_root = Path.home() / "PokerData"
    # De-dupe while preserving order.
    seen, roots = set(), []
    for r in (package_root, cwd, former_default_root):
        if r not in seen:
            seen.add(r)
            roots.append(r)
    return roots


def find_legacy_store() -> Optional[LegacyStore]:
    """Return the first legacy store found, or None.

    A candidate counts only if it holds a data/ dir or config.json AND is not
    the new data root itself (avoids self-migration).
    """
    new_root = config.DATA_ROOT
    for root in _candidate_roots():
        if root == new_root:
            continue
        legacy_data = root / "data"
        legacy_config = root / "config.json"
        legacy_hands = root / "hands"
        has_data = legacy_data.is_dir()
        has_config = legacy_config.is_file()
        has_hands = legacy_hands.is_dir()
        if has_data or has_config or has_hands:
            return LegacyStore(
                root=root,
                data_dir=legacy_data if has_data else None,
                config_file=legacy_config if has_config else None,
                hands_dir=legacy_hands if has_hands else None,
            )
    return None


def migrate(store: Optional[LegacyStore]) -> List[str]:
    """Move a legacy store into the current data root; return what moved.

    Gap-filling only: a destination that already exists is left untouched, so
    this is safe to run repeatedly and never clobbers newer data.
    """
    if store is None:
        return []
    moved = []
    pairs = [
        (store.config_file, config.CONFIG_FILE),
        (store.data_dir, config.DATA_DIR),
        (store.hands_dir, config.DATA_ROOT / "hands"),
    ]
    # The manifest only travels with a real export root (one that has hands/).
    if store.hands_dir:
        pairs.append((store.root / EXPORT_MANIFEST, config.DATA_ROOT / EXPORT_MANIFEST))
    for src, dest in pairs:
        if src and src.exists() and not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dest))
            moved.append(f"{src} -> {dest}")
    return moved
