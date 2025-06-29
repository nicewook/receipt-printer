"""
MCP 통합 테스트
"""

import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock, AsyncMock
import aiohttp

# 테스트를 위해 상위 디렉터리의 모듈들을 import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mcp_wrapper import MCPServer


class TestMCPServer:
    """MCP 서버 기본 기능 테스트"""
    
    @pytest.mark.asyncio
    async def test_server_initialization(self):
        """MCP 서버 초기화 테스트"""
        async with MCPServer() as server:
            assert server.session is not None
            assert isinstance(server.tools, dict)
            assert len(server.tools) == 4  # 4개의 도구가 정의되어야 함
    
    def test_tools_definition(self):
        """도구 정의 테스트"""
        server = MCPServer()
        
        # 모든 필수 도구가 정의되어 있는지 확인
        expected_tools = ["print_receipt", "list_printers", "get_printer_status", "preview_receipt"]
        for tool_name in expected_tools:
            assert tool_name in server.tools
            
            tool = server.tools[tool_name]
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
    
    def test_tool_schemas(self):
        """도구 스키마 검증 테스트"""
        server = MCPServer()
        
        # print_receipt 스키마 확인
        print_tool = server.tools["print_receipt"]
        schema = print_tool["inputSchema"]
        assert "properties" in schema
        assert "content" in schema["properties"]
        assert "printer_name" in schema["properties"]
        assert "preview" in schema["properties"]
        
        # list_printers 스키마 확인 (매개변수 없음)
        list_tool = server.tools["list_printers"]
        list_schema = list_tool["inputSchema"]
        assert list_schema["type"] == "object"


class TestMCPProtocol:
    """MCP 프로토콜 메시지 처리 테스트"""
    
    @pytest.mark.asyncio
    async def test_initialize_request(self):
        """초기화 요청 처리 테스트"""
        async with MCPServer() as server:
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {}
            }
            
            response = await server.handle_request(request)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 1
            assert "result" in response
            assert "protocolVersion" in response["result"]
            assert "serverInfo" in response["result"]
    
    @pytest.mark.asyncio
    async def test_tools_list_request(self):
        """도구 목록 요청 처리 테스트"""
        async with MCPServer() as server:
            request = {
                "jsonrpc": "2.0",
                "id": 2,
                "method": "tools/list",
                "params": {}
            }
            
            response = await server.handle_request(request)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 2
            assert "result" in response
            assert "tools" in response["result"]
            assert len(response["result"]["tools"]) == 4
    
    @pytest.mark.asyncio
    async def test_unknown_method(self):
        """알 수 없는 메소드 처리 테스트"""
        async with MCPServer() as server:
            request = {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "unknown/method",
                "params": {}
            }
            
            response = await server.handle_request(request)
            
            assert response["jsonrpc"] == "2.0"
            assert response["id"] == 3
            assert "error" in response
            assert response["error"]["code"] == -32601  # Method not found


