"""
⚔️ mf_conflicts.py
Detects mod conflicts (duplicate TGI keys) and broken or corrupt Sims 4 mod files.
Extracted from modfix.py for modularization.
"""

from pathlib import Path
from colorama import Fore
from .mf_utils import c

CACHE_FILE = Path(__file__).parent / "manual_mods_path.txt"

SAFE_ROOT_KEYWORDS = ["Electronic Arts", "The Sims 4"]

def is_within_ea_mods(path: Path) -> bool:
    """Ensure all operations are confined to Electronic Arts/The Sims 4/Mods."""
    try:
        parts = [p.lower() for p in path.parts]
        return any("electronic arts" in p or "the sims 4" in p for p in parts) and "mods" in parts
    except Exception:
        return False

def clear_cached_mod_path():
    """
    Delete the cached manual Mods folder path file.
    Call this to force ModFix to re-prompt for Mods folder next run.
    """
    if CACHE_FILE.exists():
        CACHE_FILE.unlink()
        print(f"🗑️ Deleted cached Mods path file: {CACHE_FILE}")
    else:
        print("ℹ️ No cached Mods path file found.")

# ──────────────────────────────
# ⚔️ TGI KEY READER
# ──────────────────────────────
def read_tgi_keys(pkg_path: Path) -> set[bytes]:
    """
    Extract raw TGI keys (Type, Group, Instance identifiers)
    from a Sims 4 .package file for conflict detection.
    """
    keys = set()
    try:
        if not pkg_path.exists():
            return keys
        with pkg_path.open("rb") as f:
            data = f.read()
            offset = 0
            while True:
                idx = data.find(b'TGIN', offset)
                if idx == -1:
                    break
                keys.add(data[idx:idx + 16])
                offset = idx + 1
    except Exception as e:
        print(f"Error reading TGI from {pkg_path}: {e}")
    return keys


# ──────────────────────────────
# ⚔️ CONFLICT DETECTOR
# ──────────────────────────────
def detect_conflicting_tgi(mods: Path, output_path: Path, quarantine: bool = True, log_callback=print) -> list[tuple[str, str]]:
    """
    Identify mod conflicts where two mods contain identical TGI keys.
    Optionally quarantines duplicates and streams progress updates.
    Returns a list of conflicting pairs.
    """
    try:
        total_files = sum(1 for _ in mods.rglob("*.package"))
        if total_files > 10000:
            log_callback(f"⚠️ [DEBUG] Too many package files ({total_files}), skipping scan to prevent hang.")
            return []
    except Exception as e:
        log_callback(f"⚠️ [DEBUG] Could not count mod files: {e}")

    tgi_map = {}
    conflicts = []
    quarantined = []

    if not mods.exists():
        log_callback(f"❌ Mods folder not found: {mods}")
        return conflicts

    # Limit search scope to only Electronic Arts and The Sims 4 directories within Mods folder
    mod_files = []
    for folder in mods.rglob("*"):
        if folder.is_dir() and is_within_ea_mods(folder):
            mod_files.extend(folder.glob("*.package"))
    log_callback(f"🧩 [DEBUG] Restricted scan scope. Found {len(mod_files)} package files in Sims-related folders.")
    log_callback(f"📦 Scanning {len(mod_files)} package files for TGI keys...")

    for i, file in enumerate(mod_files, 1):
        # Skip files outside of Electronic Arts or The Sims 4 Mods folders
        if not is_within_ea_mods(file):
            log_callback(f"🚫 [SAFEGUARD] Skipping file outside EA Mods folder: {file}")
            continue
        log_callback(f"🧩 [DEBUG] Starting file {i}/{len(mod_files)}: {file.name}")
        try:
            keys = read_tgi_keys(file)
            log_callback(f"🧩 [DEBUG] Finished reading TGI keys from: {file.name} ({len(keys)} keys)")
            for key in keys:
                if key in tgi_map:
                    conflict_pair = (file.name, tgi_map[key].name)
                    conflicts.append(conflict_pair)

                    # Quarantine handling
                    if quarantine:
                        if not is_within_ea_mods(file):
                            log_callback(f"🚫 [SAFEGUARD] Prevented quarantining file outside EA Mods folder: {file}")
                            continue
                        q_dir = mods / "ModFix_Quarantine"
                        q_dir.mkdir(exist_ok=True)
                        dest = q_dir / file.name
                        file.rename(dest)
                        quarantined.append(dest)
                        log_callback(f"⚔️ Conflict detected between {file.name} and {tgi_map[key].name}. Quarantined {file.name}.")
                else:
                    tgi_map[key] = file

            log_callback(f"🧩 [DEBUG] Completed scan of {i} files so far...")

            if i % 25 == 0 or i == len(mod_files):
                log_callback(f"🔍 Scanned {i}/{len(mod_files)} mods...")

        except Exception as e:
            log_callback(f"⚠️ Error scanning {file.name}: {e}")

    # Write CSV
    with open(output_path, "w") as f:
        f.write("mod1,mod2\n")
        for m1, m2 in conflicts:
            f.write(f"{m1},{m2}\n")

    if conflicts:
        log_callback(f"⚠️ Found {len(conflicts)} TGI conflicts. Results saved to {output_path}")
    else:
        log_callback("✅ No TGI conflicts found.")

    if quarantined:
        log_callback(f"🚷 Quarantined {len(quarantined)} mods to /ModFix_Quarantine")

    return conflicts


# ──────────────────────────────
# 🚫 BROKEN MOD DETECTION
# ──────────────────────────────
def detect_broken_mods(mods: Path, output_path: Path) -> None:
    """
    Scan for broken or unreadable Sims 4 mod files and export results.
    """
    broken = []
    for file in mods.rglob("*"):
        if file.suffix.lower() in {".package", ".ts4script"}:
            try:
                if file.stat().st_size == 0:
                    broken.append(file.name)
                else:
                    with file.open("rb") as f:
                        f.read(1)
            except Exception:
                broken.append(file.name)

    if broken:
        with open(output_path, "w") as f:
            f.write("broken_mods\n")
            for name in broken:
                f.write(f"{name}\n")
        print(c(f"🚫 Found {len(broken)} broken mods. Exported to {output_path}", Fore.YELLOW))
    else:
        print(c("✅ No broken mods found.", Fore.GREEN))
