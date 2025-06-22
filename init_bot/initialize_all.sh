#!/bin/bash

# ==============================================================================
# Initialize ALL Alvik Robots Script (Simple Version)
#
# This master script automatically discovers all connected Alvik robots and
# runs the individual `initialize_robot.sh` script for each one.
# It assumes all robots will be initialized with the exact same set of files.
#
# ==============================================================================

set -e # Exit immediately if a command exits with a non-zero status.

# --- SCRIPT LOGIC ---

echo "🚀 Starting initialization for all connected robots..."
echo "====================================================="

# Check if the individual init script exists
if [ ! -f "initialize_robot.sh" ];
then
    echo "❌ ERROR: The 'initialize_robot.sh' script was not found in this directory."
    exit 1
fi

# Get the list of connected devices, filter for lines containing 'usbmodem'
# to avoid other serial devices, extract just the port (first column),
# and then loop through each one.
mpremote connect list | grep 'usbmodem' | awk '{print $1}' | while read -r robot_port; do
    echo ""
    echo "--- Initializing Robot on Port: ${robot_port} ---"

    # Run the individual init script, passing the port to the -p flag.
    # It will use the files in the current directory (config.py, main.py, etc.)
    ./initialize_robot.sh -p "${robot_port}"

    echo "   - ✅  Initialization complete for ${robot_port}."

done

echo ""
echo "====================================================="
echo "🎉 All robots have been initialized."
