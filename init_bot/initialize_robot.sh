#!/bin/bash
# v13 - Architectural refactor to a directory-mirroring model.

# ==============================================================================
# Alvik Robot Synchronization Script
#
# This script synchronizes a MicroPython device to mirror a local source
# directory, while protecting whitelisted paths on the device.
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- SCRIPT LOGIC ---
PORT=""
SOURCE_DIR=""
WHITELIST_FILENAME=".robotignore"

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
        *)
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

echo "Running initialize_robot.sh - v13"

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


# --- EXECUTION ---

echo "🚀 Starting SYNCHRONIZATION for device..."
echo "   (This will delete non-whitelisted remote files)"

# --- Read Whitelist ---
WHITELIST_FILE="${SOURCE_DIR}/${WHITELIST_FILENAME}"
WHITELIST=() # Initialize as empty array
if [ -f "$WHITELIST_FILE" ]; then
    echo "------------------------------------------"
    echo "🔎 Found whitelist file: $WHITELIST_FILE"
    # Read file into array, skipping comments and empty lines
    mapfile -t WHITELIST < <(grep -v -e '^#' -e '^[[:space:]]*$' "$WHITELIST_FILE")
else
    echo "------------------------------------------"
    echo "🔎 No whitelist file found. All remote files are subject to deletion."
fi

# --- Clean Device ---
echo "------------------------------------------"
echo "🔎 Reading remote file system..."
REMOTE_FILES=$(mpremote "${CONNECT_ARGS[@]}" ls : 2>/dev/null || true)
echo "✅ Remote file system read."
echo "------------------------------------------"
echo "🧹 Cleaning the device (respecting whitelist)..."

while IFS= read -r line; do
    if [ -z "$line" ] || [[ "$line" == "ls :"* ]]; then continue; fi

    item_name=$(echo "$line" | sed 's/^[ ]*[0-9]*[ ]*//')
    normalized_path="/${item_name}"

    on_whitelist=false
    for whitelisted_item in "${WHITELIST[@]}"; do
        if [[ "$normalized_path" == "$whitelisted_item"* ]]; then
            on_whitelist=true
            break
        fi
    done
    
    if [ "$on_whitelist" = false ]; then
        path_to_delete=":${item_name}"
        echo "   - Deleting '$path_to_delete'"
        mpremote "${CONNECT_ARGS[@]}" rm -r "$path_to_delete" > /dev/null 2>&1 || true
    else
        echo "   - Keeping '/${item_name}' (whitelisted)"
    fi
done <<< "$REMOTE_FILES"
echo "✅ Device cleaned."

# --- Copy Files ---
echo "------------------------------------------"
echo "📂 Copying new files to the device from '$SOURCE_DIR'..."

# Use find to get a list of all files and directories to copy
find "$SOURCE_DIR" -mindepth 1 -maxdepth 1 | while IFS= read -r item_path; do
    item_name=$(basename "$item_path")
    
    # Skip the whitelist file itself
    if [ "$item_name" = "$WHITELIST_FILENAME" ]; then
        echo "   - Skipping copy of '$WHITELIST_FILENAME'"
        continue
    fi

    echo "   - Copying '$item_name' to ':'"
    mpremote "${CONNECT_ARGS[@]}" cp -r "$item_path" ":"
done

echo "✅ Synchronization complete."

