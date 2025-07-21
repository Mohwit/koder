"""Utility functions for creating new code files.

This module provides the create_code_file helper that writes code to disk,
automatically resolving relative paths against the CODE_REPO_PATH
environment variable and ensuring parent directories exist.
"""

import os
from dotenv import load_dotenv

load_dotenv()

CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")


def create_code_file(file_path: str, code: str) -> str:
    """
    Creates a new file at the given file path and embeds it in ChromaDB.
    Automatically resolves relative paths to absolute paths using CODE_REPO_PATH.

    Parameters:
        file_path (str): The path (relative or absolute) where the file should be created
        code (str): The code to write into the file

    Returns:
        tuple: (success message, file content)
    """
    # Convert relative path to absolute path if needed
    if not os.path.isabs(file_path):
        file_path = os.path.join(os.getenv("CODE_REPO_PATH"), file_path.lstrip("/"))

    # Ensure the parent directories exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Write the code to the file
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(code)

    return f"File created at: {file_path}\n"


# Example usage:
if __name__ == "__main__":
    pass
