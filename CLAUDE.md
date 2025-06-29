# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code), AND Gemini CLI when working with code in this repository.

## Project Overview

This is a single-file Python application (`main.py`) for printing Korean and English text to BIXOLON SRP-330II receipt printers via CUPS. The project prioritizes simplicity and Korean language support over complex architecture.

## AI Collaboration (Claude Code + Gemini)
Claude Code can collaborate with Gemini to solve complex problems through bash commands. This enables a problem-solving dialogue between the two AI assistants.
### How to Collaborate
1. **Execute Gemini commands via bash**: Use the `gemini` command in bash to interact with Gemini
2. **Pass prompts as arguments**: Provide your question or request as arguments to the gemini command
3. **Iterative problem solving**: Use the responses from Gemini to refine your approach and continue the dialogue
### Example Usage
```bash
# Ask Gemini for help with a specific problem
gemini -p "How should I optimize this Flutter widget for better performance?"
# Request code review or suggestions
gemini -p "Review this GetX controller implementation and suggest improvements"
# Collaborate on debugging
gemini -p "This error occurs when running flutter build ios. What could be the cause?"
```
### Collaboration Workflow
1. **Identify complex problems**: When encountering challenging issues, consider leveraging Gemini's perspective
2. **Formulate clear questions**: Create specific, context-rich prompts for better responses
3. **Iterate on solutions**: Use responses to refine your approach and ask follow-up questions
4. **Combine insights**: Merge insights from both Claude Code and Gemini for comprehensive solutions

## Commands

### MCP Server Mode (Recommended)
```bash
# 1. Start FastAPI backend server
python3 server.py
# or
uvicorn server:app --host 127.0.0.1 --port 8000 --reload

# 2. Configure Claude Desktop (see README.md)
# 3. Use through Claude Desktop interface
```

### Legacy CLI Mode (Backward Compatibility)
```bash
# Basic text printing
python3 main.py "출력할 텍스트"

# Print to specific printer
python3 main.py "텍스트" -p PRINTER_NAME

# Preview output without printing
python3 main.py "텍스트" --preview

# List available printers
python3 main.py --list-printers

# Check printer status
python3 main.py --status -p PRINTER_NAME
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
pytest tests/test_printer_utils.py -v
pytest --cov=. --cov-report=html

# Run FastAPI development server
python3 server.py

# Test MCP wrapper directly
python3 mcp_wrapper.py

# Check CUPS printer setup (system dependency)
lpstat -p
brew services list | grep cups  # macOS
```

## Architecture

### Hybrid Architecture (MCP + FastAPI)
- **FastAPI Backend**: Core printer logic with REST endpoints (`server.py`)
- **MCP Wrapper**: Lightweight stdio interface for Claude Desktop (`mcp_wrapper.py`)
- **Legacy CLI**: Backward compatibility with original script (`main.py`)
- **Modular Design**: Separated concerns across multiple files

### Core Components

1. **Text Processing Engine** (`printer_utils.py`):
   - Handles mixed-width characters (Korean=2, English=1)
   - Word-boundary-aware text wrapping at 40 characters
   - Accurate center alignment considering character widths

2. **ESC/POS Protocol Handler** (`printer_utils.py`):
   - Generates binary ESC/POS commands for printer control
   - Korean support via EUC-KR encoding and specific ESC commands
   - Paper cutting and text alignment commands

3. **FastAPI REST Server** (`server.py`):
   - Secure API endpoints with authentication
   - Pydantic data validation and structured receipts
   - Comprehensive error handling and troubleshooting

4. **MCP Protocol Interface** (`mcp_wrapper.py`):
   - JSON-RPC communication with Claude Desktop
   - Tool definitions for receipt printing operations
   - HTTP-to-MCP protocol translation

5. **Security & Configuration** (`config.py`, `schemas.py`):
   - API key authentication and printer whitelisting
   - Input validation and sanitization
   - Structured data models for receipts

### Data Flow
**MCP Mode (Recommended):**
1. Claude Desktop → JSON-RPC request → MCP Wrapper
2. MCP Wrapper → HTTP API request → FastAPI Server
3. FastAPI → Data validation → Printer Utils
4. ESC/POS generation → CUPS execution → Response chain

**Legacy CLI Mode:**
1. Text input → Character width calculation
2. Text wrapping and formatting → ESC/POS command generation
3. Temporary binary file creation → CUPS `lp` command execution
4. File cleanup and status reporting

## Korean Language Support

- **Character Encoding**: EUC-KR primary, UTF-8 fallback
- **ESC/POS Commands**: `\x1B\x74\x12` (codepage), `\x1C\x26` (Korean mode)
- **Width Calculation**: Korean characters count as 2 units for proper alignment

## System Requirements

- **Runtime**: Python 3.x (no external packages)
- **System Service**: CUPS installed and running
- **Hardware**: ESC/POS compatible receipt printer
- **OS**: macOS/Linux (CUPS-supported systems)

## Development Notes

- **Testing Framework**: Comprehensive pytest suite with unit, integration, and MCP tests
- **Modular Package Structure**: Organized across multiple specialized files
- **Configuration Management**: Centralized config with environment variable support
- **Security Features**: API authentication, input validation, and printer whitelisting
- **Error Handling**: Multi-layer error translation from CUPS → HTTP → MCP → User
- **File Management**: Automatic temporary file cleanup after printing

## Code Conventions

- **Korean Comments**: All code comments are in Korean
- **Mixed Language**: Korean for user-facing messages, English for technical terms
- **Print Statements**: Used for user feedback (no logging framework)
- **Exception Handling**: Broad try/catch blocks with user-friendly error messages