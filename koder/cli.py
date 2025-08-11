#!/usr/bin/env python3
"""
KODER - An intelligent CLI tool for code understanding and assistance
"""

import os
import json
import threading
from datetime import datetime
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich.live import Live
from rich.spinner import Spinner
from rich.markdown import Markdown
from rich.table import Table
from rich import box
from rich.align import Align

from dotenv import load_dotenv

from koder.agent.agent import Agent
from koder.prompts.main_agent_prompt import system_prompt
from koder.tools.main_agent_tools_schema import tools_schema
from koder.utils.inialize_code_rag import initialize_code_rag

# Load environment variables
load_dotenv()

# Initialize Rich console
console = Console()
app = typer.Typer(
    name="koder",
    help="🤖 KODER - Your AI-Powered Coding Assistant",
    rich_markup_mode="rich",
    no_args_is_help=False,
)

# Global variable to store RAG status messages
rag_status_messages = []

# Global flag to enable/disable enhanced tool display
enhanced_tools_enabled = True

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
    footer = Text("Made with ❤️  for developers | Version 1.0.0", style="italic")
    console.print(Align.center(footer), style="blue")
    console.print()

def display_help() -> None:
    """Display help information and available commands."""
    table = Table(title="[bold blue]Available Commands[/bold blue]", box=box.ROUNDED)
    table.add_column("Command", style="cyan", no_wrap=True)
    table.add_column("Description", style="white")
    
    table.add_row("chat", "Start interactive chat session (default)")
    table.add_row("help", "Show this help message")
    table.add_row("version", "Show version information")
    table.add_row("config", "Show current configuration")
    table.add_row("rag-status", "Show RAG system status and history")
    table.add_row("clear", "Clear screen and show welcome")
    table.add_row("quit/exit/q", "Exit the application")
    
    console.print()
    console.print(table)
    console.print()
    
    # Tips panel
    tips_text = Text()
    tips_text.append("💡 Pro Tips:\\n", style="bold yellow")
    tips_text.append("• Use natural language: 'Create a Python function that...'\\n", style="white")
    tips_text.append("• Ask for explanations: 'How does this code work?'\\n", style="white")
    tips_text.append("• Request refactoring: 'Make this code more efficient'\\n", style="white")
    tips_text.append("• Debug issues: 'Find the bug in this function'\\n", style="white")
    
    console.print(Panel(
        tips_text,
        title="[bold yellow]Usage Tips[/bold yellow]",
        border_style="yellow",
        padding=(1, 2),
    ))

def check_configuration() -> bool:
    """Check if the required configuration is available."""
    api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not api_key:
        console.print()
        console.print(Panel(
            "[bold red]❌ Error: ANTHROPIC_API_KEY not found![/bold red]\\n\\n"
            "Please set your Anthropic API key:\\n"
            "• Create a .env file in your project root\\n"
            "• Add: ANTHROPIC_API_KEY=your_api_key_here\\n"
            "• Or export it as an environment variable",
            title="[bold red]Configuration Error[/bold red]",
            border_style="red",
            padding=(1, 2),
        ))
        return False
    
    return True

def show_config() -> None:
    """Show current configuration."""
    table = Table(title="[bold blue]Current Configuration[/bold blue]", box=box.ROUNDED)
    table.add_column("Setting", style="cyan", no_wrap=True)
    table.add_column("Value", style="white")
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    table.add_row("API Key", "✅ Configured" if api_key else "❌ Not set")
    table.add_row("Model", "claude-3-7-sonnet-20250219")
    table.add_row("Base URL", "https://api.anthropic.com/v1")
    table.add_row("Temperature", "0.0")
    table.add_row("Max Tokens", "8096")
    
    console.print()
    console.print(table)
    console.print()

