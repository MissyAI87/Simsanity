class ConverterBridge:
    def convert(self, json_data):
        print("[ConverterBridge] (stub) Would convert JSON to tuning XML here...")
        print(f" - Mod type: {json_data.get('type')}")
        print(f" - Name: {json_data.get('mod_name')}")
