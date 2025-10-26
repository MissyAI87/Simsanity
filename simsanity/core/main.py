#!/usr/bin/env python3
# main.py — Echo Shell entrypoint
# All logging now defers to support/logging




import sys, os

# --- Global UTF-8 Logging Fix (cross-platform safe) ---
import io, logging
if os.name == "nt":
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding="utf-8", errors="replace")

logging.basicConfig(encoding="utf-8", errors="replace")


# --- Cross-platform import fix ---
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Ensure 'simsanity' package is importable (universal) ---
import types
if 'simsanity' not in sys.modules:
    simsanity_pkg = types.ModuleType('simsanity')
    simsanity_pkg.__path__ = [ROOT_DIR]
    sys.modules['simsanity'] = simsanity_pkg

# --- Dynamic import patch (universal build-safe version) ---
# Makes sure "core", "support", "ui", etc. can be imported
# whether running from source or from a compiled Nuitka onefile binary.

# Absolute path to this file (inside /core/)
this_dir = os.path.abspath(os.path.dirname(__file__))

# Path to the project root (parent of /core/)
project_root = os.path.dirname(this_dir)

# Path Nuitka uses when the app extracts to a temp folder
runtime_root = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else None

# Add all candidate roots to sys.path if missing
for path in filter(None, [this_dir, project_root, runtime_root]):
    if path not in sys.path:
        sys.path.append(path)

import importlib.util, types

# --- onefile runtime patch for Nuitka ---
# Prefer the extracted runtime location if running from a Nuitka onefile bundle
if getattr(sys, "frozen", False):
    core_path = os.path.join(os.path.dirname(sys.executable), "core")
else:
    core_path = os.path.join(project_root, "core")

if not importlib.util.find_spec("core") and os.path.isdir(core_path):
    core_module = types.ModuleType("core")
    core_module.__path__ = [core_path]
    sys.modules["core"] = core_module

# --- EA folder check ---
from core.utils import get_ea_folder

def preflight_setup():
    """Run EA folder check before anything else."""
    try:
        ea_folder = get_ea_folder(auto_confirm=True)
        print(f"📂 EA folder detected at: {ea_folder}")
    except Exception as e:
        print(f"⚠️ EA folder setup failed: {e}")

core_module = __import__("core.controller", fromlist=["execute"])
execute = core_module.execute

logging_module = __import__("support.logger_utils", fromlist=["trace_log", "conditional_debug"])
logging = logging_module

# --- Flask Clarity Checker Route Integration ---
from flask import Flask, request, jsonify


app = Flask(__name__)

@app.route("/check_clarity", methods=["POST"])
def check_clarity():
    """Route to evaluate description clarity."""
    try:
        data = request.get_json(force=True)
        message = data.get("message", "")
        logging.trace_log(f"[TRACE main] /check_clarity message={message!r}")
        result = assess_clarity(message)
        logging.conditional_debug(f"[DEBUG main] clarity result={result}")
        return jsonify(result)
    except Exception as e:
        logging.trace_log(f"[ERROR /check_clarity] {e}")
        return jsonify({
            "is_clear": False,
            "score": 0,
            "feedback": f"❌ Internal error while checking clarity: {str(e)}"
        }), 500

def cli_loop():
    print("✨ Echo Shell is running. Type 'exit' to quit.")
    logging.trace_log("[TRACE main] cli_loop started")
    logging.conditional_debug("[DEBUG main] cli_loop entered")
    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n👋 Goodbye!")
            break
        if user_input.lower() in ("exit", "quit"):
            print("👋 Session ended.")
            break
        logging.conditional_debug(f"[DEBUG main] received user_input={user_input!r}")
        logging.trace_log(f"[TRACE main] received user_input={user_input!r}")
        try:
            response = execute(user_input)
            logging.trace_log(f"[TRACE main] response full={response!r}")
        except Exception as e:
            logging.trace_log(f"[ERROR] Main loop failed: {e}")
            logging.conditional_debug(f"[DEBUG main] exception={e!r}")
            response = f"❌ Error: {e}"
        logging.conditional_debug(f"[DEBUG main] response preview={response[:60]!r}")
        print("Echo:", response)

def web_loop():
    # lightweight switch — expects ui/server.py to define run_server()
    import webbrowser, time, os
    server_module = __import__("ui.server", fromlist=["run_server"])
    run_server = server_module.run_server
    logging.trace_log("[TRACE main] web_loop starting server")
    logging.conditional_debug("[DEBUG main] web_loop invoked run_server")

    port = int(os.getenv("ECHO_PORT", 8080))

    # Open browser first (so user sees it right away)
    webbrowser.open(f"http://127.0.0.1:{port}")
    time.sleep(1)

    # Run Flask directly in main thread (so it stays alive)
    try:
        run_server(port=port)
    except TypeError:
        logging.trace_log("[TRACE main] run_server() fallback — no port arg")
        run_server()

if __name__ == "__main__":
    preflight_setup()  # Run EA folder check first
    mode = os.getenv("ECHO_MODE", "web")  # default to web
    logging.trace_log(f"[TRACE main] starting in mode={mode}")
    logging.conditional_debug(f"[DEBUG main] environment ECHO_MODE={mode}")
    if mode == "cli":
        cli_loop()
    else:
        web_loop()
