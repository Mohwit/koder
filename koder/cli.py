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
from koder.prompts.main_agent_prompt import system_prompt
from koder.tools.main_agent_tools_schema import tools_schema
from koder.utils.query_constructions import construct_query

load_dotenv()

console = Console()


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
    footer = Text("Made for developers | Version 0.1.0", style="italic")
    console.print(Align.center(footer), style="blue")
    console.print()
    
def create_agent():
    """Create and return an Agent instance"""
    try:
        agent = Agent(
            model="claude-sonnet-4-20250514", 
            base_url="https://api.anthropic.com/v1", 
            api_key=os.getenv("ANTHROPIC_API_KEY"), 
            system_prompt=system_prompt, 
            tools=tools_schema
        )
        return agent
    except Exception as e:
        console.print(f"[red]❌ Error creating agent: {str(e)}[/red]")
        return None
    
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
            ## Construct the query
            query = construct_query(user_prompt)
            console.print(f"[bold yellow]🔍 Query:[/bold yellow] {user_prompt}")
            
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
                    
                    # Execute the tool
                    tool_call_response = agent._execute_tool_call(tool_call)
                    
                    # Execute the tool
                    tool_call_response = agent._execute_tool_call(tool_call)
                    
                    response_str = str(tool_call_response["tool_response"])
                    if (response_str.startswith("Error:") or 
                        response_str.startswith("Error executing tool") or 
                        response_str.startswith("Error parsing tool arguments")):
                        display_tool_execution(tool_name, args, "error", response_str)
                    
                    else:
                        display_tool_execution(tool_name, args, "success")
                    
                    # Add to messages
                    agent.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call_response["tool_call_id"],
                        "name": tool_call_response["tool_name"],
                        "content": tool_call_response["tool_response"],
                    })
                
            # Temporarily replace the method
            agent._process_tool_calls = enhanced_process_tool_calls
            
            ## Get the response from the agent
            response = agent.query(query)
            
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