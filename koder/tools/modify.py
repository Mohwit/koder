"""
This tool is used to modify a code file by making multiple edits in one operation.
Each edit contains the exact text to replace and the new text.
"""

import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


def modify_code_file(file_path: str, edits: List[Dict[str, str]]) -> str:
    """
    Makes multiple changes to a single file in one operation.

    Args:
        file_path: Absolute path to the file to modify
        edits: Array of edit operations, each containing old_string and new_string

    Returns:
        Success message with details of changes made

    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If edits are invalid
        Exception: If file operations fail
    """

    # Validate inputs
    if not file_path:
        raise ValueError("file_path is required")

    if not edits or not isinstance(edits, list):
        raise ValueError("edits must be a non-empty list")

    # Validate each edit
    for i, edit in enumerate(edits):
        if not isinstance(edit, dict):
            raise ValueError(f"Edit {i+1} must be a dictionary")

        if "old_string" not in edit or "new_string" not in edit:
            raise ValueError(
                f"Edit {i+1} must contain 'old_string' and 'new_string' keys"
            )

        if not isinstance(edit["old_string"], str) or not isinstance(
            edit["new_string"], str
        ):
            raise ValueError(f"Edit {i+1} old_string and new_string must be strings")

    # Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Initialize variables
    original_content = None
    changes_made = []

    try:
        # Read the file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Store original content for backup
        original_content = content

        # Apply each edit
        for i, edit in enumerate(edits):
            old_string = edit["old_string"]
            new_string = edit["new_string"]

            preview = old_string[:50] + ("..." if len(old_string) > 50 else "")

            # Check if old_string exists in content
            if old_string not in content:
                # Don't fail, just skip and report
                changes_made.append(f"Edit {i+1}: Text not found - '{preview}'")
                continue

            # Count occurrences
            occurrences = content.count(old_string)
            if occurrences == 0:
                changes_made.append(f"Edit {i+1}: Text not found - '{preview}'")
                continue
            elif occurrences > 1:
                # For safety, only replace the first occurrence
                content = content.replace(old_string, new_string, 1)
                changes_made.append(
                    (
                        f"Edit {i+1}: Replaced first occurrence of '{preview}' "
                        f"(found {occurrences} total)"
                    )
                )
            else:
                # Replace the single occurrence
                content = content.replace(old_string, new_string)
                changes_made.append(f"Edit {i+1}: Replaced '{preview}'")

        # Write the modified content back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Create success message
        replaced_count = sum(1 for c in changes_made if "Replaced" in c)
        success_msg = f"Successfully modified {file_path}\n"
        success_msg += f"Applied {replaced_count} of {len(edits)} edits:\n"
        success_msg += "\n".join(changes_made)

        return success_msg

    except Exception as e:
        # If something went wrong, try to restore original content
        try:
            if original_content is not None:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(original_content)
        except (IOError, OSError, PermissionError):
            pass  # Best effort to restore

        raise RuntimeError(f"Error modifying file {file_path}: {str(e)}") from e
