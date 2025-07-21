"""
This tool is used to execute bash commands safely with proper error handling.
It can run various shell commands and return their output.
"""

import os
import subprocess
from typing import Optional
from dotenv import load_dotenv

load_dotenv()

CODE_REPO_PATH = os.getcwd()


def execute_bash_command(
    command: str,
    working_directory: Optional[str] = None,
    timeout: int = 30,
    capture_output: bool = True,
) -> str:
    """
    Execute a bash command safely and return the result.

    Parameters:
        command (str): The bash command to execute
        working_directory (str, optional): Directory to run command in (defaults to CODE_REPO_PATH)
        timeout (int): Timeout in seconds for command execution
        capture_output (bool): Whether to capture and return command output

    Returns:
        str: Command output and execution details

    Raises:
        ValueError: If command is empty or contains dangerous operations
        IOError: If command execution fails
    """
    try:
        if not command or not command.strip():
            raise ValueError("Command cannot be empty")

        # Basic security checks
        dangerous_commands = [
            "rm -rf /",
            "rm -rf *",
            "dd if=",
            "mkfs",
            "fdisk",
            "chmod -R 777",
            "sudo rm",
            "sudo dd",
            "sudo mkfs",
            "sudo fdisk",
            "> /dev/null; rm",
            "curl | sh",
            "wget | sh",
            "eval",
            "exec",
        ]

        command_lower = command.lower()
        for dangerous in dangerous_commands:
            if dangerous in command_lower:
                raise ValueError(f"Potentially dangerous command blocked: {command}")

        # Set working directory
        if working_directory:
            if not os.path.isabs(working_directory):
                cwd = os.path.join(CODE_REPO_PATH, working_directory.lstrip("/"))
            else:
                cwd = working_directory
        else:
            cwd = CODE_REPO_PATH

        if not os.path.exists(cwd):
            raise FileNotFoundError(f"Working directory not found: {cwd}")

        # Execute command
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd,
            capture_output=capture_output,
            text=True,
            timeout=timeout,
            env=os.environ.copy(),
            check=False,
        )

        # Format output
        output_lines = []
        output_lines.append(f"Command: {command}")
        output_lines.append(f"Working Directory: {cwd}")
        output_lines.append(f"Exit Code: {result.returncode}")
        output_lines.append("-" * 50)

        if capture_output:
            if result.stdout:
                output_lines.append("STDOUT:")
                output_lines.append(result.stdout)

            if result.stderr:
                output_lines.append("STDERR:")
                output_lines.append(result.stderr)

        if result.returncode != 0:
            output_lines.append(f"⚠️  Command failed with exit code {result.returncode}")
        else:
            output_lines.append("✅ Command executed successfully")

        return "\n".join(output_lines)

    except (OSError, ValueError, FileNotFoundError) as e:
        raise IOError(f"Error executing command '{command}': {str(e)}") from e


def get_system_info() -> str:
    """
    Get basic system information.

    Returns:
        str: System information including OS, Python version, etc.
    """
    try:
        info_commands = [
            ("OS Info", "uname -a"),
            ("Python Version", "python --version"),
            ("Current Directory", "pwd"),
            ("Current User", "whoami"),
            ("Available Disk Space", "df -h"),
            ("Memory Usage", "free -h"),
        ]

        results = []
        for title, cmd in info_commands:
            try:
                result = subprocess.run(
                    cmd,
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5,
                    cwd=CODE_REPO_PATH,
                    check=False,
                )

                if result.returncode == 0:
                    results.append(f"{title}: {result.stdout.strip()}")
                else:
                    results.append(f"{title}: N/A")

            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                results.append(f"{title}: N/A")

        return "\n".join(results)

    except (OSError, subprocess.SubprocessError) as e:
        return f"Error getting system info: {str(e)}"


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
        print(OUTPUT)

        # Test system info
        print("\n" + "=" * 50)
        print("System Info:")
        print(get_system_info())

    except (OSError, subprocess.SubprocessError, ValueError) as e:
        print(f"Error: {e}")
