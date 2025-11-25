"""
KODER - An intelligent CLI tool for code understanding and assistance
"""

import click 
import sys
import os
import threading
from rich.console import Console
from rich.text import Text
from dotenv import load_dotenv

# Import Agent and tools
from koder.agent.agent import Agent
from koder.prompts.main_agent_prompt import system_prompt
from koder.tools.main_agent_tools_schema import tools_schema
from koder.utils.query_constructions import construct_query

load_dotenv()

console = Console()


def show_tool_executing(tool_name: str, context: str = ""):
    """Show tool is executing"""
    console.print(f"  [yellow]→[/yellow] [bold blue]{tool_name}[/bold blue][dim]{context}[/dim]", end="")

def show_tool_complete(status: str = "success", error_msg: str = None):
    """Show tool completed"""
    if status == "success":
        console.print("\r  [green]✓[/green] [bold green]completed[/bold green]")
    else:
        console.print(f"\r  [red]✗[/red] [bold red]failed[/bold red] [dim red]({error_msg})[/dim red]")


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
    """Display the minimal welcome screen"""
    console.clear()
    
    # Simple left-aligned logo display
    logo_text = Text(display_logo(), style="bold cyan")
    console.print(logo_text)
    
    # Simple left-aligned tagline
    console.print("[bold bright_white]🚀 AI-Powered Code Assistant[/bold bright_white]")
    console.print("[dim]Made for developers | Version 0.1.0[/dim]")
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
    """Display simple tool execution"""
    # Get the main argument for context (typically file_path, command, etc.)
    main_arg = ""
    if args:
        # Common argument names that provide context
        context_keys = ['file_path', 'command', 'query', 'path', 'target_file']
        for key in context_keys:
            if key in args:
                value = str(args[key])
                if len(value) > 60:
                    value = value[:57] + "..."
                main_arg = f": {value}"
                break
    
    if status == "executing":
        show_tool_executing(tool_name, main_arg)
    else:
        show_tool_complete(status, error_msg)


def display_response(content: str, tool_calls_count: int = 0):
    """Display agent response with minimal formatting"""
    if content.strip():
        # Simple response display without panels
        console.print(f"\n{content}")
    
    # Optional: Show minimal tool execution summary
    if tool_calls_count > 0:
        console.print(f"[dim]→ {tool_calls_count} tool{'s' if tool_calls_count > 1 else ''} executed[/dim]")


def interactive_mode():
    """Run interactive mode with continuous conversation"""
    console.print("[bold cyan]🎯 Interaction [/bold cyan]")
    console.print("Type your questions and I'll help you with your code!")
    console.print("[dim]Commands: 'quit', 'exit', 'q' to exit | 'clear' to clear screen[/dim]")
    console.print()
    
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
            console.print("\n[bold yellow]🔄 Processing...[/bold yellow]\n")
            ## Construct the query
            query = construct_query(user_prompt)

            
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
                    
                    # Show executing
                    display_tool_execution(tool_name, args, "executing")
                    
                    # Execute the tool
                    tool_call_response = agent._execute_tool_call(tool_call)
                    
                    # Show completion
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