class TestToolExecution:
    """도구 실행 테스트"""
    
    @pytest.mark.asyncio
    async def test_list_printers_tool(self):
        """프린터 목록 도구 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.return_value = {
                    "printers": [
                        {"name": "BIXOLON_SRP_330II", "status": "idle", "available": True}
                    ],
                    "total_count": 1
                }
                
                result = await server.handle_tool_call("list_printers", {})
                
                assert "content" in result
                assert len(result["content"]) > 0
                assert "사용 가능한 프린터" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_get_printer_status_tool(self):
        """프린터 상태 확인 도구 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.return_value = {
                    "printer_name": "BIXOLON_SRP_330II",
                    "status": "printer is idle. enabled",
                    "available": True,
                    "last_checked": "2024-01-01T00:00:00"
                }
                
                result = await server.handle_tool_call("get_printer_status", {
                    "printer_name": "BIXOLON_SRP_330II"
                })
                
                assert "content" in result
                assert "프린터 상태" in result["content"][0]["text"]
                assert "BIXOLON_SRP_330II" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_preview_receipt_tool(self):
        """영수증 미리보기 도구 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.return_value = {
                    "preview": ["", "Test Receipt", "Item 1", ""],
                    "total_lines": 4
                }
                
                result = await server.handle_tool_call("preview_receipt", {
                    "content": {"text": "Test Receipt"}
                })
                
                assert "content" in result
                assert "미리보기" in result["content"][0]["text"]
                assert "총 4줄" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_print_receipt_preview_mode(self):
        """영수증 출력 미리보기 모드 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.return_value = {
                    "preview": ["", "테스트 영수증", "항목 1", ""],
                    "total_lines": 4
                }
                
                result = await server.handle_tool_call("print_receipt", {
                    "printer_name": "BIXOLON_SRP_330II",
                    "content": {"text": "테스트 영수증"},
                    "preview": True
                })
                
                assert "content" in result
                assert "미리보기" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_print_receipt_actual_print(self):
        """실제 영수증 출력 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.return_value = {
                    "success": True,
                    "message": "출력 완료: 5줄 → BIXOLON_SRP_330II",
                    "job_id": "BIXOLON_SRP_330II-123",
                    "lines_printed": 5
                }
                
                result = await server.handle_tool_call("print_receipt", {
                    "printer_name": "BIXOLON_SRP_330II",
                    "content": {"text": "실제 출력 테스트"},
                    "preview": False
                })
                
                assert "content" in result
                content_text = result["content"][0]["text"]
                assert "출력 완료" in content_text
                assert "작업 ID" in content_text
                assert "출력 라인 수" in content_text


class TestErrorHandling:
    """에러 처리 테스트"""
    
    @pytest.mark.asyncio
    async def test_api_request_error(self):
        """API 요청 오류 처리 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.side_effect = aiohttp.ClientError("Connection failed")
                
                result = await server.handle_tool_call("list_printers", {})
                
                assert "isError" in result
                assert result["isError"] is True
                assert "오류 발생" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_unknown_tool_error(self):
        """알 수 없는 도구 오류 처리 테스트"""
        async with MCPServer() as server:
            result = await server.handle_tool_call("unknown_tool", {})
            
            assert "isError" in result
            assert result["isError"] is True
            assert "오류 발생" in result["content"][0]["text"]
    
    @pytest.mark.asyncio
    async def test_malformed_request_handling(self):
        """잘못된 형식의 요청 처리 테스트"""
        async with MCPServer() as server:
            # 필수 필드가 누락된 요청
            request = {
                "jsonrpc": "2.0",
                # id 필드 누락
                "method": "tools/call"
            }
            
            response = await server.handle_request(request)
            
            assert response["jsonrpc"] == "2.0"
            assert "error" in response


class TestAPIIntegration:
    """API 통합 테스트"""
    
    @pytest.mark.asyncio
    async def test_make_api_request_get(self):
        """GET API 요청 테스트"""
        async with MCPServer() as server:
            with patch.object(server.session, 'get') as mock_get:
                # Mock response
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"test": "data"})
                mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
                mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
                
                result = await server.make_api_request("GET", "/test")
                
                assert result == {"test": "data"}
                mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_make_api_request_post(self):
        """POST API 요청 테스트"""
        async with MCPServer() as server:
            with patch.object(server.session, 'post') as mock_post:
                # Mock response
                mock_response = AsyncMock()
                mock_response.status = 200
                mock_response.json = AsyncMock(return_value={"success": True})
                mock_post.return_value.__aenter__ = AsyncMock(return_value=mock_response)
                mock_post.return_value.__aexit__ = AsyncMock(return_value=None)
                
                test_data = {"content": {"text": "test"}}
                result = await server.make_api_request("POST", "/test", test_data)
                
                assert result == {"success": True}
                mock_post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_api_request_error_status(self):
        """API 요청 에러 상태 코드 처리 테스트"""
        async with MCPServer() as server:
            with patch.object(server.session, 'get') as mock_get:
                # Mock 에러 응답
                mock_response = AsyncMock()
                mock_response.status = 404
                mock_response.json = AsyncMock(return_value={"message": "Not found"})
                mock_get.return_value.__aenter__ = AsyncMock(return_value=mock_response)
                mock_get.return_value.__aexit__ = AsyncMock(return_value=None)
                
                with pytest.raises(aiohttp.ClientError):
                    await server.make_api_request("GET", "/nonexistent")


class TestStructuredContentHandling:
    """구조화된 내용 처리 테스트"""
    
    @pytest.mark.asyncio
    async def test_structured_receipt_content(self):
        """구조화된 영수증 내용 처리 테스트"""
        async with MCPServer() as server:
            with patch.object(server, 'make_api_request') as mock_request:
                mock_request.return_value = {
                    "success": True,
                    "message": "출력 완료",
                    "lines_printed": 8
                }
                
                structured_content = {
                    "header": "테스트 영수증",
                    "items": [
                        {"name": "아메리카노", "quantity": 2, "price": 4500, "total": 9000},
                        {"name": "카페라떼", "quantity": 1, "price": 5000, "total": 5000}
                    ],
                    "footer": "감사합니다"
                }
                
                result = await server.handle_tool_call("print_receipt", {
                    "printer_name": "BIXOLON_SRP_330II",
                    "content": structured_content,
                    "preview": False
                })
                
                assert "content" in result
                assert "출력 완료" in result["content"][0]["text"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])