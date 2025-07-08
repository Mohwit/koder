#!/usr/bin/env python3
"""
KODER - An intelligent CLI tool for code understanding and assistance
"""

import click
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.syntax import Syntax
from rich.table import Table
from rich.live import Live
from rich.markdown import Markdown
import sys
import os
from dotenv import load_dotenv

# Import Agent and tools
from koder.agent.agent import Agent
from koder.prompts.system_prompt import system_prompt
from koder.tools.write import create_code_file
from koder.tools.modify import modify_code_file
from koder.tools.read import read_code_file
from koder.tools.grep import grep_search
from koder.tools.bash import execute_bash_command

load_dotenv()

console = Console()

# Tools configuration
tools = [    
    {
        "type": "function",
        "function": {
            "name": "read_code_file",
            "description": "Read and retrieve code content from a file. Can read either the entire file or a specific range of lines. Useful for inspecting existing code, understanding context, or verifying file contents. Returns the file content as a string.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to be read"
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Optional starting line number to read from (1-based indexing)",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Optional ending line number to read until (1-based indexing)",
                    }
                },
                "required": ["file_path"]
            },
            "callable": read_code_file
        }
    },
    {
        "type": "function",
        "function": {
            "name": "modify_code_file",
            "description": "Replace the entire content of a code file with new code. Shows diff preview and asks for user confirmation before applying changes. This tool handles both file modification and backup/restore functionality. Returns a success message and the updated content.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Path to the file to modify (relative or absolute)"
                    },
                    "new_code": {
                        "type": "string",
                        "description": "New code to replace the entire file content with"
                    },
                    "interactive": {
                        "type": "boolean",
                        "description": "Whether to show diff and ask for user confirmation (default: true)"
                    }
                },
                "required": ["file_path", "new_code"]
            },
            "callable": modify_code_file
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_code_file",
            "description": "Create a new file or overwrite an existing one with provided code. This tool handles file creation, directory validation, and writes the specified content. Useful for generating new source files, configuration files, or documentation. Returns the path of the created file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The full path (including filename) where the file should be created"
                    },
                    "code": {
                        "type": "string",
                        "description": "The code (or text) to write into the file"
                    }
                },
                "required": ["file_path", "code"]
            },
            "callable": create_code_file
        }
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": "Search for patterns in files using grep-like functionality. Can search in specific files or across directories with various options including regex support, case sensitivity, and recursive search. Returns matches with line numbers and file paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The search pattern (regex supported)"
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional specific file to search in"
                    },
                    "directory": {
                        "type": "string",
                        "description": "Optional directory to search in (if file_path not provided)"
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": "Whether to search recursively in subdirectories (default: false)"
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": "Whether search should be case sensitive (default: true)"
                    },
                    "line_numbers": {
                        "type": "boolean",
                        "description": "Whether to include line numbers in results (default: true)"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 100)"
                    }
                },
                "required": ["pattern"]
            },
            "callable": grep_search
        }
    },
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": "Execute a bash command safely and return the result. Includes basic security checks to prevent dangerous operations. Returns command output, exit code, and execution details. Useful for running shell commands, checking system status, or performing file operations.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute"
                    },
                    "working_directory": {
                        "type": "string",
                        "description": "Optional directory to run command in (defaults to CODE_REPO_PATH)"
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Timeout in seconds for command execution (default: 30)"
                    },
                    "capture_output": {
                        "type": "boolean",
                        "description": "Whether to capture and return command output (default: true)"
                    }
                },
                "required": ["command"]
            },
            "callable": execute_bash_command
        }
    },
]

def display_logo():
    """Display the KODER ASCII logo"""
    logo = """
    ██╗  ██╗ ██████╗ ██████╗ ███████╗██████╗ 
    ██║ ██╔╝██╔═══██╗██╔══██╗██╔════╝██╔══██╗
    █████╔╝ ██║   ██║██║  ██║█████╗  ██████╔╝
    ██╔═██╗ ██║   ██║██║  ██║██╔══╝  ██╔══██╗
    ██║  ██╗╚██████╔╝██████╔╝███████╗██║  ██║
    ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝
    """
    return logo

