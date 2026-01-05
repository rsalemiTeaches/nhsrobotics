# V01 - Git Submodule Branch Sync Script
# This script iterates through submodules, identifies the remote default branch (main vs master),
# and updates the .gitmodules configuration to ensure 'git submodule update --remote' works correctly.

import subprocess
import os
import re

def run_command(command, cwd=None):
    """Helper to run shell commands and return output."""
    try:
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=cwd, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        return None

def get_submodules():
    """Parses .gitmodules to find submodule paths."""
    output = run_command("git config --file .gitmodules --get-regexp path")
    if not output:
        return []
    
    # Each line looks like: submodule.libs_on_github/Qwiic_Buzzer_Py.path libs_on_github/Qwiic_Buzzer_Py
    submodules = []
    for line in output.split('\n'):
        parts = line.split()
        if len(parts) >= 2:
            submodules.append(parts[1])
    return submodules

def get_remote_default_branch(submodule_path):
    """Queries the remote of the submodule to find the HEAD branch name."""
    # Use ls-remote to find where HEAD points without needing a full fetch
    output = run_command(f"git ls-remote --symref origin HEAD", cwd=submodule_path)
    if not output:
        return None
    
    # Look for the line: ref: refs/heads/main	HEAD
    match = re.search(r"ref: refs/heads/(.*?)\s+HEAD", output)
    if match:
        return match.group(1)
    return None

def main():
    print("--- Submodule Branch Sync Utility (V01) ---")
    submodules = get_submodules()
    
    if not submodules:
        print("No submodules found in .gitmodules.")
        return

    changes_made = False

    for path in submodules:
        print(f"\nChecking: {path}")
        
        if not os.path.exists(os.path.join(path, ".git")):
            print(f"  [!] Submodule not initialized. Skipping.")
            continue

        remote_branch = get_remote_default_branch(path)
        
        if not remote_branch:
            print("  [!] Could not determine remote branch.")
            continue

        # Get currently configured branch in .gitmodules
        current_cfg = run_command(f"git config --file .gitmodules submodule.{path}.branch")
        
        print(f"  Remote Default: {remote_branch}")
        print(f"  Current Config: {current_cfg if current_cfg else 'None (defaults to master)'}")

        if current_cfg != remote_branch:
            print(f"  [+] Updating configuration to track '{remote_branch}'...")
            run_command(f"git submodule set-branch --branch {remote_branch} {path}")
            changes_made = True
        else:
            print("  [=] Configuration is already correct.")

    if changes_made:
        print("\n--- Summary ---")
        print("Updated .gitmodules. Running sync...")
        run_command("git submodule sync")
        print("Done! You can now run 'git submodule update --remote --merge'")
        print("Don't forget to commit your changes to .gitmodules.")
    else:
        print("\nNo configuration changes needed.")

if __name__ == "__main__":
    main()

# V01
