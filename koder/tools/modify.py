"""
This tool is used to modify a code file by either replacing a range of lines or inserting new code.
Enhanced with diff display and user confirmation.
"""

import os
import difflib
import shutil
from dotenv import load_dotenv

# Try to import rich components - handle CLI context gracefully
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

load_dotenv()

CODE_REPO_PATH = os.getenv("CODE_REPO_PATH")

# Use a shared console instance or create a new one
try:
    # Try to get the console from CLI if available
    from koder.cli import console as cli_console
    console = cli_console
except ImportError:
    # Fallback to creating a new console instance
    if RICH_AVAILABLE:
        console = Console()
    else:
        console = None


def safe_console_print(message: str):
    """Safely print to console with fallback"""
    if console and RICH_AVAILABLE:
        console.print(message)
    else:
        print(message)


def safe_console_input(prompt: str) -> str:
    """Safely get input with fallback"""
    if console and RICH_AVAILABLE:
        return console.input(prompt)
    else:
        return input(prompt)


def generate_unified_diff(old_content: str, new_content: str, filename: str) -> str:
    """Generate unified diff without git"""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(
        old_lines, 
        new_lines, 
        fromfile=f"a/{os.path.basename(filename)}",
        tofile=f"b/{os.path.basename(filename)}",
        lineterm=""
    )
    
    return ''.join(diff)


def generate_change_summary(old_content: str, new_content: str) -> dict:
    """Generate change statistics"""
    old_lines = old_content.splitlines()
    new_lines = new_content.splitlines()
    
    matcher = difflib.SequenceMatcher(None, old_lines, new_lines)
    changes = {
        'added': 0,
        'removed': 0,
        'modified': 0,
        'unchanged': 0
    }
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'insert':
            changes['added'] += j2 - j1
        elif tag == 'delete':
            changes['removed'] += i2 - i1
        elif tag == 'replace':
            changes['modified'] += max(i2 - i1, j2 - j1)
        elif tag == 'equal':
            changes['unchanged'] += i2 - i1
    
    return changes


def display_change_summary(changes: dict) -> None:
    """Display change summary in a table"""
    if not RICH_AVAILABLE or not console:
        # Fallback to simple text display
        safe_console_print("Change Summary:")
        if changes['added'] > 0:
            safe_console_print(f"  Added: +{changes['added']} lines")
        if changes['removed'] > 0:
            safe_console_print(f"  Removed: -{changes['removed']} lines")
        if changes['modified'] > 0:
            safe_console_print(f"  Modified: ~{changes['modified']} lines")
        if changes['unchanged'] > 0:
            safe_console_print(f"  Unchanged: ={changes['unchanged']} lines")
        return
    
    table = Table(title="📊 Change Summary", show_header=True)
    table.add_column("Type", style="bold", width=15)
    table.add_column("Count", style="cyan", width=10)
    table.add_column("Description", style="white")
    
    if changes['added'] > 0:
        table.add_row("Added", f"[green]+{changes['added']}[/green]", "New lines added")
    if changes['removed'] > 0:
        table.add_row("Removed", f"[red]-{changes['removed']}[/red]", "Lines removed")
    if changes['modified'] > 0:
        table.add_row("Modified", f"[yellow]~{changes['modified']}[/yellow]", "Lines changed")
    if changes['unchanged'] > 0:
        table.add_row("Unchanged", f"[blue]={changes['unchanged']}[/blue]", "Lines unchanged")
    
    console.print(table)


def display_unified_diff(old_content: str, new_content: str, filename: str) -> None:
    """Display unified diff with syntax highlighting"""
    diff_text = generate_unified_diff(old_content, new_content, filename)
    
    if not diff_text.strip():
        safe_console_print("⚠️  No changes detected")
        return
    
    if not RICH_AVAILABLE or not console:
        # Fallback to plain text diff
        safe_console_print("Proposed Changes:")
        safe_console_print("-" * 50)
        safe_console_print(diff_text)
        safe_console_print("-" * 50)
        return
    
    # Apply syntax highlighting for diff
    syntax = Syntax(diff_text, "diff", theme="monokai", line_numbers=True)
    panel = Panel(
        syntax, 
        title="📋 Proposed Changes", 
        border_style="yellow",
        padding=(1, 2)
    )
    console.print(panel)


