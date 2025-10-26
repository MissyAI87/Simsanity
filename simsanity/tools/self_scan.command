#!/usr/bin/env python3
import os
import re
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime

# Point directly to the marketor folder (parent of tools/)
MARKETOR_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Setup logging
LOG_DIR = os.path.join(MARKETOR_DIR, "support", "logs")
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, "self_scan.log")

logger = logging.getLogger("self_scan")
logger.setLevel(logging.DEBUG)

handler = RotatingFileHandler(log_path, maxBytes=5*1024*1024*1024, backupCount=2)
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def log_and_print(message, level="info"):
    print(message)
    if level == "info":
        logger.info(message)
    elif level == "warning":
        logger.warning(message)
    elif level == "error":
        logger.error(message)


log_and_print("=============================================", level="info")
log_and_print(f"🕒 Self Scan Run at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", level="info")
log_and_print("=============================================", level="info")
log_and_print(f"📄 Logging scan output to: {log_path}")

# Registry of checks
CHECKS = []

def register_check(func):
    CHECKS.append(func)
    return func

@register_check
def check_bad_imports(filepath, lines):
    issues = []
    for i, line in enumerate(lines, 1):
        if "marketor.tools.support" in line:
            issues.append((i, "Bad import: marketor.tools.support should be marketor.support"))
    return issues

@register_check
def check_import_from_route(filepath, lines):
    issues = []
    for i, line in enumerate(lines, 1):
        if re.match(r"from support\.", line) or re.match(r"import support", line):
            issues.append((i, "Direct support import should use import_from_route"))
    return issues

@register_check
def check_missing_files(filepath, lines):
    issues = []
    pattern = re.compile(r'import_from_route\("([^"]+)"\)')
    for i, line in enumerate(lines, 1):
        m = pattern.search(line)
        if m:
            target = m.group(1)
            # Normalize to file path under marketor/
            target = target.replace(".", "/")
            if target.endswith("/py"):
                target = target[:-3] + ".py"
            elif not target.endswith(".py"):
                target = target + ".py"
            abs_path = os.path.join(MARKETOR_DIR, target)
            if not os.path.exists(abs_path):
                issues.append((i, f"Missing target file for import_from_route: {target}"))
    return issues

def scan_file(filepath):
    issues = []
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
        for check in CHECKS:
            try:
                issues.extend(check(filepath, lines))
            except Exception as e:
                issues.append((0, f"Check {check.__name__} failed: {e}"))
    except Exception as e:
        issues.append((0, f"Could not read file: {e}"))
    return issues

def scan_directory(root):
    results = {}
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            if filename.endswith(".py"):
                filepath = os.path.join(dirpath, filename)
                file_issues = scan_file(filepath)
                if file_issues:
                    results[filepath] = file_issues
    return results

def main():
    results = scan_directory(MARKETOR_DIR)

    scanned_files = sum(len([f for f in files if f.endswith(".py")]) for _, _, files in os.walk(MARKETOR_DIR))

    if not results:
        log_and_print(f"✅ No issues found (scanned {scanned_files} .py files)", level="info")
    else:
        log_and_print(f"⚠️ Scan complete (scanned {scanned_files} .py files)", level="warning")
        for filepath, issues in results.items():
            log_and_print(f"\nIssues in {filepath}:", level="info")
            for line, msg in issues:
                msg_text = f"Line {line}: {msg}" if line > 0 else msg
                log_and_print(f"  {msg_text}", level="info")

        # Ask user if they want to auto-fix map_route, but only if import_from_route is missing or outdated
        for filepath, issues in results.items():
            if filepath.endswith("map_route.py"):
                missing_func = any("missing import_from_route" in msg for _, msg in issues)
                inconsistent_func = any("import_from_route function is outdated or inconsistent" in msg for _, msg in issues)
                if missing_func:
                    print("\nmap_route.py is missing import_from_route. Would you like to auto-fix it? (yes/no): ", end="")
                    choice = input().strip().lower()
                    if choice == "yes":
                        fix_map_route(filepath)
                elif inconsistent_func:
                    print("\nmap_route.py import_from_route looks outdated. Would you like to update it to the standard version? (yes/no): ", end="")
                    choice = input().strip().lower()
                    if choice == "yes":
                        fix_map_route(filepath)

if __name__ == "__main__":
    main()

    # Ensure logs are flushed and closed
    for h in logger.handlers:
        try:
            h.flush()
            h.close()
        except Exception:
            pass


# --- Additional checks and fixes for map_route.py ---

@register_check
def check_map_route(filepath, lines):
    issues = []
    if filepath.endswith("map_route.py"):
        has_func = any("def import_from_route" in line for line in lines)
        if not has_func:
            issues.append((0, "map_route.py is missing import_from_route function"))
    return issues

@register_check
def check_map_route_consistency(filepath, lines):
    issues = []
    if filepath.endswith("map_route.py"):
        code_str = "".join(lines)
        if "def import_from_route" in code_str:
            expected_snippet = "def import_from_route(filepath: str):"
            if expected_snippet not in code_str:
                issues.append((0, "map_route.py import_from_route function is outdated or inconsistent"))
    return issues

def fix_map_route(filepath):
    correct_code = """def import_from_route(filepath: str):
    import importlib
    clean_path = filepath.replace("/", ".").replace(".py", "")
    if clean_path.startswith("marketor."):
        module_name = clean_path
    else:
        first_segment, *rest = clean_path.split(".")
        if first_segment in ("support", "core", "skills", "safety", "ui", "chat_only", "static", "templates"):
            module_name = f"marketor.{clean_path}"
        elif first_segment == "tools":
            module_name = f"marketor.tools.{'.'.join(rest)}"
        else:
            module_name = f"marketor.{clean_path}"
    module = importlib.import_module(module_name)
    return importlib.reload(module)
"""
    with open(filepath, "r") as f:
        lines = f.readlines()
    new_lines = []
    skip = False
    for line in lines:
        if line.strip().startswith("def import_from_route"):
            skip = True
            continue
        if skip and line.strip().startswith("def ") and not line.strip().startswith("def import_from_route"):
            skip = False
        if not skip:
            new_lines.append(line)
    new_lines.append("\n" + correct_code + "\n")
    with open(filepath, "w") as f:
        f.writelines(new_lines)
    log_and_print(f"✅ map_route.py import_from_route function replaced with correct version", level="info")
