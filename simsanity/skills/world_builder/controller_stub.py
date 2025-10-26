from . import (
    region_tools_stub,
    terrain_editor_stub,
    weather_manager_stub,
    population_planner_stub,
    economy_balancer_stub,
    event_scheduler_stub,
    save_exporter_stub,
    world_editor_stub,
)

class WorldBuilderDashboard:
    def __init__(self):
        self.modules = {
            "region_tools": region_tools_stub.RegionTools(),
            "terrain": terrain_editor_stub.TerrainEditor(),
            "weather": weather_manager_stub.WeatherManager(),
            "population": population_planner_stub.PopulationPlanner(),
            "economy": economy_balancer_stub.EconomyBalancer(),
            "events": event_scheduler_stub.EventScheduler(),
            "export": save_exporter_stub.SaveExporter(),
            "editor": world_editor_stub.WorldEditor(),
        }

    def initialize(self):
        print("[WorldBuilderDashboard] Initializing stubbed modules...")
        for name, mod in self.modules.items():
            print(f" - Loaded {name}: {mod.__class__.__name__}")

    def build_world(self, seed=None):
        print(f"[WorldBuilderDashboard] Building world (seed={seed})...")
        self.modules["region_tools"].prepare_regions()
        self.modules["terrain"].generate_terrain()
        self.modules["weather"].setup_weather()
        self.modules["population"].populate()
        self.modules["economy"].initialize_economy()
        self.modules["events"].schedule_core_events()
        self.modules["export"].export_summary()
        self.modules["editor"].package_world()
        print("[WorldBuilderDashboard] Stub world build complete.")
