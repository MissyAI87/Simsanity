"""
🧹 modfix_cleaner.py
Handles cleaning, deletion, and maintenance tasks for Sims 4 ModFixer.
Extracted from modfix.py for modular structure.
"""

from pathlib import Path
from colorama import Fore
import os

SAFE_ROOT_KEYWORDS = ["Electronic Arts", "The Sims 4"]

def is_within_ea_mods(path: Path) -> bool:
    """Ensure all operations are confined to Electronic Arts/The Sims 4/Mods."""
    try:
        parts = [p.lower() for p in path.parts]
        return any("electronic arts" in p or "the sims 4" in p for p in parts) and "mods" in parts
    except Exception:
        return False

# ──────────────────────────────
# 🧹 FILE CLEANUP & MAINTENANCE
# ──────────────────────────────

def clean_garbage_files(mods: Path) -> None:
    """
    Remove common unwanted system files from the Mods folder.
    Example: .DS_Store, Thumbs.db, desktop.ini
    """
    garbage = {".DS_Store", "Thumbs.db", "desktop.ini"}
    removed = []

    for file in mods.rglob("*"):
        if file.name in garbage:
            if not is_within_ea_mods(file):
                print(f"🚫 [SAFEGUARD] Skipping unsafe delete outside EA Mods: {file}")
                continue
            try:
                file.unlink()
                removed.append(file)
            except Exception as e:
                print(f"{Fore.YELLOW} ! Failed to delete {file} → {e}{Fore.RESET}")

    if removed:
        print(f"{Fore.GREEN}🧹 Removed {len(removed)} garbage files{Fore.RESET}")


def clear_keyword_files(keywords, path, base=None):
    """
    Clean Sims 4 directory of known problematic files
    (e.g., lastexception, lastuiexception, lastcrash).
    Skips folders that match keywords.
    """
    print(f"{Fore.MAGENTA}🔍 Scanning Sims 4 folder for keyword-matching files...{Fore.RESET}")
    deleted = []
    path = Path(path)

    for file in path.rglob("*"):
        if not file.is_file():
            print(f"{Fore.CYAN}🛑 Skipped folder (not a file): {file.name}{Fore.RESET}")
        print(f"  Checking: {file.name}")

        if file.is_file() and any(kw.lower() in file.name.lower() for kw in keywords):
            if not is_within_ea_mods(file):
                print(f"🚫 [SAFEGUARD] Skipping unsafe keyword delete outside EA Mods: {file}")
                continue
            try:
                file.unlink()
                deleted.append(file)
                print(f"{Fore.RED}  🗑 Deleted: {file.name}{Fore.RESET}")
            except Exception as e:
                print(f"{Fore.YELLOW} ! Failed to delete {file} → {e}{Fore.RESET}")

        elif not file.is_file() and any(kw.lower() in file.name.lower() for kw in keywords):
            print(f"{Fore.CYAN}🛑 Skipped folder (matches keyword, not deleted): {file.name}{Fore.RESET}")

    if deleted:
        print(f"{Fore.GREEN}🧹 Removed {len(deleted)} keyword files from {base or path}{Fore.RESET}")

    return deleted


def remove_empty_folders(path: Path, log_callback=print, aggressive: bool = False) -> None:
    """
    Remove empty directories inside a given path and optionally perform
    deeper cleanup (temporary/log/backup files). Reports live to ModFix stream.
    """
    removed_folders = 0
    removed_extra = 0

    # Normal folder cleanup
    for root, dirs, files in os.walk(path, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            if not is_within_ea_mods(dir_path):
                log_callback(f"🚫 [SAFEGUARD] Skipping unsafe folder removal outside EA Mods: {dir_path}")
                continue
            if not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    removed_folders += 1
                    log_callback(f"🗑 Removed empty folder: {dir_path}")
                except Exception as e:
                    log_callback(f"⚠️ Error removing {dir_path}: {e}")

    # Aggressive mode — remove junk files
    if aggressive:
        junk_exts = {".tmp", ".log", ".bak"}
        for file in path.rglob("*"):
            if file.suffix.lower() in junk_exts:
                if not is_within_ea_mods(file):
                    log_callback(f"🚫 [SAFEGUARD] Skipping unsafe file delete outside EA Mods: {file}")
                    continue
                try:
                    file.unlink()
                    removed_extra += 1
                    log_callback(f"🧼 Deleted leftover file: {file.name}")
                except Exception as e:
                    log_callback(f"⚠️ Could not delete {file}: {e}")

    if removed_folders or removed_extra:
        log_callback(f"✅ Cleanup complete — {removed_folders} empty folders, {removed_extra} junk files removed.")
    else:
        log_callback("✨ No empty folders or junk files found — Mods folder already clean.")