def display_welcome():
    """Display the welcome screen"""
    console.clear()
    
    # Logo
    logo_text = Text(display_logo(), style="bold cyan")
    logo_panel = Panel(
        Align.center(logo_text),
        style="bright_blue",
        padding=(0, 1)
    )
    
    # Tagline
    tagline = Text("🚀 AI-Powered Code Assistant on Your Terminal", style="bold bright_white")
    tagline_panel = Panel(
        Align.center(tagline),
        style="bright_magenta",
        padding=(0, 2)
    )
    
    # Display everything
    console.print(logo_panel)
    console.print(tagline_panel)
    
    # Footer
    footer = Text("Made with 🥲  for developers | Version 0.1.0", style="italic")
    console.print(Align.center(footer), style="blue")
    console.print()

def display_tool_execution(tool_name: str, args: dict, status: str, error_msg: str = None):
    """Display tool execution with rich formatting"""
    # Create status icon and color
    if status == "success":
        status_icon = "✅"
        status_color = "green"
    elif status == "error":
        status_icon = "❌"
        status_color = "red"
    else:  # executing
        status_icon = "🔄"
        status_color = "yellow"
    
    # Create tool info table
    table = Table(show_header=False, show_lines=True, box=None, padding=(0, 1))
    table.add_column("Field", style="bold cyan", width=12)
    table.add_column("Value", style="white")
    
    table.add_row("Tool", f"[bold]{tool_name}[/bold]")
    table.add_row("Status", f"[{status_color}]{status_icon} {status.title()}[/{status_color}]")
    
    # Add arguments if provided
    if args:
        for key, value in args.items():
            # Truncate long values
            str_value = str(value)
            if len(str_value) > 50:
                str_value = str_value[:47] + "..."
            table.add_row(key.title(), str_value)
    
    # Add error message if provided
    if error_msg:
        table.add_row("Error", f"[red]{error_msg}[/red]")
    
    # Display in panel
    panel = Panel(
        table,
        title=f"🛠️  Tool Execution",
        border_style="bright_blue",
        padding=(0, 1)
    )
    
    console.print(panel)

def display_response(content: str, tool_calls_count: int = 0):
    """Display agent response with rich formatting"""
    if content.strip():
        # Try to render as markdown if it looks like markdown
        if any(marker in content for marker in ['#', '*', '`', '-', '1.']):
            try:
                markdown_content = Markdown(content)
                response_panel = Panel(
                    markdown_content,
                    title="🤖 Agent Response",
                    border_style="bright_green",
                    padding=(1, 2)
                )
            except:
                # Fallback to plain text if markdown parsing fails
                response_panel = Panel(
                    content,
                    title="🤖 Agent Response",
                    border_style="bright_green",
                    padding=(1, 2)
                )
        else:
            response_panel = Panel(
                content,
                title="🤖 Agent Response",
                border_style="bright_green",
                padding=(1, 2)
            )
        
        console.print(response_panel)
    
    # Show tool execution summary
    if tool_calls_count > 0:
        summary = f"🔧 Executed {tool_calls_count} tool call{'s' if tool_calls_count > 1 else ''}"
        console.print(f"[dim]{summary}[/dim]")

def create_agent():
    """Create and return an Agent instance"""
    try:
        agent = Agent(
            model="claude-3-5-sonnet-20241022", 
            base_url="https://api.anthropic.com/v1", 
            api_key=os.getenv("ANTHROPIC_API_KEY"), 
            system_prompt=system_prompt, 
            tools=tools
        )
        return agent
    except Exception as e:
        console.print(f"[red]❌ Error creating agent: {str(e)}[/red]")
        return None

