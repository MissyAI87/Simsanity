# ui/routes.py
from flask import Blueprint, render_template, request, jsonify, make_response, session
from tools.map_route import import_from_route
from core.commands import match_command, normalize_command

controller = import_from_route("core/controller.py")
execute = controller.execute

logging_mod = import_from_route("support/logger_utils.py")
trace_log = logging_mod.trace_log
debug_log = logging_mod.debug_log
unified_log = logging_mod.unified_log

# Create a Flask Blueprint for routes
routes = Blueprint("routes", __name__)

@routes.route("/log_user_input", methods=["POST"])
def log_user_input():
    """Log user-typed input sent from the frontend."""
    payload = request.get_json()
    message = payload.get("message") if payload else None
    # Update the message text as requested
    if message == "🛠️ ModFix activated — upload or describe the mods to check.":
        message = "🛠️ ModFix initializing"
    debug_log(f"[DEBUG route.log_user_input] User input message: {message!r}")
    unified_log(f"[ROUTE log_user_input] User input message: {message!r}")
    return jsonify({"status": "logged", "message": message})

@routes.before_request
def log_all_requests():
    """Log all incoming requests with method, path, and payload."""
    try:
        payload = request.get_json(silent=True)
    except Exception:
        payload = None
    debug_log(f"[DEBUG route.before_request] {request.method} {request.path} payload={payload}")
    unified_log(f"[ROUTE before_request] {request.method} {request.path} payload={payload}")

@routes.route("/")
def index():
    """Render the main chat UI page via Jinja template."""
    trace_log("[TRACE route.index] GET /")
    debug_log("[DEBUG route.index] serving index.html")
    unified_log("[ROUTE index] served index.html")
    return render_template("index.html")

@routes.route("/test")
def test():
    """Simple test route to confirm HTML rendering works."""
    trace_log("[TRACE route.test] GET /test")
    debug_log("[DEBUG route.test] returning Hello World")
    unified_log("[ROUTE test] returned Hello World")
    return "<h1>Hello World</h1>"

@routes.route("/chat", methods=["POST"])
def chat():
    """Handle chat messages from the frontend."""
    trace_log(f"[TRACE route.chat] POST /chat payload={request.json}")
    debug_log(f"[DEBUG route.chat] request.json={request.json}")
    unified_log(f"[ROUTE chat] received payload={request.json}")
    data = request.json
    if isinstance(data, str):
        try:
            import json
            data = json.loads(data)
        except Exception:
            data = {"message": data}
    user_input = data.get("message", "")
    debug_log(f"[DEBUG route.chat] user typed message: {user_input!r}")
    unified_log(f"[ROUTE chat] user typed message: {user_input!r}")
    mode = data.get("currentMode") or data.get("mode") or session.get("mode")
    if "state" not in session:
        session["state"] = {}

    # Only apply match_command logic if session or mode indicates the system is asking "what socials"
    apply_match_command = False
    if mode == "what_socials":
        apply_match_command = True
    elif "state" in session and session["state"].get("awaiting_socials_response"):
        apply_match_command = True

    if apply_match_command:
        matched_command = match_command(user_input)
        if not matched_command:
            # Try normalizing and matching again
            normalized_input = normalize_command(user_input)
            if normalized_input:
                matched_command = match_command(normalized_input)
            # Alias map for short forms
            alias_map = {
                "a": "amazon",
                "fb": "facebook",
                "ig": "instagram",
                "tw": "twitter"
            }
            if not matched_command and user_input.lower() in alias_map:
                matched_command = alias_map[user_input.lower()]
        if matched_command:
            user_input = matched_command
        else:
            # If no valid social matched, immediately re-prompt the user
            prompt = "Please select a valid social from the available options."
            trace_log(f"[TRACE route.chat] invalid social input received, re-prompting user.")
            debug_log(f"[DEBUG route.chat] invalid social input: {user_input!r}")
            unified_log(f"[ROUTE chat] invalid social input: {user_input!r}, re-prompt sent.")
            unified_log(f"[ROUTE chat] sending re-prompt to user: {prompt}")
            return jsonify({"response": prompt})

    # Only call execute if not in the chooseSocials-like mode or if a valid match was found
    if not apply_match_command or (apply_match_command and matched_command):
        trace_log(f"[TRACE route.chat] calling execute with user_input={user_input!r}, mode={mode}")
        debug_log(f"[DEBUG route.chat] session keys={list(session.keys())}")
        unified_log(f"[ROUTE chat] calling execute with user_input={user_input!r}, mode={mode}")
        try:
            response = execute(user_input, USER_TOKEN=mode, session=session)
        except Exception as e:
            debug_log(f"[DEBUG route.chat] exception={e!r}")
            unified_log(f"[ROUTE chat] exception occurred: {e!r}")
            response = f"❌ Error: {e}"
        trace_log(f"[TRACE route.chat] response={response!r}")
        debug_log(f"[DEBUG route.chat] response length={len(str(response))}")
        unified_log(f"[ROUTE chat] response={response!r}")
        return jsonify({"response": response})


@routes.route("/log_button_click", methods=["POST"])
def log_button_click():
    """Log button click payloads sent from the frontend."""
    payload = request.json
    debug_log(f"[DEBUG route.log_button_click] Button clicked with payload: {payload}")
    unified_log(f"[ROUTE log_button_click] Button clicked with payload: {payload}")
    return jsonify({"status": "logged"})