def show_rag_status() -> None:
    """Show RAG system status and message history."""
    console.print()
    
    if not rag_status_messages:
        console.print(Panel(
            "[dim yellow]No RAG status messages yet.\\n"
            "The system may still be initializing...[/dim yellow]",
            title="[bold yellow]🔄 RAG System Status[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        ))
    else:
        # Show last 10 messages with better formatting
        recent_messages = rag_status_messages[-10:]
        status_text = "\\n".join(f"• {msg}" for msg in recent_messages)
        
        console.print(Panel(
            f"[dim yellow]Recent status updates (last {len(recent_messages)}): \\n\\n{status_text}[/dim yellow]",
            title="[bold yellow]🔄 RAG System Status History[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        ))
    
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
        title="🛠️  Tool Execution",
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
            except Exception:
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

def initialize_agent() -> Optional[Agent]:
    """Initialize the Koder agent with proper error handling."""
    try:
        with console.status("[bold blue]Initializing Koder Agent...", spinner="dots"):
            # Create the agent
            agent = Agent(
                model="claude-3-7-sonnet-20250219",
                base_url="https://api.anthropic.com/v1",
                api_key=os.getenv("ANTHROPIC_API_KEY"),
                system_prompt=system_prompt,
                tools=tools_schema,
            )
            
        console.print("✅ [bold green]Agent initialized successfully![/bold green]")
        
        # Start code RAG initialization in background with status display
        console.print()
        console.print(Panel(
            "[dim yellow]🔄 Initializing code RAG system in background...\\n"
            "Status updates will appear in separate panels below.[/dim yellow]",
            title="[bold yellow]Background Processing[/bold yellow]",
            border_style="yellow",
            padding=(0, 1),
        ))
        
        def rag_status_display(message):
            """Display RAG status message in a separate panel."""
            timestamp = datetime.now().strftime("%H:%M:%S")
            timestamped_message = f"[{timestamp}] {message}"
            rag_status_messages.append(timestamped_message)
            
            # Add some visual spacing and display status panel
            console.print()
            console.print(Panel(
                f"[dim yellow]{timestamped_message}[/dim yellow]",
                title="[bold yellow]🔄 RAG System Status[/bold yellow]",
                border_style="yellow",
                padding=(0, 1),
            ))
            
            # Add visual separator to maintain consistency
            console.print("[dim]" + "─" * 60 + "[/dim]")
        
        def rag_init_with_callback():
            """Initialize RAG with status callback."""
            initialize_code_rag(status_callback=rag_status_display)
        
        threading.Thread(target=rag_init_with_callback, daemon=True).start()
        
        return agent
        
    except (OSError, ValueError, RuntimeError) as e:
        console.print(f"❌ [bold red]Failed to initialize agent: {str(e)}[/bold red]")
        return None

def process_user_input(agent: Agent, user_input: str) -> None:
    """Process user input and display the response with enhanced tool visualization."""
    global enhanced_tools_enabled
    
    try:
        # Create a spinner for processing
        with Live(
            Panel(
                Spinner("dots", text="[bold blue]Processing your request..."),
                title="[bold blue]🤖 Koder is thinking...[/bold blue]",
                border_style="blue",
            ),
            refresh_per_second=4,
        ) as live:
            # Only use enhanced tools if enabled and no previous errors
            if not enhanced_tools_enabled:
                response = agent.query(user_input)
                live.stop()
                
                # Simple display without enhanced tools
                console.print()
                display_response(response["content"], len(response["tool_calls"]) if response["tool_calls"] else 0)
                return
            
            # Store original method for safe restoration
            original_process_tool_calls = agent._process_tool_calls
            
            def enhanced_process_tool_calls(tool_calls):
                """Enhanced tool call processing with beautiful display."""
                try:
                    for i, tool_call in enumerate(tool_calls, 1):
                        tool_name = tool_call.function.name
                        
                        # Parse arguments
                        try:
                            args = json.loads(tool_call.function.arguments)
                        except json.JSONDecodeError:
                            args = {}
                        
                        # Check if this is an interactive tool
                        is_interactive_tool = tool_name == "modify_code_file" and args.get("interactive", True)
                        
                        if is_interactive_tool:
                            # For interactive tools, don't show executing status
                            console.print(f"\\n🛠️  Executing interactive tool: [bold]{tool_name}[/bold]")
                            console.print("[dim]Note: This tool will show a diff and ask for your confirmation[/dim]\\n")
                        else:
                            # For non-interactive tools, show executing status
                            display_tool_execution(tool_name, args, "executing")
                        
                        # Execute the tool call using the original method's logic
                        tool_call_response = agent._execute_tool_call(tool_call)
                        
                        # Show result with beautiful display
                        response_str = str(tool_call_response["tool_response"])
                        is_error = (
                            response_str.startswith("Error:")
                            or response_str.startswith("Error executing tool")
                            or response_str.startswith("Error parsing tool arguments")
                        )
                        
                        if not is_interactive_tool:
                            if is_error:
                                display_tool_execution(tool_name, args, "error", response_str)
                            else:
                                display_tool_execution(tool_name, args, "success")
                        else:
                            # For interactive tools, just show completion
                            if "rejected by user" in response_str:
                                console.print("[yellow]🚫 Changes rejected by user[/yellow]")
                            elif "successfully" in response_str.lower():
                                console.print("[green]✅ Changes applied successfully[/green]")
                            else:
                                console.print(f"[blue]ℹ️  {response_str}[/blue]")
                        
                        # Ensure tool response is a string for API compatibility (from original)
                        tool_response_content = tool_call_response["tool_response"]
                        if not isinstance(tool_response_content, str):
                            tool_response_content = json.dumps(tool_response_content, indent=2)
                        
                        # Add tool response to messages (exactly like original)
                        agent.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call_response["tool_call_id"],
                            "name": tool_call_response["tool_name"],
                            "content": tool_response_content,
                        })
                            
                except Exception as e:
                    # If our enhanced processing fails, fall back to original
                    console.print(f"[yellow]⚠️  Tool display error: {e}[/yellow]")
                    console.print("[dim yellow]Disabling enhanced tool display for this session.[/dim yellow]")
                    global enhanced_tools_enabled
                    enhanced_tools_enabled = False
                    agent._process_tool_calls = original_process_tool_calls
                    original_process_tool_calls(tool_calls)
                    return
            
            # Temporarily replace the method
            agent._process_tool_calls = enhanced_process_tool_calls
            
            try:
                response = agent.query(user_input)
            finally:
                # Always restore original method
                agent._process_tool_calls = original_process_tool_calls
            
            # Clear the spinner
            live.stop()
            
            # Display response
            console.print()
            tool_calls_count = len(response["tool_calls"]) if response["tool_calls"] else 0
            display_response(response["content"], tool_calls_count)
            
    except KeyboardInterrupt:
        console.print("\\n[yellow]⏸️  Request cancelled by user[/yellow]")
    except Exception as e:
        console.print(f"\\n[bold red]❌ Error: {str(e)}[/bold red]")
        # Print more details for debugging API errors
        if "tool_call_id" in str(e):
            console.print("[dim red]This appears to be a tool call API error. Please try again.[/dim red]")

@app.command()
def chat() -> None:
    """Start an interactive chat session with Koder."""
    display_welcome()
    
    if not check_configuration():
        raise typer.Exit(1)
    
    agent = initialize_agent()
    if not agent:
        raise typer.Exit(1)
    
    console.print()
    console.print(Panel(
        "[bold cyan]🎯 Interactive Mode[/bold cyan]\\n"
        "Type your questions and I'll help you with your code!\\n"
        "Commands: [bold]'quit', 'exit', 'q'[/bold] to exit | [bold]'clear'[/bold] to clear screen | [bold]'help'[/bold] for usage tips",
        title="Welcome to KODER",
        border_style="bright_blue",
        padding=(1, 2),
    ))
    
    while True:
        try:
            # Ensure there's always a blank line before the prompt for consistency
            console.print()
            
            # Create a visual separator for better UX
            console.print("[dim]" + "─" * 60 + "[/dim]")
            
            user_input = Prompt.ask(
                "[bold magenta]💬 You",
                default="",
                show_default=False,
            ).strip()
            
            if not user_input:
                continue
                
            # Handle special commands
            if user_input.lower() in ["quit", "exit", "q"]:
                if Confirm.ask("[yellow]Are you sure you want to exit?[/yellow]"):
                    console.print("[bold green]👋 Thanks for using Koder! Happy coding![/bold green]")
                    break
                continue
                
            elif user_input.lower() == "help":
                display_help()
                continue
                
            elif user_input.lower() == "config":
                show_config()
                continue
                
            elif user_input.lower() == "clear":
                console.clear()
                display_welcome()
                continue
                
            elif user_input.lower() == "rag-status":
                show_rag_status()
                continue
                
            elif user_input.lower() == "enable-enhanced-tools":
                global enhanced_tools_enabled
                enhanced_tools_enabled = True
                console.print("[green]✅ Enhanced tool display re-enabled![/green]")
                continue
            
            # Process the user input
            process_user_input(agent, user_input)
            
        except KeyboardInterrupt:
            console.print("\\n[yellow]⏸️  Use 'quit' to exit gracefully[/yellow]")
        except (OSError, ValueError, RuntimeError) as e:
            console.print(f"\\n[bold red]❌ Unexpected error: {str(e)}[/bold red]")

@app.command()
def version() -> None:
    """Show version information."""
    console.print()
    console.print(Panel(
        "[bold blue]Koder AI Coding Assistant[/bold blue]\\n\\n"
        "Version: 1.0.0\\n"
        "Model: Claude-3.7-Sonnet\\n"
        "Framework: Typer + Rich\\n\\n"
        "[dim]Built with ❤️ for developers[/dim]",
        title="[bold blue]Version Info[/bold blue]",
        border_style="blue",
        padding=(1, 2),
    ))

@app.command()
def config() -> None:
    """Show current configuration."""
    show_config()

@app.command()
def analyze():
    """Analyze the current codebase"""
    console.print("🔍 [bold cyan]Analyzing codebase...[/bold cyan]")
    console.print("This feature is coming soon! 🚀")

@app.command()
def fix():
    """Fix detected issues in the codebase"""
    console.print("🐛 [bold green]Fixing issues...[/bold green]")
    console.print("This feature is coming soon! 🚀")

@app.command()
def refactor():
    """Refactor code with AI suggestions"""
    console.print("🔧 [bold yellow]Refactoring code...[/bold yellow]")
    console.print("This feature is coming soon! 🚀")

@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version_flag: bool = typer.Option(
        False, "--version", "-v", help="Show version information"
    ),
    help_flag: bool = typer.Option(
        False, "--help", "-h", help="Show help information"
    ),
) -> None:
    """🤖 KODER - Your AI-Powered Coding Assistant
    
    Transform your coding workflow with intelligent assistance.
    Ask questions, get code written, debug issues, and more!
    """
    if version_flag:
        version()
        raise typer.Exit()
    
    if help_flag:
        display_help()
        raise typer.Exit()
    
    # If no command is specified, start chat by default
    if ctx.invoked_subcommand is None:
        # Auto-start interactive mode if no args
        try:
            chat()
        except KeyboardInterrupt:
            console.print("\\n[bold green]👋 Goodbye![/bold green]")

if __name__ == "__main__":
    app()
