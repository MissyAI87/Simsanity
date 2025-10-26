#!/bin/bash
# Archive all .log files in marketor/support/logs/ to archive/ with timestamped names

BASE_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_DIR="$BASE_DIR/support/logs"
ARCHIVE_DIR="$LOG_DIR/archive"

mkdir -p "$ARCHIVE_DIR"

timestamp=$(date +"%Y-%m-%d_%H-%M-%S")

for log in "$LOG_DIR"/*.log; do
  if [ -f "$log" ]; then
    fname=$(basename "$log")
    mv "$log" "$ARCHIVE_DIR/${fname%.log}_$timestamp.log"
  fi
done

# recreate empty active log files
touch "$LOG_DIR/analyze_logs.log"
touch "$LOG_DIR/self_scan.log"
touch "$LOG_DIR/fix_imports.log"
touch "$LOG_DIR/marketor.log"

echo "✅ Archived all logs at $timestamp and recreated empty log files"

# log archive event
for log in "$LOG_DIR"/*.log; do
  if [ -f "$ARCHIVE_DIR/${fname%.log}_$timestamp.log" ]; then
    echo "[$timestamp] Archived $(basename "$log") -> ${fname%.log}_$timestamp.log" >> "$ARCHIVE_DIR/archive.log"
  fi
done
