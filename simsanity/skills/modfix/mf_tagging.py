"""
🏷️ mf_tagging.py
Bridges ModFix with Tiny Tagger's classification logic.
Allows tagging and organizing without full CLI execution.
"""

from pathlib import Path
from .tinytagger import move_files as tagger_move_files

def analyze_and_tag_mods(mods_path: Path, dry_run: bool = True) -> dict:
    """
    Run Tiny Tagger’s logic to analyze or organize mod files.
    Returns a structured result summary instead of raw print.
    """
    try:
        print(f"🧩 Running Tiny Tagger on: {mods_path}")
        tagger_move_files(str(mods_path), dry_run=dry_run)
        return {"status": "success", "dry_run": dry_run, "path": str(mods_path)}
    except Exception as e:
        return {"status": "error", "message": str(e)}
