#!/bin/bash
# v20 - Implement intelligent sync: only delete remote files not present locally.

# ==============================================================================
# Alvik Robot Synchronization Script
#
# This script synchronizes a MicroPython device to mirror a local source
# directory. It protects the /workspace path and any path specified in the
# local .robotignore file.
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- SCRIPT LOGIC ---
PORT=""
SOURCE_DIR=""
ROBOTIGNORE_FILENAME=".robotignore"

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

echo "Running initialize_robot.sh - v20"

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
echo "   (This will delete stale remote files)"

# --- Read Ignore File to build Whitelist and Ignore List ---
ROBOTIGNORE_FILE="${SOURCE_DIR}/${ROBOTIGNORE_FILENAME}"
WHITELIST=("/workspace")
IGNORE_LIST=()

if [ -f "$ROBOTIGNORE_FILE" ]; then
    echo "------------------------------------------"
    echo "🔎 Found ignore file: $ROBOTIGNORE_FILE"
    while IFS= read -r line; do
        if [[ "$line" =~ ^# ]] || [[ -z "$line" ]]; then continue; fi
        IGNORE_LIST+=("$line")
    done < "$ROBOTIGNORE_FILE"
    
    for item in "${IGNORE_LIST[@]}"; do
        WHITELIST+=("/${item}")
    done
else
    echo "------------------------------------------"
    echo "🔎 No .robotignore file found."
fi

echo "ℹ️ The '/workspace' directory on the robot is protected from deletion."

# --- Get Local File List (respecting ignore list) ---
echo "------------------------------------------"
echo "🔎 Reading local file system from '$SOURCE_DIR'..."
LOCAL_FILES=()
while IFS= read -r item_path; do
    item_name=$(basename "$item_path")
    if [ "$item_name" = "$ROBOTIGNORE_FILENAME" ]; then continue; fi
    is_ignored=false
    for ignored_item in "${IGNORE_LIST[@]}"; do
        if [[ "$item_name" == "$ignored_item" ]]; then
            is_ignored=true
            break
        fi
    done
    if [ "$is_ignored" = false ]; then
        LOCAL_FILES+=("$item_name")
    fi
done < <(find "$SOURCE_DIR" -mindepth 1 -maxdepth 1)
echo "✅ Local file system read."


# --- Clean Stale Files from Device ---
echo "------------------------------------------"
echo "🔎 Reading remote file system..."
REMOTE_FILES=$(mpremote "${CONNECT_ARGS[@]}" ls : 2>/dev/null || true)
echo "✅ Remote file system read."
echo "------------------------------------------"
echo "🧹 Cleaning stale files from the device..."

while IFS= read -r line; do
    if [ -z "$line" ] || [[ "$line" == "ls :"* ]]; then continue; fi

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

for item_name in "${LOCAL_FILES[@]}"; do
    item_path="${SOURCE_DIR}/${item_name}"
    echo "   - Syncing '$item_name' to ':'"
    mpremote "${CONNECT_ARGS[@]}" cp -r "$item_path" ":"
done

echo "✅ Synchronization complete."

