_cached_state = {}
"""
controller.py
Generic Echo Shell controller.
Routes user input → security → parser → handler → ethics → logging.
All logging is deferred to support.logging.
Routing consults (e.g., imports) use core.map_route.
"""

import ast
import json
import re

# Import get_ea_folder for Sims-specific initialization
from core.utils import get_ea_folder

from tools import map_route
from core.parser import parse_intent
from core.handler import handle_message as handle_intent
from support import logger_utils as logging

safety = map_route.import_from_route("safety/security.py")
ethics = map_route.import_from_route("safety/ethics.py")

SKILLS = {}

# Helper: parse description input with inline tags (tone=, platform=, cta=)
def parse_description_input(raw_input: str):
    """
    Parse ad description input allowing inline tags like:
    'candles tone=inspirational platform=Instagram cta="Shop now!"'
    Returns tuple: (message, tone, platform, cta)
    """
    match = re.match(r"^(.*?)\s*(?:tone=(\w+))?\s*(?:platform=(\w+))?\s*(?:cta=['\"](.*?)['\"])?$", raw_input.strip())
    message = (match.group(1) or "").strip()
    tone = (match.group(2) or "casual").strip()
    platform = (match.group(3) or "Instagram").strip()
    cta = (match.group(4) or "").strip()
    return message, tone, platform, cta

def execute(user_input, USER_TOKEN=None, session=None):
    # Defensive guard: ensure user_input is a dict for downstream .get() calls
    if isinstance(user_input, str):
        user_input = {"message": user_input}
    """Main execution pipeline for Echo Shell."""
    logging.trace_log("[TRACE controller] execute entered")
    logging.conditional_debug(f"[DEBUG controller] user_input={user_input!r}, USER_TOKEN={USER_TOKEN}")
    global _cached_state
    if session is None or not isinstance(session, dict):
        session = _cached_state
    else:
        _cached_state = session

    logging.trace_log(f"[INPUT] {user_input}")

    # 0. Locate EA folder before processing (Sims-specific initialization)
    try:
        ea_folder = get_ea_folder(auto_confirm=False)
        logging.trace_log(f"[INFO] EA folder located at: {ea_folder}")
    except Exception as e:
        logging.trace_log(f"[WARN] EA folder lookup skipped or failed: {e}")

    # 1. Security check
    # Ensure downstream functions receive plain text, not dicts
    if isinstance(user_input, dict):
        raw_input = user_input.get("message", "")
    else:
        raw_input = str(user_input)

    safe_input = safety.sanitize_input(raw_input)
    logging.trace_log(f"[TRACE controller] sanitized input={safe_input!r}")

    # 2. Parse and handle intent
    intent = parse_intent(safe_input)
    result = handle_intent(safe_input, SKILLS)

    # 3. Ethics review
    reviewed = ethics.review_output(result)

    # 4. Log + return
    if reviewed is None:  # fallback for testing so outputs aren't lost
        reviewed = result
    logging.trace_log(f"[OUTPUT] {reviewed}")
    logging.trace_log("[TRACE controller] execute completed")
    logging.conditional_debug(f"[DEBUG controller] reviewed output={reviewed!r}")
    _cached_state = session
    return reviewed
