#!/bin/bash
# v8 - Corrected cleanup logic

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
DESTINATION_LIST=(":" ":" ":" ":" ":" ":")

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

echo "Running initialize_robot.sh - v8"

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

# CORRECTED: Use an array for command arguments for robustness.
CONNECT_ARGS=("connect" "${PORT}")


# --- EXECUTION ---

if [ "$MODE" = "full" ]; then
    echo "🚀 Starting FULL INSTALLATION for device..."
    echo "   (This will delete existing files)"
    
    echo "------------------------------------------"
    echo "🔎 Reading remote file system..."
    # Use the argument array for the command
    REMOTE_FILES=$(mpremote "${CONNECT_ARGS[@]}" ls -r :)
    echo "✅ Remote file system read."
    echo "------------------------------------------"
    echo "🧹 Cleaning the device (keeping whitelist)..."

    while IFS= read -r path; do
        if [ -z "$path" ]; then continue; fi
        normalized_path="/${path#*:}"
        on_whitelist=false
        for whitelisted_item in "${WHITELIST[@]}"; do
            if [[ "$normalized_path" == "$whitelisted_item"* ]]; then
                on_whitelist=true
                break
            fi
        done
        if [ "$on_whitelist" = false ]; then
            echo "   - Deleting '$path'"
            mpremote "${CONNECT_ARGS[@]}" rm -r "$path" > /dev/null 2>&1 || true
        else
            echo "   - Keeping '$path' (whitelisted)"
        fi
    done <<< "$REMOTE_FILES"
    echo "✅ Device cleaned."
    
    # --- FIX ---
    # The redundant /lib cleanup block that was here has been removed.
    # The main loop above now correctly handles the whitelist.

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