def get_user_confirmation() -> bool:
    """Get user confirmation for changes"""
    while True:
        choice = safe_console_input("\nApply these changes? [y/N]: ").strip()
        
        if choice.lower() in ['y', 'yes']:
            return True
        elif choice.lower() in ['n', 'no', '']:
            return False
        else:
            safe_console_print("Please enter 'y' for yes or 'n' for no")


def display_file_info(file_path: str, is_new_file: bool) -> None:
    """Display file information"""
    if not RICH_AVAILABLE or not console:
        # Fallback to simple text display
        safe_console_print(f"File: {os.path.basename(file_path)}")
        safe_console_print(f"Path: {file_path}")
        safe_console_print(f"Status: {'New File' if is_new_file else 'Existing File'}")
        return
    
    table = Table(show_header=False, box=None, padding=(0, 1))
    table.add_column("Field", style="bold cyan", width=12)
    table.add_column("Value", style="white")
    
    table.add_row("File", os.path.basename(file_path))
    table.add_row("Path", file_path)
    table.add_row("Status", "[green]New File[/green]" if is_new_file else "[blue]Existing File[/blue]")
    
    panel = Panel(
        table,
        title="📄 File Information",
        border_style="bright_blue",
        padding=(0, 1)
    )
    console.print(panel)


def interactive_diff_review(old_content: str, new_content: str, filename: str, is_new_file: bool = False) -> bool:
    """Interactive review of changes with rich formatting"""
    safe_console_print("\n" + "="*60)
    safe_console_print("🔍 REVIEWING CHANGES")
    safe_console_print("="*60)
    
    # Show file information
    display_file_info(filename, is_new_file)
    
    if is_new_file:
        # For new files, show creation summary
        new_lines = len(new_content.splitlines())
        safe_console_print(f"\n📝 Creating new file with {new_lines} lines")
        
        # Show preview of new content (first 20 lines)
        lines = new_content.splitlines()
        preview_lines = lines[:20]
        if len(lines) > 20:
            preview_lines.append("... (truncated)")
        
        preview_text = "\n".join(preview_lines)
        
        if RICH_AVAILABLE and console:
            syntax = Syntax(preview_text, "python", theme="monokai", line_numbers=True)
            panel = Panel(
                syntax,
                title="📋 New File Content Preview",
                border_style="green",
                padding=(1, 2)
            )
            console.print(panel)
        else:
            safe_console_print("New File Content Preview:")
            safe_console_print("-" * 40)
            safe_console_print(preview_text)
            safe_console_print("-" * 40)
    else:
        # Show change summary
        changes = generate_change_summary(old_content, new_content)
        display_change_summary(changes)
        
        # Show detailed diff
        safe_console_print("\n📋 Detailed Changes:")
        display_unified_diff(old_content, new_content, filename)
    
    # Get user confirmation
    return get_user_confirmation()


def modify_code_file_non_interactive(file_path: str, new_code: str) -> str:
    """
    Replaces the entire content of a code file without user interaction.
    Used for automated operations where user confirmation isn't possible.

    Parameters:
        file_path (str): Path to the file to modify (relative or absolute)
        new_code (str): New code to replace the entire file content with

    Returns:
        str: A success message

    Raises:
        FileNotFoundError: If the specified file doesn't exist and can't be created
        IOError: If there's an error modifying the file
    """
    try:
        # Convert relative path to absolute path if needed
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getenv("CODE_REPO_PATH"), file_path.lstrip('/'))

        # Read original content (if file exists)
        original_content = ""
        is_new_file = False
        backup_path = None
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
            
            # Create backup
            backup_path = f"{file_path}.backup"
            shutil.copy2(file_path, backup_path)
        else:
            # New file
            is_new_file = True
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if there are any changes
        if not is_new_file and original_content == new_code:
            return f"No changes needed for: {file_path}"
        
        # Apply changes directly without user confirmation
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_code)
        
        # Remove backup on success
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
        
        # Success message
        action = "created" if is_new_file else "modified"
        return f"File {action} successfully at: {file_path}"
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {file_path}")
    except IOError as e:
        # Restore from backup if error occurred
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
        raise IOError(f"Error modifying file {file_path}: {str(e)}")
    except Exception as e:
        # Restore from backup if any other error occurred
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
        raise Exception(f"Unexpected error modifying file {file_path}: {str(e)}")