def interactive_mode():
    """Run interactive mode with continuous conversation"""
    console.print(Panel(
        "[bold cyan]🎯 Interactive Mode[/bold cyan]\n"
        "Type your questions and I'll help you with your code!\n"
        "Commands: [bold]'quit', 'exit', 'q'[/bold] to exit | [bold]'clear'[/bold] to clear screen",
        title="Welcome to KODER",
        border_style="bright_blue"
    ))
    
    agent = create_agent()
    if not agent:
        return
    
    while True:
        try:
            # Get user input
            user_prompt = console.input("\n[bold magenta]💬 You:[/bold magenta] ")
            
            # Handle special commands
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                console.print("[bold green]👋 Goodbye![/bold green]")
                break
            elif user_prompt.lower() == 'clear':
                console.clear()
                continue
            elif not user_prompt.strip():
                continue
            
            # Process without status spinner for interactive tools
            console.print("\n[bold yellow]🔄 Processing...[/bold yellow]")
            
            # Override the agent's tool processing to show better UI
            original_process_tool_calls = agent._process_tool_calls
            
            def enhanced_process_tool_calls(tool_calls):
                for i, tool_call in enumerate(tool_calls, 1):
                    import json
                    tool_name = tool_call.function.name
                    
                    # Parse arguments
                    try:
                        args = json.loads(tool_call.function.arguments)
                    except json.JSONDecodeError:
                        args = {}
                    
                    # Check if this is an interactive tool
                    is_interactive_tool = tool_name == "modify_code_file" and args.get("interactive", True)
                    
                    if is_interactive_tool:
                        # For interactive tools, don't show executing status - let the tool handle its own UI
                        console.print(f"\n🛠️  Executing interactive tool: [bold]{tool_name}[/bold]")
                        console.print("[dim]Note: This tool will show a diff and ask for your confirmation[/dim]\n")
                    else:
                        # For non-interactive tools, show executing status
                        display_tool_execution(tool_name, args, "executing")
                    
                    # Execute the tool
                    tool_call_response = agent._execute_tool_call(tool_call)
                    
                    # Show result only for non-interactive tools
                    if not is_interactive_tool:
                        response_str = str(tool_call_response["tool_response"])
                        if (response_str.startswith("Error:") or 
                            response_str.startswith("Error executing tool") or 
                            response_str.startswith("Error parsing tool arguments")):
                            display_tool_execution(tool_name, args, "error", response_str)
                        else:
                            display_tool_execution(tool_name, args, "success")
                    else:
                        # For interactive tools, just show completion
                        response_str = str(tool_call_response["tool_response"])
                        if "rejected by user" in response_str:
                            console.print("[yellow]🚫 Changes rejected by user[/yellow]")
                        elif "successfully" in response_str.lower():
                            console.print("[green]✅ Changes applied successfully[/green]")
                        else:
                            console.print(f"[blue]ℹ️  {response_str}[/blue]")
                    
                    # Add to messages
                    agent.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_response["tool_call_id"],
                        "name": tool_call_response["tool_name"],
                        "content": tool_call_response["tool_response"],
                    })
            
            # Temporarily replace the method
            agent._process_tool_calls = enhanced_process_tool_calls
            
            # Get response
            response = agent.query(user_prompt)
            
            # Restore original method
            agent._process_tool_calls = original_process_tool_calls
            
            # Display response
            tool_calls_count = len(response["tool_calls"]) if response["tool_calls"] else 0
            display_response(response["content"], tool_calls_count)
            
        except KeyboardInterrupt:
            console.print("\n[bold green]👋 Goodbye![/bold green]")
            break
        except Exception as e:
            console.print(f"[red]❌ Error: {str(e)}[/red]")
            console.print("[yellow]Please try again.[/yellow]")

@click.group()
@click.version_option(version="1.0.0", prog_name="koder")
def cli():
    """KODER - Your AI-powered coding co-pilot"""
    pass

@cli.command()
def welcome():
    """Display the welcome screen"""
    display_welcome()

