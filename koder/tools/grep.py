"""
This tool is used to search for patterns in files using grep-like functionality.
It can search in specific files or across directories with various options.
"""

import os
import re
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

CODE_REPO_PATH = os.getcwd()


def grep_search(
    pattern: str,
    file_path: Optional[str] = None,
    directory: Optional[str] = None,
    recursive: bool = False,
    case_sensitive: bool = True,
    line_numbers: bool = True,
    max_results: int = 100,
) -> str:
    """
    Search for patterns in files using grep-like functionality.

    Parameters:
        pattern (str): The search pattern (regex supported)
        file_path (str, optional): Specific file to search in
        directory (str, optional): Directory to search in (if file_path not provided)
        recursive (bool): Whether to search recursively in subdirectories
        case_sensitive (bool): Whether search should be case sensitive
        line_numbers (bool): Whether to include line numbers in results
        max_results (int): Maximum number of results to return

    Returns:
        str: Search results with matches found

    Raises:
        ValueError: If neither file_path nor directory is provided
        FileNotFoundError: If specified file or directory doesn't exist
        IOError: If there are issues reading files
    """
    try:
        if not file_path and not directory:
            raise ValueError("Either file_path or directory must be provided")

        results = []

        if file_path:
            # Search in specific file
            abs_file_path = _resolve_path(file_path)
            if not os.path.exists(abs_file_path):
                raise FileNotFoundError(f"File not found: {abs_file_path}")

            matches = _search_in_file(
                abs_file_path, pattern, case_sensitive, line_numbers
            )
            results.extend(matches)

        elif directory:
            # Search in directory
            abs_dir_path = _resolve_path(directory)
            if not os.path.exists(abs_dir_path):
                raise FileNotFoundError(f"Directory not found: {abs_dir_path}")

            files_to_search = _get_files_to_search(abs_dir_path, recursive)

            for file_path in files_to_search:
                try:
                    matches = _search_in_file(
                        file_path, pattern, case_sensitive, line_numbers
                    )
                    results.extend(matches)

                    if len(results) >= max_results:
                        break
                except (IOError, UnicodeDecodeError):
                    # Skip files that can't be read (binary files, etc.)
                    continue

        # Limit results
        results = results[:max_results]

        if not results:
            return f"No matches found for pattern: {pattern}"

        result_text = f"Found {len(results)} matches for pattern: {pattern}\n"
        result_text += "=" * 50 + "\n"
        result_text += "\n".join(results)

        if len(results) >= max_results:
            result_text += f"\n\n... (truncated to {max_results} results)"

        return result_text

    except (OSError, re.error, ValueError) as e:
        raise IOError(f"Error during grep search: {str(e)}") from e


def _resolve_path(path: str) -> str:
    """Resolve relative path to absolute path."""
    if not os.path.isabs(path):
        return os.path.join(CODE_REPO_PATH, path.lstrip("/"))
    return path


def _search_in_file(
    file_path: str, pattern: str, case_sensitive: bool, line_numbers: bool
) -> List[str]:
    """Search for pattern in a single file."""
    matches = []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            rel_path = os.path.relpath(file_path, CODE_REPO_PATH)

            for line_num, line in enumerate(file, 1):
                line = line.rstrip("\n")

                # Perform regex search
                flags = 0 if case_sensitive else re.IGNORECASE
                if re.search(pattern, line, flags):
                    if line_numbers:
                        match_text = f"{rel_path}:{line_num}: {line}"
                    else:
                        match_text = f"{rel_path}: {line}"
                    matches.append(match_text)

    except (IOError, UnicodeDecodeError):
        # Skip files that can't be read
        pass

    return matches


def _get_files_to_search(directory: str, recursive: bool) -> List[str]:
    """Get list of files to search in."""
    files = []

    if recursive:
        for root, dirs, filenames in os.walk(directory):
            # Skip hidden directories and common non-text directories
            dirs[:] = [
                d
                for d in dirs
                if not d.startswith(".")
                and d not in ["node_modules", "__pycache__", ".git"]
            ]

            for filename in filenames:
                if not filename.startswith(".") and _is_text_file(filename):
                    files.append(os.path.join(root, filename))
    else:
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if (
                os.path.isfile(file_path)
                and not filename.startswith(".")
                and _is_text_file(filename)
            ):
                files.append(file_path)

    return files


def _is_text_file(filename: str) -> bool:
    """Check if file is likely a text file based on extension."""
    text_extensions = {
        ".py",
        ".js",
        ".ts",
        ".html",
        ".css",
        ".json",
        ".xml",
        ".yml",
        ".yaml",
        ".md",
        ".txt",
        ".csv",
        ".sql",
        ".sh",
        ".bash",
        ".zsh",
        ".php",
        ".rb",
        ".go",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".hpp",
        ".rs",
        ".swift",
        ".kt",
        ".scala",
        ".clj",
        ".hs",
        ".ml",
        ".r",
        ".jl",
        ".pl",
        ".lua",
        ".vim",
        ".cfg",
        ".conf",
        ".ini",
        ".toml",
        ".env",
        ".gitignore",
        ".dockerignore",
    }

    _, ext = os.path.splitext(filename.lower())
    return ext in text_extensions or not ext  # Include files without extension


if __name__ == "__main__":
    # Example usage
    try:
        # Search in current directory
        result = grep_search("def ", directory=".", recursive=True, max_results=10)
        print(result)

    except (OSError, ValueError, re.error) as e:
        print(f"Error: {e}")
