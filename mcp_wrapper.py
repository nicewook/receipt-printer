#!/usr/bin/env python3
"""
MCP (Model Context Protocol) 래퍼
Claude Desktop과 printer 간의 직접 인터페이스
"""

import json
import sys
import os
import asyncio
import printer
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

# MCP 프로토콜 관련 상수
MCP_VERSION = "2024-11-05"
SERVER_NAME = "todo-printer"
SERVER_VERSION = "1.0.0"

# MCP 서버 설정 (환경변수 의존성 제거)

class MCPServer:
    """MCP 서버 구현"""
    
    def __init__(self):
        # ThreadPoolExecutor로 동기 함수들을 비동기로 실행
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.tools = {
            "print_receipt": {
                "name": "print_receipt",
                "description": "간단한 메모, 할일 목록, 텍스트를 출력합니다. '>' 로 시작하는 메시지나 짧은 텍스트를 즉시 출력할 때 사용하세요.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "출력할 텍스트 (500자 이내, 예: '우유 사오기', '회의 준비사항')",
                            "maxLength": 500
                        },
                        "printer_name": {
                            "type": "string",
                            "description": "프린터 이름",
                            "default": "BIXOLON_SRP_330II"
                        },
                        "preview": {
                            "type": "boolean",
                            "description": "미리보기 모드 (실제로 출력하지 않음)",
                            "default": False
                        }
                    },
                    "required": ["text"]
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
        }

    def __del__(self):
        """소멸자에서 ThreadPoolExecutor 정리"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=True)

    def log_debug(self, message: str):
        """디버그 로그 (stderr로 출력)"""
        print(f"[DEBUG] {datetime.now().isoformat()} - {message}", file=sys.stderr)

    async def _run_sync(self, func, *args):
        """동기 함수를 비동기로 실행"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args)
    

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """MCP 도구 호출 처리"""
        try:
            if tool_name == "print_receipt":
                return await self._handle_print_receipt(arguments)
            elif tool_name == "list_printers":
                return await self._handle_list_printers(arguments)
            elif tool_name == "get_printer_status":
                return await self._handle_get_printer_status(arguments)
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
        """단순 텍스트 출력 처리"""
        text = arguments.get("text", "").strip()
        printer_name = arguments.get("printer_name", "BIXOLON_SRP_330II")
        preview = arguments.get("preview", False)
        
        # 텍스트 길이 검증
        if not text:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": "❌ 출력할 텍스트가 비어있습니다."
                }]
            }
        
        if len(text) > 500:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ 텍스트가 너무 깁니다. ({len(text)}/500자) 500자 이내로 입력하세요."
                }]
            }
        
        if preview:
            # 미리보기 생성
            try:
                preview_text = await self._run_sync(printer.printer_preview, text)
                return {
                    "content": [{
                        "type": "text",
                        "text": f"📄 출력 미리보기 ({len(text)}자):\n{preview_text}"
                    }]
                }
            except Exception as e:
                return {
                    "isError": True,
                    "content": [{
                        "type": "text",
                        "text": f"❌ 미리보기 생성 실패: {str(e)}"
                    }]
                }
        else:
            # 실제 출력
            try:
                success = await self._run_sync(printer.printer_print, text, printer_name)
                if success:
                    return {
                        "content": [{
                            "type": "text", 
                            "text": f"✅ 출력 완료: {len(text)}자 → {printer_name}"
                        }]
                    }
                else:
                    return {
                        "isError": True,
                        "content": [{
                            "type": "text",
                            "text": f"❌ 출력 실패: {printer_name}"
                        }]
                    }
            except Exception as e:
                return {
                    "isError": True,
                    "content": [{
                        "type": "text",
                        "text": f"❌ 출력 오류: {str(e)}"
                    }]
                }

    async def _handle_list_printers(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """프린터 목록 조회 처리 (직접 호출)"""
        try:
            printers = await self._run_sync(printer.printer_list)
            
            if not printers:
                return {
                    "content": [{
                        "type": "text",
                        "text": "❌ 사용 가능한 프린터가 없습니다.\n💡 CUPS에 프린터가 등록되어 있는지 확인하세요: lpstat -p"
                    }]
                }
            
            printer_list = ["🖨️  사용 가능한 프린터:"]
            for printer_name in printers:
                try:
                    status = await self._run_sync(printer.printer_status, printer_name)
                    printer_list.append(f"  ✅ {printer_name}")
                    printer_list.append(f"     상태: {status}")
                except Exception as e:
                    printer_list.append(f"  ❌ {printer_name} (상태 확인 실패: {str(e)})")
            
            printer_list.append(f"\n총 {len(printers)}개 프린터")
            
            return {
                "content": [{
                    "type": "text",
                    "text": "\n".join(printer_list)
                }]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ 프린터 목록 조회 실패: {str(e)}"
                }]
            }

    async def _handle_get_printer_status(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """프린터 상태 확인 처리 (직접 호출)"""
        printer_name = arguments.get("printer_name", "BIXOLON_SRP_330II")
        
        try:
            status = await self._run_sync(printer.printer_status, printer_name)
            
            # 상태 메시지에서 'idle'나 'processing' 같은 키워드로 가용성 판단
            is_available = "idle" in status.lower() or "accepting" in status.lower()
            status_icon = "✅" if is_available else "❌"
            
            response_text = f"📊 프린터 상태: {printer_name}\n"
            response_text += f"{status_icon} {status}\n"
            response_text += f"🕒 확인 시각: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            return {
                "content": [{
                    "type": "text",
                    "text": response_text
                }]
            }
        except Exception as e:
            return {
                "isError": True,
                "content": [{
                    "type": "text",
                    "text": f"❌ 프린터 상태 확인 실패: {str(e)}"
                }]
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
    server = MCPServer()
    try:
        await server.run()
    finally:
        # ThreadPoolExecutor 정리
        if hasattr(server, 'executor'):
            server.executor.shutdown(wait=True)

if __name__ == "__main__":
    asyncio.run(main())