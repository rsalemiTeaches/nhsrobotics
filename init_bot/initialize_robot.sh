#!/bin/bash
# v12 - Reverted to 'ls' with robust sed parsing, as directed.

# ==============================================================================
# Alvik Robot Initialization Script (with Update Mode)
#
# This script synchronizes a MicroPython device to a desired state.
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- CONFIGURATION ---
WHITELIST=("/lib" "/solutions")

FULL_COPY_LIST=("config.py" "main.py" "batterycheck.py" "demo" "lib" "projects" "firmware.bin")
DESTINATION_LIST=(":" ":" ":" ":" ":" ":" ":")

UPDATE_COPY_LIST=("lib")

# --- SCRIPT LOGIC ---
MODE="full"
PORT=""

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -u|--update)
        MODE="update"
        shift
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

echo "Running initialize_robot.sh - v12"

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

if [ "$MODE" = "full" ]; then
    echo "🚀 Starting FULL INSTALLATION for device..."
    echo "   (This will delete existing files)"
    
    echo "------------------------------------------"
    echo "🔎 Reading remote file system..."
    # Get the file listing. Add '|| true' to prevent script exit if ls fails.
    REMOTE_FILES=$(mpremote "${CONNECT_ARGS[@]}" ls : 2>/dev/null || true)
    echo "✅ Remote file system read."
    echo "------------------------------------------"
    echo "🧹 Cleaning the device (keeping whitelist)..."

    while IFS= read -r line; do
        # Skip empty lines or the header from ls
        if [ -z "$line" ] || [[ "$line" == "ls :"* ]]; then continue; fi

        # FIX: Use sed to robustly extract the filename by stripping leading whitespace and numbers.
        item_name=$(echo "$line" | sed 's/^[ ]*[0-9]*[ ]*//')
        
        # Normalize path for whitelist check (e.g., "/config.py")
        normalized_path="/${item_name}"

        on_whitelist=false
        for whitelisted_item in "${WHITELIST[@]}"; do
            # Check if the path starts with a whitelisted item.
            if [[ "$normalized_path" == "$whitelisted_item"* ]]; then
                on_whitelist=true
                break
            fi
        done
        
        if [ "$on_whitelist" = false ]; then
            # Path for mpremote rm needs a colon prefix, e.g., ":config.py"
            path_to_delete=":${item_name}"
            echo "   - Deleting '$path_to_delete'"
            mpremote "${CONNECT_ARGS[@]}" rm -r "$path_to_delete" > /dev/null 2>&1 || true
        else
            echo "   - Keeping '/${item_name}' (whitelisted)"
        fi
    done <<< "$REMOTE_FILES"
    echo "✅ Device cleaned."

    echo "------------------------------------------"
    echo "📂 Copying new files to the device..."
    for i in "${!FULL_COPY_LIST[@]}"; do
        source_item="${FULL_COPY_LIST[$i]}"
        dest_item="${DESTINATION_LIST[$i]}"
        if [ -e "$source_item" ]; then
            echo "   - Copying '$source_item' to '$dest_item'"
            mpremote "${CONNECT_ARGS[@]}" cp -r "$source_item" "$dest_item"
        else
            echo "   - WARNING: Local file '$source_item' not found. Skipping."
        fi
    done
    echo "✅ File copy complete."

elif [ "$MODE" = "update" ]; then
    echo "🚀 Starting LIBRARY UPDATE for device..."
    echo "   (This will NOT delete any files)"
    echo "------------------------------------------"
    echo "📂 Syncing updated library files to the device..."

    for item in "${UPDATE_COPY_LIST[@]}"; do
        if [ ! -e "$item" ]; then
            echo "   - WARNING: Local item '$item' not found. Skipping."
            continue
        fi

        if [ -d "$item" ]; then
            source_path_glob="${item}/*"
            dest_path=":${item}/"
            echo "   - Syncing contents of '$item' to '$dest_path'"
            mpremote "${CONNECT_ARGS[@]}" cp -r ${source_path_glob} "${dest_path}"
        else
            source_path="$item"
            dest_path=":"
            echo "   - Copying file '$source_path' to '$dest_path'"
            mpremote "${CONNECT_ARGS[@]}" cp "$source_path" "$dest_path"
        fi
    done
    echo "✅ Update complete."
fi

