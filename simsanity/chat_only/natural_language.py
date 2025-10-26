from support import logger_utils as logging
from core.controller import execute
from core import map_route

DEBUG_PREFLIGHT = True   # set to False to silence debug logs

def generate_natural_language_response(prompt, USER_TOKEN=None):
    """
    Generic natural language passthrough to controller.execute().
    When direction is unclear or an exception occurs, defers to map_route for resolution.
    """
    try:
        if DEBUG_PREFLIGHT:
            logging.conditional_debug(f"[DEBUG] Entering natural_language.generate_natural_language_response with prompt length={len(prompt)} and token={'set' if USER_TOKEN else 'missing'}")
        return execute(prompt, USER_TOKEN)
    except Exception as e:
        logging.trace_log(f"[ERROR] Exception in natural_language: {e}")
        try:
            controller = map_route.import_from_route("core/controller.py")
            return controller.execute(prompt, USER_TOKEN)
        except Exception as e2:
            logging.trace_log(f"[ERROR] Secondary exception in natural_language fallback: {e2}")
            raise
