"""
Generic parser stub for Echo shells.

This module provides a simple parse_intent function that interprets input text
either as a skill invocation (if containing a colon) or as plain NLP text.

Logs are sent to support/logging, and routing consults are deferred to map_route when necessary.
"""

from support import logger_utils as logging
from tools import map_route

def parse_intent(text: str):
    try:
        if not text or not text.strip():
            intent = {"type": "nlp", "text": ""}
            logging.conditional_debug(f"parse_intent detected intent: {intent}")
            return intent
        if ':' in text:
            skill, rest = text.split(':', 1)
            intent = {"type": "skill", "name": skill.strip(), "args": rest.strip()}
            logging.conditional_debug(f"parse_intent detected intent: {intent}")
            return intent
        intent = {"type": "nlp", "text": text.strip()}
        logging.conditional_debug(f"parse_intent detected intent: {intent}")
        return intent
    except Exception as e:
        logging.trace_log(f"parse_intent error: {e}")
        map_route.import_from_route("core/controller.py")
        return {"type": "nlp", "text": text.strip()}
