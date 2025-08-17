"""
Clean and simple modify_code_file tool implementation.
Supports multiple edits with syntax-highlighted unified diff display.
"""

import os
import difflib
import shutil
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Rich imports for enhanced display
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    console = Console()
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    console = None

load_dotenv()

# Light backgrounds for diff highlighting
REMOVED_BG = "#4a1a1a"  # Light red
ADDED_BG = "#1a4a1a"    # Light green

# Language mapping for syntax highlighting
LANGUAGE_MAP = {
    '.py': 'python', '.js': 'javascript', '.jsx': 'jsx', '.ts': 'typescript', '.tsx': 'tsx',
    '.java': 'java', '.c': 'c', '.cpp': 'cpp', '.cc': 'cpp', '.cxx': 'cpp', '.h': 'c', '.hpp': 'cpp',
    '.cs': 'csharp', '.php': 'php', '.rb': 'ruby', '.go': 'go', '.rs': 'rust',
    '.sh': 'bash', '.bash': 'bash', '.zsh': 'zsh', '.fish': 'fish', '.ps1': 'powershell',
    '.html': 'html', '.htm': 'html', '.xml': 'xml', '.css': 'css', '.scss': 'scss', '.sass': 'sass', '.less': 'less',
    '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml', '.toml': 'toml', '.ini': 'ini', '.cfg': 'ini', '.conf': 'ini',
    '.md': 'markdown', '.markdown': 'markdown', '.sql': 'sql', '.r': 'r', '.R': 'r',
    '.swift': 'swift', '.kt': 'kotlin', '.scala': 'scala', '.clj': 'clojure', '.hs': 'haskell',
    '.elm': 'elm', '.ex': 'elixir', '.exs': 'elixir', '.erl': 'erlang', '.pl': 'perl', '.lua': 'lua',
    '.vim': 'vim', '.dockerfile': 'dockerfile', '.tf': 'terraform', '.hcl': 'hcl'
}


def _get_file_language(file_path: str) -> str:
    """Get programming language from file extension."""
    ext = os.path.splitext(file_path)[1].lower()
    return LANGUAGE_MAP.get(ext, 'text')


def _create_syntax_highlight(code: str, language: str, background_color: Optional[str] = None) -> Text:
    """Create syntax highlighted text with optional background."""
    if not code.strip():
        return Text(code, style=f"on {background_color}" if background_color else "")
    
    try:
        return Syntax(
            code,
            language,
            theme=None,
            background_color=background_color,
            line_numbers=False,
            code_width=None,
            word_wrap=True
        )
    except Exception:
        # Fallback to plain text with background
        return Text(code, style=f"on {background_color}" if background_color else "")


def _create_unified_diff(original_content: str, modified_content: str, file_path: str) -> Optional[Text]:
    """Create a clean unified diff with syntax highlighting."""
    if not RICH_AVAILABLE:
        return None
    
    language = _get_file_language(file_path)
    original_lines = original_content.splitlines()
    modified_lines = modified_content.splitlines()
    
    # Generate unified diff
    diff_lines = list(difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile="original",
        tofile="modified",
        lineterm="",
        n=3
    ))
    
    if not diff_lines:
        return None
    
    unified_text = Text()
    
    for line in diff_lines:
        # Skip file headers
        if line.startswith('+++') or line.startswith('---'):
            continue
        
        if line.startswith('@@'):
            # Hunk header
            unified_text.append(line + "\n", style="bold blue")
        elif line.startswith('-'):
            # Removed line
            code_line = line[1:]
            unified_text.append("-", style=f"on {REMOVED_BG}")
            highlighted = _create_syntax_highlight(code_line, language, REMOVED_BG)
            unified_text.append(highlighted)
            unified_text.append("\n")
        elif line.startswith('+'):
            # Added line
            code_line = line[1:]
            unified_text.append("+", style=f"on {ADDED_BG}")
            highlighted = _create_syntax_highlight(code_line, language, ADDED_BG)
            unified_text.append(highlighted)
            unified_text.append("\n")
        else:
            # Context line
            code_line = line[1:] if line.startswith(' ') else line
            if line.startswith(' '):
                unified_text.append(" ")
            highlighted = _create_syntax_highlight(code_line, language)
            unified_text.append(highlighted)
            unified_text.append("\n")
    
    return unified_text if unified_text.plain else None


