#!/bin/bash
# Build guides from markdown, pad odd page counts, and report.
# V01
#
#   ./build-all.sh            build every pNN.md
#   ./build-all.sh p02.md     build just one
#
# Add -d to copy the results into the Project Guides folder.

set -e
cd "$(dirname "$0")"

# Where the finished .docx files go. Override with GUIDES=... if needed.
if [ -z "$GUIDES" ]; then
    for candidate in \
        "$HOME/Library/CloudStorage/GoogleDrive-rdsalemi@gmail.com/My Drive/Teaching/Class Development/Robotics/Project Guides" \
        /sessions/*/mnt/"Class Development"/Robotics/"Project Guides"
    do
        if [ -d "$candidate" ]; then GUIDES="$candidate"; break; fi
    done
fi
DEPLOY=false
FILES=()

for arg in "$@"; do
    if [ "$arg" = "-d" ]; then DEPLOY=true; else FILES+=("$arg"); fi
done
if [ ${#FILES[@]} -eq 0 ]; then FILES=(p*.md); fi

WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

for md in "${FILES[@]}"; do
    out=$(grep -m1 '^out:' "$md" | sed 's/^out:[[:space:]]*//')

    node make.js "$md" > /dev/null

    # Count pages, then rebuild padded if the count is odd.
    cp "$out" "$WORK/"
    (cd "$WORK" && soffice --headless --convert-to pdf "$out" > /dev/null 2>&1 \
        && pdftoppm -jpeg -r 30 "${out%.docx}.pdf" pg)
    pages=$(ls "$WORK"/pg-*.jpg 2>/dev/null | wc -l | tr -d ' ')
    rm -f "$WORK"/*

    if [ $((pages % 2)) -ne 0 ]; then
        PAD_EVEN=1 node make.js "$md" > /dev/null
        printf "%-38s %s pages -> padded to %s\n" "$out" "$pages" "$((pages + 1))"
    else
        printf "%-38s %s pages\n" "$out" "$pages"
    fi

    if [ "$DEPLOY" = true ]; then
        if [ -z "$GUIDES" ] || [ ! -d "$GUIDES" ]; then
            echo "ERROR: Project Guides folder not found. Set GUIDES=/path/to/it" >&2
            exit 1
        fi
        cp "$out" "$GUIDES/"
    fi
done

if [ "$DEPLOY" = true ]; then echo "deployed to $GUIDES"; fi
