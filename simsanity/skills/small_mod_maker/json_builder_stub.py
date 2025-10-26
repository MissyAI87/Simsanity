class JSONBuilder:
    def compile_json(self, schema):
        print("[JSONBuilder] (stub) Compiling JSON from schema...")
        return {
            "mod_name": schema.get("name"),
            "type": schema.get("type"),
            "details": schema
        }
