from . import (
    mod_schema_stub,
    json_builder_stub,
    converter_bridge_stub,
    visualizer_bridge_stub,
    package_exporter_stub,
)

class SmallModMaker:
    def __init__(self):
        self.modules = {
            "schema": mod_schema_stub.ModSchema(),
            "builder": json_builder_stub.JSONBuilder(),
            "converter": converter_bridge_stub.ConverterBridge(),
            "visualizer": visualizer_bridge_stub.VisualizerBridge(),
            "exporter": package_exporter_stub.PackageExporter(),
        }

    def initialize(self):
        print("[SmallModMaker] Initializing stub modules...")
        for name, mod in self.modules.items():
            print(f" - Loaded {name}: {mod.__class__.__name__}")

    def build_mod(self, mod_name="Orb of Mastery"):
        print(f"[SmallModMaker] (stub) Starting build for mod: {mod_name}")
        schema = self.modules["schema"].get_template("buff")
        json_data = self.modules["builder"].compile_json(schema)
        self.modules["converter"].convert(json_data)
        self.modules["visualizer"].preview(json_data)
        self.modules["exporter"].export_package(mod_name)
        self.show_instructions(mod_name)

    def show_instructions(self, mod_name):
        print(f"\n✅ Your mod '{mod_name}' has been created (stub)!")
        print("📝 How to use it:")
        print("1. Move to The Sims 4 Mods folder.")
        print("2. Enable Custom Content + Script Mods in settings.")
        print("3. Restart your game.")
        print("4. Your item or buff will appear automatically (stub mode).")
