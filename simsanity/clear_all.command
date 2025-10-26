#!/usr/bin/env bash

read -p "Enter the FULL path to the ECHO TOOL FOLDER (must contain config.py, core/, support/, ui/): " BASE_DIR
if [ ! -d "$BASE_DIR" ]; then
  echo "Invalid path: $BASE_DIR"
  exit 1
fi
cd "$BASE_DIR"
CONFIG_PATH="$BASE_DIR/support/config.py"

if [ -z "$BASE_DIR" ] || [ "$BASE_DIR" = "/" ]; then
  echo "Refusing to run on empty or root path."; exit 1;
fi

if [ ! -f "$CONFIG_PATH" ]; then
  echo "Warning: config.py not found at $CONFIG_PATH. Continuing anyway."
fi


echo "Base directory set to: $BASE_DIR"


LOG_FILE="$BASE_DIR/support/logs/clear_all.log"
echo "---- clear_all run on $(date) ----" >> "$LOG_FILE"

log_change() {
  echo "$1"
  echo "$1" >> "$LOG_FILE"
}

#
# Define file extensions to process (common text files)
exts=("*.txt" "*.md" "*.html" "*.htm" "*.js" "*.jsx" "*.ts" "*.tsx" "*.json" "*.yaml" "*.yml" "*.py" "*.sh" "*.css" "*.scss" "*.java" "*.c" "*.cpp" "*.h" "*.hpp" "*.rb" "*.go" "*.pl" "*.php" "*.xml" "*.ini" "*.conf" "*.cfg")

# Build find expression for extensions
find_expr=()
for ext in "${exts[@]}"; do
  find_expr+=(-name "$ext" -o)
done
# Remove trailing -o
unset 'find_expr[${#find_expr[@]}-1]'

# Function to rename files and directories containing a substring (case-sensitive)
rename_paths() {
  local old="$1"
  local new="$2"
  # Find files and directories containing the old name in their basename
  find "$BASE_DIR" -depth \( -name "*$old*" \) ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" | while read -r path; do
    if [ "$path" = "$BASE_DIR" ]; then
      continue
    fi
    base=$(basename "$path")
    dir=$(dirname "$path")
    newbase="${base//$old/$new}"
    if [ "$base" != "$newbase" ]; then
      newpath="$dir/$newbase"
      if [ ! -e "$newpath" ]; then
        mv "$path" "$newpath"
        log_change "Renamed '$path' to '$newpath'"
      else
        log_change "Cannot rename '$path' to '$newpath': target exists, skipping."
      fi
    fi
  done
}

