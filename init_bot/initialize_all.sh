#!/bin/bash

# ==============================================================================
# Initialize ALL Alvik Robots Script (with Update Mode)
#
# This master script discovers all connected Alvik robots and runs the
# individual `initialize_robot.sh` script for each one.
#
# Usage (Full Install - DELETES existing files):
#   ./initialize_all.sh
#
# Usage (Library Update - SAFE for student work):
#   ./initialize_all.sh -u
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- SCRIPT LOGIC ---

# Check for the '-u' flag to pass to the worker script.
INIT_FLAGS=""
if [[ "$1" == "-u" || "$1" == "--update" ]]; then
    INIT_FLAGS="-u"
    echo " MODE: Library Update"
else
    echo " MODE: Full Installation"
fi

echo "🚀 Starting initialization for all connected robots..."
echo "====================================================="

if [ ! -f "initialize_robot.sh" ]; then
    echo "❌ ERROR: The 'initialize_robot.sh' script was not found."
    exit 1
fi

mpremote connect list | grep 'usbmodem' | awk '{print $1}' | while read -r robot_port; do
    echo ""
    echo "--- Initializing Robot on Port: ${robot_port} ---"

    # Pass the flags to the individual init script.
    # The ${INIT_FLAGS} variable will either be empty or contain "-u".
    ./initialize_robot.sh ${INIT_FLAGS} -p "${robot_port}"

    echo "   - ✅  Initialization complete for ${robot_port}."
done

echo ""
echo "====================================================="
echo "🎉 All robots have been initialized."

