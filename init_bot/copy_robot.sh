#!/bin/bash
# v3 - Reworked copy logic to loop through items, fixing permission error.

# ==============================================================================
# Alvik Robot File Retrieval Script
#
# This script copies all files and directories from a connected Alvik robot's
# file system to a specified local directory.
#
# Usage:
#   ./copy_robot.sh -d <destination_directory>
#
# Example:
#   ./copy_robot.sh -d ./robot_backup
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- SCRIPT LOGIC ---
PORT=""
DEST_DIR=""

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -d|--dir)
        DEST_DIR="$2"
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

echo "Running copy_robot.sh - v3"

# --- Validate Arguments ---
if [ -z "$DEST_DIR" ]; then
    echo "❌ ERROR: Destination directory not specified. Use -d <path>."
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

# --- Ensure Destination Directory Exists ---
echo "------------------------------------------"
echo "🛠️  Checking destination directory..."
if [ ! -d "$DEST_DIR" ]; then
    echo "   - Destination '$DEST_DIR' not found. Creating it..."
    mkdir -p "$DEST_DIR"
    echo "   - ✅ Destination directory created."
else
    echo "   - ✅ Destination directory already exists."
fi

# --- CORRECTED: Loop through items instead of one bulk copy ---
echo "------------------------------------------"
echo "📂 Copying all files from the robot to '$DEST_DIR'..."

# 1. Get a list of all items in the root directory of the robot
REMOTE_ITEMS=$(mpremote "${CONNECT_ARGS[@]}" ls :)

# 2. Loop through each item and copy it individually
while IFS= read -r line; do
    # Skip empty lines or the header line that 'ls' sometimes outputs
    if [ -z "$line" ] || [[ "$line" == "ls :"* ]]; then
        continue
    fi

    # Extract just the file/directory name, removing size and trailing slash
    item_name=$(echo "$line" | sed 's/^[ ]*[0-9]*[ ]*//' | sed 's/\/$//')

    source_path=":${item_name}"
    
    echo "   - Copying '${source_path}' to '${DEST_DIR}/'"
    # The trailing slash on the destination ensures items are copied INTO it.
    mpremote "${CONNECT_ARGS[@]}" cp -r "${source_path}" "${DEST_DIR}/"

done <<< "$REMOTE_ITEMS"

echo "✅ Copy complete."

