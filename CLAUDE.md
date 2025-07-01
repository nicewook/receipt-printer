# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code), AND Gemini CLI when working with code in this repository.

## Project Overview

This is a simplified Python application for printing Korean and English text (200 characters max) to BIXOLON SRP-330II receipt printers via CUPS. The project features a direct MCP interface that calls printer utilities without HTTP server dependencies, prioritizing simplicity and Korean language support.

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
# 1. Configure Claude Desktop (see README.md)
# 2. Use through Claude Desktop interface
# Example: "> 우유 사오기" or "프린터 상태 확인해줘"
```

### MCP Tools Available
```bash
# Available tools in Claude Desktop:
# 1. print_receipt - 간단한 메모, 할일 목록 출력 (200자 이내)
# 2. list_printers - 사용 가능한 프린터 목록 조회
# 3. get_printer_status - 특정 프린터의 상태 확인

# Trigger patterns for Claude Desktop:
# "> 우유 사오기" - 직접 텍스트 출력
# "프린터 목록 보여줘" - 프린터 목록 조회
# "프린터 상태 확인" - 상태 체크
```

### Legacy CLI Mode (Backward Compatibility)
```bash
# Basic text printing
python3 printer.py "출력할 텍스트"

# Print to specific printer
python3 printer.py "텍스트" -p PRINTER_NAME

# Preview output without printing
python3 printer.py "텍스트" --preview

# List available printers
python3 printer.py --list-printers

# Check printer status
python3 printer.py --status -p PRINTER_NAME
```

### Development Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest
pytest tests/test_printer.py -v
pytest --cov=. --cov-report=html

# Test MCP wrapper directly
python3 mcp_wrapper.py

# Example MCP commands
echo '{"method":"tools/list","id":1}' | python3 mcp_wrapper.py
echo '{"method":"tools/call","id":2,"params":{"name":"print_receipt","arguments":{"text":"테스트","preview":true}}}' | python3 mcp_wrapper.py
echo '{"method":"tools/call","id":3,"params":{"name":"list_printers","arguments":{}}}' | python3 mcp_wrapper.py

# Check CUPS printer setup (system dependency)
lpstat -p
brew services list | grep cups  # macOS
```

## Architecture

### Direct Architecture (MCP → Printer Utils)
- **MCP Wrapper**: Direct stdio interface for Claude Desktop (`mcp_wrapper.py`)
- **Printer Utils**: Core printer logic with ESC/POS commands (`printer.py`)
- **Direct CLI**: CLI interface built into printer module (`printer.py`)
- **Simplified Design**: Minimal layers for maximum performance

### Core Components

1. **Text Processing Engine** (`printer.py`):
   - Handles mixed-width characters (Korean=2, English=1)
   - Word-boundary-aware text wrapping at 40 characters
   - Accurate center alignment considering character widths

2. **ESC/POS Protocol Handler** (`printer.py`):
   - Generates binary ESC/POS commands for printer control
   - Korean support via EUC-KR encoding and specific ESC commands
   - Paper cutting and text alignment commands

3. **MCP Protocol Interface** (`mcp_wrapper.py`):
   - JSON-RPC communication with Claude Desktop
   - Direct tool calls to printer utilities
   - Simple text validation (200 characters max)
   - ThreadPoolExecutor for async/sync bridge

### Data Flow
**MCP Mode (Recommended):**
1. Claude Desktop → JSON-RPC request → MCP Wrapper
2. MCP Wrapper → Direct function call → Printer Utils
3. ESC/POS generation → CUPS execution → Response

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

- **Runtime**: Python 3.x (minimal dependencies)
- **System Service**: CUPS installed and running
- **Hardware**: ESC/POS compatible receipt printer
- **OS**: macOS/Linux (CUPS-supported systems)
- **Text Limit**: 200 characters maximum per print job

## Development Notes

- **Testing Framework**: Comprehensive pytest suite with unit, integration, and MCP tests
- **Simplified Architecture**: Direct function calls without HTTP middleware
- **Text Validation**: 200-character limit with Korean/English mixed-width support
- **Error Handling**: Direct error translation from CUPS → MCP → User
- **File Management**: Automatic temporary file cleanup after printing
- **Async Bridge**: ThreadPoolExecutor for sync/async function calls

## Code Conventions

- **Korean Comments**: All code comments are in Korean
- **Mixed Language**: Korean for user-facing messages, English for technical terms
- **Print Statements**: Used for user feedback (no logging framework)
- **Exception Handling**: Broad try/catch blocks with user-friendly error messages

## Documentation Standards

For markdown files in the `/docs` directory, refer to `docs/CLAUDE.md` for specific formatting and header requirements. This ensures consistency with Cursor IDE rules and proper integration with the documentation portal.