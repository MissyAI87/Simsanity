"""
🎮 cheats_controller.py
Handles user requests for Sims 4 cheats.
Loads data from cheats_data.json and performs fuzzy matching.

Author: Mary Hayes
Created: 10/10/25
Updated: 10/13/25
"""

import os
import json
import difflib
from colorama import Fore
from support import logger_utils as logging

# Load cheats from JSON
DATA_PATH = os.path.join(os.path.dirname(__file__), "cheats_data.json")

try:
    with open(DATA_PATH, "r") as f:
        CHEATS = json.load(f)
except Exception as e:
    CHEATS = {}
    print(f"{Fore.YELLOW}⚠️ Could not load cheats_data.json: {e}{Fore.RESET}")

def find_cheats(query: str):
    """Fuzzy search for cheats by keyword or alias."""
    results = []
    query_lower = query.lower()

    for category, entries in CHEATS.items():
        for cheat in entries:
            search_fields = [cheat.get("command", ""), cheat.get("description", "")]
            search_fields.extend(cheat.get("aliases", []))

            for field in search_fields:
                if query_lower in field.lower():
                    results.append({
                        "category": category,
                        "command": cheat.get("command"),
                        "description": cheat.get("description")
                    })
                    break
            else:
                # fuzzy match if no direct match
                combined = " ".join(search_fields).lower()
                if difflib.SequenceMatcher(None, query_lower, combined).ratio() > 0.6:
                    results.append({
                        "category": category,
                        "command": cheat.get("command"),
                        "description": cheat.get("description")
                    })

    return results


# New function for /cheats route: list all cheats, optionally filtered by category
def list_cheats(category: str = None):
    """Return all available cheats, optionally filtered by category."""
    if not CHEATS:
        return []

    if category:
        filtered = {
            cat: cheats for cat, cheats in CHEATS.items() if cat.lower() == category.lower()
        }
        return filtered

    return CHEATS


def handle(user_input=None, context=None):
    """Main entry point for the Cheats skill."""
    if not user_input:
        return {"response": "Please provide a cheat name or description."}

    text = user_input.strip()
    matches = find_cheats(text)

    if not matches:
        response = f"Unknown cheat: '{user_input}'. Try common ones like 'motherlode' or 'freerealestate on'."
    else:
        lines = [f"{Fore.CYAN}🎮 Cheats matching '{user_input}':{Fore.RESET}"]
        for m in matches[:10]:
            lines.append(f"• {m['command']} — {m['description']} ({m['category']})")
        response = "\n".join(lines)

    logging.log(f"Cheats Skill executed: {user_input} → {response}")
    return {"response": response}
