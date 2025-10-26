#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simsanity — Cross-Platform Self-Bootstrapping Launcher
Automatically installs all required dependencies on first run (Windows + macOS)
and ensures Python itself is present or guides the user to install it.
Safe for PyInstaller builds.
"""


import os, sys, subprocess, platform, webbrowser

# --- Ensure Simsanity package is discoverable ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# --- Step 0: Detect if Python is even functional ---
def python_exists():
    try:
        subprocess.check_output([sys.executable, "--version"])
        return True
    except Exception:
        return False


if not python_exists():
    print("❌ Python is not installed or not accessible.")
    system = platform.system().lower()
    if system.startswith("windows"):
        print("➡️ Opening official Python download page for Windows...")
        webbrowser.open("https://www.python.org/downloads/windows/")
    elif system.startswith("darwin"):
        print("➡️ Opening official Python download page for macOS...")
        webbrowser.open("https://www.python.org/downloads/macos/")
    else:
        print("Please install Python 3.9+ manually from https://www.python.org/downloads/")
    sys.exit(1)

# --- Step 0.5: Ensure virtual environment exists ---
VENV_PATH = os.path.join(os.path.dirname(__file__), "venv")

if not os.path.exists(VENV_PATH):
    print("🐍 Creating local virtual environment...")
    subprocess.check_call([sys.executable, "-m", "venv", VENV_PATH])
    print("✅ Virtual environment created.\n")

# Activate venv automatically
if platform.system().lower().startswith("windows"):
    activate_script = os.path.join(VENV_PATH, "Scripts", "activate_this.py")
else:
    activate_script = os.path.join(VENV_PATH, "bin", "activate_this.py")

if os.path.exists(activate_script):
    with open(activate_script) as f:
        exec(f.read(), {'__file__': activate_script})
    print("🔹 Virtual environment activated.\n")
else:
    print("⚠️ Could not auto-activate venv — continuing anyway.\n")

# --- Step 1: Universal dependency list ---
REQUIRED_PACKAGES = [
    "flask", "pyyaml", "tqdm", "jinja2", "werkzeug", "setuptools", "wheel"
]

def ensure_package(pkg):
    """Import a package or auto-install if missing."""
    try:
        __import__(pkg)
    except ImportError:
        print(f"⚙️ Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

def ensure_all():
    """Verify all required packages."""
    print("🔍 Checking for required Python packages...")
    for pkg in REQUIRED_PACKAGES:
        ensure_package(pkg)
    print("✅ All dependencies are ready.\n")

# --- Step 2: One-time bootstrap marker ---
BOOTSTRAP_MARKER = os.path.expanduser("~/.simsanity_bootstrap_done")

if not os.path.exists(BOOTSTRAP_MARKER):
    print("🛠️ First-time setup detected — installing dependencies...")
    # Make sure pip itself exists and is upgraded
    subprocess.call([sys.executable, "-m", "ensurepip", "--upgrade"])
    subprocess.call([sys.executable, "-m", "pip", "install", "--upgrade", "pip", "setuptools", "wheel"])
    ensure_all()
    with open(BOOTSTRAP_MARKER, "w") as f:
        f.write("ok")
    print("🎉 Setup complete! Future runs will skip installation.\n")
else:
    ensure_all()

# --- Step 3: OS-specific environment adjustments ---
SYSTEM = platform.system().lower()
if SYSTEM.startswith("darwin"):
    SEP = ":"
elif SYSTEM.startswith("windows"):
    SEP = ";"
else:
    SEP = ":"

# --- Step 4: Continue with main app startup ---
print(f"🚀 Launching Simsanity on {SYSTEM.capitalize()}...\n")

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from support.config import ECHO_NAME
ECHO_NAME = "simsanity"

import argparse
from flask import Flask, request, jsonify, render_template
controller_module = __import__(f"{ECHO_NAME}.core.controller", fromlist=["execute"])
controller = controller_module

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    if hasattr(sys, '_MEIPASS'):
        base_path = os.path.join(sys._MEIPASS, "simsanity", "ui")
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

app = Flask(
    __name__,
    template_folder=resource_path("templates"),
    static_folder=resource_path("static")
)
app.secret_key = "simsanity_dev_2025"

from simsanity.ui import routes
app.register_blueprint(routes.routes)

@app.route("/")
def index():
    return render_template("index.html")

from simsanity.skills.modfix import modfix_controller
from flask import Response

@app.route("/modfix", methods=["POST"])
def run_modfix():
    """Handle ModFix POST requests from the web UI."""
    data = request.get_json(silent=True) or {}
    context = data or {}

    try:
        result = modfix_controller.handle(user_input=None, context=context)
        if isinstance(result, dict):
            return jsonify(result)
        else:
            return jsonify({"response": str(result)})
    except Exception as e:
        return jsonify({"response": f"❌ Error: {str(e)}"}), 500

@app.route("/modfix/stream", methods=["GET"])
def stream_modfix():
    """Stream ModFix progress updates to the frontend."""
    def generate():
        try:
            for message in modfix_controller.stream_handle({}):
                yield f"data: {message}\n\n"
        except Exception as e:
            yield f"data: ⚠️ Error during ModFix stream: {str(e)}\n\n"

    return Response(generate(), mimetype="text/event-stream")

def run_server(port):
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)

import socket

def find_free_port(default=5154):
    port = default
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("127.0.0.1", port))
                return port
            except OSError:
                port += 1

import threading, time

def open_browser(port):
    time.sleep(1)
    webbrowser.open(f"http://127.0.0.1:{port}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Flask server.")
    parser.add_argument("--port", type=int, help="Port to run the server on (auto if not specified)")
    args = parser.parse_args()
    port = args.port or find_free_port()
    print(f"🚀 Starting Simsanity Flask server on port {port}")

    # --- Kill Flask’s auto-reloader entirely ---
    os.environ["FLASK_RUN_FROM_CLI"] = "false"
    os.environ.pop("WERKZEUG_RUN_MAIN", None)

    # --- Prevent duplicate launches across OS or packaging ---
    if not getattr(sys, "frozen", False) and not os.environ.get("_SIMSANITY_STARTED"):
        os.environ["_SIMSANITY_STARTED"] = "1"
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    run_server(port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run the Flask server.")
    parser.add_argument("--port", type=int, help="Port to run the server on (auto if not specified)")
    args = parser.parse_args()
    port = args.port or find_free_port()
    print(f"🚀 Starting Simsanity Flask server on port {port}")

    # --- Disable Flask's reloader in all cases ---
    os.environ["FLASK_ENV"] = "production"
    os.environ["FLASK_DEBUG"] = "0"
    os.environ["WERKZEUG_RUN_MAIN"] = "false"
    os.environ["FLASK_RUN_FROM_CLI"] = "false"

    # --- Single-instance lock ---
    LOCK_FILE = os.path.join(os.path.dirname(__file__), ".simsanity_lock")
    if os.path.exists(LOCK_FILE):
        print("⚠️ Simsanity is already running.")
        sys.exit(0)
    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    def cleanup_lock():
        if os.path.exists(LOCK_FILE):
            os.remove(LOCK_FILE)
    import atexit
    atexit.register(cleanup_lock)

    # --- Launch browser only once ---
    if not os.environ.get("_SIMSANITY_BROWSER_OPENED"):
        os.environ["_SIMSANITY_BROWSER_OPENED"] = "1"
        threading.Thread(target=open_browser, args=(port,), daemon=True).start()

    run_server(port)
