import os
import shutil
import argparse
from pathlib import Path

# ── CONFIG ──────────────────────────────────────────────────────────────────
DESKTOP = Path.home() /"OneDrive - Lear Corporation" / "Desktop"

SKIP_FOLDERS = {"Alex"}

APP_EXTENSIONS = {
    ".app", ".exe", ".lnk", ".msi", ".dmg", ".pkg", ".appimage", ".deb", ".rpm", ".snap"
}

# ── NAME-BASED RULES ───────────────────────────────────────────────────────
# If any keyword (case-insensitive) appears in the file name (without extension),
# the file is moved to the corresponding folder.
# First match wins — order matters. Customize these to fit your desktop.
NAME_RULES: list[tuple[list[str], str]] = [
    # ( [keywords], destination_folder )
    (["2-way", "MX5", "Hyundai", "4-way"],        "Hyundai MX5"),
    (["Gravity", "Lucid Gravity", "Transys"],      "Lucid Gravity"),
    (["Earth", "Touring", "Lucid Lumbar"],         "Lucid Earth"),
    (["Lucid"],                                   "Lucid Programs"),
    (["DT", "WS", "Shift", "Adient"],           "Stellantis WS_WL_DT"),
    (["tax", "w2", "1099"],                 "Test Requests"),
    (["meeting", "agenda", "minutes"],      "Test Reports"),
    (["GM", "T1", "Energy Tables"],      "General Motors"),
    (["TCS", "TC", "analysis"],     "TCS Documents"),
    (["NX5"],     "NX5 Program"),
]

# ── LOGIC ───────────────────────────────────────────────────────────────────

def match_name(filename_stem: str) -> str | None:
    lower = filename_stem.lower()
    for keywords, folder in NAME_RULES:                          # ← for loop
        if any(kw.lower() in lower for kw in keywords if kw):   # ← indented inside it
            return folder
    return None



def gather_moves(desktop: Path) -> list[tuple[Path, Path]]:
    moves: list[tuple[Path, Path]] = []

    for item in desktop.iterdir():
        if item.is_dir() or item.name.startswith("."):
            continue

        ext = item.suffix.lower()

        if ext in APP_EXTENSIONS:
            continue

        folder = match_name(item.stem)

        if folder:
            dest = desktop / folder / item.name
        else:
            # Unknown → Unsorted, organized by file type
            ext_label = ext.lstrip(".").upper() if ext else "NO_EXTENSION"
            dest = desktop / "Unsorted" / ext_label / item.name

        moves.append((item, dest))

    return moves


def resolve_conflicts(moves: list[tuple[Path, Path]]) -> list[tuple[Path, Path]]:
    resolved = []
    for src, dst in moves:
        if dst.exists() and dst != src:
            stem, suffix = dst.stem, dst.suffix
            counter = 1
            while dst.exists():
                dst = dst.parent / f"{stem} ({counter}){suffix}"
                counter += 1
        resolved.append((src, dst))
    return resolved


def execute(moves: list[tuple[Path, Path]], dry_run: bool = True):
    if not moves:
        print("✅  Desktop is already tidy — nothing to move.")
        return

    label = "DRY RUN" if dry_run else "MOVING"
    print(f"\n{'─'*60}")
    print(f"  {label} — {len(moves)} file(s)")
    print(f"{'─'*60}\n")

    for src, dst in moves:
        rel_src = src.relative_to(DESKTOP)
        rel_dst = dst.relative_to(DESKTOP)
        print(f"  {'→' if dry_run else '✓'}  {rel_src}  ➜  {rel_dst}")

        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

    print(f"\n{'─'*60}")
    if dry_run:
        print("  This was a dry run. Re-run with --execute to apply changes.")
    else:
        print("  Done! All files moved.")
    print(f"{'─'*60}\n")


# ── ENTRY POINT ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Organize desktop files.")
    parser.add_argument(
        "--execute", action="store_true",
        help="Actually move files. Without this flag the script runs in dry-run mode.",
    )
    args = parser.parse_args()

    moves = gather_moves(DESKTOP)
    moves = resolve_conflicts(moves)
    execute(moves, dry_run=not args.execute)
