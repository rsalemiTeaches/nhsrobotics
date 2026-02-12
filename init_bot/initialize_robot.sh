#!/bin/bash
# v27 - FIXED: Added carriage return stripping (tr -d '\r') to remote output.
#       This fixes the bug where files were falsely identified as "extraneous"
#       due to invisible characters in the serial output.
#
# Developed with the assistance of Google Gemini

set -e

# --- CONFIGURATION ---
PORT=""
SOURCE_DIR=""
CLEAN_WORKSPACE=false
ROBOTIGNORE_FILENAME=".robotignore"
SAFETY_FILE_NAME="STORE_FILES_HERE_FOR_SAFETY.md"

# --- ARGUMENT PARSING ---
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--dir) SOURCE_DIR="$2"; shift 2 ;;
        -p|--port) PORT="$2"; shift 2 ;;
        -c|--clean-workspace) CLEAN_WORKSPACE=true; shift ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

echo "Running initialize_robot.sh - v27 (CRLF Fix)"

# --- VALIDATION ---
if [ -z "$SOURCE_DIR" ]; then echo "❌ ERROR: Source directory not specified. Use -d <path>."; exit 1; fi
if [ ! -d "$SOURCE_DIR" ]; then echo "❌ ERROR: Source '$SOURCE_DIR' is not a valid directory."; exit 1; fi

# --- AUTO-DETECT PORT ---
if [ -z "$PORT" ]; then
    echo "🔎 Auto-detecting Alvik..."
    PORT=$(mpremote connect list | grep 'usbmodem' | awk '{print $1}' | head -n 1)
    if [ -z "$PORT" ]; then echo "❌ ERROR: No robot found."; exit 1; fi
    echo "✅ Found Alvik on port: $PORT"
fi
CONNECT_ARGS=("connect" "${PORT}")

# --- SETUP WORKSPACE ---
echo "------------------------------------------"
echo "🛠️  Checking /workspace..."
if ! mpremote "${CONNECT_ARGS[@]}" ls :workspace > /dev/null 2>&1; then
    mpremote "${CONNECT_ARGS[@]}" mkdir :workspace
    echo "   - Created /workspace"
fi
# Ensure safety file
mpremote "${CONNECT_ARGS[@]}" exec "
import os
try:
    with open('/workspace/${SAFETY_FILE_NAME}', 'w') as f: f.write('# Safe place!')
except: pass
"

# --- OPTIONAL WORKSPACE CLEAN ---
if [ "$CLEAN_WORKSPACE" = true ]; then
    echo "🧹 Cleaning /workspace (keeping safety file)..."
    mpremote "${CONNECT_ARGS[@]}" exec "
import os
try:
    for f in os.ilistdir('/workspace'):
        name = f[0]
        if name != '${SAFETY_FILE_NAME}':
            path = '/workspace/' + name
            try:
                os.remove(path)
            except:
                pass 
            print('Deleted ' + path)
except: pass
"
    echo "✅ Workspace cleaned."
fi

# --- BUILD WHITELIST ---
WHITELIST=("/workspace") 
if [ -f "${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}" ]; then
    echo "Found .robotignore. Building whitelist..."
    while IFS= read -r line; do
        if [[ -n "$line" && ! "$line" =~ ^\s*# ]]; then
            # Ensure leading slash for comparison
            [[ "$line" != /* ]] && line="/$line"
            WHITELIST+=("$line")
        fi
    done < "${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}"
fi

# --- PYTHON FILESYSTEM WALKER ---
WALKER_SCRIPT="
import os
def walk(top):
    try:
        for entry in os.ilistdir(top):
            name = entry[0]
            if name in ['.', '..']: continue
            
            # Construct full path
            if top == '/': path = '/' + name
            elif top == '': path = name
            else: path = top + '/' + name
            
            # Entry[1] is type. 0x4000=Dir, 0x8000=File
            is_dir = (entry[1] & 0x4000) == 0x4000
            
            if is_dir:
                print('D|' + path)
                walk(path)
            else:
                print('F|' + path)
    except OSError:
        pass
walk('')
"

echo "------------------------------------------"
echo "🔎 Scanning remote filesystem recursively..."
# FIX: Pipe output to tr -d '\r' to strip carriage returns
REMOTE_ITEMS=$(mpremote "${CONNECT_ARGS[@]}" exec "$WALKER_SCRIPT" | tr -d '\r')

echo "🧹 Comparing and Cleaning..."

# Process the remote list line by line
while IFS= read -r line; do
    if [[ -z "$line" ]]; then continue; fi
    
    TYPE=$(echo "$line" | cut -d'|' -f1)
    RPATH=$(echo "$line" | cut -d'|' -f2)
    
    # Normalize path with leading slash for whitelist check
    NORM_PATH="/$RPATH"
    [[ "$RPATH" == /* ]] || NORM_PATH="/$RPATH"

    # 1. WHITELIST CHECK
    SKIP=false
    for allow in "${WHITELIST[@]}"; do
        if [[ "$NORM_PATH" == "$allow"* ]]; then
            # echo "   - Keeping '$RPATH' (Whitelisted)"
            SKIP=true
            break
        fi
    done
    if [ "$SKIP" = true ]; then continue; fi

    # 2. LOCAL EXISTENCE CHECK
    LOCAL_PATH="${SOURCE_DIR}/${RPATH}"
    
    EXISTS_LOCALLY=false
    if [ "$TYPE" == "D" ]; then
        if [ -d "$LOCAL_PATH" ]; then EXISTS_LOCALLY=true; fi
    else
        if [ -f "$LOCAL_PATH" ]; then EXISTS_LOCALLY=true; fi
    fi

    # 3. DELETE IF STALE
    if [ "$EXISTS_LOCALLY" = false ]; then
        echo "   - 🗑️  Removing extraneous item: $RPATH"
        mpremote "${CONNECT_ARGS[@]}" rm -r ":$RPATH" > /dev/null 2>&1 || true
    fi

done <<< "$REMOTE_ITEMS"

echo "✅ Cleanup complete."

# --- COPY FILES ---
echo "------------------------------------------"
echo "📂 Uploading local files..."
mpremote "${CONNECT_ARGS[@]}" cp -r "${SOURCE_DIR}/"* :

echo "✅ Synchronization complete."
