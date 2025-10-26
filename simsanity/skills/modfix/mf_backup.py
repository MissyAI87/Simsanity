"""
📦 modfix_backup.py
Handles backup creation, archive extraction, and quarantine logic
for the Sims 4 ModFixer tool.
Extracted from modfix.py for modular structure.
"""

import shutil
from pathlib import Path
from colorama import Fore
from tqdm import tqdm
import zipfile
import os
from datetime import datetime

# ──────────────────────────────
# 🗃 BACKUP & ARCHIVE HANDLING
# ──────────────────────────────

def zip_backup(src: Path, dst: Path) -> None:
    """
    Create a ZIP backup of all files under `src` and store it at `dst`.
    """
    with zipfile.ZipFile(dst, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in tqdm(list(src.rglob("*")), desc="Creating backup ZIP"):
            if f.is_file():
                zf.write(f, f.relative_to(src))
    print(f"{Fore.GREEN}✅ Backup created at {dst}{Fore.RESET}")


def extract_archives(archives: list[Path], qdir: Path) -> None:
    """
    Extract archives to the given quarantine or destination directory.
    """
    extracted = []
    for arc in archives:
        try:
            shutil.unpack_archive(arc, qdir / arc.stem)
            extracted.append(arc)
        except Exception as e:
            print(f"{Fore.YELLOW} ! Failed to extract {arc} → {e}{Fore.RESET}")

    if extracted:
        print(f"{Fore.GREEN}📦 Extracted {len(extracted)} archive(s) to {qdir}{Fore.RESET}")


# ──────────────────────────────
# 🧰 QUARANTINE MANAGEMENT
# ──────────────────────────────

def quarantine_file(file_path: Path, quarantine_dir: Path, log_file: Path, log_callback=print) -> None:
    """
    Move a suspicious or unwanted file to the quarantine directory and log the action.
    """
    try:
        quarantine_dir.mkdir(parents=True, exist_ok=True)
        target = quarantine_dir / file_path.name
        if file_path.exists():
            shutil.move(str(file_path), str(target))
            log_callback(f"{Fore.YELLOW}⚠️ Moved to quarantine: {file_path.name}{Fore.RESET}")
            with open(log_file, "a") as logf:
                logf.write(f"{datetime.now().isoformat()} - Moved to quarantine: {file_path.name}\n")
    except Exception as e:
        log_callback(f"{Fore.RED}❌ Failed to quarantine {file_path}: {e}{Fore.RESET}")


def quarantine_batch(file_list: list[Path], quarantine_dir: Path, log_file: Path, log_callback=print) -> None:
    """
    Quarantine multiple files in one call.
    """
    for f in file_list:
        quarantine_file(f, quarantine_dir, log_file, log_callback)
