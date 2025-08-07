# Koder Agent

A powerful coding agent system with Claude integration, tool calling capabilities, and RAG (Retrieval-Augmented Generation) for code analysis.

## Features

- 🤖 **AI-Powered Coding Agent**: Interactive CLI with Claude integration
- 🛠️ **Tool Execution**: Built-in tools for file operations, bash commands, and code search
- 🔍 **RAG System**: Vector-based code search and analysis using the coderag library
- 📊 **Comprehensive Logging**: Detailed logging system for debugging and monitoring
- 🔄 **Real-time File Watching**: Automatic re-indexing when code changes

## Setup

1. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**

   ```bash
   cp .env.example .env
   # Edit .env and add your ANTHROPIC_API_KEY
   ```

3. **Run the Agent**
   ```bash
   python -m koder.main
   ```

## Logging

The application includes comprehensive logging capabilities:

### Log Levels

- `DEBUG`: Detailed debugging information
- `INFO`: General application flow (default)
- `WARNING`: Warning messages and potential issues
- `ERROR`: Error conditions
- `CRITICAL`: Critical errors that may stop the application

### Configuration

Set logging level via environment variable:

```bash
export KODER_LOG_LEVEL=DEBUG
```

### Log Files

Logs are automatically saved to the `./logs/` directory:

- `koder.log`: Main application log
- `koder_errors.log`: Errors and warnings only
- `tools.log`: Tool execution details

### Log Rotation

Log files automatically rotate when they reach 10MB, keeping 5 backup files.

### Performance Monitoring

The logging system tracks:

- API call durations
- Tool execution times
- File operation performance
- RAG indexing and search metrics

## Tools

The agent has access to several built-in tools:

- **File Operations**: Read, write, and modify files
- **Bash Execution**: Run shell commands safely
- **Code Search**: Vector-based similarity search
- **Grep Search**: Pattern matching in files
- **Todo Tool**: Task management and tracking

All tool executions are logged with performance metrics and error tracking.

### Task Management

The `.todos` directory stores task lists created by the todo tool, allowing for:
- Breaking down complex tasks into manageable steps
- Tracking progress on implementation tasks
- Persisting todo lists between sessions

## Architecture

```
koder/
├── agent/          # Core agent logic
├── tools/          # Built-in tools
├── prompts/        # System prompts
├── utils/          # Utilities (logging, RAG)
├── vector_db/      # ChromaDB vector storage
├── .todos/         # Task management storage
└── main.py         # CLI entry point
```

### Vector Database

The `vector_db` directory contains the ChromaDB vector storage used for code embeddings and semantic search. This enables:

- Fast similarity search across the codebase
- Persistent storage of code embeddings
- Efficient retrieval for the RAG system

### Real-time Indexing

The system includes file watching capabilities that:

- Monitor the codebase for changes in real-time
- Automatically re-index modified files
- Update the vector database with new code embeddings
- Ensure search results always reflect the current state of the codebase

## Monitoring

Monitor your Koder Agent with:

```bash
# Follow main log
tail -f logs/koder.log

# Monitor errors only
tail -f logs/koder_errors.log

# Watch tool executions
tail -f logs/tools.log
```

## Development

To debug issues:

1. Set log level to DEBUG:

   ```bash
   export KODER_LOG_LEVEL=DEBUG
   ```

2. Check logs for detailed execution traces
3. Use performance metrics to identify bottlenecks

## License

See LICENSE file for details.
