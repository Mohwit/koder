"""Agent module for handling OpenAI API interactions with tool calling support."""

import json
import os
from typing import Any, List, Dict, Optional, Union
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from openai._types import NOT_GIVEN
from rich.console import Console

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


# Agent class
class Agent:
    """OpenAI API client with tool calling and conversation management."""

    def __init__(
        self,
        model: str,
        api_key: str,
        system_prompt: str,
        base_url: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 8096,
        messages: Optional[
            List[Union[Dict[str, Any], ChatCompletionMessageParam]]
        ] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.messages = messages or []
        self.tools = tools or []
        self.kwargs = kwargs
        self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        self.current_todo_state = None  # Track current todo list
        self.todo_displayed = False  # Track if static todo is displayed
        self.todo_lines_count = 0  # Track number of lines in todo display

        # Create a mapping of tool names to their callable functions
        self._tool_functions = {}
        for tool in self.tools:
            if tool.get("type") == "function":
                func_info = tool.get("function", {})
                name = func_info.get("name")
                callable_func = func_info.get("callable")
                if name and callable_func:
                    self._tool_functions[name] = callable_func

    def _display_todo_list(self):
        """Display current todo list in a clean table format with colors."""
        if not self.current_todo_state:
            return
        
        items = self.current_todo_state.get("items", [])
        
        if not items:
            return  # Don't show anything if no tasks exist
        
        task_desc = self.current_todo_state.get("task_description", "Tasks")
        
        console.print(f"\n┌─ 📋 {task_desc}")
        console.print("│")
        
        for item in items:
            name = item.get("name", "")
            status = item.get("status", "pending")
            
            if status == "completed":
                bullet = "●"  # solid circle for completed
                # Strike through completed tasks
                console.print(f"│  [dim]{bullet} [strikethrough]{name}[/strikethrough][/dim]")
            elif status == "in_progress":
                bullet = "◐"  # half-filled circle for in-progress
                # Green color for current task
                console.print(f"│  [green]{bullet} {name}[/green]")
            else:
                bullet = "○"  # hollow circle for pending
                # Normal display for pending tasks
                console.print(f"│  {bullet} {name}")
        
        console.print("└" + "─" * (len(task_desc) + 5))

    # Query the agent with the provided user prompt.
    # Continues conversation until final response is received.
    def query(self, user_prompt: str) -> Dict[str, Any]:
        """
        Query the agent with the provided user prompt.
        Continues conversation until final response is received.
        """
        self._set_system_prompt(self.system_prompt)
        self.messages.append({"role": "user", "content": user_prompt})

        # Continue conversation loop until we get a final response
        while True:
            response = self._make_api_call()
            self.messages.append(response.choices[0].message.model_dump())

            # If there are tool calls, process them and continue
            if response.choices[0].message.tool_calls:
                self._process_tool_calls(response.choices[0].message.tool_calls)
                continue

            # If no tool calls, this is the final response
            final_response = {
                "content": response.choices[0].message.content or "",
                "tool_calls": response.choices[0].message.tool_calls or None,
            }
            
            # Display todo list at the end if it exists
            if self.current_todo_state:
                self._display_todo_list()
            
            return final_response

    # Make an API call to the OpenAI client.
    def _make_api_call(self) -> Any:
        """
        Make an API call to the OpenAI client.
        """
        # Create clean tool definitions without callable functions for API
        clean_tools = []
        for tool in self.tools:
            if tool.get("type") == "function":
                func_info = tool.get("function", {})
                clean_tool = {
                    "type": "function",
                    "function": {
                        "name": func_info.get("name"),
                        "description": func_info.get("description", ""),
                        "parameters": func_info.get("parameters", {}),
                    },
                }
                clean_tools.append(clean_tool)

        return self._client.chat.completions.create(
            model=self.model,
            messages=self.messages,  # type: ignore
            temperature=self.temperature,
            max_completion_tokens=self.max_tokens,
            tools=clean_tools if clean_tools else NOT_GIVEN,
        )

    # Process multiple tool calls and add their responses to messages.
    def _process_tool_calls(self, tool_calls: List[Any]) -> None:
        """
        Process multiple tool calls and add their responses to messages.
        """
        for i, tool_call in enumerate(tool_calls, 1):
            # Parse arguments first
            try:
                args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError:
                args = {}

            # Get the main argument for context
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

            # Show executing
            show_tool_executing(tool_call.function.name, main_arg)

            # Execute the tool
            tool_call_response = self._execute_tool_call(tool_call)

            # Show completion
            response_str = str(tool_call_response["tool_response"])
            if (
                response_str.startswith("Error:")
                or response_str.startswith("Error executing tool")
                or response_str.startswith("Error parsing tool arguments")
            ):
                show_tool_complete("error", tool_call_response['tool_response'])
            else:
                show_tool_complete("success")

            # Update and display todo state if this was a todo tool
            if tool_call.function.name in ["create_todo_list", "update_todo_list"]:
                if isinstance(tool_call_response["tool_response"], dict):
                    new_state = tool_call_response["tool_response"]
                    
                    if tool_call.function.name == "create_todo_list":
                        # For create, replace completely
                        self.current_todo_state = new_state
                    else:
                        # For update, merge with existing state
                        if self.current_todo_state:
                            # Update task description
                            self.current_todo_state["task_description"] = new_state.get("task_description", self.current_todo_state.get("task_description", ""))
                            
                            # Merge items - update existing items or add new ones
                            existing_items = {item["name"]: item for item in self.current_todo_state.get("items", [])}
                            
                            for new_item in new_state.get("items", []):
                                existing_items[new_item["name"]] = new_item
                            
                            self.current_todo_state["items"] = list(existing_items.values())
                        else:
                            self.current_todo_state = new_state
                    
                    # Display the updated todo list immediately
                    self._display_todo_list()

            # Ensure tool response is a string for OpenAI API compatibility
            tool_response_content = tool_call_response["tool_response"]
            if not isinstance(tool_response_content, str):
                tool_response_content = json.dumps(tool_response_content, indent=2)
            
            self.messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call_response["tool_call_id"],
                    "name": tool_call_response["tool_name"],
                    "content": tool_response_content,
                }
            )

    # Execute a single tool call and return the response.
    def _execute_tool_call(self, tool_call: Any) -> Dict[str, Any]:
        """
        Execute a single tool call and return the response.
        """
        tool_call_id = tool_call.id
        tool_name = tool_call.function.name

        try:
            tool_args = json.loads(tool_call.function.arguments)
        except json.JSONDecodeError as e:
            return {
                "tool_call_id": tool_call_id,
                "tool_name": tool_name,
                "tool_args": {},
                "tool_response": f"Error parsing tool arguments: {str(e)}",
            }

        # Get the tool function from our mapping
        tool_function = self._tool_functions.get(tool_name)

        if tool_function is None:
            tool_response = f"Error: Tool '{tool_name}' not found"
        else:
            try:
                tool_response = tool_function(**tool_args)
            except (TypeError, ValueError, AttributeError, RuntimeError) as e:
                tool_response = f"Error executing tool '{tool_name}': {str(e)}"

        return {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_response": tool_response,
        }

    # Set the system prompt for the agent if not already set.
    def _set_system_prompt(self, system_prompt: str) -> None:
        """
        Set the system prompt for the agent if not already set.
        """
        if not self.messages:
            self.messages.append({"role": "system", "content": system_prompt})
        elif self.messages[0].get("role") != "system":
            self.messages.insert(0, {"role": "system", "content": system_prompt})