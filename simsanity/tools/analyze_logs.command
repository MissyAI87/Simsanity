#!/usr/bin/env python3
# Falls back to system Python if venv not found (manual run)
# NOTE: Future Option
# Add support for auto-batch mode:
#   Run with "./analyze_logs.command auto" to automatically fix all issues
#   without prompting (calls fix_imports.command or self_scan.command).
# Currently, script runs in interactive mode only.
import os
import sys
import time
# try:
#     from watchdog.observers import Observer
#     from watchdog.events import FileSystemEventHandler
# except ImportError:
#     import subprocess
#     print("⚠️ watchdog not installed. Attempting to install...")
#     MARKETOR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
#     venv_pip = os.path.join(MARKETOR_DIR, "venv", "bin", "pip")
#     if os.path.exists(venv_pip):
#         print(f"🔧 Found virtual environment pip at {venv_pip}. Installing watchdog there...")
#         try:
#             subprocess.check_call([venv_pip, "install", "--upgrade", "watchdog"])
#             from watchdog.observers import Observer
#             from watchdog.events import FileSystemEventHandler
#             print("✅ watchdog installed successfully in virtual environment.")
#         except Exception as e:
#             print(f"❌ Failed to install watchdog in virtual environment: {e}")
#             sys.exit(1)
#     else:
#         print("⚠️ No virtual environment found. Installing watchdog using system python with --break-system-packages...")
#         try:
#             subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "watchdog", "--break-system-packages"])
#             from watchdog.observers import Observer
#             from watchdog.events import FileSystemEventHandler
#             print("✅ watchdog installed successfully using system python.")
#         except Exception as e:
#             print(f"❌ Failed to install watchdog automatically: {e}")
#             sys.exit(1)
import logging
import subprocess
from logging.handlers import RotatingFileHandler

import importlib.util

MARKETOR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if MARKETOR_DIR not in sys.path:
    sys.path.insert(0, MARKETOR_DIR)