@routes.route("/locate_ea", methods=["POST"])
def locate_ea():
    """Re-run the EA folder search manually from the UI."""
    from core.utils import get_ea_folder
    try:
        ea_folder = get_ea_folder(auto_confirm=True)
        unified_log(f"[ROUTE locate_ea] EA folder found: {ea_folder}")
        return jsonify({"status": "success", "message": f"EA folder found at: {ea_folder}"})
    except Exception as e:
        unified_log(f"[ROUTE locate_ea] EA folder search failed: {e}")
        return jsonify({"status": "error", "message": str(e)})


# === Cheats and How-To routes ===

@routes.route("/cheats", methods=["POST"])
def cheats():
    """Handle requests for the Cheats feature."""
    from skills.cheats_controller import handle as cheats_handle
    try:
        data = request.get_json(silent=True) or {}
        result = cheats_handle(data)
        unified_log(f"[ROUTE cheats] executed successfully: {result}")
        return jsonify({"status": "success", "response": result})
    except Exception as e:
        unified_log(f"[ROUTE cheats] failed: {e}")
        return jsonify({"status": "error", "message": str(e)})

@routes.route("/cheats", methods=["GET"])
def cheats_list():
    """Return Sims 4 cheat codes and descriptions."""
    from skills.cheats import cheats_controller
    try:
        result = cheats_controller.list_cheats()
        unified_log(f"[ROUTE cheats_list] Served cheats list successfully.")
        return jsonify({"status": "success", "cheats": result})
    except Exception as e:
        unified_log(f"[ROUTE cheats_list] failed: {e}")
        return jsonify({"status": "error", "message": str(e)})


@routes.route("/howto", methods=["POST"])
@routes.route("/how_to", methods=["POST"])
def how_to():
    """Handle requests for the How-To feature."""
    from skills.how_to.how_to_controller import handle as howto_handle
    try:
        data = request.get_json(silent=True) or {}
        # Log incoming payload for debugging
        debug_log(f"[DEBUG route.how_to] Incoming payload: {data}")
        # Pass both user_input and context to howto_handle
        query = data.get("query") if isinstance(data, dict) else str(data)
        result = howto_handle(user_input=query, context=data if isinstance(data, dict) else {"query": query})
        unified_log(f"[ROUTE how_to] executed successfully: {result}")
        # Ensure JSON-only return for How-To
        response_text = result.get("response") if isinstance(result, dict) else result
        response = jsonify({"status": "success", "response": response_text})
        response.headers["Content-Type"] = "application/json"
        return response
    except Exception as e:
        unified_log(f"[ROUTE how_to] failed: {e}")
        return jsonify({"status": "error", "message": str(e)})

from flask import Response

@routes.route("/modfix", methods=["GET"])
def modfix():
    """Run the ModFix process and stream progress updates to the UI."""
    from skills.modfix import modfix_controller
    from flask import Response

    def generate():
        unified_log("[ROUTE modfix] Starting ModFix process (streaming mode).")
        yield "data: 🧩 Starting ModFix...\n\n"
        # Detect if ModFix needs manual Mods path from the UI
        from skills.modfix import mf_utils
        mods_folder = mf_utils.validate_mod_paths()
        if mods_folder == "manual_required":
            unified_log("[ROUTE modfix] Manual Mods folder path required — notifying UI.")
            yield "data: {\"status\": \"manual_required\"}\n\n"
            return
        try:
            for update in modfix_controller.stream_handle({"action": "run_modfix"}):
                unified_log(f"[ROUTE modfix] Progress: {update}")
                yield f"data: {update}\n\n"
            unified_log("[ROUTE modfix] Completed successfully.")
            yield "data: ✅ ModFix completed successfully.\n\n"
        except Exception as e:
            unified_log(f"[ROUTE modfix] Failed: {e}")
            yield f"data: ❌ ModFix failed: {e}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no",
        "Content-Type": "text/event-stream",
    }

    return Response(generate(), headers=headers)


# === Manual Mods Path route ===
@routes.route("/manual_mods_path", methods=["POST"])
def manual_mods_path():
    """Receive a manually entered or dropped Mods folder path from the UI."""
    from pathlib import Path
    data = request.get_json(force=True)
    manual_path = Path(data.get("path", "")).expanduser().resolve()

    if manual_path.exists():
        unified_log(f"[ROUTE manual_mods_path] ✅ Using manual Mods folder: {manual_path}")
        # Cache or store this path for ModFix session use
        global MANUAL_MODS_PATH
        MANUAL_MODS_PATH = manual_path
        # Persist the manual path to the ModFix cache file
        try:
            from skills.modfix import mf_utils
            mf_utils.CACHE_FILE.write_text(str(manual_path))
            unified_log(f"[ROUTE manual_mods_path] 💾 Saved manual Mods folder path to cache file: {manual_path}")
        except Exception as e:
            unified_log(f"[ROUTE manual_mods_path] ⚠️ Failed to save manual path to cache file: {e}")
        try:
            from skills.modfix import mf_utils
            if hasattr(mf_utils, "MODFIX_STATE"):
                mf_utils.MODFIX_STATE["manual_required"] = False
                unified_log("[ROUTE manual_mods_path] 🔄 Cleared manual_required flag in ModFix state.")
        except Exception as e:
            unified_log(f"[ROUTE manual_mods_path] ⚠️ Could not clear manual_required flag: {e}")
        unified_log(f"[ROUTE manual_mods_path] ✅ Mods folder received and saved. Frontend should re-trigger ModFix stream.")
        return jsonify({
            "status": "manual_path_received",
            "message": f"✅ Using Mods folder: {manual_path}"
        })
    else:
        unified_log(f"[ROUTE manual_mods_path] ❌ Invalid Mods path: {manual_path}")
        return jsonify({"status": "error", "message": f"Invalid path: {manual_path}"})
