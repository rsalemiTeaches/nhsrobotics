#!/bin/bash
# v3 - Added support for passing the --clean-workspace flag to individual robots.
# Developed with the assistance of Google Gemini
# --- Version: V03 ---
# ==============================================================================
# Initialize All Robots Script
# This script finds all connected Alvik robots and runs the
# initialize_robot.sh script for each one.
# ==============================================================================
set -e # Exit immediately if a command exits with a non-zero status.
# --- SCRIPT LOGIC ---
SOURCE_DIR=""
CLEAN_WORKSPACE_FLAG=""
# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
key="$1"
case $key in
-d|--dir)
SOURCE_DIR="$2"
shift 2
;;
-c|--clean-workspace)
CLEAN_WORKSPACE_FLAG="-c"
shift
;;
*)
echo "Unknown option: $1"
exit 1
;;
esac
done
echo "Running initialize_all.sh - v3"
# --- Validate Arguments ---
if [ -z "$SOURCE_DIR" ]; then
echo "❌ ERROR: Source directory not specified. Use -d <path>."
exit 1
fi
if [ ! -d "$SOURCE_DIR" ]; then
echo "❌ ERROR: Source '$SOURCE_DIR' is not a valid directory."
exit 1
fi
# --- Find All Robots ---
echo "------------------------------------------"
echo "🔎 Finding all connected Alvik robots..."
PORT_LIST=$(mpremote connect list | grep 'usbmodem' | awk '{print $1}')
if [ -z "$PORT_LIST" ]; then
echo "❌ No Alvik robots found. Please connect at least one robot and try again."
exit 1
fi
echo "✅ Found robots on the following ports:"
echo "$PORT_LIST"
# --- Initialize Each Robot ---
for port in $PORT_LIST; do
echo "------------------------------------------"
echo "🚀 Initializing robot on port: $port"
echo "=========================================="
# Pass the directory, the specific port, and the optional clean flag
./initialize_robot.sh -d "$SOURCE_DIR" -p "$port" $CLEAN_WORKSPACE_FLAG
echo "=========================================="
echo "✅ Finished initializing robot on port: $port"
echo ""
done
echo "🎉 All connected robots have been initialized."
