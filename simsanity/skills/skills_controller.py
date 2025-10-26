"""
Central Skills Registry for Simsanity
Handles import and registration of all skill modules.
"""

from support import logger_utils as logging
from tools import map_route

# Central registry
SKILLS = {}

def register_skill(name, fn):
    """Register a skill handler function."""
    logging.log(f"Registering skill: {name}")
    SKILLS[name] = fn

def execute_skill(name, *args, **kwargs):
    """Execute a skill by name."""
    skill = SKILLS.get(name)
    if skill:
        logging.log(f"Executing skill: {name}")
        return skill(*args, **kwargs)
    else:
        logging.trace_log(f"Skill '{name}' not found in registry.")
        return map_route.import_from_route(name, *args, **kwargs)

# Import skill controllers
# Import skill controllers
from skills.cheats import cheats_controller
from skills.how_to import how_to_controller

# Inline cheat skill functions
def cheats_money_function(user_input=None, context=None):
    return "💰 To increase money in The Sims 4: open the cheat console (Ctrl+Shift+C) and type `kaching` (+1,000) or `motherlode` (+50,000). You can also type `money [amount]` to set a specific total."

def cheats_relationships_function(user_input=None, context=None):
    return "❤️ To adjust relationships: open the console (Ctrl+Shift+C) and type `modifyrelationship [YourFirstName] [YourLastName] [TargetFirstName] [TargetLastName] [amount] LTR_Friendship_Main` for friendships or replace with `LTR_Romance_Main` for romance."

def cheats_build_function(user_input=None, context=None):
    return "🏗️ To use build cheats: open the console (Ctrl+Shift+C) and type `bb.moveobjects` to freely place items. You can also use `bb.showhiddenobjects` and `bb.showliveeditobjects` for hidden items."

def cheats_skills_function(user_input=None, context=None):
    return "📚 To max skills: open the console (Ctrl+Shift+C), then type `stats.set_skill_level [skillname] [level]` (example: `stats.set_skill_level major_painting 10`)."

def cheats_career_function(user_input=None, context=None):
    return "💼 To promote or demote careers: open the console (Ctrl+Shift+C) and type `careers.promote [career]` or `careers.demote [career]`."

def cheats_needs_function(user_input=None, context=None):
    return "⚡ To adjust needs: open the console (Ctrl+Shift+C), then type `fillmotive motive_[need]` (like `motive_energy`), or `sims.fill_all_commodities` to max everything."
# ModFix is now modularized; controller routes to mf_ components (backup, cleaner, sorter, etc.)
from skills.modfix import modfix_controller  # uses modular mf_ files internally
from skills.read_save import rs_controller

# Register all skills
register_skill("cheats", cheats_controller.handle)
register_skill("how_to", lambda message, context=None: how_to_controller.handle(user_input=message, context=context))
register_skill("modfix", modfix_controller.handle)
register_skill("read_save", rs_controller.handle)

# Register cheat-related skills
register_skill("cheats_money", cheats_money_function)
register_skill("cheats_relationships", cheats_relationships_function)
register_skill("cheats_build", cheats_build_function)
register_skill("cheats_skills", cheats_skills_function)
register_skill("cheats_career", cheats_career_function)
register_skill("cheats_needs", cheats_needs_function)

# Removed Organize Mods module (no longer in use)
logging.log("✅ All Simsanity skills successfully registered: Cheats, How-To, ModFix, Read Save.")
