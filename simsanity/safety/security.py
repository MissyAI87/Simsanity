"""
security.py — Echo Shell Security Gate
Handles basic input sanitization before routing to skills.
"""

import re
from tools.map_route import import_from_route
logging_mod = import_from_route("support/logger_utils.py")
conditional_debug = logging_mod.conditional_debug
trace_log = logging_mod.trace_log

def sanitize_input(user_input: str) -> str:
    """
    Very simple sanitization layer.
    - Removes leading/trailing whitespace
    - Blocks obvious injection attempts (shell commands, code)
    """
    trace_log(f"[TRACE security] sanitize_input called with user_input={str(user_input)[:60]!r}")
    if not isinstance(user_input, str):
        return ""

    clean = user_input.strip()

    # Block dangerous patterns
    blacklist = [r";", r"&&", r"\|\|", r"rm -rf", r"import os", r"__"]
    for pattern in blacklist:
        if re.search(pattern, clean, re.IGNORECASE):
            conditional_debug(f"[DEBUG security] blocked pattern={pattern}")
            return "[BLOCKED INPUT]"

    conditional_debug(f"[DEBUG security] sanitized input={clean!r}")
    return clean
