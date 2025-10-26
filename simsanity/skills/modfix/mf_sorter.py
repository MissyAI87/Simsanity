"""
🏷️ mf_sorter.py
Replaces legacy sorting logic with Tiny Tagger tagging system.
Handles classification safely via tagging rather than direct movement.
"""

from pathlib import Path
from colorama import Fore
from .mf_tagging import analyze_and_tag_mods

def category_for(mod_name: str) -> str:
    """
    Determine the category for a mod based on its filename.
    Used by mf_inventory for organizing mod listings.
    """
    name = mod_name.lower()
    if "script" in name:
        return "Scripts"
    elif "package" in name:
        return "Packages"
    elif "override" in name:
        return "Overrides"
    elif "preset" in name:
        return "Presets"
    else:
        return "Uncategorized"

def sort_mods_by_type(mods_folder: Path, dry_run: bool = True, log_callback=print) -> None:
    """
    Uses Tiny Tagger's tagging logic instead of the legacy sorter.
    Tags mods by category and writes analysis reports instead of moving files.
    """
    mods_folder = Path(mods_folder)
    log_callback(f"{Fore.CYAN}🔍 Running Tiny Tagger analysis on: {mods_folder}{Fore.RESET}")
    
    result = analyze_and_tag_mods(mods_folder, dry_run=dry_run)
    if result["status"] == "success":
        log_callback(f"{Fore.GREEN}✅ Tagging complete. Mode: {'Dry Run' if dry_run else 'Live'}{Fore.RESET}")
        log_callback(f"{Fore.CYAN}📄 Review 'tagdb.json' for detailed results before applying changes.{Fore.RESET}")
    else:
        log_callback(f"{Fore.RED}❌ Tagging failed: {result['message']}{Fore.RESET}")
