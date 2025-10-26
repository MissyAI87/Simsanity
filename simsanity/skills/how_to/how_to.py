from pathlib import Path

def get_how_to(cheat_command: str) -> str:
    """
    Returns usage instructions for specific Sims 4 cheats.
    """
    # Normalize input: accept dicts or strings
    if isinstance(cheat_command, dict):
        cheat_command = cheat_command.get("query", "")
    elif not isinstance(cheat_command, str):
        cheat_command = str(cheat_command or "")
    cheat = (cheat_command or "").lower().strip()

    # 🧩 General Requirement / Activation
    if "testingcheats" in cheat or "cas.fulleditmode" in cheat:
        return (
            "🧠 To use cheats in The Sims 4:\n"
            "1. Press Ctrl + Shift + C (or Command + Shift + C on Mac) to open the cheat console.\n"
            "2. Type `testingcheats true` and press Enter.\n"
            "3. Then enter the desired cheat (e.g. `cas.fulleditmode`)."
        )

    # 🏠 Build Mode Cheats
    elif ("bb." in cheat) or ("build" in cheat) or ("build mode" in cheat):
        return (
            "🛠️ Build Mode Cheats:\n"
            "1. Open the cheat console (Ctrl + Shift + C).\n"
            "2. Type `testingcheats true`, then enter one of the following:\n"
            "   • `bb.moveobjects` — place items freely without grid constraints.\n"
            "   • `bb.showhiddenobjects` — unlock hidden debug objects.\n"
            "   • `bb.showliveeditobjects` — display world-edit items.\n"
            "   • `bb.enablefreebuild` — enable build on locked/lot-restricted spaces.\n"
            "3. To disable, re-enter the same command or close build mode."
        )

    # 💰 Money Cheats
    elif any(x in cheat for x in ["motherlode", "kaching", "rosebud", "money", "simoleon", "funds", "cash"]):
        return (
            "💰 Money Cheats:\n"
            "1. Open the cheat console (Ctrl + Shift + C).\n"
            "2. Type one of the following:\n"
            "   • `motherlode` — gives §50,000\n"
            "   • `kaching` or `rosebud` — gives §1,000\n"
            "💡 Tip: You can enter these multiple times to accumulate more money."
        )

    # 💞 Relationship / Social
    elif "modifyrelationship" in cheat or ("relationship" in cheat) or ("friendship" in cheat) or ("romance" in cheat):
        return (
            "💞 Relationship Cheats:\n"
            "1. You must know both Sims’ full names (first and last).\n"
            "2. Use format:\n"
            "   `modifyrelationship FirstName1 LastName1 FirstName2 LastName2 100 LTR_Friendship_Main`\n"
            "   or use `LTR_Romance_Main` for romance points.\n"
            "3. You can set to negative values to lower relationships too."
        )

    # 🎓 Skill Cheats
    elif "stats.set_skill_level" in cheat or ("skill" in cheat):
        return (
            "🎓 Skill Cheats:\n"
            "1. Open the cheat console (Ctrl + Shift + C).\n"
            "2. Type `testingcheats true`.\n"
            "3. Enter:\n"
            "   `stats.set_skill_level Major_[SkillName] [Level]`\n"
            "   e.g., `stats.set_skill_level Major_Painting 10` for max painting."
        )

    # ⚡ Needs / Motives
    elif "sims.fill_all_commodities" in cheat or "fill_all_commodities" in cheat or "sims.add_buff" in cheat or ("sim motives" in cheat) or ("needs" in cheat):
        return (
            "⚡ Needs / Motives Cheats:\n"
            "1. Open the cheat console (Ctrl + Shift + C).\n"
            "2. Type `testingcheats true`.\n"
            "3. Use one of these:\n"
            "   • `sims.fill_all_commodities` — fill all needs for selected Sim.\n"
            "   • `sims.add_buff Buff_Motives_Hunger_Full` — fill hunger only.\n"
            "   • Use SHIFT + click a Sim (with testingcheats on) → “Cheat Needs” options."
        )

    # 👻 Death / Ghost / Occult Cheats
    elif ("traits.equip_trait trait_ghost" in cheat) or ("vampire" in cheat) or ("mermaid" in cheat) or ("plant" in cheat) or ("occult" in cheat) or ("ghost" in cheat) or ("resurrect" in cheat):
        return (
            "🧬 Occult / Death Cheats:\n"
            "1. Open the console (Ctrl + Shift + C).\n"
            "2. Type `testingcheats true`.\n"
            "3. Use these commands:\n"
            "   • `traits.equip_trait trait_OccultVampire` — turn Sim into Vampire.\n"
            "   • `traits.equip_trait trait_OccultMermaid` — turn Sim into Mermaid.\n"
            "   • `traits.equip_trait trait_Ghost_*` — convert Sim to ghost of different death types.\n"
            "   • `stats.set_stat commodity_BecomingVampire [value]` — manage vampire transformation."
        )

    # 🏛 Career Cheats
    elif cheat.startswith("careers.") or "career" in cheat or "promote" in cheat or "add_career" in cheat or "remove_career" in cheat:
        return (
            "🏛 Career Cheats:\n"
            "1. With testingcheats enabled, open the console.\n"
            "2. Use one of these:\n"
            "   • `careers.add_career [CareerName]` — assign a new career.\n"
            "   • `careers.promote [CareerName]` — promote current job.\n"
            "   • `careers.demote [CareerName]` — demote.\n"
            "   • `careers.remove_career [CareerName]` — quit the job."
        )

    # 🖥 UI / Toggle / Debug Cheats
    elif ("headlineeffects" in cheat) or ("fullscreen" in cheat) or ("ui.toggle" in cheat) or ("debug" in cheat) or ("freebuild" in cheat and "enable" not in cheat) or ("freerealestate" in cheat):
        return (
            "🖥️ UI / Debug Cheats:\n"
            "1. Open the console (Ctrl + Shift + C).\n"
            "2. Use commands like:\n"
            "   • `headlineEffects off` / `headlineEffects on` — toggle UI icons.\n"
            "   • `fullscreen` — toggle full screen mode.\n"
            "   • `freerealestate true/false` — make all lots free.\n"
            "   • `bb.showhiddenobjects` / `bb.showliveeditobjects` — reveal debug objects."
        )

    # 🎭 Trait Cheats
    elif "traits.equip_trait" in cheat or ("trait" in cheat):
        return (
            "🎭 Trait Cheats:\n"
            "1. Enable testingcheats via console.\n"
            "2. Use `traits.equip_trait [TraitName]` to add that trait.\n"
            "   (Use official trait ID names, e.g. `trait_OccultVampire`, `trait_Fairy`, etc.)"
        )

    # 🧩 Default fallback
    else:
        return (
            "ℹ️ To use Sims 4 cheats:\n"
            "1. Press Ctrl + Shift + C to open the cheat console.\n"
            "2. Type `testingcheats true` and press Enter.\n"
            "3. Then enter your desired cheat (for example, `motherlode`)."
        )
