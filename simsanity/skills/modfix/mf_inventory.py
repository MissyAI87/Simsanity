"""
📊 modfix_inventory.py
Exports a detailed inventory of Sims 4 mods to JSON and CSV formats.
Integrates optional ModNotes.csv data for custom descriptions and URLs.
Extracted from modfix.py for modularization.
"""

from pathlib import Path
from datetime import datetime
from colorama import Fore
import json
import csv

from .mf_sorter import category_for  # helper that categorizes mods

# ──────────────────────────────
# 📦 JSON EXPORT
# ──────────────────────────────
def export_mod_inventory_to_json(mods: Path, output_path: Path) -> None:
    """
    Scan mods directory and export mod metadata to a JSON file.
    Each entry includes: name, path, size, category, and creation date.
    """
    inventory = []
    for file in mods.rglob("*"):
        if file.suffix.lower() in {".package", ".ts4script"}:
            entry = {
                "name": file.name,
                "path": str(file.relative_to(mods)),
                "size_kb": round(file.stat().st_size / 1024, 2),
                "category": category_for(file),
                "added": datetime.fromtimestamp(file.stat().st_ctime).isoformat()
            }
            inventory.append(entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(inventory, f, indent=2)
    print(f"{Fore.GREEN}🗃️ Exported mod inventory to {output_path}{Fore.RESET}")


# ──────────────────────────────
# 📄 CSV EXPORT (MERGED WITH MODNOTES)
# ──────────────────────────────
def export_mod_inventory_to_csv(mods: Path, output_path: Path) -> None:
    """
    Export mods list to CSV, merging ModNotes.csv (custom user descriptions and URLs).
    """
    notes_path = Path.home() / "Documents/mod manager/mod info/ModNotes.csv"
    notes = {}

    # Merge ModNotes if available
    if notes_path.exists():
        with open(notes_path, "r", newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                notes[row["name"]] = {
                    "description": row.get("description", ""),
                    "source_url": row.get("source_url", "")
                }

    inventory = []
    for file in mods.rglob("*"):
        if file.suffix.lower() in {".package", ".ts4script"}:
            note = notes.get(file.name, {})
            entry = {
                "name": file.name,
                "path": str(file.relative_to(mods)),
                "size_kb": round(file.stat().st_size / 1024, 2),
                "category": category_for(file),
                "added": datetime.fromtimestamp(file.stat().st_ctime).isoformat(),
                "description": note.get("description", ""),
                "source_url": note.get("source_url", "")
            }
            inventory.append(entry)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "name", "path", "size_kb", "category", "added", "description", "source_url"
        ])
        writer.writeheader()
        writer.writerows(inventory)

    print(f"{Fore.GREEN}📄 Exported mod inventory to {output_path}{Fore.RESET}")
