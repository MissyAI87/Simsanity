"""
core/utils.py
System-wide utilities shared by Simsanity tools.
Includes logic for locating the Electronic Arts folder (The Sims 4 base directory).
"""

import os
import json
from pathlib import Path
from colorama import Fore
from typing import Optional

CONFIG_FILE = Path(__file__).resolve().parent.parent / "support" / "config" / "ea_path.json"

def ask_permission() -> bool:
    """Ask the user for permission to search their Documents folder."""
    print(f"{Fore.CYAN}🔍 Simsanity needs to locate your 'Electronic Arts' folder to continue.{Fore.RESET}")
    choice = input("Do you allow this search? (y/n): ").strip().lower()
    return choice in ("y", "yes")

def find_ea_folder() -> Path:
    """Search common paths for the Electronic Arts folder (macOS, Windows, OneDrive, Parallels, Desktop, Downloads),
    honoring an optional EA_FOLDER_OVERRIDE env var, and performing a shallow scan if the usual locations fail.
    """
    home = Path.home()
    win_user = os.getenv("USERNAME") or "User"

    # 0) Explicit override via env var
    override = os.getenv("EA_FOLDER_OVERRIDE")
    if override:
        override_path = Path(override).expanduser().resolve()
        print(f"{Fore.CYAN}🔧 EA override detected: {override_path}{Fore.RESET}")
        if override_path.exists():
            return override_path
        else:
            print(f"{Fore.YELLOW}⚠️ EA_FOLDER_OVERRIDE does not exist: {override_path}{Fore.RESET}")

    # 1) Build candidate list of common locations
    userprofile = Path(os.getenv("USERPROFILE") or home)
    onedrive = Path(os.getenv("ONEDRIVE") or userprofile / "OneDrive")

    common_roots = [
        home,
        userprofile,
        onedrive,
        Path(f"C:/Users/{win_user}"),
        Path("C:/Users/Public"),
    ]
    subfolders = [
        "Documents",
        "Desktop",
        "Downloads",
        "OneDrive/Documents",
        "",
    ]
    ea_names = [
        "Electronic Arts",
        "EA Games",
        "ElectronicArts",
    ]

    candidates: list[Path] = []
    for root in common_roots:
        for sub in subfolders:
            base = root / sub if sub else root
            for name in ea_names:
                candidates.append((base / name).resolve())

    # 2) Check candidates in order, with debug prints
    print(f"{Fore.CYAN}🔎 EA SEARCH: evaluating {len(candidates)} candidate paths...{Fore.RESET}")
    for cand in candidates:
        try:
            if cand.exists():
                print(f"{Fore.GREEN}✅ Found Electronic Arts folder at: {cand}{Fore.RESET}")
                return cand
            else:
                print(f"{Fore.WHITE}… not found: {cand}{Fore.RESET}")
        except Exception:
            # Skip any permission or odd path errors
            pass

    # 3) Shallow scan: look for a folder literally named like EA in typical roots (max depth ~3)
    print(f"{Fore.YELLOW}⚠️ Standard locations failed. Performing a shallow scan…{Fore.RESET}")
    scan_roots = [p for p in common_roots if p.exists()]
    MAX_HITS = 3
    hits = 0
    for root in scan_roots:
        # Walk only a few levels to avoid long scans
        for path in root.rglob("Electronic Arts"):
            try:
                rel_depth = len(path.parts) - len(root.parts)
                if rel_depth <= 4 and path.is_dir():
                    print(f"{Fore.GREEN}✅ Found Electronic Arts folder via scan: {path}{Fore.RESET}")
                    return path
                if rel_depth > 4:
                    break
            except Exception:
                pass
        # Also check EA Games name
        for path in root.rglob("EA Games"):
            try:
                rel_depth = len(path.parts) - len(root.parts)
                if rel_depth <= 4 and path.is_dir():
                    print(f"{Fore.GREEN}✅ Found EA Games folder via scan: {path}{Fore.RESET}")
                    return path
                if rel_depth > 4:
                    break
            except Exception:
                pass
        hits += 1
        if hits >= MAX_HITS:
            break

    # 4) Manual fallback prompt
    print(f"{Fore.YELLOW}⚠️ Could not find the EA folder automatically.{Fore.RESET}")
    manual = input("Please enter the full path to your 'Electronic Arts' folder manually: ").strip('\" ')
    manual_path = Path(manual).expanduser().resolve()
    if manual_path.exists():
        print(f"{Fore.GREEN}✅ Using manual EA folder: {manual_path}{Fore.RESET}")
        return manual_path

    raise FileNotFoundError(f"❌ Invalid EA folder path: {manual_path}")

def save_ea_path(path: Path):
    """Save the located EA folder path to a JSON config file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(CONFIG_FILE, "w") as f:
        json.dump({"ea_path": str(path)}, f, indent=2)
    print(f"{Fore.YELLOW}💾 Saved EA folder path to {CONFIG_FILE}{Fore.RESET}")

def load_saved_ea_path() -> Optional[Path]:
    """Load the saved EA folder path if available."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
            ea_path = Path(data.get("ea_path"))
            if ea_path.exists():
                print(f"{Fore.CYAN}📂 Using saved EA folder: {ea_path}{Fore.RESET}")
                return ea_path
        except Exception:
            pass
    return None

def get_ea_folder(auto_confirm=False) -> Path:
    """
    Always rebuilds the EA folder configuration each run.
    Searches for the folder, verifies it, and saves a new config file.
    Forces recheck every time and prompts manually if not found.
    """
    if not auto_confirm and not ask_permission():
        raise PermissionError("Search for EA folder denied by user.")

    # Always force a new search (ignore cached config)
    path = find_ea_folder()

    # Confirm the path exists before saving
    if not path.exists():
        print(f"{Fore.RED}❌ EA folder path not valid or accessible: {path}{Fore.RESET}")
        print("💡 Tip: Drag and drop your 'Electronic Arts' folder here, then press Enter.")
        manual = input("Drop your 'Electronic Arts' folder path: ").strip('\" ').strip("'")
        manual_path = Path(manual).expanduser().resolve()
        if manual_path.exists():
            path = manual_path
        else:
            raise FileNotFoundError(f"❌ Invalid EA folder path: {manual_path}")

    save_ea_path(path)
    return path


# Manual test block for EA folder detection
if __name__ == "__main__":
    print("\n🧩 Testing EA folder detection manually...\n")
    ea_path = get_ea_folder()
    print(f"\n✅ Final EA folder path: {ea_path}\n")
