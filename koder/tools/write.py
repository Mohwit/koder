"""Utility functions for creating new code files.

This module provides the create_code_file helper that writes code to disk,
automatically resolving relative paths against the CODE_REPO_PATH
environment variable and ensuring parent directories exist.
"""

import os
from dotenv import load_dotenv

# Try to import rich for enhanced display
try:
    from rich.console import Console
    from rich.syntax import Syntax
    from rich.panel import Panel
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

load_dotenv()

CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")


def _display_code_preview(file_path: str, code: str):
    """Display the code that will be saved with syntax highlighting and no background."""
    if not RICH_AVAILABLE:
        print(f"\n--- Code to be saved to {file_path} ---")
        print(code)
        print("--- End of code ---\n")
        return
    
    # Get file extension for syntax highlighting
    file_ext = os.path.splitext(file_path)[1].lstrip('.')
    if not file_ext:
        file_ext = "text"
    
    # Create header info
    header_text = Text()
    header_text.append("📄 File: ", style="bold")
    header_text.append(f"{os.path.basename(file_path)}", style="bold cyan")
    header_text.append(f"\n📁 Path: ", style="bold")
    header_text.append(f"{file_path}", style="dim")
    header_text.append("\n")
    
    # Create syntax highlighted code with no background
    try:
        syntax_highlighted = Syntax(
            code,
            file_ext,
            theme=None,  # Use terminal default theme
            background_color=None,  # No background color
            line_numbers=True,
            word_wrap=True
        )
    except Exception:
        # Fallback to plain text if syntax highlighting fails
        syntax_highlighted = Text(code)
    
    # Combine header and code
    content = Text()
    content.append(header_text)
    content.append("\n")
    content.append(syntax_highlighted)
    
    # Display in a panel
    panel = Panel(
        content,
        title="💾 Code Preview",
        border_style="green",
        padding=(1, 2),
        expand=True
    )
    console.print(panel)


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
        code_repo_path = os.getenv("CODE_REPO_PATH")
        if code_repo_path is None:
            # Default to current working directory if CODE_REPO_PATH is not set
            code_repo_path = os.getcwd()
        file_path = os.path.join(code_repo_path, file_path.lstrip("/"))

    # Display code preview
    _display_code_preview(file_path, code)
    
    # Ask for confirmation before proceeding
    user_input = input("Type 'Y' or 'y' to execute the command: ").strip().lower()
    if user_input != 'y':
        return "Command not executed: user did not confirm."

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
