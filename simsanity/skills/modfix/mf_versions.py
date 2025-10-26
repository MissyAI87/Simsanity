"""
🧭 mf_versions.py
Checks Sims 4 mod versions against a known JSON file of latest releases.
Optionally downloads updates automatically.

Extracted from modfix.py for modular structure.
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from colorama import Fore
from .mf_utils import c

# ──────────────────────────────
# 🔎 VERSION CHECKING
# ──────────────────────────────
def check_mod_versions(mods: Path, version_file: Path) -> None:
    """
    Compare local mod timestamps against a JSON file of known versions.
    JSON format:
    {
        "mod_filename.package": {
            "latest": "2025-06-01",
            "url": "https://example.com/mod_filename.package"
        }
    }
    """
    try:
        with open(version_file, "r") as f:
            known_versions = json.load(f)
    except Exception as e:
        print(c(f"⚠️ Could not load version file: {e}", Fore.YELLOW))
        return

    outdated = []
    for file in mods.rglob("*"):
        if file.suffix.lower() in {".package", ".ts4script"}:
            name = file.name
            if name in known_versions:
                info = known_versions[name]
                try:
                    latest_time = datetime.fromisoformat(info["latest"])
                except Exception:
                    continue
                file_time = datetime.fromtimestamp(file.stat().st_ctime)
                if file_time < latest_time:
                    outdated.append((file, latest_time.date(), file_time.date(), info.get("url")))

    if outdated:
        print(c("\n🔎 Outdated Mods Found:", Fore.YELLOW))
        for file, latest, current, url in outdated:
            print(f" - {file.name}: Installed {current}, Latest {latest}")
            if url:
                print(f"   ➜ Attempting to auto-download from {url}")
                download_file(url, file)
    else:
        print(c("✅ All mods are up to date.", Fore.GREEN))


# ──────────────────────────────
# ⬇️ DOWNLOAD HELPER
# ──────────────────────────────
def download_file(url: str, dest: Path) -> bool:
    """Download a file from the given URL and overwrite existing mod."""
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response, open(dest, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(c(f"⬇️ Downloaded update for {dest.name}", Fore.GREEN))
        return True
    except Exception as e:
        print(c(f"⚠️ Failed to download {dest.name} → {e}", Fore.YELLOW))
        return False


# ──────────────────────────────
# 🌐 UPDATE VERSION FILE
# ──────────────────────────────
def update_known_versions_file(url: str, dest: Path) -> None:
    """Fetch the remote KnownModVersions.json and save locally."""
    try:
        import urllib.request
        with urllib.request.urlopen(url) as response:
            data = response.read()
        dest.write_bytes(data)
        print(c(f"🌐 Updated KnownModVersions.json from {url}", Fore.GREEN))
    except Exception as e:
        print(c(f"⚠️ Could not update KnownModVersions.json → {e}", Fore.YELLOW))
