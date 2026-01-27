#!/bin/bash
# v24 - Added --clean-workspace (-c) flag to purge student files while keeping safety marker.
# Developed with the assistance of Google Gemini

# ==============================================================================
# Alvik Robot Synchronization Script
#
# This script synchronizes a MicroPython device to mirror a local source
# directory. It protects the /workspace path and any path specified in the
# local .robotignore file.
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- SCRIPT LOGIC ---
PORT=""
SOURCE_DIR=""
CLEAN_WORKSPACE=false
ROBOTIGNORE_FILENAME=".robotignore"
SAFETY_FILE_NAME="STORE_FILES_HERE_FOR_SAFETY.md"

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--dir)
        SOURCE_DIR="$2"
        shift 2
        ;;
        -p|--port)
        PORT="$2"
        shift 2
        ;;
        -c|--clean-workspace)
        CLEAN_WORKSPACE=true
        shift
        ;;
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

echo "Running initialize_robot.sh - v24"

# --- Validate Arguments ---
if [ -z "$SOURCE_DIR" ]; then
    echo "❌ ERROR: Source directory not specified. Use -d <path>."
    exit 1
fi
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ ERROR: Source '$SOURCE_DIR' is not a valid directory."
    exit 1
fi

# --- Auto-detect port and build command arguments ---
if [ -z "$PORT" ]; then
    echo "🔎 Port not specified. Auto-detecting Alvik..."
    PORT=$(mpremote connect list | grep 'usbmodem' | awk '{print $1}' | head -n 1)
    if [ -z "$PORT" ]; then
        echo "❌ ERROR: No Alvik robot found. Please connect the robot and try again, or specify a port with -p."
        exit 1
    fi
    echo "✅ Found Alvik on port: $PORT"
fi

# Use an array for command arguments for robustness.
CONNECT_ARGS=("connect" "${PORT}")

# --- Ensure /workspace directory and safety file exist ---
echo "------------------------------------------"
echo "🛠️  Ensuring /workspace directory and safety file exist..."
if ! mpremote "${CONNECT_ARGS[@]}" ls :workspace > /dev/null 2>&1; then
    echo "   - /workspace not found. Creating it..."
    mpremote "${CONNECT_ARGS[@]}" mkdir :workspace
    echo "   - ✅ /workspace created."
else
    echo "   - ✅ /workspace already exists."
fi

SAFETY_FILE_PATH=":workspace/${SAFETY_FILE_NAME}"
if ! mpremote "${CONNECT_ARGS[@]}" ls "${SAFETY_FILE_PATH}" > /dev/null 2>&1; then
    echo "   - Safety marker file not found. Creating it..."
    mpremote "${CONNECT_ARGS[@]}" exec "with open('/workspace/${SAFETY_FILE_NAME}', 'w') as f: f.write('# This is a safe place for your files!')"
    echo "   - ✅ Safety marker file created."
else
    echo "   - ✅ Safety marker file already exists."
fi

# --- Optional Workspace Cleanup ---
if [ "$CLEAN_WORKSPACE" = true ]; then
    echo "------------------------------------------"
    echo "🧹 Cleaning /workspace directory..."
    WORKSPACE_FILES=$(mpremote "${CONNECT_ARGS[@]}" ls :workspace)
    while IFS= read -r line; do
        if [ -z "$line" ]; then continue; fi
        item_name=$(echo "$line" | sed 's/^[ ]*[0-9]*[ ]*//')
        item_name=${item_name%/}
        if [[ "$item_name" != "$SAFETY_FILE_NAME" ]]; then
            echo "   - Deleting ':workspace/$item_name'"
            mpremote "${CONNECT_ARGS[@]}" rm -r ":workspace/$item_name" > /dev/null 2>&1 || true
        fi
    done <<< "$WORKSPACE_FILES"
    echo "✅ Workspace cleaned."
fi

# --- Build Whitelist ---
WHITELIST=("/workspace") 
if [ -f "${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}" ]; then
    echo "------------------------------------------"
    echo "Found .robotignore file. Building whitelist..."
    while IFS= read -r line; do
        if [[ -n "$line" && ! "$line" =~ ^\s*# ]]; then
            WHITELIST+=("/${line}")
            echo "   - Adding '/${line}' to whitelist."
        fi
    done < "${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}"
fi

# --- Get File Lists ---
echo "------------------------------------------"
echo "🔎 Reading local and remote file systems..."
LOCAL_FILES=($(cd "$SOURCE_DIR" && ls -A))
REMOTE_FILES=$(mpremote "${CONNECT_ARGS[@]}" ls -r :)
echo "✅ File systems read."

# --- Clean Stale Files ---
echo "------------------------------------------"
echo "🧹 Cleaning stale files from the device..."
while IFS= read -r line; do
    if [ -z "$line" ] || [[ "$line" == "ls :/"* ]]; then continue; fi
    item_name=$(echo "$line" | sed 's/^[ ]*[0-9]*[ ]*//')
    item_name=${item_name%/}
    normalized_path="/${item_name}"
    on_whitelist=false
    for whitelisted_item in "${WHITELIST[@]}"; do
        if [[ "${normalized_path}" == "${whitelisted_item}"* ]]; then
            on_whitelist=true
            break
        fi
    done
    if [ "$on_whitelist" = true ]; then
        echo "   - Keeping '/${item_name}' (whitelisted)"
        continue
    fi
    is_in_source=false
    for local_item in "${LOCAL_FILES[@]}"; do
        if [[ "$item_name" == "$local_item" ]]; then
            is_in_source=true
            break
        fi
    done
    if [ "$is_in_source" = false ]; then
        path_to_delete=":${item_name}"
        echo "   - Deleting '$path_to_delete' (stale)"
        mpremote "${CONNECT_ARGS[@]}" rm -r "$path_to_delete" > /dev/null 2>&1 || true
    fi
done <<< "$REMOTE_FILES"
echo "✅ Stale files cleaned."

# --- Copy Files ---
echo "------------------------------------------"
echo "📂 Copying new/changed files to the device from '$SOURCE_DIR'..."
for item in "${LOCAL_FILES[@]}"; do
    if [[ "$item" == "$ROBOTIGNORE_FILENAME" ]]; then
        continue
    fi
    source_path="${SOURCE_DIR}/${item}"
    dest_path=":"
    echo "   - Copying '${item}' to '${dest_path}'"
    mpremote "${CONNECT_ARGS[@]}" cp -r "${source_path}" "${dest_path}"
done

echo "✅ Synchronization complete."
