#!/bin/bash

# ==============================================================================
# Alvik Robot Initialization Script
#
# This script synchronizes a MicroPython device to a desired state by:
# 1. Deleting all files and directories not in a predefined whitelist.
# 2. Copying a list of specified local files and directories to the device.
#
# Usage:
#   ./initialize_robot.sh
#   ./initialize_robot.sh -p /dev/tty.usbmodem1234561 # Specify a port
#   ./initialize_robot.sh -c "id:e6616407e3496e2e" # Specify a device ID
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- CONFIGURATION ---

# A whitelist of files and directories to KEEP on the device.
# Any file or directory NOT in this list will be deleted.
# IMPORTANT: All paths MUST start with a leading slash '/'.
# TIP: Add files from your COPY_LIST here if you don't want them
#      to be deleted and re-copied every time.
WHITELIST=(
    "/lib" # Whitelisting a directory keeps it and its contents
    "/firmware.bin"
    "/solutions"
)

# A list of local files and directories to COPY to the device.
# The script will use `cp -r`, so directories are copied recursively.
COPY_LIST=(
    "config.py"
    "main.py"
    "demo"
    "lib"
    "projects"
)

# The corresponding destination directories on the device for each item in COPY_LIST.
# Make sure this has the same number of items as COPY_LIST.
# Use ":" for the root directory.
DESTINATION_LIST=(
    ":"
    ":"
    ":"
    ":"
    ":"
)

# --- SCRIPT LOGIC ---

# Function to display help message
usage() {
    echo "Usage: $0 [-p PORT] [-c CONNECT_STRING] [-h]"
    echo "  -p PORT            Specify the serial port (e.g., /dev/ttyACM0)"
    echo "  -c CONNECT_STRING  Specify a full mpremote connect string (e.g., 'id:your_id')"
    echo "  -h                 Display this help message"
    exit 1
}

# Parse command-line options
CONNECT_ARG=""
while getopts ":p:c:h" opt; do
    case ${opt} in
        p)
            CONNECT_ARG="connect port:${OPTARG}"
            ;;
        c)
            CONNECT_ARG="connect ${OPTARG}"
            ;;
        h)
            usage
            ;;
        \?)
            echo "Invalid Option: -$OPTARG" 1>&2
            usage
            ;;
    esac
done

echo "🤖 Starting Alvik Robot Initialization..."
echo "=========================================="

# 1. Get a recursive list of all files on the device.
echo "🔎 Fetching list of all files from the device..."
# We use `ls -r` for a recursive list and redirect stderr to /dev/null to suppress
# the "Connected to ..." message. The `grep` command filters out any potential
# header lines, only matching lines that look like file/dir listings.
# We also reverse the list with `tail -r` (macOS) or `tac` (Linux) to delete
# files before their parent directories.
REMOTE_FILES=$(mpremote ${CONNECT_ARG} ls -r / 2>/dev/null | grep -E "^\s*(<dir>|[0-9]+)\s" | tail -r)

if [ -z "$REMOTE_FILES" ]; then
    echo "✅ Device is empty or could not be read. Proceeding to copy files."
    # We set REMOTE_FILES to an empty string to avoid errors in the loop below
    REMOTE_FILES=""
else
    echo "🧹 Cleaning device. Only whitelisted files will be kept."
fi

# 2. Iterate through remote files and delete those not on the whitelist.
while IFS= read -r item; do
    # `item` will be in the format "  1234 /path/to/file.py" or "   <dir> /dirname"
    # We extract the path, which is the last field.
    path=$(echo "$item" | awk '{print $NF}')

    # --- Normalize the path to always start with a '/' ---
    normalized_path=$path
    if [[ "${path:0:1}" != "/" ]]; then
        normalized_path="/$path"
    fi
    # Remove trailing slash for consistent directory matching
    if [[ "${normalized_path: -1}" == "/" && ${#normalized_path} -gt 1 ]]; then
        normalized_path="${normalized_path%?}"
    fi

    # Skip the root directory itself
    if [ "$normalized_path" == "/" ]; then
        continue
    fi
    
    # Check if the normalized path or any of its parent directories are in the whitelist
    on_whitelist=false
    for whitelisted_item in "${WHITELIST[@]}"; do
        # Check if the normalized path starts with the whitelisted item
        if [[ "$normalized_path" == "$whitelisted_item"* ]]; then
            on_whitelist=true
            break
        fi
    done

    if [ "$on_whitelist" = false ]; then
        echo "   - Deleting '$path'"
        # Use `rm -r` for both files and directories for simplicity.
        # Add '|| true' to prevent script exit on failure.
        mpremote ${CONNECT_ARG} rm -r "$path" > /dev/null 2>&1 || true
    else
        echo "   - Keeping '$path' (whitelisted)"
    fi
done <<< "$REMOTE_FILES"

echo "✅ Device cleaned."
echo "------------------------------------------"
echo "📂 Copying new files to the device..."

# 3. Copy files from the copy list to the device.
for i in "${!COPY_LIST[@]}"; do
    source_item="${COPY_LIST[$i]}"
    dest_item="${DESTINATION_LIST[$i]}"
    
    if [ -e "$source_item" ]; then
        echo "   - Copying '$source_item' to '$dest_item'"
        # Use mpremote directly, assuming it is in the system's PATH.
        mpremote ${CONNECT_ARG} cp -r "$source_item" "$dest_item"
    else
        echo "   - WARNING: Local file '$source_item' not found. Skipping."
    fi
done

echo "✅ Files copied."
echo "=========================================="
echo "🎉 Robot initialization complete!"

