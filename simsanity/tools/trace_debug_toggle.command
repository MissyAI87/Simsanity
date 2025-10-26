#!/bin/bash
# Toggle DEBUG_MODE and TRACE_MODE in config.py


# Find the repo root and config.py location-independently
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_FILE="$REPO_ROOT/support/config.py"

if [ ! -f "$CONFIG_FILE" ]; then
  echo "❌ config.py not found at $CONFIG_FILE"
  exit 1
fi

if [ "$1" == "status" ]; then
  if grep -q "DEBUG_MODE = True" "$CONFIG_FILE"; then
    echo "ℹ️ Current status: DEBUG/TRACE are ON"
  else
    echo "ℹ️ Current status: DEBUG/TRACE are OFF"
  fi
  exit 0
fi

if [ "$1" == "on" ]; then
  echo "🔔 Turning DEBUG/TRACE ON"
  sed -i.bak 's/DEBUG_MODE = False/DEBUG_MODE = True/' "$CONFIG_FILE"
  sed -i.bak 's/TRACE_MODE = False/TRACE_MODE = True/' "$CONFIG_FILE"
elif [ "$1" == "off" ]; then
  echo "🔕 Turning DEBUG/TRACE OFF"
  sed -i.bak 's/DEBUG_MODE = True/DEBUG_MODE = False/' "$CONFIG_FILE"
  sed -i.bak 's/TRACE_MODE = True/TRACE_MODE = False/' "$CONFIG_FILE"
else
  if grep -q "DEBUG_MODE = True" "$CONFIG_FILE"; then
    echo "🔕 Turning DEBUG/TRACE OFF"
    sed -i.bak 's/DEBUG_MODE = True/DEBUG_MODE = False/' "$CONFIG_FILE"
    sed -i.bak 's/TRACE_MODE = True/TRACE_MODE = False/' "$CONFIG_FILE"
  else
    echo "🔔 Turning DEBUG/TRACE ON"
    sed -i.bak 's/DEBUG_MODE = False/DEBUG_MODE = True/' "$CONFIG_FILE"
    sed -i.bak 's/TRACE_MODE = False/TRACE_MODE = True/' "$CONFIG_FILE"
  fi
fi

rm -f "$CONFIG_FILE.bak"
echo "✅ Done. Restart Marketor to apply changes."
