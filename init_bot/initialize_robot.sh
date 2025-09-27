#!/bin/bash

# ==============================================================================
# Alvik Robot Initialization Script (with Update Mode)
#
# This script synchronizes a MicroPython device to a desired state.
#
# Usage (Full Install - DELETES existing files):
#   ./initialize_robot.sh -p /dev/tty.usbmodem1234561
#
# Usage (Library Update - SAFE for student work):
#   ./initialize_robot.sh -u -p /dev/tty.usbmodem1234561
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- CONFIGURATION ---

WHITELIST=(
    "/lib"
    "/firmware.bin"
    "/solutions"
)

# A list of files/dirs for a FULL installation
# REMOVED: "nhs_robotics.py" because it is now included in the 'lib' directory.
FULL_COPY_LIST=(
    "config.py"
    "main.py"
    "demo"
    "lib"
    "projects"
)

# A list of files/dirs for an UPDATE
# REMOVED: "nhs_robotics.py" because it is now included in the 'lib' directory.
UPDATE_COPY_LIST=(
    "lib"
)

# --- SCRIPT LOGIC ---

MODE="full"
CONNECT_ARG=""

while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -u|--update)
        MODE="update"
        shift # past argument
        ;;
        -p|--port)
        CONNECT_ARG="connect $2"
        shift # past argument
        shift # past value
        ;;
        *)    # unknown option
        echo "Unknown option: $1"
        exit 1
        ;;
    esac
done

# --- EXECUTION ---

if [ "$MODE" = "full" ]; then
    echo "🚀 Starting FULL INSTALLATION for device..."
    echo "   (This will delete existing files)"
    COPY_LIST=("${FULL_COPY_LIST[@]}")
    
    echo "------------------------------------------"
    echo "🔎 Reading remote file system..."
    REMOTE_FILES=$(mpremote ${CONNECT_ARG} ls -r)
    echo "✅ Remote file system read."
    echo "------------------------------------------"
    echo "🧹 Cleaning the device (keeping whitelist)..."

    while IFS= read -r path; do
        if [ -z "$path" ]; then
            continue
        fi
        
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
            mpremote ${CONNECT_ARG} rm -r "$path" > /dev/null 2>&1 || true
        else
            echo "   - Keeping '$path' (whitelisted)"
        fi
    done <<< "$REMOTE_FILES"

    echo "✅ Device cleaned."
    
    echo "------------------------------------------"
    echo "🧹 Cleaning contents of /lib directory..."
    LIB_CONTENTS=$(mpremote ${CONNECT_ARG} ls /lib 2>/dev/null || true)
    while IFS= read -r item; do
        if [ -n "$item" ]; then
            item_path="/lib/${item#*:}"
            echo "   - Deleting '$item_path'"
            mpremote ${CONNECT_ARG} rm -r "$item_path" > /dev/null 2>&1 || true
        fi
    done <<< "$LIB_CONTENTS"
    echo "✅ /lib directory contents cleaned."


elif [ "$MODE" = "update" ]; then
    echo "🚀 Starting LIBRARY UPDATE for device..."
    echo "   (This will NOT delete any files)"
    COPY_LIST=("${UPDATE_COPY_LIST[@]}")
fi

echo "------------------------------------------"
echo "📂 Copying files to the device..."

for source_item in "${COPY_LIST[@]}"; do
    # CORRECTED: Use a colon ':' for the remote root directory, which is the
    # standard for mpremote.
    dest_item=":${source_item}"
    
    if [ -e "$source_item" ]; then
        echo "   - Copying '$source_item' to '$dest_item'"
        mpremote ${CONNECT_ARG} cp -r "$source_item" "$dest_item"
    else
        echo "   - WARNING: Local file '$source_item' not found. Skipping."
    fi
done

echo "✅ File copy complete."

