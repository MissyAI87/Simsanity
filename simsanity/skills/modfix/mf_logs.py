from datetime import datetime
from pathlib import Path

# Define the global log file location
LOG_FILE = Path.home() / "Documents" / "mod manager" / "quarantine" / "quarantine_log.txt"

def log_action(message: str, reason: str = None):
    """
    Write a timestamped entry to the quarantine log file.
    If a reason is provided, include it in the message.
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().isoformat()
    entry = f"{timestamp} - {reason + ': ' if reason else ''}{message}\n"
    with open(LOG_FILE, "a") as logf:
        logf.write(entry)