def _display_diff(original_content: str, modified_content: str, file_path: str) -> None:
    """Display the diff with clean formatting."""
    if original_content == modified_content:
        print("No changes detected")
        return
    
    if RICH_AVAILABLE and console:
        # Create and display clean diff
        unified_diff = _create_unified_diff(original_content, modified_content, file_path)
        if unified_diff:
            console.print()
            console.print("[bold cyan]📝 Code Changes[/bold cyan]")
            console.print("[dim]" + "─" * 50 + "[/dim]")
            console.print(unified_diff)
            console.print("[dim]" + "─" * 50 + "[/dim]")
        else:
            print("No changes detected")
    else:
        # Plain text fallback
        _display_plain_diff(original_content, modified_content)


def _display_plain_diff(original_content: str, modified_content: str) -> None:
    """Plain text diff display fallback."""
    original_lines = original_content.splitlines(keepends=True)
    modified_lines = modified_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        original_lines,
        modified_lines,
        fromfile="original",
        tofile="modified",
        lineterm="",
        n=3
    )
    
    diff_text = '\n'.join(diff)
    terminal_width = getattr(shutil.get_terminal_size(), 'columns', 80)
    
    print()
    print("─" * terminal_width)
    print(diff_text)
    print("─" * terminal_width)


def _get_user_confirmation() -> bool:
    """Get user confirmation for applying changes."""
    while True:
        response = input("\nApply these changes? (y/n): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no']:
            return False
        else:
            print("Please enter 'y' or 'n'")


def _resolve_file_path(file_path: str) -> str:
    """Resolve relative path to absolute path."""
    if os.path.isabs(file_path):
        return file_path
    
    # Use current directory instead of environment variable [[memory:3925830]]
    base_path = os.getcwd()
    return os.path.join(base_path, file_path.lstrip('/'))


def _apply_edits(content: str, edits: List[Dict[str, str]]) -> tuple[str, List[str]]:
    """Apply edits sequentially and return modified content and edit descriptions."""
    modified_content = content
    applied_edits = []
    
    for i, edit in enumerate(edits):
        old_string = edit.get('old_string', '')
        new_string = edit.get('new_string', '')
        
        if not old_string:
            raise ValueError(f"Edit {i+1} has empty old_string")
        
        if old_string not in modified_content:
            raise ValueError(f"Edit {i+1} - old_string not found: '{old_string[:50]}...'")
        
        modified_content = modified_content.replace(old_string, new_string, 1)
        applied_edits.append(f"Edit {i+1}: Replaced '{old_string[:30]}...' with '{new_string[:30]}...'")
    
    return modified_content, applied_edits


def _backup_and_write(file_path: str, original_content: str, modified_content: str) -> None:
    """Create backup, write modified content, and clean up backup on success."""
    backup_path = f"{file_path}.backup"
    
    try:
        # Create backup
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)
        
        # Write modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        # Remove backup on success
        if os.path.exists(backup_path):
            os.remove(backup_path)
            
    except Exception:
        # Restore from backup on failure
        if os.path.exists(backup_path):
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_content = f.read()
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(backup_content)
            os.remove(backup_path)
        raise


def modify_code_file(file_path: str, edits: List[Dict[str, str]]) -> str:
    """
    Modify a code file by applying multiple edits in sequence.
    
    Args:
        file_path: Path to the file to modify (relative or absolute)
        edits: List of edit operations, each containing:
            - old_string: Exact text to replace
            - new_string: Replacement text
    
    Returns:
        Success or error message
    """
    try:
        # Resolve file path
        resolved_path = _resolve_file_path(file_path)
        
        # Validate file exists
        if not os.path.exists(resolved_path):
            return f"Error: File not found: {resolved_path}"
        
        # Read original content
        with open(resolved_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Apply edits
        modified_content, applied_edits = _apply_edits(original_content, edits)
        
        # Display diff
        _display_diff(original_content, modified_content, resolved_path)
        
        # Get user confirmation
        if not _get_user_confirmation():
            return f"SUCCESS: User rejected the proposed changes for {os.path.basename(resolved_path)}. No modifications were applied."
        
        # Write changes
        _backup_and_write(resolved_path, original_content, modified_content)
        
        # Return success message
        success_msg = f"SUCCESS: User accepted and applied {len(applied_edits)} edit(s) to {os.path.basename(resolved_path)}\n"
        success_msg += f"File path: {resolved_path}\n"
        success_msg += "Changes applied:\n"
        success_msg += "\n".join(applied_edits)
        
        return success_msg
        
    except Exception as e:
        return f"Error modifying file: {str(e)}"


# Backward compatibility alias
modify_code_file_non_interactive = modify_code_file


if __name__ == "__main__":
    # Example usage
    test_edits = [
        {
            "old_string": "print('hello')",
            "new_string": "print('Hello, World!')"
        }
    ]
    print(modify_code_file("test.py", test_edits))