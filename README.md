# Koder 🤖

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

**Koder** is an AI-powered coding assistant that combines the intelligence of Claude AI with advanced RAG (Retrieval-Augmented Generation) capabilities for intelligent code analysis, understanding, and assistance.

## ✨ Features

### 🤖 **AI-Powered Assistant**

- **Claude Integration**: Powered by Anthropic's Claude for intelligent code understanding
- **Interactive CLI**: Beautiful, responsive command-line interface
- **Natural Language Processing**: Communicate with your codebase in plain English

### 🔍 **Advanced Code Analysis**

- **RAG System**: Vector-based semantic code search using [CodeRAG](https://github.com/Mohwit/coderag)
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java
- **Hierarchical Understanding**: Maintains class-method relationships and code structure
- **Real-time Indexing**: Automatic re-indexing when code changes

### 🛠️ **Comprehensive Tool Suite**

- **File Operations**: Read, write, and modify files with syntax highlighting
- **Code Search**: Semantic similarity search across your entire codebase
- **Pattern Matching**: Advanced grep functionality for precise code queries
- **Shell Integration**: Safe bash command execution with output capture
- **Task Management**: Built-in todo system for complex development tasks
- **Sub-Agent Support**: Delegate complex queries to specialized sub-agents

### 📊 **Professional Development Features**

- **Comprehensive Logging**: Detailed performance monitoring and debugging
- **Error Tracking**: Automatic error capture and analysis
- **Performance Metrics**: API call durations and tool execution times
- **Log Rotation**: Automated log management with configurable retention

## 🚀 Quick Start

### Installation

#### Option 1: Direct Installation (Recommended)

```bash
# Install directly from repository
pip install git+https://github.com/Mohwit/koder.git

# Or clone and install locally
git clone https://github.com/Mohwit/koder.git
cd koder
pip install .
```

#### Option 2: Development Installation

```bash
# Clone the repository
git clone https://github.com/Mohwit/koder.git
cd koder

# Install with development dependencies
pip install .[dev]

# Or use requirements.txt for full environment
pip install -r requirements.txt
```

#### Option 3: Enhanced Installation

```bash
# Install with all optional features
pip install .[all]

# Or specific feature sets
pip install .[ml]     # Enhanced ML capabilities
pip install .[web]    # Web interface features
```

### Environment Setup

1. **Configure API Access**

   ```bash
   # Copy environment template
   cp .env.example .env

   # Edit .env file and add your API key
   echo "ANTHROPIC_API_KEY=your_api_key_here" >> .env
   ```

2. **Run Koder**

   ```bash
   # If installed via pip
   koder

   # Or run directly
   python -m koder.main
   ```

## 💻 Usage Examples

### Basic Code Analysis

```bash
🤖 Koder Agent is ready! Type 'quit' to exit.
==================================================

💬 Enter your prompt: Explain how the authentication system works

🔄 Processing...

🤖 Response:
Based on my analysis of your codebase, I found the authentication system...
```

### Advanced Code Search

```bash
💬 Enter your prompt: Find all functions that handle HTTP requests

🔄 Processing...
🛠️ Tool calls executed: 2

🤖 Response:
I found several HTTP request handlers in your codebase:
1. `handle_request()` in api/handlers.py
2. `process_http()` in server/middleware.py
...
```

### Task Management

```bash
💬 Enter your prompt: Help me refactor the user authentication module

🔄 Processing...

🤖 Response:
I'll help you refactor the authentication module. Let me break this down:

📋 Created Todo List: Authentication Refactoring
- ✅ Analyze current auth structure
- 🔄 Extract auth logic into separate service
- ⏳ Implement proper error handling
- ⏳ Add comprehensive tests
```

## 🏗️ Architecture

```
koder/
├── agent/              # Core AI agent logic
│   └── agent.py       # Main agent implementation
├── tools/             # Built-in tool suite
│   ├── read.py       # File reading operations
│   ├── write.py      # File writing operations
│   ├── modify.py     # Code modification tools
│   ├── search.py     # Semantic code search
│   ├── grep.py       # Pattern matching
│   ├── bash.py       # Shell command execution
│   ├── todo.py       # Task management
│   └── sub_agent.py  # Sub-agent delegation
├── prompts/           # System prompts and configurations
├── utils/             # Utilities and helpers
│   ├── inialize_code_rag.py  # RAG system setup
│   └── query_constructions.py # Query processing
├── cli.py            # Command-line interface
├── main.py           # Entry point
└── vector_db/        # ChromaDB vector storage
```

## 🔧 Available Tools

### File Operations

- **`read_code_file`**: Read files with optional line range selection
- **`create_code_file`**: Create new files with proper formatting
- **`modify_code_file`**: Edit existing files with syntax highlighting

### Code Analysis

- **`search_similar_code`**: Semantic search across the codebase
- **`grep_search`**: Pattern-based code search with regex support

### System Integration

- **`execute_bash_command`**: Safe shell command execution
- **`sub_agent`**: Delegate complex queries to specialized agents

### Task Management

- **`create_todo_list`**: Break down complex tasks
- **`update_todo_list`**: Track progress and update status

## 📊 Monitoring & Logging

### Log Configuration

```bash
# Set log level
export KODER_LOG_LEVEL=DEBUG  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

### Log Files

- **`logs/koder.log`**: Main application log
- **`logs/koder_errors.log`**: Errors and warnings only
- **`logs/tools.log`**: Tool execution details

### Monitor Logs

```bash
# Follow main log
tail -f logs/koder.log

# Monitor errors only
tail -f logs/koder_errors.log

# Watch tool executions
tail -f logs/tools.log
```

### Performance Tracking

The logging system automatically tracks:

- API call durations and costs
- Tool execution times
- File operation performance
- RAG indexing and search metrics
- Memory usage and optimization opportunities

## 🎯 Advanced Features

### RAG System

Powered by [CodeRAG](https://github.com/Mohwit/coderag), the system provides:

- **Intelligent Code Parsing**: Uses tree-sitter for accurate syntax analysis
- **Hierarchical Chunking**: Preserves class-method relationships
- **Semantic Embeddings**: Advanced vector representations of code
- **Real-time Updates**: Automatic re-indexing on file changes

### Multi-Language Support

- **Python**: Full AST analysis and intelligent chunking
- **JavaScript/TypeScript**: Modern JS features and TypeScript support
- **Java**: Object-oriented structure preservation
- **Extensible**: Easy to add support for additional languages

### Task Management System

- **Persistent Todos**: Stored in `.todos/` directory
- **Progress Tracking**: Visual status indicators
- **Session Persistence**: Todo lists survive between sessions
- **Complex Task Breakdown**: Automatic decomposition of large tasks

## 🛠️ Development

### Development Setup

```bash
# Clone repository
git clone https://github.com/Mohwit/koder.git
cd koder

# Install development dependencies
pip install .[dev]

# Install pre-commit hooks (optional)
pre-commit install
```

### Code Quality Tools

```bash
# Format code
black koder/

# Lint code
ruff check koder/

# Type checking
mypy koder/
```

### Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=koder tests/
```

## 📝 Configuration

### Environment Variables

- **`ANTHROPIC_API_KEY`**: Required for Claude AI integration
- **`KODER_LOG_LEVEL`**: Set logging verbosity (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **`CODE_REPO_PATH`**: Override default repository path (defaults to current directory)

### Optional Dependencies

```bash
# Development tools
pip install .[dev]     # black, ruff, mypy, build tools

# Enhanced ML features
pip install .[ml]      # torch, transformers, numpy, scikit-learn

# Web interface capabilities
pip install .[web]     # fastapi, uvicorn

# All features
pip install .[all]     # Everything above
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

1. **Fork the Repository**
2. **Create a Feature Branch**: `git checkout -b feature/amazing-feature`
3. **Commit Changes**: `git commit -m 'Add amazing feature'`
4. **Push to Branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **[Anthropic](https://www.anthropic.com/)** for the Claude AI model
- **[CodeRAG](https://github.com/Mohwit/coderag)** for the RAG infrastructure
- **[ChromaDB](https://www.trychroma.com/)** for vector storage
- **[Rich](https://github.com/Textualize/rich)** for beautiful terminal output

## 📞 Support

- **Documentation**: [GitHub Wiki](https://github.com/Mohwit/koder/wiki)
- **Issues**: [GitHub Issues](https://github.com/Mohwit/koder/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Mohwit/koder/discussions)

---

**Made with ❤️ by developers, for developers**