parent_folder_renamed=""
new_echo_name=""
echo
read -p "Do you want to rename the parent folder and update config? (y/n) " rename_parent_answer
if [[ "$rename_parent_answer" == "y" || "$rename_parent_answer" == "Y" ]]; then
  read -p "Enter old parent folder name: " old_parent
  read -p "Enter the new tool name: " new_name
  if [ -d "$BASE_DIR/../$old_parent" ]; then
    new_abs_path="$(dirname "$BASE_DIR")/$new_name"
    mv "$(dirname "$BASE_DIR")/$old_parent" "$new_abs_path"
    log_change "Renamed parent folder '$old_parent' to '$new_name'"
    BASE_DIR="$(cd "$new_abs_path" && pwd)"
    CONFIG_PATH="$BASE_DIR/support/config.py"
    LOG_FILE="$BASE_DIR/support/logs/clear_all.log"
    echo "---- clear_all resumed after rename on $(date) ----" >> "$LOG_FILE"
    echo "New BASE_DIR resolved to: $BASE_DIR"
    cd "$BASE_DIR" || { log_change "Failed to cd into $BASE_DIR after rename"; exit 1; }
    log_change "Recalculated BASE_DIR after rename: $BASE_DIR"
    parent_folder_renamed="$new_name"
    new_echo_name="$new_name"
    # Update ECHO_NAME in config.py robustly
    if [ -f "$CONFIG_PATH" ]; then
      if grep -Eq "^[[:space:]]*ECHO_NAME[[:space:]]*=" "$CONFIG_PATH"; then
        sed -i '' -E "s|^[[:space:]]*ECHO_NAME[[:space:]]*=.*|ECHO_NAME = \"${new_echo_name}\"|" "$CONFIG_PATH"
        log_change "Updated existing ECHO_NAME line in $CONFIG_PATH to $new_echo_name"
      else
        log_change "ECHO_NAME line not found in $CONFIG_PATH — appending it."
        printf "\nECHO_NAME = \"%s\"\n" "$new_echo_name" >> "$CONFIG_PATH"
      fi
    else
      log_change "ERROR: config.py not found at $CONFIG_PATH, cannot update."
    fi

    # Prompt to update UI title and header to reflect new tool name
    echo
    read -p "Do you want to update the UI title and header to the new tool name? (y/n) " update_ui_name
    if [[ "$update_ui_name" == "y" || "$update_ui_name" == "Y" ]]; then
      INDEX_HTML="$BASE_DIR/ui/templates/index.html"
      if [ -f "$INDEX_HTML" ]; then
        sed -i '' -E "s|(<title>).*?(</title>)|\1${new_echo_name}\2|" "$INDEX_HTML"
        sed -i '' -E "s|(<h1>).*?(</h1>)|\1${new_echo_name}\2|" "$INDEX_HTML"
        log_change "Updated UI title and header in $INDEX_HTML to '$new_echo_name'"
      else
        log_change "No index.html found at $INDEX_HTML, skipped UI name update."
      fi
    else
      log_change "UI name update skipped by user."
    fi

    # Prompt to update imports referencing old parent folder
    echo
    read -p "Do you want to update imports that reference the old parent folder? (y/n) " update_imports_answer
    if [[ "$update_imports_answer" == "y" || "$update_imports_answer" == "Y" ]]; then
      log_change "Updating import statements in .py files: replacing '$old_parent' with '$new_name' in import statements..."
      # Find all .py files except in .git, node_modules, __pycache__
      find "$BASE_DIR" -type f -name "*.py" ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" | while read -r pyfile; do
        # Use grep to check if file contains 'from old_parent' or 'import old_parent'
        if grep -qE "^[[:space:]]*(from|import)[[:space:]]+$old_parent(\.|[[:space:]])" "$pyfile"; then
          # Use sed to replace in-place: from old_parent -> from new_name, import old_parent -> import new_name
          sed -i '' -E "s/^([[:space:]]*from[[:space:]]+)$old_parent([\. ])/\\1$new_name\\2/g; s/^([[:space:]]*import[[:space:]]+)$old_parent([\. ])/\\1$new_name\\2/g" "$pyfile"
          log_change "Updated imports in $pyfile"
        fi
      done
      log_change "Import statements update complete."
    fi
  else
    log_change "Parent folder '$old_parent' not found. Skipping rename."
    new_name=""
  fi
else
  new_name=""
fi

