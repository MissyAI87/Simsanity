"""
⚠️ mf_quarantine.py
Replaces legacy quarantine logic with Tiny Tagger's safe tagging system.
Scans for suspicious files and tags them for review instead of moving.
"""

from pathlib import Path
from colorama import Fore
from .mf_tagging import analyze_and_tag_mods

def quarantine_suspicious_files(mods_dir: Path, quarantine_dir: Path, log_callback=print, dry_run: bool = True) -> None:
    """
    Runs Tiny Tagger in analysis mode to identify suspicious or unwanted files.
    Does not move or delete anything — only generates tag results and logs.
    """
    log_callback(f"{Fore.CYAN}🔍 Running Tiny Tagger quarantine-safe analysis...{Fore.RESET}")
    
    result = analyze_and_tag_mods(mods_dir, dry_run=dry_run)
    if result["status"] == "success":
        log_callback(f"{Fore.GREEN}✅ Scan complete. Review 'tagdb.json' for flagged or uncategorized files.{Fore.RESET}")
        log_callback(f"{Fore.CYAN}📄 Quarantine suggestions recorded in Tiny Tagger output.{Fore.RESET}")
    else:
        log_callback(f"{Fore.RED}❌ Scan failed: {result['message']}{Fore.RESET}")
