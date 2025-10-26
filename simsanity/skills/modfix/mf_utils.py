"""
🧰 modfix_utils.py
Shared utility functions for ModFix modules:
color printing, hashing, path validation, and file helpers.
"""


import hashlib
from colorama import Fore, Style
from pathlib import Path
import os

# ──────────────────────────────
# 🌐 STATE VARIABLES
# ──────────────────────────────
MANUAL_MODS_PATH = None
MODFIX_STATE = {"manual_required": False}
CACHE_FILE = Path(__file__).parent / "manual_mods_path.txt"

# ──────────────────────────────
# 🎨 COLOR HELPERS
# ──────────────────────────────
def c(msg: str, col: str = Fore.WHITE) -> str:
    """Return a colorized string for console output."""
    return f"{col}{msg}{Style.RESET_ALL}"


# ──────────────────────────────
# 🔍 PATH VALIDATION
# ──────────────────────────────
def validate_mod_paths() -> Path:
    global MANUAL_MODS_PATH
    global MODFIX_STATE
    """
    Ensure the Sims 4 Mods folder exists and return it.
    Dynamically searches for the Mods folder instead of using a hardcoded path.
    """
    from core.utils import get_ea_folder

    # Dynamically detect EA folder
    ea_folder = get_ea_folder(auto_confirm=True)

    # Build candidate Mods paths to search
    possible_mods = [
        ea_folder / "The Sims 4" / "Mods",
        ea_folder / "Mods",
        ea_folder.parent / "Mods",
    ]

    # Search for a valid Mods folder
    for mods_path in possible_mods:
        if mods_path.exists():
            print(f"{Fore.GREEN}✅ Found Mods folder at: {mods_path}{Fore.RESET}")
            # Ensure the returned path is the Mods folder, not its parent
            mods_dir = Path(MANUAL_MODS_PATH or mods_path or ea_folder)
            if mods_dir.name.lower() != "mods":
                possible_mods = list(mods_dir.glob("**/Mods"))
                if possible_mods:
                    mods_dir = possible_mods[0]
            return mods_dir

    # Shallow scan if not found
    print(f"{Fore.YELLOW}⚠️ Mods folder not found in typical locations, performing a quick scan...{Fore.RESET}")
    for root, dirs, _ in os.walk(ea_folder.parent):
        for d in dirs:
            if d.lower() == "mods":
                mods_path = Path(root) / d
                print(f"{Fore.GREEN}✅ Found Mods folder by scan: {mods_path}{Fore.RESET}")
                # Ensure the returned path is the Mods folder, not its parent
                mods_dir = Path(MANUAL_MODS_PATH or mods_path or ea_folder)
                if mods_dir.name.lower() != "mods":
                    possible_mods = list(mods_dir.glob("**/Mods"))
                    if possible_mods:
                        mods_dir = possible_mods[0]
                return mods_dir

    # Detect if running under Flask/web server
    import sys
    if "flask" in sys.modules or "werkzeug" in sys.modules:
        if MANUAL_MODS_PATH and Path(MANUAL_MODS_PATH).exists():
            print(f"{Fore.GREEN}✅ Using manually provided Mods folder: {MANUAL_MODS_PATH}{Fore.RESET}")
            # Ensure the returned path is the Mods folder, not its parent
            mods_dir = Path(MANUAL_MODS_PATH or ea_folder)
            if mods_dir.name.lower() != "mods":
                possible_mods = list(mods_dir.glob("**/Mods"))
                if possible_mods:
                    mods_dir = possible_mods[0]
            return mods_dir

        # Check persistent cache
        if CACHE_FILE.exists():
            cached = CACHE_FILE.read_text().strip()
            if cached and Path(cached).exists():
                MANUAL_MODS_PATH = cached
                print(f"{Fore.GREEN}✅ Loaded cached Mods folder: {cached}{Fore.RESET}")
                # Ensure the returned path is the Mods folder, not its parent
                mods_dir = Path(MANUAL_MODS_PATH or ea_folder)
                if mods_dir.name.lower() != "mods":
                    possible_mods = list(mods_dir.glob("**/Mods"))
                    if possible_mods:
                        mods_dir = possible_mods[0]
                return mods_dir

        print(f"{Fore.CYAN}🌐 Running in web mode — requesting manual Mods folder path via UI.{Fore.RESET}")
        MODFIX_STATE["manual_required"] = True
        return "manual_required"

    # --- Final fallback: ask the user to drop the folder path ---
    print(f"{Fore.YELLOW}⚠️ Could not locate a Mods folder automatically.{Fore.RESET}")
    print("💡 Tip: You can drag and drop your Mods folder here, then press Enter.")
    manual = input("Drop your 'Mods' folder path: ").strip('" ').strip("'")
    manual_path = Path(manual).expanduser().resolve()

    if manual_path.exists():
        print(f"{Fore.GREEN}✅ Using manual Mods folder: {manual_path}{Fore.RESET}")
        # Ensure the returned path is the Mods folder, not its parent
        mods_dir = Path(manual_path)
        if mods_dir.name.lower() != "mods":
            possible_mods = list(mods_dir.glob("**/Mods"))
            if possible_mods:
                mods_dir = possible_mods[0]
        return mods_dir
    else:
        print(f"{Fore.RED}❌ Invalid path: {manual_path}{Fore.RESET}")

    raise FileNotFoundError(f"❌ Could not locate a Mods folder under or near {ea_folder}")


# ──────────────────────────────
# 🔑 FILE HASHING
# ──────────────────────────────
def md5(file: Path, chunk: int = 8192) -> str:
    """Generate an MD5 hash for a given file (used for duplicate detection)."""
    h = hashlib.md5()
    with file.open("rb") as f:
        for part in iter(lambda: f.read(chunk), b""):
            h.update(part)
    return h.hexdigest()


# ──────────────────────────────
# 🧠 OLD TS4SCRIPT DETECTOR
# ──────────────────────────────
def is_old_ts4script(file: Path) -> bool:
    """
    Return True if a .ts4script file was compiled with old (pre-3.10) Python bytecode.
    """
    with file.open("rb") as f:
        head = f.read(4)
        return head in {b"\x42\x0D\x0D\x0A", b"\x33\x0D\x0D\x0A"}  # py 3.7/3.8/3.9


# ──────────────────────────────
# 🗑️ EMPTY FOLDER REMOVER
# ──────────────────────────────
def remove_empty_folders(path: Path, log_callback=print) -> None:
    """
    Recursively remove empty folders from a given path.
    """
    for root, dirs, _ in os.walk(path, topdown=False):
        for d in dirs:
            dir_path = Path(root) / d
            if not any(dir_path.iterdir()):
                try:
                    dir_path.rmdir()
                    log_callback(f"Removed empty folder: {dir_path}")
                except Exception as e:
                    log_callback(f"Error removing {dir_path}: {e}")
