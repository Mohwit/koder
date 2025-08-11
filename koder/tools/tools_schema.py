"""Tools schema for the Koder agent."""

from koder.tools.bash import execute_bash_command
from koder.tools.grep import grep_search
from koder.tools.modify import modify_code_file
from koder.tools.read import read_code_file
from koder.tools.search import search_similar_code
from koder.tools.write import create_code_file
from koder.tools.sub_agent import sub_agent
from koder.tools.todo import (
    create_todo_list,
    update_todo_list,
)

tools_schema = [
    {
        "type": "function",
        "function": {
            "name": "read_code_file",
            "description": (
                "Read and retrieve code content from a file. "
                "Can read either the entire file or a specific range of lines. "
                "Useful for inspecting existing code, understanding context, "
                "or verifying file contents. Returns the file content as a string."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "The path to the file to be read",
                    },
                    "start_line": {
                        "type": "integer",
                        "description": "Optional starting line number to read from "
                        "(1-based indexing)",
                    },
                    "end_line": {
                        "type": "integer",
                        "description": "Optional ending line number to read until "
                        "(1-based indexing)",
                    },
                },
                "required": ["file_path"],
            },
            "callable": read_code_file,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "modify_code_file",
            "description": (
                "Makes multiple changes to a single file in one operation. "
                "Use this tool to edit files by providing the exact text to replace "
                "and the new text."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": "Absolute path to the file to modify",
                    },
                    "edits": {
                        "type": "array",
                        "description": (
                            "Array of edit operations, each containing old_string "
                            "and new_string"
                        ),
                        "items": {
                            "type": "object",
                            "properties": {
                                "old_string": {
                                    "type": "string",
                                    "description": "Exact text to replace",
                                },
                                "new_string": {
                                    "type": "string",
                                    "description": "The replacement text",
                                },
                            },
                            "required": ["old_string", "new_string"],
                        },
                    },
                },
                "required": ["file_path", "edits"],
            },
            "callable": modify_code_file,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_code_file",
            "description": (
                "Create a new file or overwrite an existing one with provided code. "
                "This tool handles file creation, directory validation, and writes "
                "the specified content. Useful for generating new source files, "
                "configuration files, or documentation. Returns the path of the "
                "created file."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {
                        "type": "string",
                        "description": (
                            "The full path (including filename) where the file "
                            "should be created"
                        ),
                    },
                    "code": {
                        "type": "string",
                        "description": "The code (or text) to write into the file",
                    },
                },
                "required": ["file_path", "code"],
            },
            "callable": create_code_file,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "grep_search",
            "description": (
                "Search for patterns in files using grep-like functionality. "
                "Can search in specific files or across directories with various "
                "options including regex support, case sensitivity, and recursive "
                "search. Returns matches with line numbers and file paths."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "pattern": {
                        "type": "string",
                        "description": "The search pattern (regex supported)",
                    },
                    "file_path": {
                        "type": "string",
                        "description": "Optional specific file to search in",
                    },
                    "directory": {
                        "type": "string",
                        "description": (
                            "Optional directory to search in (if file_path not "
                            "provided)"
                        ),
                    },
                    "recursive": {
                        "type": "boolean",
                        "description": (
                            "Whether to search recursively in subdirectories "
                            "(default: false)"
                        ),
                    },
                    "case_sensitive": {
                        "type": "boolean",
                        "description": (
                            "Whether search should be case sensitive (default: true)"
                        ),
                    },
                    "line_numbers": {
                        "type": "boolean",
                        "description": (
                            "Whether to include line numbers in results "
                            "(default: true)"
                        ),
                    },
                    "max_results": {
                        "type": "integer",
                        "description": (
                            "Maximum number of results to return (default: 100)"
                        ),
                    },
                },
                "required": ["pattern"],
            },
            "callable": grep_search,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "execute_bash_command",
            "description": (
                "Execute a bash command safely and return the result. Includes basic "
                "security checks to prevent dangerous operations. Returns command "
                "output, exit code, and execution details. Useful for running shell "
                "commands, checking system status, or performing file operations."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The bash command to execute",
                    },
                    "working_directory": {
                        "type": "string",
                        "description": (
                            "Optional directory to run command in "
                            "(defaults to CODE_REPO_PATH)"
                        ),
                    },
                    "timeout": {
                        "type": "integer",
                        "description": (
                            "Timeout in seconds for command execution " "(default: 30)"
                        ),
                    },
                    "capture_output": {
                        "type": "boolean",
                        "description": (
                            "Whether to capture and return command output "
                            "(default: true)"
                        ),
                    },
                },
                "required": ["command"],
            },
            "callable": execute_bash_command,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_similar_code",
            "description": (
                "Search for similar code in the codebase. Returns the results of "
                "the search."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for",
                    },
                },
                "required": ["query"],
            },
            "callable": search_similar_code,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sub_agent",
            "description": ("Use this tool to call a sub agent to answer the query."),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for",
                    },
                },
                "required": ["query"],
            },
            "callable": sub_agent,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "create_todo_list",
            "description": ("Use this tool to create a todo list at the start of a complex task."),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "High-level task name or description"
                    },
                    "list_of_items": {
                        "type": "array",
                        "description": "List of todo items to create",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Todo item title"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                    "description": "Initial status. If omitted or invalid, defaults to 'pending'."
                                }
                            },
                            "required": ["name", "status"]
                        }
                    }
                },
                "required": ["task_description", "list_of_items"],
            },
            "callable": create_todo_list,
        },
    },
    {
        "type": "function",
        "function": {
            "name": "update_todo_list",
            "description": ("Use this tool to update the state of a todo items as you complete tasks and get state of the todo list."),
            "parameters": {
                "type": "object",
                "properties": {
                    "task_description": {
                        "type": "string",
                        "description": "High-level task name or description"
                    },
                    "list_of_items": {
                        "type": "array",
                        "description": "List of todo items to set/update",
                        "items": {
                            "type": "object",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "Todo item title"
                                },
                                "status": {
                                    "type": "string",
                                    "enum": ["pending", "in_progress", "completed"],
                                    "description": "Desired status for the item"
                                }
                            },
                            "required": ["name", "status"]
                        }
                    }
                },
                "required": ["task_description", "list_of_items"],
            },
            "callable": update_todo_list,
        },
    },

]