echo
read -p "Do you want to rename files or folders? (y/n) " rename_files_answer
if [[ "$rename_files_answer" == "y" || "$rename_files_answer" == "Y" ]]; then
  log_change "Enter rename pairs in the format 'old_name new_name' or 'old_name what_name_we_use new_name', one per line."
  log_change "You can rename both files and folders. The script will search recursively under the base directory."
  log_change "When done, enter an empty line."

  while true; do
    read -p "Rename file/folder: " line
    if [[ -z "$line" ]]; then
      break
    fi
    # Split input into words
    read -r -a parts <<< "$line"
    if [[ ${#parts[@]} -eq 2 ]]; then
      old_name="${parts[0]}"
      new_name="${parts[1]}"
      # Find path matching old_name or old_name.*
      found_path=$(find "$BASE_DIR" -depth \( -name "$old_name" -o -name "$old_name.*" \) ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*" | head -n 1)
      if [[ -n "$found_path" ]]; then
        dir=$(dirname "$found_path")
        newpath="$dir/$new_name"
        if [ ! -e "$newpath" ]; then
          mv "$found_path" "$newpath"
          log_change "Renamed '$found_path' to '$newpath'"
        else
          log_change "Cannot rename '$found_path' to '$newpath': target exists, skipping."
        fi
      else
        log_change "Warning: '$old_name' not found under base directory, skipping."
      fi
    elif [[ ${#parts[@]} -eq 3 ]]; then
      old_name="${parts[0]}"
      what_name_we_use="${parts[1]}"
      new_name="${parts[2]}"
      # First replace old_name with what_name_we_use in file and folder names
      rename_paths "$old_name" "$what_name_we_use"
      # Then rename what_name_we_use to new_name
      rename_paths "$what_name_we_use" "$new_name"
    else
      log_change "Invalid input format. Please enter either 'old_name new_name' or 'old_name what_name_we_use new_name'."
    fi
  done
fi

stub_files_erased=0
read -p "Do you want to erase stub files? (y/n) " erase_stub_answer
if [[ "$erase_stub_answer" == "y" || "$erase_stub_answer" == "Y" ]]; then
  echo
  # Section: Optionally erase code in files containing 'stub'
  log_change "Now searching for files with 'stub' in their name (excluding .git, node_modules, __pycache__)."
  log_change "For each such file, you can choose to erase its contents."
  stub_files=()
  while IFS= read -r file; do
    stub_files+=("$file")
  done < <(find "$BASE_DIR" -type f -iname "*stub*" ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*")
  for file in "${stub_files[@]}"; do
    echo
    read -p "Erase contents of $file? (y/n) " answer
    if [[ "$answer" == "y" || "$answer" == "Y" ]]; then
      > "$file"
      log_change "Erased contents of $file"
      ((stub_files_erased++))
    else
      log_change "Left $file unchanged."
    fi
  done
fi

read -p "Do you want to change action buttons in app.js to commented-out stubs? (y/n) " update_buttons
if [[ "$update_buttons" == "y" || "$update_buttons" == "Y" ]]; then
  if [ -f "$BASE_DIR/ui/static/app.js" ]; then
    sed -i '' -E 's|(.*<button.*>.*</button>.*)|// \1 <!-- Stub -->|' "$BASE_DIR/ui/static/app.js"
    log_change "Updated action buttons in app.js to commented-out stubs."
  else
    log_change "app.js not found in ui/static/, skipping."
  fi
fi

echo
read -p "Delete logs? Options: none/log/all: " delete_logs
if [[ "$delete_logs" == "log" ]]; then
  log_change "Deleting only .log files from support/logs and support/logs/archive..."
  find "$BASE_DIR/support/logs" -type f -name "*.log" -delete
  find "$BASE_DIR/support/logs/archive" -type f -name "*.log" -delete
  log_change "Log files deleted."
elif [[ "$delete_logs" == "all" ]]; then
  log_change "Deleting ALL files from support/logs and support/logs/archive..."
  rm -f "$BASE_DIR/support/logs"/*
  rm -f "$BASE_DIR/support/logs/archive"/*
  log_change "All log and archive files deleted."
else
  log_change "Log files left unchanged."
fi

echo
read -p "Do you want me to create a run command file? (y/n) " create_run_command
if [[ "$create_run_command" == "y" || "$create_run_command" == "Y" ]]; then
  read -p "Enter the directory path where run_echo.command should be created: " run_command_dir
  # Determine which parent folder to use for run command creation
  parent_folder="$BASE_DIR"

  # Set new_echo_name for use in run_echo.command
  if [[ -n "$parent_folder_renamed" ]]; then
    new_echo_name="$parent_folder_renamed"
  elif [[ -n "$new_name" ]]; then
    new_echo_name="$new_name"
  fi
  # If still not set, use the basename of BASE_DIR
  if [[ -z "$new_echo_name" ]]; then
    new_echo_name="$(basename "$BASE_DIR")"
  fi

  if [ ! -d "$parent_folder" ]; then
    log_change "Parent folder path for run command does not exist: $parent_folder"
    exit 1
  fi

  log_change "Creating run_echo.command in directory: $run_command_dir"
  log_change "Using parent folder path: $parent_folder"
  log_change "Using tool/module name: $new_echo_name"

  run_command_path="$run_command_dir/run_echo.command"

  cat > "$run_command_path" <<EOF
#!/bin/zsh
# Usage: ./run_echo.command [PORT]

PORT="\${1:-8080}"

if [ -d "$parent_folder/venv" ]; then
  source "$parent_folder/venv/bin/activate"
fi

# --- Cleanup Section: Remove macOS Finder .DS_Store files ---
find "$parent_folder" -name '*.DS_Store' -type f -delete
find "$parent_folder" -name '.*.DS_Store' -type f -delete
echo "Cleaned up macOS Finder .DS_Store files."

upgrade_pip() {
  python3 -m pip install --upgrade pip
}

install_requirements() {
  if [ -f "$parent_folder/requirements.txt" ]; then
    python3 -m pip install -r "$parent_folder/requirements.txt"
  fi
}

run_server() {
  cd "\$(dirname "$parent_folder")"
  python3 -u -m "${new_echo_name}.ui.server" --port "\$PORT" 2>&1 | tee "$parent_folder/support/logs/server-\$PORT.log"
}

open_browser() {
  open "http://localhost:\$PORT"
}

upgrade_pip
install_requirements
run_server &
sleep 2
open_browser
wait
EOF

  chmod +x "$run_command_path"
  log_change "Created and made executable: $run_command_path"
fi

echo
log_change "Summary of changes made:"
if [[ -n "$parent_folder_renamed" ]]; then
  log_change "- Parent folder renamed to: $parent_folder_renamed"
else
  log_change "- Parent folder not renamed."
fi

if [[ -n "$new_echo_name" ]]; then
  log_change "- ECHO_NAME updated in $CONFIG_PATH to: $new_echo_name"
else
  log_change "- ECHO_NAME in $CONFIG_PATH not updated."
fi

# UI name update summary
if [[ "$update_ui_name" == "y" || "$update_ui_name" == "Y" ]]; then
  log_change "- UI title and header updated to: $new_echo_name"
else
  log_change "- UI title and header not updated."
fi

if [[ "$create_run_command" == "y" || "$create_run_command" == "Y" ]]; then
  log_change "- Run command file created at: $run_command_path"
else
  log_change "- Run command file not created."
fi

log_change "- Log files deletion choice: $delete_logs"

log_change "- Stub files erased: $stub_files_erased"

if [[ "$update_buttons" == "y" || "$update_buttons" == "Y" ]]; then
  log_change "- Action buttons in app.js changed to commented-out stubs."
else
  log_change "- Action buttons in app.js left unchanged."
fi

echo
log_change "Script completed."

echo
echo "---- INTERNAL SELF-SCAN ----"
log_change "---- Internal Self-Scan initiated ----"

# --- Find Echo Modules ---
# Echo module = directory with core/ and support/ as subdirs
find_echo_modules() {
  local base="$1"
  base="$(cd "$base" && pwd)"  # normalize absolute path
  local modules=()

  # include base itself if it's an Echo
  if [ -d "$base/core" ] && [ -d "$base/support" ]; then
    modules+=("$base")
  fi

  # find submodules strictly inside base, using absolute paths only
  while IFS= read -r d; do
    local abs="$(realpath "$d" 2>/dev/null)"
    if [[ "$abs" == "$base"* ]] && [ -d "$abs/core" ] && [ -d "$abs/support" ]; then
      modules+=("$abs")
    fi
  done < <(find "$base" -mindepth 1 -maxdepth 3 -type d -name core -prune -exec dirname {} \; | sort -u)

  # remove duplicates
  modules=($(printf "%s\n" "${modules[@]}" | sort -u))
  echo "${modules[@]}"
}

# --- Scan Functions, param is echo module dir ---
scan_structure() {
  local dir="$1"
  local issues=()
  local required=("core" "support" "ui")
  for d in "${required[@]}"; do
    if [ ! -d "$dir/$d" ]; then
      issues+=("❌ Missing folder: $d/")
    else
      log_change "[$(basename "$dir")] ✅ Folder exists: $d/"
    fi
  done
  echo "${issues[@]}"
}

scan_imports() {
  local dir="$1"
  local issues=()
  local fixables=()
  log_change "[$(basename "$dir")] Scanning for bad imports..."
  while IFS= read -r pyfile; do
    if grep -q "marketor.tools.support" "$pyfile"; then
      issues+=("⚠️ Bad import path in $pyfile (marketor.tools.support)")
      fixables+=("$pyfile")
    fi
    if grep -qE "^[[:space:]]*(from|import)[[:space:]]+support" "$pyfile"; then
      issues+=("⚠️ Direct support import in $pyfile (should use import_from_route)")
      fixables+=("$pyfile")
    fi
  done < <(find "$dir" -type f -name "*.py" ! -path "*/.git/*" ! -path "*/node_modules/*" ! -path "*/__pycache__/*")
  # Return as two arrays: issues, fixables
  echo "${issues[@]}|${fixables[@]}"
}

scan_maps() {
  local dir="$1"
  local issues=()
  local missing=()
  log_change "[$(basename "$dir")] Checking for map files..."
  local MAP_ROUTE="$dir/core/map_route.py"
  local ROUTE_MD="$dir/route_index.md"
  local ROUTE_JSON="$dir/route_index.json"
  if [ ! -f "$MAP_ROUTE" ]; then
    issues+=("❌ Missing $MAP_ROUTE")
    missing+=("$MAP_ROUTE")
  else
    if ! grep -q "def import_from_route" "$MAP_ROUTE"; then
      issues+=("⚠️ $MAP_ROUTE missing import_from_route()")
      missing+=("$MAP_ROUTE")
    fi
  fi
  if [ ! -f "$ROUTE_MD" ]; then
    issues+=("⚠️ Missing $ROUTE_MD")
    missing+=("$ROUTE_MD")
  fi
  if [ ! -f "$ROUTE_JSON" ]; then
    issues+=("⚠️ Missing $ROUTE_JSON")
    missing+=("$ROUTE_JSON")
  fi
  echo "${issues[@]}|${missing[@]}"
}

fix_imports() {
  local files=("$@")
  for f in "${files[@]}"; do
    sed -i '' -E 's|marketor\.tools\.support|marketor.support|g' "$f"
    sed -i '' -E 's|(^[[:space:]]*(from|import)[[:space:]]+)support|\1from tools.map_route import import_from_route # patched|g' "$f"
    log_change "Fixed imports in $f"
  done
}

fix_maps() {
  local files=("$@")
  for f in "${files[@]}"; do
    if [[ "$f" == *"map_route.py"* ]]; then
      cat > "$f" <<EOF
def import_from_route(path):
    import importlib.util, os
    base_dir = os.path.dirname(__file__)
    target = os.path.join(base_dir, path)
    spec = importlib.util.spec_from_file_location("dynamic_module", target)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
EOF
      log_change "Created or repaired $f"
    elif [[ "$f" == *"route_index.md"* ]]; then
      echo "# Route Index (Auto-Generated)" > "$f"
      log_change "Generated placeholder $f"
    elif [[ "$f" == *"route_index.json"* ]]; then
      echo "{}" > "$f"
      log_change "Generated placeholder $f"
    fi
  done
}

# --- Run multi-module scan ---
echo
log_change "Searching for echo modules under $BASE_DIR..."
ECHO_MODULES=($(find_echo_modules "$BASE_DIR"))
if [ ${#ECHO_MODULES[@]} -eq 0 ]; then
  echo "❌ No echo modules found under $BASE_DIR (must have core/ and support/)."
  log_change "No echo modules found. Skipping self-scan."
else
  echo "Found echo modules:"
  for em in "${ECHO_MODULES[@]}"; do
    echo " - $(basename "$em") : $em"
    log_change "Found echo module: $em"
  done
  echo
  declare -A MODULE_ISSUES
  declare -A MODULE_FIXABLE_IMPORTS
  declare -A MODULE_MISSING_MAPS
  MODULE_OK=()
  for em in "${ECHO_MODULES[@]}"; do
    modname="$(basename "$em")"
    issues=()
    fixables=()
    missingmaps=()
    # Structure
    IFS=$'\n' read -r -a struct_issues <<< "$(scan_structure "$em")"
    # Imports
    IFS="|" read -r import_issues_raw import_fixables_raw <<< "$(scan_imports "$em")"
    IFS=$'\n' read -r -a import_issues <<< "$import_issues_raw"
    IFS=' ' read -r -a import_fixables <<< "$import_fixables_raw"
    # Maps
    IFS="|" read -r map_issues_raw map_missing_raw <<< "$(scan_maps "$em")"
    IFS=$'\n' read -r -a map_issues <<< "$map_issues_raw"
    IFS=' ' read -r -a map_missing <<< "$map_missing_raw"
    # Aggregate
    issues=("${struct_issues[@]}" "${import_issues[@]}" "${map_issues[@]}")
    fixables=("${import_fixables[@]}")
    missingmaps=("${map_missing[@]}")
    MODULE_ISSUES["$modname"]="${issues[*]}"
    MODULE_FIXABLE_IMPORTS["$modname"]="${fixables[*]}"
    MODULE_MISSING_MAPS["$modname"]="${missingmaps[*]}"
    # Print status line
    if [ ${#issues[@]} -eq 0 ]; then
      echo "✅ $modname: OK"
      log_change "[$modname] OK"
      MODULE_OK+=("$modname")
    else
      # Compose short summary
      # Show first error or warning if present, else generic
      summary=""
      for i in "${issues[@]}"; do
        if [[ "$i" == "❌"* ]]; then summary="$i"; break; fi
      done
      if [[ -z "$summary" ]]; then
        for i in "${issues[@]}"; do
          if [[ "$i" == "⚠️"* ]]; then summary="$i"; break; fi
        done
      fi
      if [[ -z "$summary" ]]; then summary="Issues found"; fi
      # Only show file part for missing map/md/json
      if [[ "$summary" == *"Missing "* ]]; then
        summary="Missing $(basename "${summary##*Missing }")"
      fi
      echo "⚠️ $modname: $summary"
      log_change "[$modname] $summary"
    fi
  done
  echo
  echo "🔍 Self-scan results:"
  for em in "${ECHO_MODULES[@]}"; do
    modname="$(basename "$em")"
    issues_str="${MODULE_ISSUES[$modname]}"
    if [ -z "$issues_str" ]; then
      echo " - ✅ $modname: OK"
      log_change "[$modname] OK"
    else
      IFS=$'\n' read -r -a issues <<< "$issues_str"
      for issue in "${issues[@]}"; do
        [ -n "$issue" ] && echo " - $issue"
        [ -n "$issue" ] && log_change "[$modname] $issue"
      done
    fi
  done
  echo
  # Aggregate all issues/fixables/missing
  all_issues=()
  all_fixables=()
  all_missing=()
  for em in "${ECHO_MODULES[@]}"; do
    modname="$(basename "$em")"
    issues=(${MODULE_ISSUES[$modname]})
    fixables=(${MODULE_FIXABLE_IMPORTS[$modname]})
    missing=(${MODULE_MISSING_MAPS[$modname]})
    all_issues+=("${issues[@]}")
    all_fixables+=("${fixables[@]}")
    all_missing+=("${missing[@]}")
  done
  if [ ${#all_issues[@]} -gt 0 ]; then
    echo "What would you like to do?"
    echo "1) Do nothing"
    echo "2) Fix only map files"
    echo "3) Fix imports"
    echo "4) Fix everything"
    read -p "Enter choice [1-4]: " fix_choice
    case $fix_choice in
      2)
        fix_maps "${all_missing[@]}"
        ;;
      3)
        fix_imports "${all_fixables[@]}"
        ;;
      4)
        fix_imports "${all_fixables[@]}"
        fix_maps "${all_missing[@]}"
        ;;
      *)
        log_change "No fixes applied."
        ;;
    esac
  fi
fi

echo
log_change "---- Internal Self-Scan completed ----"
echo "Self-scan complete. Review clear_all.log for details."

# --- Summary with colorized output ---
total_ok=${#MODULE_OK[@]}
total_mods=${#ECHO_MODULES[@]}
total_issues=$((total_mods - total_ok))

green="\033[0;32m"
yellow="\033[0;33m"
red="\033[0;31m"
nc="\033[0m"

echo
echo -e "Scan summary:"
echo -e "${green}${total_ok} OK${nc}, ${red}${total_issues} with issues${nc}, ${yellow}${total_mods} total modules${nc}"
echo
echo -e "-------------------------------------------"
echo -e "${green}Self-scan complete.${nc} Review ${yellow}support/logs/clear_all.log${nc} for full details."
echo -e "-------------------------------------------"
