import time
import sys
"""
🧩 modfix_controller.py
Handles user-facing ModFix skill requests for The Sims 4.

This controller routes commands to modular subcomponents:
- Backup
- Cleaner
- Quarantine
- Sorter
- Inventory
- Utilities
- Logs

Author: Mary Hayes
Created: 10/10/25
Updated: 10/13/25
"""

from pathlib import Path
from colorama import Fore

from .mf_backup import zip_backup
from .mf_cleaner import clean_garbage_files, clear_keyword_files, remove_empty_folders
from .mf_inventory import export_mod_inventory_to_json, export_mod_inventory_to_csv
from .mf_quarantine import quarantine_suspicious_files
from .mf_sorter import sort_mods_by_type
from .mf_utils import validate_mod_paths
from .mf_logs import log_action
from .mf_versions import update_known_versions_file, check_mod_versions
from .mf_conflicts import detect_conflicting_tgi, detect_broken_mods


def handle(user_input=None, context=None):
    """
    Central handler for ModFix skill requests.
    Accepts natural-language commands (e.g., "clean mods", "backup mods").
    Routes to the appropriate submodule and returns a response dict.
    """

    # WebUI permission check
    if not context or not context.get("permission_granted"):
        return {
            "status": "confirm",
            "response": (
                "🕵️ ModFix needs permission to scan your computer, external drives, "
                "and cloud folders for the EA Mods directory. Allow scan?"
            ),
        }

    if context.get("permission_granted") is False:
        print("❌ Permission denied by user. ModFix scan aborted.")
        return {"response": "❌ ModFix scan denied by user. No folders were searched."}

    print("✅ Permission granted. Searching now...")
    try:
        mods = validate_mod_paths()
    except FileNotFoundError as e:
        return {"response": f"❌ {e}"}

    if isinstance(mods, str) and mods == "manual_required":
        print("[MODFIX] Manual Mods folder path required — halting until user input.")
        return {"status": "manual_required", "response": "⚠️ Manual Mods folder path required. Please provide it in the UI."}

    if not mods:
        return {"response": "⚠️ No EA Mods folder found during scan."}

    # Notify the user which folder was found before continuing
    found_message = f"📂 Found EA Mods folder: {mods}"
    print(found_message)
    log_action(f"Found Mods folder at {mods}", reason="FolderDetection")
    return {"response": found_message}

    text = (user_input or "").strip().lower()

    # ──────────────────────────────
    # 🗃 BACKUP
    # ──────────────────────────────
    if "backup" in text:
        dst = mods.parent / "ModFix_Backup.zip"
        zip_backup(mods, dst)
        log_action(f"Backup created at {dst}", reason="User request")
        return {"response": f"✅ Backup completed: {dst}"}

    # ──────────────────────────────
    # 🧹 CLEANER
    # ──────────────────────────────
    elif "clean" in text or "cache" in text or "thumb" in text:
        clean_garbage_files(mods)
        clear_keyword_files(["lastexception", "lastcrash", "lastuiexception"], mods)
        remove_empty_folders(mods)
        log_action("Garbage and cache files removed.", reason="Cleaner")
        return {"response": "🧹 Mods folder cleaned and cache cleared."}

    # ──────────────────────────────
    # ⚠️ QUARANTINE / SCAN
    # ──────────────────────────────
    elif "scan" in text or "quarantine" in text:
        qdir = mods.parent / "ModFix_Quarantine"
        quarantined = quarantine_suspicious_files(mods, qdir)
        log_action(f"Quarantined {len(quarantined)} files.", reason="Scan")
        return {"response": f"⚠️ {len(quarantined)} suspicious files moved to quarantine."}

    # ──────────────────────────────
    # 🗂 SORTER
    # ──────────────────────────────
    elif "sort" in text or "organize" in text:
        sort_mods_by_type(mods)
        log_action("Mods sorted by category.", reason="Sorter")
        return {"response": "🗂 Mods sorted into category folders."}

    # ──────────────────────────────
    # 📄 INVENTORY EXPORT
    # ──────────────────────────────
    elif "inventory" in text or "list" in text or "export" in text:
        json_path = mods.parent / "ModsInventory.json"
        csv_path = mods.parent / "ModsInventory.csv"
        export_mod_inventory_to_json(mods, json_path)
        export_mod_inventory_to_csv(mods, csv_path)
        log_action("Inventory exported (JSON + CSV).", reason="Inventory")
        return {"response": f"📄 Exported mod inventory to:\n- {json_path}\n- {csv_path}"}

    # ──────────────────────────────
    # 🧭 VERSION CHECK
    # ──────────────────────────────
    elif "version" in text or "update" in text:
        version_file = mods.parent / "KnownModVersions.json"
        remote_url = "https://example.com/KnownModVersions.json"  # placeholder
        update_known_versions_file(remote_url, version_file)
        check_mod_versions(mods, version_file)
        log_action("Checked mod versions and updates.", reason="VersionCheck")
        return {"response": "🧭 Mod versions checked and updates applied where available."}

    # ──────────────────────────────
    # ⚔️ CONFLICT DETECTION (Tiny Tagger Integration)
    # ──────────────────────────────
    elif "conflict" in text or "broken" in text or "duplicate" in text:
        log_action("Running Tiny Tagger conflict and integrity scan.", reason="ConflictCheck")

        try:
            from .mf_tagging import analyze_and_tag_mods
            log_action("Delegating conflict analysis to Tiny Tagger.", reason="TaggerIntegration")
            result = analyze_and_tag_mods(mods, dry_run=True)

            if result["status"] == "success":
                log_action("Tiny Tagger scan completed safely.", reason="ConflictScan")
                return {"response": "⚔️ Tiny Tagger completed conflict and duplicate scan in dry-run mode. Review tagdb.json for detailed results."}
            else:
                log_action(f"Tiny Tagger scan failed: {result['message']}", reason="ConflictScanError")
                return {"response": f"❌ Tiny Tagger scan failed: {result['message']}"}
        except Exception as e:
            log_action(f"Error running Tiny Tagger conflict scan: {e}", reason="ConflictError")
            return {"response": f"❌ Failed to run Tiny Tagger conflict detection: {e}"}

    # No fallback/help response; stop here if command not recognized.



