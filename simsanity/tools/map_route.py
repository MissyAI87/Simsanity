import importlib

from support.config import ECHO_NAME

"""
Generic Route Map for Echo Shell
Auto-generated from folder structure
"""

ROUTES = {
    "core": {
        "files": [
            "core/commands.py",
            "core/controller.py",
            "core/handler.py",
            "core/main.py",
            "core/parser.py",
            "core/utils.py"
        ]
    },
    "skills": {
        "files": [
            "skills/cheats_controller.py",
            "skills/how_to_controller.py",
            "skills/modfix/modfix_controller.py",
            "skills/read_save/rs_controller.py",
            "skills/small_mod_maker/smm_controller.py",
            "skills/world_builder/wb_controller.py"
        ]
    },
    "support": {
        "files": [
            "support/config.py",
            "support/logging.py"
        ]
    },
    "safety": {
        "files": [
            "safety/ethics.py",
            "safety/security.py"
        ]
    },
    "ui": {
        "files": [
            "ui/routes.py",
            "ui/server.py"
        ]
    },
    "tools": {
        "files": [
            "tools/controller.py",
            "tools/main.py",
            "tools/parser.py",
            "tools/handler.py"
        ]
    },
    "chat_only": {
        "files": [
            "chat_only/natural_language.py",
            "chat_only/chat_shell.command"
        ]
    },
    "static": {
        "files": [
            "static/app.js",
            "static/style.css"
        ]
    },
    "templates": {
        "files": [
            "templates/index.html"
        ]
    }
}

def import_from_route(filepath: str):
    """
    Dynamically import a module given its filepath from ROUTES.
    Accepts relative paths like 'support/logging.py' or 'core/controller.py'.
    Example: 'core/controller.py' -> core.controller
    Always reloads the module to ensure updates are reflected.
    """
    clean_path = filepath.replace("/", ".").replace(".py", "")
    print(f"[MAP ROUTE DEBUG] filepath={filepath}, clean_path={clean_path}")
    first_segment, *rest = clean_path.split(".")
    known_sections = ("support", "tools", "skills", "safety", "ui", "chat_only", "static", "templates")
    if first_segment in known_sections:
        module_name = f"simsanity.{clean_path}"
    else:
        module_name = f"simsanity.{clean_path}"
    print(f"[MAP ROUTE DEBUG] resolved module_name={module_name}")
    module = importlib.import_module(module_name)
    return importlib.reload(module)

def list_routes():
    """Pretty print the route map."""
    for section, data in ROUTES.items():
        print(f"\n[{section.upper()}]")
        for f in data["files"]:
            print(f" - {f}")

if __name__ == "__main__":
    list_routes()

# NOTE:
# ROUTES dictionary now lists files without any tool prefix.
# Tool-specific test files like support/test_oracle.py are excluded.
# When calling import_from_route(), use relative paths like "core/parser.py".

def socials_parser():
    return import_from_route("tools/parser.py").parse_socials

def socials_handler():
    return import_from_route("tools/handler.py").handle_message
