from koder.agent.agent import Agent
from dotenv import load_dotenv
from koder.prompts.system_prompt import system_prompt
from koder.tools.write import create_code_file
from koder.tools.modify import modify_code_file
from koder.tools.read import read_code_file
from koder.tools.grep import grep_search
from koder.tools.bash import execute_bash_command
import os

load_dotenv()

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


def main():
    # Create the agent with proper configuration
    agent = Agent(
        model="claude-3-5-sonnet-20241022", 
        base_url="https://api.anthropic.com/v1", 
        api_key=os.getenv("ANTHROPIC_API_KEY"), 
        system_prompt=system_prompt, 
        tools=tools
    )
    
    print("🤖 Koder Agent is ready! Type 'quit' to exit.")
    print("=" * 50)
    
    while True:
        try:
            user_prompt = input("\n💬 Enter your prompt: ")
            
            if user_prompt.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
                
            if not user_prompt.strip():
                continue
                
            print("\n🔄 Processing...")
            response = agent.query(user_prompt)
            
            print(f"\n🤖 Response:")
            print("-" * 30)
            print(response["content"])
            
            if response["tool_calls"]:
                print(f"\n🛠️  Tool calls executed: {len(response['tool_calls'])}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            print("Please try again.")


if __name__ == "__main__":
    main()