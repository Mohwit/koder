"""Execute bash commands with enhanced safety and output processing."""

import os
import platform
import re
import subprocess
import time
from typing import Dict, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

load_dotenv()

CODE_REPO_PATH = os.getcwd()

# Common directories to exclude from file searches
EXCLUDE_DIRS = [
    ".venv",
    "venv",
    "env",  # Python virtual environments
    "node_modules",  # Node.js dependencies
    ".git",  # Git repository data
    "__pycache__",  # Python cache
    ".pytest_cache",  # Pytest cache
    ".mypy_cache",  # MyPy cache
    "build",
    "dist",  # Build artifacts
    ".coverage",  # Coverage data
    ".tox",  # Tox environments
    ".idea",
    ".vscode",  # IDE files
    "*.egg-info",  # Python package info
    ".DS_Store",  # macOS files
    "vector_db",  # Vector database (project specific)
]


def _modify_find_command(command: str) -> str:
    """
    Modify find commands to exclude common non-code directories and use relative paths.

    Parameters:
        command (str): The original command

    Returns:
        str: Modified command with exclusions
    """

    # Check if this is a find command
    if command.strip().startswith('find '):
        # Replace absolute project path with current directory
        project_path = CODE_REPO_PATH
        if project_path in command:
            command = command.replace(project_path, '.')

        # Add exclusions for common directories
        exclusion_parts = []
        for exclude_dir in EXCLUDE_DIRS:
            exclusion_parts.append(f'-not -path "*/{exclude_dir}/*"')

        exclusions = ' '.join(exclusion_parts)

        # Insert exclusions after the find path but before other arguments
        find_parts = command.split(' ', 2)
        if len(find_parts) >= 2:
            if len(find_parts) == 2:
                # Just "find path"
                modified_command = f"{find_parts[0]} {find_parts[1]} {exclusions}"
            else:
                # "find path other_args"
                modified_command = (
                    f"{find_parts[0]} {find_parts[1]} {exclusions} {find_parts[2]}"
                )
        else:
            modified_command = command

        return modified_command

    return command


def _is_command_safe(command: str) -> tuple[bool, str]:
    """
    Check if a command is safe to execute.

    Parameters:
        command (str): The command to check

    Returns:
        tuple[bool, str]: (is_safe, reason_if_not_safe)
    """

    # List of dangerous commands/patterns
    dangerous_patterns = [
        r'\brm\s+-rf\s*/',  # rm -rf / (and variations)
        r'\bsudo\s+rm',  # sudo rm
        r'\bchmod\s+777',  # chmod 777
        r'\bchown\s+',  # chown commands
        r'\bmkfs\.',  # filesystem creation
        r'\bdd\s+if=',  # dd command
        r'\b>\s*/dev/',  # writing to device files
        r'\bmount\b',  # mount commands
        r'\bumount\b',  # umount commands
        r'\bfdisk\b',  # fdisk
        r'\bparted\b',  # parted
        r'\biptables\b',  # iptables
        r'\bsystemctl\b',  # systemctl
        r'\bservice\b',  # service control
        r'\breboot\b',  # reboot
        r'\bshutdown\b',  # shutdown
        r'\bhalt\b',  # halt
        r'\bpoweroff\b',  # poweroff
        r'\bcrontab\s+-r',  # crontab deletion
        r'\>/etc/',  # writing to etc
        r'\>/usr/',  # writing to usr
        r'\>/bin/',  # writing to bin
        r'\>/sbin/',  # writing to sbin
    ]

    for pattern in dangerous_patterns:
        if re.search(pattern, command, re.IGNORECASE):
            reason = f"Command contains dangerous pattern: {pattern}"
            return False, reason

    # Check for file operations outside the project directory
    if any(op in command for op in ['rm ', 'mv ', 'cp ', '>', '>>']):
        # Allow operations within project directory
        if not any(
            safe_indicator in command
            for safe_indicator in ['./', '../', CODE_REPO_PATH]
        ):
            # Check if command contains absolute paths outside project
            abs_path_pattern = r'/[a-zA-Z]+'
            matches = re.findall(abs_path_pattern, command)
            for match in matches:
                if not match.startswith(CODE_REPO_PATH):
                    reason = f"File operation outside project directory: {match}"
                    return False, reason

    return True, ""


def execute_bash_command(
    command: str,
    timeout: int = 30,
) -> str:
    """
    Execute a bash command safely with timeout and error handling.

    Args:
        command: The bash command to execute
        timeout: Maximum execution time in seconds

    Returns:
        str: Command output or error message
    """
    start_time = time.time()

    try:
        # Safety check
        is_safe, reason = _is_command_safe(command)
        if not is_safe:
            error_msg = f"Command blocked for security reasons: {reason}"
            return error_msg

        # Interactive confirmation with simple, consistent CLI styling
        console = Console()
        panel = Panel(
            f"[bold]Tool:[/bold] execute_bash_command\n[bold]Command:[/bold] {command}",
            title="🛠️ Tool Confirmation",
            border_style="bright_red",
            padding=(0, 1)
        )
        console.print(panel)
        user_input = console.input("[bold yellow]Type 'Y' or 'y' to execute this command:[/bold yellow] ").strip().lower()
        if user_input != 'y':
            return "Command not executed: user did not confirm."
    

        # Modify find commands to exclude common directories
        modified_command = _modify_find_command(command)

        # Change to the code repository directory
        original_cwd = os.getcwd()
        os.chdir(CODE_REPO_PATH)

        try:
            # Execute the command

            result = subprocess.run(
                modified_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=CODE_REPO_PATH,
            )

            # Check if command was successful
            if result.returncode == 0:
                output = result.stdout.strip()
                output_length = len(output)

                if output_length > 10000:  # Log warning for very long outputs
                    pass  # Removed logging

                # Limit output size to prevent overwhelming the agent
                if len(output) > 5000:
                    truncated_output = (
                        output[:5000]
                        + f"\n... [Output truncated. Total length: {len(output)} characters]"
                    )
                    return truncated_output

                return output if output else "Command executed successfully (no output)"
            else:
                error_output = result.stderr.strip()
                return f"Command failed with return code {result.returncode}:\n{error_output}"

        finally:
            # Always restore the original directory
            os.chdir(original_cwd)

    except subprocess.TimeoutExpired:
        error_msg = f"Command timed out after {timeout} seconds"
        return error_msg
    except subprocess.CalledProcessError as e:
        error_msg = f"Command failed: {str(e)}"
        return error_msg
    except Exception as e:
        error_msg = f"Error executing command: {str(e)}"
        return error_msg


def get_system_info() -> Dict[str, str]:
    """Get basic system information."""
    return {
        "platform": platform.system(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "current_directory": os.getcwd(),
    }


def list_processes() -> str:
    """
    List running processes.

    Returns:
        str: List of running processes
    """
    try:
        result = subprocess.run(
            "ps aux",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=CODE_REPO_PATH,
            check=False,
        )

        if result.returncode == 0:
            lines = result.stdout.strip().split("\n")
            # Return first 20 lines to avoid too much output
            limited_output = "\n".join(lines[:20])
            if len(lines) > 20:
                limited_output += f"\n... (showing first 20 of {len(lines)} processes)"
            return limited_output
        else:
            return f"Error listing processes: {result.stderr}"

    except (OSError, subprocess.SubprocessError) as e:
        return f"Error listing processes: {str(e)}"


if __name__ == "__main__":
    # Example usage
    try:
        # Test basic command
        OUTPUT = execute_bash_command("ls -la")

        # Test system info
        get_system_info()

    except (OSError, subprocess.SubprocessError, ValueError):
        pass
