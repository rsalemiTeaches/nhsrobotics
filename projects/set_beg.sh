#!/bin/bash

# Define the source directory containing the '_beg' files.
# Assumes the source is one level up from the current directory.
SRC_DIR="../proj_beg"

# Define the destination directory (the current directory).
DEST_DIR="."

# --- Pre-flight Checks ---

# Check if the source directory actually exists
if [[ ! -d "$SRC_DIR" ]]; then
  echo "Error: Source directory '$SRC_DIR' not found."
  echo "Are you in the 'projects' directory as expected?"
  exit 1
fi

echo "--- Starting Symbolic Link Creation (Beg -> Clean) ---"
echo "Source: $(cd "$SRC_DIR" && pwd)"
echo "Destination: $(pwd)"
echo "------------------------------------------------------"

# Change to the destination directory to simplify link paths (using relative paths)
cd "$DEST_DIR" || { echo "Error: Could not enter destination directory '$DEST_DIR'"; exit 1; }

# Track successful and failed links
success_count=0
fail_count=0

# Loop through all files matching the pattern *pxx_*_beg.py in the source directory
for src_file in "$SRC_DIR"/p??_*_beg.py; do
  
  # Check if any matching files were actually found (avoids errors if no matches)
  if [[ -e "$src_file" ]]; then
    
    # Get just the filename itself (e.g., p01_leds_beg.py)
    filename=$(basename "$src_file")

    # Generate the destination (clean) filename by removing '_beg'
    # Use Bash pattern replacement: ${var//pattern/replacement}
    dest_filename="${filename//_beg/}"

    # --- Symlink Creation and Overwrite Protection ---

    # Check if the clean destination filename already exists (as a file or a link)
    if [[ -e "$dest_filename" ]]; then
      echo "[Skipping] Destination exists: $dest_filename"
      ((fail_count++))
    else
      # Attempt to create the symbolic link. 
      # 'ln -s source destination'
      # We use "$src_file" (relative to where we started) or a fully resolved absolute path. 
      # Since we 'cd'-ed into DEST_DIR, we must make sure the link is relative *from* DEST_DIR *to* SRC_DIR, 
      # or simply use the full path to the source. Let's use the path variable we have.
      
      # Correcting the path for relative linking from DEST_DIR:
      # If SRC_DIR is "../proj_beg", the relative link needs to point precisely to that relative to DEST_DIR.
      # The loop variable src_file is defined as "$SRC_DIR"/pattern. This works.
      
      if ln -s "$src_file" "$dest_filename" 2>/dev/null; then
        echo "[Success] Linked: $filename -> $dest_filename"
        ((success_count++))
      else
        echo "[Failed] Failed to link: $filename -> $dest_filename (Check permissions)"
        ((fail_count++))
      fi
    fi

  fi
done

echo "------------------------------------------------------"
echo "Symbolic link operation complete."
echo "Created: $success_count links."
if [[ $fail_count -gt 0 ]]; then
  echo "Skipped/Failed: $fail_count links (Destination existed or permission error)."
fi