@cli.command()
def analyze():
    """Analyze the current codebase"""
    console.print("🔍 [bold cyan]Analyzing codebase...[/bold cyan]")
    console.print("This feature is coming soon! 🚀")

@cli.command()
def fix():
    """Fix detected issues in the codebase"""
    console.print("🐛 [bold green]Fixing issues...[/bold green]")
    console.print("This feature is coming soon! 🚀")

@cli.command()
def refactor():
    """Refactor code with AI suggestions"""
    console.print("🔧 [bold yellow]Refactoring code...[/bold yellow]")
    console.print("This feature is coming soon! 🚀")

@cli.command()
@click.argument('prompt', required=False)
@click.option('--interactive', '-i', is_flag=True, help='Start interactive mode')
def ask(prompt, interactive):
    """Ask KODER to help with a specific coding task"""
    if interactive or not prompt:
        interactive_mode()
        return
    
    # Single prompt mode
    agent = create_agent()
    if not agent:
        return
    
    try:
        console.print(f"[bold magenta]💬 You:[/bold magenta] {prompt}")
        
        # Process without status spinner for interactive tools
        console.print("\n[bold yellow]🔄 Processing...[/bold yellow]")
        
        # Override the agent's tool processing to show better UI
        original_process_tool_calls = agent._process_tool_calls
        
        def enhanced_process_tool_calls(tool_calls):
            for i, tool_call in enumerate(tool_calls, 1):
                import json
                tool_name = tool_call.function.name
                
                # Parse arguments
                try:
                    args = json.loads(tool_call.function.arguments)
                except json.JSONDecodeError:
                    args = {}
                
                # Check if this is an interactive tool
                is_interactive_tool = tool_name == "modify_code_file" and args.get("interactive", True)
                
                if is_interactive_tool:
                    # For interactive tools, don't show executing status - let the tool handle its own UI
                    console.print(f"\n🛠️  Executing interactive tool: [bold]{tool_name}[/bold]")
                    console.print("[dim]Note: This tool will show a diff and ask for your confirmation[/dim]\n")
                else:
                    # For non-interactive tools, show executing status
                    display_tool_execution(tool_name, args, "executing")
                
                # Execute the tool
                tool_call_response = agent._execute_tool_call(tool_call)
                
                # Show result only for non-interactive tools
                if not is_interactive_tool:
                    response_str = str(tool_call_response["tool_response"])
                    if (response_str.startswith("Error:") or 
                        response_str.startswith("Error executing tool") or 
                        response_str.startswith("Error parsing tool arguments")):
                        display_tool_execution(tool_name, args, "error", response_str)
                    else:
                        display_tool_execution(tool_name, args, "success")
                else:
                    # For interactive tools, just show completion
                    response_str = str(tool_call_response["tool_response"])
                    if "rejected by user" in response_str:
                        console.print("[yellow]🚫 Changes rejected by user[/yellow]")
                    elif "successfully" in response_str.lower():
                        console.print("[green]✅ Changes applied successfully[/green]")
                    else:
                        console.print(f"[blue]ℹ️  {response_str}[/blue]")
                
                # Add to messages
                agent.messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call_response["tool_call_id"],
                    "name": tool_call_response["tool_name"],
                    "content": tool_call_response["tool_response"],
                })
        
        # Temporarily replace the method
        agent._process_tool_calls = enhanced_process_tool_calls
        
        # Get response
        response = agent.query(prompt)
        
        # Restore original method
        agent._process_tool_calls = original_process_tool_calls
        
        # Display response
        tool_calls_count = len(response["tool_calls"]) if response["tool_calls"] else 0
        display_response(response["content"], tool_calls_count)
        
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")

def main():
    """Main entry point"""
    if len(sys.argv) == 1:
        display_welcome()
        # Auto-start interactive mode if no args
        try:
            interactive_mode()
        except KeyboardInterrupt:
            console.print("\n[bold green]👋 Goodbye![/bold green]")
    else:
        cli()

if __name__ == "__main__":
    main()
