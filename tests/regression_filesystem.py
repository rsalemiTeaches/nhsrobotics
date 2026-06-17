import os

def test_filesystem_unicode(bot=None):
    """
    Recursively scans the filesystem for illegal (non-ASCII) characters in filenames.
    """
    def check_dir(path):
        try:
            for entry in os.ilistdir(path):
                name = entry[0]
                entry_type = entry[1]
                
                # Check if the filename contains non-ASCII characters
                if not all(ord(char) < 128 for char in name):
                    return False, f"Illegal filename found: {path}/{name}"
                
                # If directory, recurse
                if entry_type == 0x4000:
                    full_path = f"{path.rstrip('/')}/{name}"
                    success, msg = check_dir(full_path)
                    if not success:
                        return False, msg
            return True, ""
        except OSError as e:
            return False, f"Error accessing {path}: {e}"

    success, message = check_dir("/")
    if success:
        return 1, "Filesystem clean"
    else:
        return 0, message