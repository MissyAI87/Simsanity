#!/bin/bash

LOG_DIR="./support/logs"
ARCHIVE_DIR="./support/logs/archive"
SUMMARY_TMP=$(mktemp)

for LOG_FILE in "$LOG_DIR"/*.log "$ARCHIVE_DIR"/*.log; do
  if [[ -f "$LOG_FILE" ]]; then
    echo "==== $(date -r "$LOG_FILE" '+%Y-%m-%d %H:%M:%S') - $LOG_FILE ====" >> "$SUMMARY_TMP"
    cat "$LOG_FILE" >> "$SUMMARY_TMP"
    echo "" >> "$SUMMARY_TMP"
  fi
done

SUMMARY=$(python3 -c "
import re
from datetime import datetime

with open('$SUMMARY_TMP', 'r') as f:
    lines = f.readlines()

fixed_keywords = re.compile(r'fixed|resolved', re.I)
missing_imports = []
missing_targets = []
route_errors = []
trace_debug_notes = []

already_fixed = []
still_broken = []

for line in lines:
    if fixed_keywords.search(line):
        already_fixed.append(line.strip())
    if 'missing import' in line.lower():
        missing_imports.append(line.strip())
    if 'missing target' in line.lower():
        missing_targets.append(line.strip())
    if 'route error' in line.lower():
        route_errors.append(line.strip())
    if re.search(r'trace|debug', line, re.I):
        trace_debug_notes.append(line.strip())

def unique(lst):
    return list(dict.fromkeys(lst))

missing_imports = unique(missing_imports)
missing_targets = unique(missing_targets)
route_errors = unique(route_errors)
trace_debug_notes = unique(trace_debug_notes)
already_fixed = unique(already_fixed)

def has_issue():
    return bool(missing_imports or missing_targets or route_errors or trace_debug_notes)

summary = []
summary.append('=== What happened ===')
if missing_imports:
    summary.append('Missing imports detected:')
    summary.extend(' - ' + i for i in missing_imports)
if missing_targets:
    summary.append('Missing targets detected:')
    summary.extend(' - ' + i for i in missing_targets)
if route_errors:
    summary.append('Route errors detected:')
    summary.extend(' - ' + i for i in route_errors)
if trace_debug_notes:
    summary.append('Trace and debug notes found:')
    summary.extend(' - ' + i for i in trace_debug_notes)
if not has_issue():
    summary.append('No notable issues found in logs.')

summary.append('\n=== What was already fixed ===')
if already_fixed:
    summary.extend(' - ' + i for i in already_fixed)
else:
    summary.append('No issues marked as fixed or resolved.')

summary.append('\n=== What is still broken ===')
current_issues = missing_imports + missing_targets + route_errors + trace_debug_notes
current_issues = [i for i in current_issues if not fixed_keywords.search(i)]
if current_issues:
    summary.extend(' - ' + i for i in unique(current_issues))
else:
    summary.append('No current unresolved issues detected.')

summary.append('\n=== Next steps ===')
if current_issues:
    summary.append('Please investigate the above current issues, prioritize fixes for missing imports and targets, resolve route errors, and review trace/debug notes for underlying problems.')
else:
    summary.append('No action needed at this time.')

print('\\n'.join(summary))
")

echo "$SUMMARY"

rm "$SUMMARY_TMP"