def stream_handle(context):
    """
    Orchestrates full ModFix pipeline:
    - Validate EA/Mods path
    - Detect conflicts
    - Run Tiny Tagger (sort + tag)
    - Clean up leftovers
    - Report progress live
    """
    try:
        yield "🔍 Scanning mod folder, please wait..."
        time.sleep(0.5)
        from .mf_utils import validate_mod_paths
        # yield "🧩 [DEBUG] validate_mod_paths() starting..."
        mods = validate_mod_paths()
        # yield "🧩 [DEBUG] validate_mod_paths() returned."
        # Ensure we are operating inside the actual Mods folder
        from pathlib import Path
        if Path(mods).name.lower() != "mods":
            possible_mods = list(Path(mods).glob("**/Mods"))
            if possible_mods:
                mods = possible_mods[0]
                yield f"📂 Adjusted Mods path to: {mods}"
            else:
                yield f"❌ Mods folder not found under {mods}. Halting."
                return
        if isinstance(mods, str) and mods == "manual_required":
            yield "data: {\"status\": \"manual_required\"}\n\n"
            return
        yield f"📂 Found Mods folder: {mods}"

        # --- Step 1: Conflict analysis ---
        yield "⚙️ Analyzing mod conflicts... 💡 The more mods you have, the longer this step may take — please wait patiently."
        time.sleep(0.5)
        from .mf_conflicts import detect_conflicting_tgi
        # yield "🧩 [DEBUG] detect_conflicting_tgi() starting..."
        output_path = Path(mods).parent / "ModFix_Conflicts.json"
        detect_conflicting_tgi(mods, output_path, quarantine=True)
        # yield "🧩 [DEBUG] detect_conflicting_tgi() finished."
        yield f"⚔️ Conflict analysis complete. Results saved to {output_path}"

        # --- Step 2: Sorting (Tiny Tagger integration) ---
        yield "✨ Sorting and labeling your Sims mods — this could take a while, please wait..."
        time.sleep(0.5)
        from .tinytagger import move_files
        # yield "🧩 [DEBUG] move_files() starting..."
        move_files(mods, dry_run=False)
        # yield "🧩 [DEBUG] move_files() finished."
        yield "📁 Organization complete."

        # --- Step 3: Cleanup ---
        yield "🧹 Running post-sort cleanup..."
        time.sleep(0.5)
        from .mf_cleaner import remove_empty_folders
        # yield "🧩 [DEBUG] remove_empty_folders() starting..."
        remove_empty_folders(mods, aggressive=True, log_callback=print)
        # yield "🧩 [DEBUG] remove_empty_folders() finished."
        yield "🧼 Cleanup complete."

        yield "✅ ModFix complete!"
    except Exception as e:
        yield f"❌ ModFix encountered an error: {e}"
