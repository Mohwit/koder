import json
from typing import Any, List, Dict, Optional
from openai import OpenAI


class Agent:
    def __init__(
        self, 
        model: str, 
        base_url: str, 
        api_key: str, 
        system_prompt: str, 
        temperature: float = 0.0, 
        max_tokens: int = 8096, 
        messages: Optional[List[Dict[str, Any]]] = None, 
        tools: Optional[List[Dict[str, Any]]] = None, 
        **kwargs: Any
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
        
        # Create a mapping of tool names to their callable functions
        self._tool_functions = {}
        for tool in self.tools:
            if tool.get("type") == "function":
                func_info = tool.get("function", {})
                name = func_info.get("name")
                callable_func = func_info.get("callable")
                if name and callable_func:
                    self._tool_functions[name] = callable_func

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
            return {
                "content": response.choices[0].message.content or "",
                "tool_calls": response.choices[0].message.tool_calls or None,
            }

    def _make_api_call(self):
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
                        "parameters": func_info.get("parameters", {})
                    }
                }
                clean_tools.append(clean_tool)
        
        return self._client.chat.completions.create(
            model=self.model,
            messages=self.messages,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            tools=clean_tools if clean_tools else None,
        )

    def _process_tool_calls(self, tool_calls: List[Any]) -> None:
        """
        Process multiple tool calls and add their responses to messages.
        """
        for i, tool_call in enumerate(tool_calls, 1):
            print(f"\n🛠️  Executing tool {i}/{len(tool_calls)}: {tool_call.function.name}")
            
            # Parse and display arguments
            try:
                args = json.loads(tool_call.function.arguments)
                print(f"   📋 Arguments: {args}")
            except json.JSONDecodeError:
                print(f"   ❌ Failed to parse arguments")
            
            tool_call_response = self._execute_tool_call(tool_call)
            
            # Show execution result status - check if it's an actual error message
            response_str = str(tool_call_response["tool_response"])
            if (response_str.startswith("Error:") or 
                response_str.startswith("Error executing tool") or 
                response_str.startswith("Error parsing tool arguments")):
                print(f"   ❌ Failed: {tool_call_response['tool_response']}")
            else:
                print(f"   ✅ Success")
            
            self.messages.append({
                "role": "tool",
                "tool_call_id": tool_call_response["tool_call_id"],
                "name": tool_call_response["tool_name"],
                "content": tool_call_response["tool_response"],
            })

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
            except Exception as e:
                tool_response = f"Error executing tool '{tool_name}': {str(e)}"
        
        return {
            "tool_call_id": tool_call_id,
            "tool_name": tool_name,
            "tool_args": tool_args,
            "tool_response": tool_response,
        }

    def _set_system_prompt(self, system_prompt: str) -> None:
        """
        Set the system prompt for the agent if not already set.
        """
        if not self.messages:
            self.messages.append({"role": "system", "content": system_prompt})
        elif self.messages[0].get("role") != "system":
            self.messages.insert(0, {"role": "system", "content": system_prompt})

    def add_message(self, role: str, content: str) -> None:
        """
        Add a message to the conversation history.
        """
        self.messages.append({"role": role, "content": content})
