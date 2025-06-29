# Enhanced MCP Receipt Printer Server - Detailed Implementation Plan

## Architecture Decision: Hybrid Approach ✅
Based on Gemini's analysis, we'll implement a **hybrid architecture**:
- **FastAPI Backend**: Core printer logic with REST endpoints  
- **MCP Wrapper**: Lightweight stdio interface for Claude Desktop

This provides maximum reusability, easier testing, and cleaner separation of concerns.

## Phase 1: Project Restructuring & FastAPI Backend

### 1.1 Create New Project Structure
```
/receipt-printer/
├── main.py                 # (existing, rename to printer_utils.py)
├── requirements.txt        # Add: fastapi, uvicorn, mcp
├── config.py              # Security config (API keys, allowed printers)
├── schemas.py             # Pydantic models for API validation
├── server.py              # FastAPI backend implementation
├── mcp_wrapper.py         # MCP stdio interface wrapper
└── tests/                 # Test suite
    ├── test_printer_utils.py
    ├── test_api.py
    └── test_mcp_integration.py
```

### 1.2 FastAPI Backend Implementation
**Core endpoints** with Gemini's security recommendations:
- `GET /printers` - List whitelisted printers only
- `GET /printers/{name}/status` - Check printer status
- `POST /printers/{name}/print` - Print with structured content

**Security features**:
- API key authentication via `X-API-Key` header
- Printer whitelist in config.py (`ALLOWED_PRINTERS`)
- Input sanitization using Pydantic schemas
- `shlex.quote()` for shell command safety

### 1.3 Enhanced Tool Interface Design
Replace simple text input with structured `ReceiptContent`:
```python
class ReceiptContent(BaseModel):
    header: Optional[str] = None        # Centered header text
    items: List[ReceiptItem] = []       # Structured line items
    footer: Optional[str] = None        # Centered footer text
    text: Optional[str] = None          # Simple text fallback
```

## Phase 2: MCP Protocol Integration

### 2.1 MCP Wrapper Implementation
**Tools exposed to Claude Desktop**:
1. `print_receipt(printer_name, content)` - Main printing tool
2. `list_printers()` - Discovery tool  
3. `get_printer_status(printer_name)` - Status checking
4. `preview_receipt(content)` - Preview without printing

**JSON-RPC to HTTP translation**:
- MCP tool calls → HTTP requests to localhost FastAPI
- HTTP responses → JSON-RPC responses to Claude Desktop
- Error handling: HTTP status codes → MCP error format

### 2.2 Error Handling Strategy
**Multi-layer error translation**:
1. **CUPS/Hardware errors** → HTTP status codes (FastAPI)
2. **HTTP errors** → JSON-RPC errors (MCP wrapper)
3. **User-friendly messages** for common issues:
   - Printer offline → `503 Service Unavailable`
   - Out of paper → `503` with specific message
   - CUPS not running → `500 Internal Server Error`

## Phase 3: Security & Configuration

### 3.1 Security Implementation
- **Authentication**: Mandatory API key between MCP wrapper and FastAPI
- **Authorization**: Whitelist approved printers only
- **Input Validation**: Strict Pydantic schemas for all data
- **Command Injection Prevention**: `shlex.quote()` for shell commands
- **Principle of Least Privilege**: Run as non-privileged user

### 3.2 Claude Desktop Configuration
Update `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "receipt-printer": {
      "command": "python3",
      "args": ["/path/to/receipt-printer/mcp_wrapper.py"],
      "env": {
        "PRINTER_API_URL": "http://127.0.0.1:8000",
        "API_KEY": "generated-secure-key"
      }
    }
  }
}
```

## Phase 4: Testing Strategy

### 4.1 Multi-Layer Testing Approach
1. **Unit Tests** (`pytest`):
   - Test core printer utilities (text processing, ESC/POS generation)
   - Test FastAPI endpoints with `TestClient`
   - Mock subprocess calls for printer simulation

2. **Integration Tests**:
   - FastAPI backend with real HTTP requests
   - MCP wrapper with mocked HTTP responses
   - Virtual CUPS printer for end-to-end testing

3. **Manual Testing**:
   - Real printer output verification
   - Claude Desktop integration testing

## Phase 5: Documentation & Deployment

### 5.1 Documentation Updates
- Update CLAUDE.md with MCP server usage
- Create setup guide for Claude Desktop configuration  
- Document API endpoints and tool parameters
- Add troubleshooting guide for common issues

### 5.2 Korean Language Preservation
- Maintain all existing Korean text processing (`main.py:12-84`)
- Preserve EUC-KR encoding and ESC/POS commands (`main.py:86-120`)
- Keep Korean user messages in FastAPI responses

## Implementation Order
1. **Refactor existing code** → `printer_utils.py`
2. **Build FastAPI backend** with security features
3. **Create MCP wrapper** with JSON-RPC handling
4. **Configure Claude Desktop** for MCP integration
5. **Implement comprehensive testing**
6. **Create documentation** and setup guides

This hybrid approach provides immediate Claude Desktop integration while building a reusable, secure, and well-tested foundation for future enhancements.

## Collaboration Notes
- Plan developed through collaboration between Claude Code and Gemini CLI
- Architecture recommendations based on MCP protocol requirements and security best practices
- Gemini provided crucial clarification on MCP vs REST API approaches
- Focus on maintaining existing Korean language support while adding modern API architecture