# Insert PROJECT_ROOT (parent of MARKETOR_DIR) into sys.path as well
PROJECT_ROOT = os.path.abspath(os.path.join(MARKETOR_DIR, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
map_route_path = os.path.join(MARKETOR_DIR, "tools", "map_route.py")

spec = importlib.util.spec_from_file_location("map_route", map_route_path)
map_route = importlib.util.module_from_spec(spec)
spec.loader.exec_module(map_route)

config = map_route.import_from_route("support/config.py")
DEBUG_MODE, TRACE_MODE, LOG_LEVEL = config.DEBUG_MODE, config.TRACE_MODE, config.LOG_LEVEL

TRACE_LEVEL_NUM = 5
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")

def trace(self, message, *args, **kws):
    if self.isEnabledFor(TRACE_LEVEL_NUM):
        self._log(TRACE_LEVEL_NUM, message, args, **kws)
logging.Logger.trace = trace

MARKETOR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOG_DIR = os.path.join(MARKETOR_DIR, "support", "logs")
ARCHIVE_DIR = os.path.join(LOG_DIR, "archive")
os.makedirs(LOG_DIR, exist_ok=True)
os.makedirs(ARCHIVE_DIR, exist_ok=True)

log_path = os.path.join(LOG_DIR, "analyze_logs.log")
date_marker_path = os.path.join(ARCHIVE_DIR, "analyze_logs.date")
today = time.strftime("%Y-%m-%d")

# Daily rollover: archive the active log once per day (first run after midnight)
prev_date = None
if os.path.exists(date_marker_path):
    try:
        with open(date_marker_path, "r") as dm:
            prev_date = dm.read().strip()
    except Exception:
        prev_date = None

if prev_date != today:
    # New day detected → archive yesterday's active log if present/non-empty
    if os.path.exists(log_path) and os.path.getsize(log_path) > 0:
        # Use the previous date in the archive filename if available, else current timestamp
        ts = prev_date if prev_date else today
        timestamp = ts + "_" + time.strftime("%H%M%S")
        archive_path = os.path.join(ARCHIVE_DIR, f"analyze_logs_{timestamp}.log")
        try:
            os.rename(log_path, archive_path)
        except Exception:
            # Fall back to copy+truncate if rename fails
            import shutil
            shutil.copy2(log_path, archive_path)
            open(log_path, "w").close()
    # Update the date marker to today
    try:
        with open(date_marker_path, "w") as dm:
            dm.write(today)
    except Exception:
        pass

logger = logging.getLogger("analyze_logs")

if TRACE_MODE:
    logger.setLevel(TRACE_LEVEL_NUM)
elif DEBUG_MODE:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024*1024, backupCount=2)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_and_print(msg):
    print(msg)
    logger.info(msg)

def parse_logs():
    issues_by_file = {}
    logger.trace("Starting to parse logs in directory: %s", LOG_DIR)
    for fname in os.listdir(LOG_DIR):
        if fname.endswith(".log"):
            logger.debug("Processing log file: %s", fname)
            with open(os.path.join(LOG_DIR, fname)) as f:
                content = f.read().splitlines()

            # Only consider lines after the last timestamp header (🕒)
            last_marker = None
            for i, line in enumerate(content):
                if "🕒" in line:
                    last_marker = i
            if last_marker is not None:
                content = content[last_marker:]

            for line in content:
                if any(keyword in line for keyword in [
                    "Missing target file", "Bad import",
                    "outdated", "Traceback", "ERROR"
                ]):
                    issues_by_file.setdefault(fname, []).append(line.strip())
    logger.trace("Completed parsing logs, found issues in %d files", len(issues_by_file))
    return issues_by_file

def run_command(cmd, description):
    try:
        log_and_print(f"⚡ Running: {description}")
        logger.debug("Executing command: %s in %s", cmd, os.path.join(MARKETOR_DIR, "tools"))
        subprocess.run(cmd, cwd=os.path.join(MARKETOR_DIR, "tools"))
    except Exception as e:
        log_and_print(f"❌ Failed to run {description}: {e}")

def main():
    log_and_print("🔍 Starting log analysis...")
    # Always refresh logs before analysis
    run_command(["./self_scan.command"], "self_scan.command (pre-analysis refresh)")
    run_command(["./fix_imports.command"], "fix_imports.command (pre-analysis refresh)")
    issues = parse_logs()
    if not issues:
        log_and_print("✅ No issues found in logs")
        log_and_print("\n📌 Recommended Next Steps:")
        log_and_print("  - Nothing urgent. Keep coding 🚀")
        log_and_print("📄 Analysis complete. Full log written to analyze_logs.log")
        return

    for fname, issues_list in issues.items():
        log_and_print(f"\nFile: {fname}")
        for issue in issues_list:
            log_and_print(f"  - {issue}")

        # Decide category based on first issue
        if any("Missing target file" in issue or "Bad import" in issue for issue in issues_list):
            suggestion = "Suggested Fix: Run fix_imports.command"
            log_and_print(suggestion)
            choice = input("Fix all issues in this file automatically? (yes/no/skip): ").strip().lower()
            if choice == "yes":
                run_command(["./fix_imports.command"], "fix_imports.command")
        elif any("outdated" in issue for issue in issues_list):
            suggestion = "Suggested Fix: Run self_scan.command to update map_route"
            log_and_print(suggestion)
            choice = input("Fix all issues in this file automatically? (yes/no/skip): ").strip().lower()
            if choice == "yes":
                run_command(["./self_scan.command"], "self_scan.command")
        else:
            log_and_print("⚠️ Suggest manual review. Skipping.")

    # Collect priorities for summary
    fix_needed = any("Missing target file" in issue or "Bad import" in issue
                     for issues_list in issues.values() for issue in issues_list)
    scan_needed = any("outdated" in issue
                      for issues_list in issues.values() for issue in issues_list)

    log_and_print("\n📌 Recommended Next Steps:")
    step_num = 1
    if fix_needed:
        log_and_print(f"  {step_num}. Run fix_imports.command to resolve missing or bad imports.")
        step_num += 1
    if scan_needed:
        log_and_print(f"  {step_num}. Run self_scan.command to refresh map_route and update routes.")
        step_num += 1
    if not fix_needed and not scan_needed:
        log_and_print("  - No automated fixes suggested. Review warnings manually.")

    log_and_print("📄 Analysis complete. Full log written to analyze_logs.log")

# class WatchHandler(FileSystemEventHandler):
#     def on_modified(self, event):
#         global LAST_RUN
#         if event.src_path.endswith(".log"):
#             now = time.time()
#             if now - LAST_RUN < THROTTLE_SECONDS:
#                 logger.debug("Throttled event for %s", event.src_path)
#                 return
#             LAST_RUN = now
#             log_and_print(f"🕒 Detected change in {event.src_path}, re-running analysis...")
#             main()

if __name__ == "__main__":
    # if len(sys.argv) > 1 and sys.argv[1].lower() == "watch":
    #     log_and_print("👀 Analyzer running in watch mode...")
    #     event_handler = WatchHandler()
    #     observer = Observer()
    #     observer.schedule(event_handler, LOG_DIR, recursive=False)
    #     observer.start()
    #     try:
    #         while True:
    #             time.sleep(1)
    #     except KeyboardInterrupt:
    #         observer.stop()
    #     observer.join()
    # else:
    main()
