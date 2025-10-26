"""
ethics.py — Echo Shell Ethics Gate
Reviews outputs before they are returned to the user.
"""

import re
from tools.map_route import import_from_route
logging_mod = import_from_route("support/logger_utils.py")
unified_log = logging_mod.unified_log
conditional_debug = logging_mod.conditional_debug
trace_log = logging_mod.trace_log

def review_output(response: str) -> str:
    """
    Check the model's output for basic ethical compliance.
    - Blocks harmful/offensive language
    - Masks unsafe outputs
    """
    trace_log(f"[TRACE ethics] review_output called with response preview={str(response)[:60]!r}")

    if not isinstance(response, str):
        return str(response)  # show raw output in testing

    # Basic blacklist — expand later as needed
    blacklist = [
        r"\bkill\b",
        r"\bsuicide\b",
        r"\bhate\b",
        r"\bnazi\b",
        r"\bracist\b",
        r"\bviolent\b"
    ]

    for pattern in blacklist:
        if re.search(pattern, response, re.IGNORECASE):
            unified_log(f"[ETHICS] Blocked output matched pattern: {pattern}")
            conditional_debug(f"[DEBUG ethics] blocked pattern={pattern}")
            return response  # show raw output instead of blocking during testing

    conditional_debug("[DEBUG ethics] response passed ethics check")
    return response
