# KODER CLI Usage Guide

## Installation

To install the Koder CLI, run the following command in your project directory:

```bash
pip install -e .
```

This will install Koder in development mode and make the `koder` command available globally.

## Configuration

Before using Koder, you need to set up your Anthropic API key:

1. Create a `.env` file in your project root (if not already present)
2. Add your API key:
   ```
   ANTHROPIC_API_KEY=your_api_key_here
   ```

Alternatively, you can export it as an environment variable:

```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

## Usage

### Start Interactive Chat (Default)

```bash
koder
# or
koder chat
```

### Available Commands

```bash
koder analyze      # Analyze the current codebase (coming soon)
koder fix          # Fix detected issues in the codebase (coming soon)
koder refactor     # Refactor code with AI suggestions (coming soon)
koder config       # Show current configuration
koder version      # Show version information
koder --help       # Show help information
```

## Interactive Commands

Once in the interactive chat mode, you can use these special commands:

- `help` - Show usage tips and available commands
- `config` - Display current configuration
- `rag-status` - Show RAG system status and history
- `clear` - Clear the screen and show welcome message
- `enable-enhanced-tools` - Re-enable enhanced tool display if disabled
- `quit`, `exit`, or `q` - Exit the application

## Features

🎨 **Beautiful Interface**: Modern CLI with stunning ASCII art and rich formatting
🛠️ **Enhanced Tool Execution**: Beautiful tool execution panels with status indicators
🔄 **Smart Processing**: Real-time spinners and progress indicators
📝 **Markdown Support**: Formatted responses with syntax highlighting
⚡ **Fast Setup**: Quick initialization and background RAG processing
🔧 **Configuration**: Easy configuration management and validation
🎯 **Interactive Tools**: Special handling for interactive tools like file modifications
🚀 **Error Recovery**: Graceful fallback when enhanced features encounter issues

## Enhanced Tool Display

Koder provides beautiful visualization for tool execution:

### Non-Interactive Tools

```
┌─ 🛠️ Tool Execution ──────────────────────┐
│ Tool      │ read_code_file               │
│ Status    │ 🔄 Executing                │
│ File_path │ src/main.py                  │
└──────────────────────────────────────────┘

┌─ 🛠️ Tool Execution ──────────────────────┐
│ Tool   │ read_code_file                  │
│ Status │ ✅ Success                      │
└──────────────────────────────────────────┘
```

### Interactive Tools

For tools that require user interaction (like file modifications), Koder provides special handling with diff previews and confirmation prompts.

## Examples

### Asking Questions

```
💬 You: How can I optimize this Python function for better performance?
```

### Code Generation

```
💬 You: Create a REST API endpoint for user authentication using FastAPI
```

### Code Review

```
💬 You: Review this code and suggest improvements for readability
```

### Debugging

```
💬 You: Find the bug in this function and explain how to fix it
```

### File Operations

```
💬 You: Read the main.py file and explain what it does
💬 You: Create a new Python class for user management
💬 You: Modify the authentication function to use JWT tokens
```

## Pro Tips

💡 **Natural Language**: Use natural language to describe what you want
🎯 **Be Specific**: Mention programming languages and frameworks when relevant  
📚 **Ask for Explanations**: Request explanations when you need to understand code
🔄 **Request Refactoring**: Ask for suggestions to improve existing code
🔍 **Use RAG System**: Ask questions about your codebase - Koder indexes your files
⚠️ **Error Recovery**: If enhanced tools fail, they'll automatically disable and can be re-enabled

## Troubleshooting

- **Enhanced tools disabled?** Use `enable-enhanced-tools` to re-enable them
- **RAG not working?** Check `rag-status` to see initialization progress
- **API errors?** Verify your `ANTHROPIC_API_KEY` with `config` command
- **Need help?** Use `help` command for quick reference

Happy coding with KODER! 🚀✨