def modify_code_file(file_path: str, new_code: str, interactive: bool = True) -> str:
    """
    Replaces the entire content of a code file with optional diff preview and user confirmation.

    Parameters:
        file_path (str): Path to the file to modify (relative or absolute)
        new_code (str): New code to replace the entire file content with
        interactive (bool): Whether to show diff and ask for user confirmation
    
    Returns:
        str: A success message or user rejection message
        
    Raises:
        FileNotFoundError: If the specified file doesn't exist and can't be created
        IOError: If there's an error modifying the file
    """
    if not interactive:
        return modify_code_file_non_interactive(file_path, new_code)
    
    try:
        # Convert relative path to absolute path if needed
        if not os.path.isabs(file_path):
            file_path = os.path.join(os.getenv("CODE_REPO_PATH"), file_path.lstrip('/'))

        # Read original content (if file exists)
        original_content = ""
        is_new_file = False
        backup_path = None
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                original_content = file.read()
            
            # Create backup
            backup_path = f"{file_path}.backup"
            shutil.copy2(file_path, backup_path)
        else:
            # New file
            is_new_file = True
            # Ensure directory exists
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        # Check if there are any changes
        if not is_new_file and original_content == new_code:
            safe_console_print("⚠️  No changes detected - file content is identical")
            return f"No changes needed for: {file_path}"
        
        # Show diff and get user confirmation
        if not interactive_diff_review(original_content, new_code, file_path, is_new_file):
            # User rejected changes
            if backup_path and os.path.exists(backup_path):
                os.remove(backup_path)
            return f"Changes rejected by user for: {file_path}"
        
        # Apply changes
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_code)
        
        # Remove backup on success
        if backup_path and os.path.exists(backup_path):
            os.remove(backup_path)
        
        # Success message
        action = "created" if is_new_file else "modified"
        safe_console_print(f"✅ Successfully {action}: {file_path}")
        return f"File {action} successfully at: {file_path}"
        
    except FileNotFoundError:
        raise FileNotFoundError(f"File not found at path: {file_path}")
    except IOError as e:
        # Restore from backup if error occurred
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
        raise IOError(f"Error modifying file {file_path}: {str(e)}")
    except Exception as e:
        # Restore from backup if any other error occurred
        if backup_path and os.path.exists(backup_path):
            shutil.copy2(backup_path, file_path)
            os.remove(backup_path)
        raise Exception(f"Unexpected error modifying file {file_path}: {str(e)}")


if __name__ == "__main__":
    # Example usage with interactive testing
    try:
        file_path = os.path.join(CODE_REPO_PATH, "example.py")
        
        new_code = '''def hello_world():
    """
    A simple function that prints a greeting message.
    This is a test function to verify the modify_code_file functionality.
    """
    print("Hello, world! This file was modified by the modify_code_file function.")
    
    return "Hello, world!"

def goodbye_world():
    """
    A new function added to test the diff functionality.
    """
    print("Goodbye, world!")
    return "Goodbye, world!"

if __name__ == "__main__":
    result = hello_world()
    print(f"Function returned: {result}")
    
    goodbye_result = goodbye_world()
    print(f"Goodbye function returned: {goodbye_result}")
'''
        
        if not os.path.exists(file_path):
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("# Initial content\nprint('Hello, initial world!')")
            print(f"Created test file at: {file_path}")
        
        print(f"Testing enhanced modify_code_file on: {file_path}")
        result = modify_code_file(file_path, new_code)
        
        print(f"\nResult: {result}")
        
    except (FileNotFoundError, IOError) as e:
        print(f"Error: {e}")