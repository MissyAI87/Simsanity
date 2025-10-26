#
#  how_to_controller.py
#
#  Created by Mary Hayes on 10/10/25.
#

from support import logger_utils as logging
from .how_to import get_how_to   # import helper

def handle(user_input=None, context=None):
    # Defensive guard against accidental string access
    if isinstance(user_input, str):
        user_input = user_input.strip()
    elif isinstance(user_input, dict):
        user_input = user_input.get("query", "")
    elif user_input is None and isinstance(context, dict):
        user_input = context.get("query", "")
    else:
        user_input = str(user_input or "").strip()

    # Prevent duplicate intro messages from backend
    if not user_input:
        return {"response": ""}

    """
    Responds to 'how-to' questions about The Sims 4.
    Returns tutorial-style guidance for mod setup, cheats, or gameplay systems.
    """

    if not user_input:
        return {"response": "Please tell me what you want help with, like 'how to install mods' or 'how to use motherlode'."}

    text = user_input.strip().lower()

    guides = {
        "install mods": "📦 To install mods:\n1. Go to Documents > Electronic Arts > The Sims 4 > Mods.\n2. Place your .package files there.\n3. In Game Options > Other, enable 'Custom Content and Mods'.",
        "enable cheats": "🧠 To enable cheats:\n1. Press Ctrl + Shift + C.\n2. Type `testingcheats true` and press Enter.\n3. You can now use any cheat code.",
        "build mode": "🛠️ Enter Build Mode by clicking the hammer & wrench icon or pressing F2. You can place, move, and delete objects freely.",
        "save game": "💾 To save your game:\nPress ESC → Save or Save As.",
        "max skills": "🎓 To max skills:\nEnable cheats, then type:\n`stats.set_skill_level [SkillName] 10`\nExample: `stats.set_skill_level major_cooking 10`."
    }

    response = None

    # Check predefined guides
    for key, guide_text in guides.items():
        if key in text:
            response = guide_text
            break

    # If no static match, use dynamic how_to
    if not response:
        how_to_response = get_how_to(text)
        if how_to_response and "ℹ️" not in how_to_response:
            response = how_to_response
        else:
            response = "I don’t have a guide for that yet, but I can help you write one!"

    logging.log(f"How-To Skill executed: {user_input} → {response}")
    return {"response": response}


def handle_message(user_input=None, context=None):
    """
    Wrapper for compatibility with the Echo message handler.
    It simply forwards calls to handle().
    """
    return handle(user_input=user_input, context=context)
