class ModSchema:
    def get_template(self, mod_type="buff"):
        print(f"[ModSchema] (stub) Loading template for mod type: {mod_type}")
        return {
            "type": mod_type,
            "name": "Orb of Mastery",
            "effect": "Max all skills",
            "interaction": "Absorb Knowledge",
            "loot_actions": [{"skill": "all", "level": 10}]
        }
