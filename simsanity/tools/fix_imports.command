#!/bin/bash
cd "$(dirname "$0")/.."

LOG_DIR="./support/logs"
mkdir -p "$LOG_DIR"
FIX_LOG="$LOG_DIR/fix_imports.log"
FIX_LOG="$(cd "$LOG_DIR" && pwd)/fix_imports.log"

# Function to log to both terminal and file
log_and_print() {
  echo "$1" | tee -a "$FIX_LOG"
}
log_and_print "============================================="
log_and_print "🕒 Fix Imports Run at $(date)"
log_and_print "============================================="
log_and_print "ℹ️ This script normalizes imports for Oracle and Marketor shells,"
log_and_print "routing everything through 'support' or dynamic import via map_route/config."
log_and_print "============================================="

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
log_and_print "🔄 Running self_scan.command to refresh logs..."
"$SCRIPT_DIR/tools/self_scan.command"
log_and_print "✅ self_scan.command complete."
log_and_print ""

log_and_print "🔍 Scanning for bad imports (dry run)..."

# Collect matches with line context (file:line:text)
matches=$(find . -name "*.py" | xargs grep -nE '^[[:space:]]*(from (support\.|oracle\.|Oracle\.|ORACLE\.|marketor\.support\.|marketor\.tools\.support\.)|import (support|oracle|Oracle|ORACLE|marketor\.support|marketor\.tools\.support)|import_from_route\("marketor/|import_from_route\("oracle/)' 2>/dev/null)

if [ -z "$matches" ]; then
  log_and_print "✅ No bad imports found."
  exit 0
fi

log_and_print "⚠️ The following lines contain bad imports:"
log_and_print ""
log_and_print "$matches"
log_and_print ""

# Check for issues in self_scan.log
scan_log="./support/logs/self_scan.log"
log_issues=""
if [ -f "$scan_log" ]; then
  log_issues=$(grep -E "Direct support import|Missing target file" "$scan_log")
  if [ -n "$log_issues" ]; then
    log_and_print "📝 Issues found in $scan_log (showing latest):"
    log_and_print "---------------------------------------------"
    log_and_print "$log_issues"
    log_and_print "---------------------------------------------"
    log_and_print ""
  else
    log_and_print "📝 No relevant issues found in $scan_log."
    log_and_print ""
  fi
else
  log_and_print "📝 No relevant issues found in $scan_log."
  log_and_print ""
fi

# Confirmation prompt
log_and_print "---------------------------------------------"
if [ -n "$matches" ]; then
  log_and_print "⚠️ Detected bad import matches in source files."
fi
if [ -n "$log_issues" ]; then
  log_and_print "⚠️ Detected related issues from $scan_log."
fi
log_and_print "---------------------------------------------"
read -p "Do you want to apply fixes for these imports (yes/no)? " choice
if [ "$choice" != "yes" ]; then
  log_and_print "❌ Aborted — no changes made."
  exit 1
fi

# Apply replacements
log_and_print "⚡ Fixing imports..."
files=$(echo "$matches" | cut -d: -f1 | sort -u)
for file in $files; do
  if [ "$(basename "$file")" = "map_route.py" ]; then
    continue
  fi
  sed -i.bak -E 's/^([[:space:]]*)from oracle\./\1from support./' "$file"
  sed -i.bak -E 's/^([[:space:]]*)from Oracle\./\1from support./' "$file"
  sed -i.bak -E 's/^([[:space:]]*)from ORACLE\./\1from support./' "$file"
  sed -i.bak -E 's/^([[:space:]]*)import oracle([[:space:],]|$)/\1import support\2/' "$file"
  sed -i.bak -E 's/^([[:space:]]*)import Oracle([[:space:],]|$)/\1import support\2/' "$file"
  sed -i.bak -E 's/^([[:space:]]*)import ORACLE([[:space:],]|$)/\1import support\2/' "$file"
  sed -i.bak -E 's/import_from_route\("oracle\//import_from_route\("/' "$file"
  sed -i.bak -E 's/^([[:space:]]*)from marketor\.support\./\1from support./' "$file"
  sed -i.bak -E 's/^([[:space:]]*)import marketor\.support([[:space:],]|$)/\1import support\2/' "$file"
  sed -i.bak -E 's/^([[:space:]]*)from marketor\.tools\.support\./\1from support./' "$file"
  sed -i.bak -E 's/^([[:space:]]*)import marketor\.tools\.support([[:space:],]|$)/\1import support\2/' "$file"
  sed -i.bak -E 's/import_from_route\("marketor\//import_from_route\("/' "$file"
  # Replace bare from support.logging imports with import_from_route block that preserves all names
  awk '
  {
    if ($0 ~ /^from support\.logging import/) {
      sub(/^from support\.logging import[[:space:]]*/, "", $0);
      split($0, names, /,[[:space:]]*/);
      print "from marketor.tools.map_route import import_from_route";
      print "logging_mod = import_from_route(\"support/logging.py\")";
      for (i in names) {
        gsub(/^[[:space:]]+|[[:space:]]+$/, "", names[i]);
        if (names[i] != "")
          print names[i] " = logging_mod." names[i];
      }
    } else {
      print $0;
    }
  }' "$file" > "$file.tmp" && mv "$file.tmp" "$file"
  rm -f "$file.bak"
done

log_and_print "✅ Import paths fixed safely."
log_and_print "📄 Fix imports log saved to: $FIX_LOG"
