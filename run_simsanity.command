# Simsanity launch script (2025-10-16)
# Launches the non-compiled Simsanity source build


PORT="${1:-8080}"

# --- Auto-Select Available Port ---
is_port_free() {
  nc -z localhost "$1" >/dev/null 2>&1
  return $((! $?))
}

START_PORT=${PORT}
MAX_PORT=8100

while ! is_port_free "$PORT"; do
  PORT=$((PORT+1))
  if [ "$PORT" -gt "$MAX_PORT" ]; then
    echo "❌ No free ports found between $START_PORT and $MAX_PORT."
    exit 1
  fi
done

echo "🌐 Using available port: $PORT"

# --- Locate Simsanity Source Directory Dynamically ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SIMSANITY_DIR=""

# 1. Check for simsanity folder in the same directory as this script
if [ -f "$SCRIPT_DIR/simsanity/ui/server.py" ]; then
  SIMSANITY_DIR="$SCRIPT_DIR/simsanity"
elif [ -f "$SCRIPT_DIR/simsanity/core/ui/server.py" ]; then
  SIMSANITY_DIR="$SCRIPT_DIR/simsanity/core"
fi

# 2. If not found nearby, run broader search
if [ -z "$SIMSANITY_DIR" ]; then
  echo "🔍 Searching for 'simsanity' folder starting from: $SCRIPT_DIR"
  SEARCH_PATHS=$(find "$SCRIPT_DIR" -maxdepth 3 -type d -name "simsanity" 2>/dev/null)
  if [ -z "$SEARCH_PATHS" ]; then
    PARENT=$(dirname "$SCRIPT_DIR")
    SEARCH_PATHS=$(find "$PARENT" -maxdepth 5 -type d -name "simsanity" 2>/dev/null)
  fi

  for path in $SEARCH_PATHS; do
    if [ -f "$path/ui/server.py" ] || [ -f "$path/core/ui/server.py" ]; then
      SIMSANITY_DIR="$path"
      break
    fi
  done
fi

# 3. If still not found, prompt user
if [ -z "$SIMSANITY_DIR" ]; then
  echo "⚠️ Could not automatically locate your Simsanity installation."
  echo "Please drag your Simsanity folder into this window or enter the full path:"
  read -r SIMSANITY_DIR
fi

# 4. Verify it worked
if [ -f "$SIMSANITY_DIR/ui/server.py" ]; then
  SERVER_FILE="$SIMSANITY_DIR/ui/server.py"
elif [ -f "$SIMSANITY_DIR/core/ui/server.py" ]; then
  SERVER_FILE="$SIMSANITY_DIR/core/ui/server.py"
else
  echo "❌ Could not find Simsanity server file inside: $SIMSANITY_DIR"
  echo "Please ensure your folder structure contains either ui/server.py or core/ui/server.py"
  exit 1
fi

echo "🎮 Launching Simsanity (source build)..."
echo "📁 Working directory: $SIMSANITY_DIR"

VENV_PATH="$SIMSANITY_DIR/venv"
LOG_DIR="$SIMSANITY_DIR/support/logs"
REQUIREMENTS="$SIMSANITY_DIR/requirements.txt"

# --- Python Environment Check ---
SYSTEM_PYTHON_PATH="$(which python3 2>/dev/null || true)"
if [ "$SYSTEM_PYTHON_PATH" = "/opt/homebrew/bin/python3" ]; then
  echo "🧩 Homebrew Python detected → rebuilding venv with system Python"
  rm -rf "$VENV_PATH"
  /usr/bin/python3 -m venv "$VENV_PATH"
  source "$VENV_PATH/bin/activate"
  pip install --quiet flask
else
  if [ ! -d "$VENV_PATH" ]; then
    echo "🧩 Creating new venv for Simsanity..."
    /usr/bin/python3 -m venv "$VENV_PATH"
  fi
  source "$VENV_PATH/bin/activate"
fi

echo "🐍 Python binary in use: $(which python3)"
echo "✅ Virtual environment ready."

# --- Install Dependencies ---
upgrade_pip() { python3 -m pip install --upgrade pip --quiet; }
install_requirements() {
  if [ -f "$REQUIREMENTS" ]; then
    echo "📦 Installing dependencies..."
    python3 -m pip install -r "$REQUIREMENTS"
  else
    echo "⚠️ No requirements.txt found."
  fi
}
ensure_pkg() {
  pkg="$1"
  if ! python3 -c "import $pkg" &>/dev/null; then
    echo "📦 Installing missing package: $pkg"
    python3 -m pip install "$pkg" --quiet
  fi
}

upgrade_pip
install_requirements
ensure_pkg flask
ensure_pkg colorama
ensure_pkg tqdm
ensure_pkg yaml

# --- Clean and Prepare Logs ---
find "$SIMSANITY_DIR" -name '*.DS_Store' -delete
mkdir -p "$LOG_DIR"

echo "🚀 Starting Simsanity server from source on port $PORT..."
cd "$(dirname "$SIMSANITY_DIR")" || exit
python3 -m simsanity.ui.server --port "$PORT" 2>&1 | tee "$LOG_DIR/server-$PORT.log"
echo "✅ Simsanity server stopped or closed."
