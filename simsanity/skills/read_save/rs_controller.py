#
#  rs_controller.py
#
#
#
#  Created by Mary Hayes on 10/10/25.
# Read Save Skill handler for Simsanity

from support import logger_utils as logging
import os

def handle(user_input=None, context=None):
    """
    Handles 'Read Save' tasks for The Sims 4.
    Provides info, analysis, or repair guidance for Sims 4 save files.
    """

    if not user_input:
        return {"response": "Please tell me what you want to do — like 'analyze save', 'find corrupt saves', or 'read households'."}

    text = user_input.strip().lower()
    response = None

    # Common intents
    if "analyze" in text or "scan" in text:
        response = "Scanning your Saves folder can identify broken households, missing Sims, or mods that affect the save. I can show you how to use Sims 4 Tray Importer for detailed checks."
    elif "corrupt" in text or "broken" in text:
        response = "If your save won’t load, try renaming your slot in the Saves folder, removing the last mod you installed, and reloading. Corrupted saves often come from outdated mods or custom content."
    elif "backup" in text:
        response = "You can back up your saves by copying the folder 'Documents > Electronic Arts > The Sims 4 > Saves' to another location. Always do this before mod updates or testing new content."
    elif "household" in text or "sims" in text:
        response = "To view Sims in a save, use Sims 4 Tray Importer or open the save folder to find .tray and .save files. These store all Sim and household data."
    elif "location" in text or "where" in text:
        response = "Your saves are stored in: Documents > Electronic Arts > The Sims 4 > Saves. Each numbered slot represents a different game save."
    else:
        response = "I can help analyze or back up your Sims 4 saves. Try 'how to fix a corrupted save' or 'read my household from save'."

    logging.log(f"Read Save Skill executed: {user_input} → {response}")
    return {"response": response}
#
