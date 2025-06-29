#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 래퍼
Claude Desktop과 FastAPI 서버 간의 JSON-RPC 인터페이스
"""

import json
import sys
import os
import asyncio
import aiohttp
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

# MCP 프로토콜 관련 상수
MCP_VERSION = "2024-11-05"
SERVER_NAME = "receipt-printer"
SERVER_VERSION = "1.0.0"

# 환경 변수에서 설정 읽기
API_URL = os.getenv("PRINTER_API_URL", "http://127.0.0.1:8000")

class MCPServer:
    """MCP 서버 구현"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.tools = {
            "print_receipt": {
                "name": "print_receipt",
                "description": "프린터로 영수증을 출력합니다",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "printer_name": {
                            "type": "string",
                            "description": "프린터 이름 (예: BIXOLON_SRP_330II)",
                            "default": "BIXOLON_SRP_330II"
                        },
                        "content": {
                            "type": "object",
                            "properties": {
                                "header": {
                                    "type": "string",
                                    "description": "헤더 텍스트 (선택사항)"
                                },
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string", "description": "항목명"},
                                            "quantity": {"type": "integer", "description": "수량"},
                                            "price": {"type": "number", "description": "단가"},
                                            "total": {"type": "number", "description": "합계"}
                                        },
                                        "required": ["name"]
                                    },
                                    "description": "영수증 항목 목록 (선택사항)"
                                },
                                "footer": {
                                    "type": "string",
                                    "description": "푸터 텍스트 (선택사항)"
                                },
                                "text": {
                                    "type": "string",
                                    "description": "단순 텍스트 출력 (items 대신 사용 가능)"
                                }
                            },
                            "description": "출력할 내용"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "미리보기 모드 (실제로 출력하지 않음)",
                            "default": False
                        }
                    },
                    "required": ["content"]
                }
            },
            "list_printers": {
                "name": "list_printers",
                "description": "사용 가능한 프린터 목록을 조회합니다",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "get_printer_status": {
                "name": "get_printer_status",
                "description": "특정 프린터의 상태를 확인합니다",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "printer_name": {
                            "type": "string",
                            "description": "상태를 확인할 프린터 이름",
                            "default": "BIXOLON_SRP_330II"
                        }
                    },
                    "required": ["printer_name"]
                }
            },
            "preview_receipt": {
                "name": "preview_receipt",
                "description": "영수증 출력 미리보기를 제공합니다",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "object",
                            "properties": {
                                "header": {"type": "string", "description": "헤더 텍스트"},
                                "items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {"type": "string"},
                                            "quantity": {"type": "integer"},
                                            "price": {"type": "number"},
                                            "total": {"type": "number"}
                                        },
                                        "required": ["name"]
                                    }
                                },
                                "footer": {"type": "string", "description": "푸터 텍스트"},
                                "text": {"type": "string", "description": "단순 텍스트"}
                            }
                        }
                    },
                    "required": ["content"]
                }
            }
        }

    async def __aenter__(self):
        """비동기 컨텍스트 매니저 진입"""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """비동기 컨텍스트 매니저 종료"""
        if self.session:
            await self.session.close()

    def log_debug(self, message: str):
        """디버그 로그 (stderr로 출력)"""
        print(f"[DEBUG] {datetime.now().isoformat()} - {message}", file=sys.stderr)

    async def make_api_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """FastAPI 서버에 HTTP 요청"""
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        url = f"{API_URL}{endpoint}"
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            if method.upper() == "GET":
                async with self.session.get(url, headers=headers) as response:
                    result = await response.json()
                    if response.status >= 400:
                        raise aiohttp.ClientError(f"HTTP {response.status}: {result.get('message', 'Unknown error')}")
                    return result
            
            elif method.upper() == "POST":
                async with self.session.post(url, headers=headers, json=data) as response:
                    result = await response.json()
                    if response.status >= 400:
                        raise aiohttp.ClientError(f"HTTP {response.status}: {result.get('message', 'Unknown error')}")
                    return result
            
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
        
        except aiohttp.ClientError as e:
            self.log_debug(f"API request failed: {str(e)}")
            raise
        except Exception as e:
            self.log_debug(f"Unexpected error in API request: {str(e)}")
            raise

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구 호출 처리"""
        try:
            if tool_name == "print_receipt":
                return await self._handle_print_receipt(arguments)
            elif tool_name == "list_printers":
                return await self._handle_list_printers(arguments)
            elif tool_name == "get_printer_status":
                return await self._handle_get_printer_status(arguments)
            elif tool_name == "preview_receipt":
                return await self._handle_preview_receipt(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
        
        except Exception as e:
            self.log_debug(f"Tool call error: {str(e)}")
            return {
                "isError": True,
                "content": [
                    {
                        "type": "text",
                        "text": f"오류 발생: {str(e)}"
                    }
                ]
            }

    async def _handle_print_receipt(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """영수증 출력 처리"""
        printer_name = arguments.get("printer_name", "BIXOLON_SRP_330II")
        content = arguments.get("content", {})
        preview = arguments.get("preview", False)
        
        request_data = {
            "content": content,
            "preview": preview
        }
        
        if preview:
            # 미리보기 모드
            result = await self.make_api_request("POST", f"/printers/{printer_name}/print", request_data)
            preview_lines = result.get("preview", [])
            preview_text = "\n".join(f"|{line:<40}|" for line in preview_lines)
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"📄 출력 미리보기:\n{'=' * 42}\n{preview_text}\n{'=' * 42}\n총 {len(preview_lines)}줄"
                    }
                ]
            }
        else:
            # 실제 출력
            result = await self.make_api_request("POST", f"/printers/{printer_name}/print", request_data)
            
            message = result.get("message", "출력 완료")
            job_id = result.get("job_id")
            lines_printed = result.get("lines_printed")
            
            response_text = f"✅ {message}"
            if job_id:
                response_text += f"\n📝 작업 ID: {job_id}"
            if lines_printed:
                response_text += f"\n📊 출력 라인 수: {lines_printed}"
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": response_text
                    }
                ]
            }

    async def _handle_list_printers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """프린터 목록 조회 처리"""
        result = await self.make_api_request("GET", "/printers")
        
        printers = result.get("printers", [])
        total_count = result.get("total_count", 0)
        
        if not printers:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": "❌ 사용 가능한 프린터가 없습니다."
                    }
                ]
            }
        
        printer_list = ["🖨️  사용 가능한 프린터:"]
        for printer in printers:
            status_icon = "✅" if printer.get("available") else "❌"
            printer_list.append(f"  {status_icon} {printer['name']}")
            if printer.get("status"):
                printer_list.append(f"     상태: {printer['status']}")
        
        printer_list.append(f"\n총 {total_count}개 프린터")
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": "\n".join(printer_list)
                }
            ]
        }

    async def _handle_get_printer_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """프린터 상태 확인 처리"""
        printer_name = arguments.get("printer_name", "BIXOLON_SRP_330II")
        
        result = await self.make_api_request("GET", f"/printers/{printer_name}/status")
        
        status_icon = "✅" if result.get("available") else "❌"
        response_text = f"📊 프린터 상태: {printer_name}\n"
        response_text += f"{status_icon} {result.get('status', 'Unknown')}\n"
        response_text += f"🕒 확인 시각: {result.get('last_checked', 'Unknown')}"
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": response_text
                }
            ]
        }

    async def _handle_preview_receipt(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """영수증 미리보기 처리 (실제 출력하지 않음)"""
        content = arguments.get("content", {})
        
        request_data = {
            "content": content,
            "preview": True
        }
        
        # 기본 프린터로 미리보기 요청
        result = await self.make_api_request("POST", "/printers/BIXOLON_SRP_330II/print", request_data)
        
        preview_lines = result.get("preview", [])
        preview_text = "\n".join(f"|{line:<40}|" for line in preview_lines)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"📄 영수증 미리보기:\n{'=' * 42}\n{preview_text}\n{'=' * 42}\n총 {len(preview_lines)}줄"
                }
            ]
        }

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 요청 처리"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id", 1)  # 기본값 설정
        
        # request_id가 None인 경우 기본값 사용
        if request_id is None:
            request_id = 1
        
        try:
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": MCP_VERSION,
                        "serverInfo": {
                            "name": SERVER_NAME,
                            "version": SERVER_VERSION
                        },
                        "capabilities": {
                            "tools": {}
                        }
                    }
                }
            
            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "tools": list(self.tools.values())
                    }
                }
            
            elif method == "tools/call":
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                
                if not tool_name:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32602,
                            "message": "Invalid params: missing tool name"
                        }
                    }
                
                result = await self.handle_tool_call(tool_name, arguments)
                
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": result
                }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
        
        except Exception as e:
            self.log_debug(f"Request handling error: {str(e)}")
            return {
                "jsonrpc": "2.0",
                "id": request_id if request_id is not None else 1,
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                }
            }

    async def run(self):
        """MCP 서버 실행"""
        self.log_debug("MCP Receipt Printer Server starting...")
        
        try:
            while True:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    
                    # 요청 검증
                    if not isinstance(request, dict):
                        raise ValueError("Request must be a JSON object")
                    
                    if "jsonrpc" not in request:
                        request["jsonrpc"] = "2.0"
                    
                    response = await self.handle_request(request)
                    print(json.dumps(response, ensure_ascii=False))
                    sys.stdout.flush()
                
                except json.JSONDecodeError as e:
                    self.log_debug(f"JSON decode error: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": 1,  # null 대신 기본값 사용
                        "error": {
                            "code": -32700,
                            "message": f"Parse error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
                
                except Exception as e:
                    self.log_debug(f"Unexpected error: {str(e)}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": 1,
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}"
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
        
        except KeyboardInterrupt:
            self.log_debug("Server stopped by user")
        except Exception as e:
            self.log_debug(f"Server error: {str(e)}")

async def main():
    """메인 함수"""
    async with MCPServer() as server:
        await server.run()

if __name__ == "__main__":
    asyncio.run(main())