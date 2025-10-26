# ...top of file
import re
from skills.skills_controller import SKILLS
from support import logger_utils as logging

def handle_message(user_text, session=None, context=None):
    state = session.get("state", {})
    expecting = state.get("expecting")

    logging.trace_log(f"[TRACE handler] handle_message called with expecting={expecting}, user_text={user_text!r}")

    # 0) Basic keyword intent routing for Sims 4
    intent = session.get("intent")
    if not intent:
        text = user_text.lower()
        if any(word in text for word in ["money", "simoleon", "rich", "increase funds", "kaching", "motherlode"]):
            intent = "cheats_money"
        elif any(word in text for word in ["relationship", "friend", "romance", "love", "enemy"]):
            intent = "cheats_relationships"
        elif any(word in text for word in ["build", "moveobjects", "bb.moveobjects", "placement"]):
            intent = "cheats_build"
        elif any(word in text for word in ["skill", "max skill", "increase skill"]):
            intent = "cheats_skills"
        elif any(word in text for word in ["career", "job", "promotion", "demotion"]):
            intent = "cheats_career"
        elif any(word in text for word in ["need", "motive", "hunger", "energy", "bladder", "fun"]):
            intent = "cheats_needs"
        elif any(word in text for word in ["how", "tutorial", "help", "guide"]):
            intent = "howto"

    # 1) Generic skill routing
    if intent and intent in SKILLS:
        fn = SKILLS[intent]
        try:
            return fn(user_input=user_text, context={"session": session})
        except Exception as e:
            logging.conditional_debug(f"[ERROR handler] Skill {intent} failed: {e}")
            logging.trace_log(f"[ERROR handler] Skill {intent} failed: {e}")
            return f"⚠️ Error running skill {intent}: {e}"
    else:
        return "🤔 I didn’t catch that. Can you clarify or try again?"

    # ...rest of your handler
