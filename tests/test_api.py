"""
FastAPI 엔드포인트 테스트
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient

# 테스트를 위해 상위 디렉터리의 모듈들을 import
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# 테스트용 환경 설정
os.environ["PRINTER_API_KEY"] = "test-api-key-123"

from server import app
from config import API_KEY

client = TestClient(app)

# 테스트용 헤더
TEST_HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

INVALID_HEADERS = {
    "Authorization": "Bearer invalid-key",
    "Content-Type": "application/json"
}


class TestAuthentication:
    """인증 관련 테스트"""
    
    def test_root_endpoint_no_auth(self):
        """루트 엔드포인트는 인증 없이 접근 가능"""
        response = client.get("/")
        assert response.status_code == 200
        assert "BIXOLON Receipt Printer API" in response.json()["name"]
    
    def test_protected_endpoint_no_auth(self):
        """보호된 엔드포인트는 인증 없이 접근 불가"""
        response = client.get("/printers")
        assert response.status_code == 403  # Forbidden (no auth header)
    
    def test_protected_endpoint_invalid_auth(self):
        """잘못된 인증으로 접근 불가"""
        response = client.get("/printers", headers=INVALID_HEADERS)
        assert response.status_code == 401  # Unauthorized
        assert "잘못된 API 키" in response.json()["detail"]
    
    def test_protected_endpoint_valid_auth(self):
        """올바른 인증으로 접근 가능"""
        with patch('server.get_available_printers') as mock_get_printers:
            mock_get_printers.return_value = ["BIXOLON_SRP_330II"]
            
            with patch('server.check_printer_status') as mock_check_status:
                mock_check_status.return_value = "printer BIXOLON_SRP_330II is idle. enabled"
                
                response = client.get("/printers", headers=TEST_HEADERS)
                assert response.status_code == 200


class TestPrinterEndpoints:
    """프린터 관련 엔드포인트 테스트"""
    
    @patch('server.get_available_printers')
    @patch('server.check_printer_status')
    def test_list_printers_success(self, mock_check_status, mock_get_printers):
        """프린터 목록 조회 성공 테스트"""
        mock_get_printers.return_value = ["BIXOLON_SRP_330II"]
        mock_check_status.return_value = "printer BIXOLON_SRP_330II is idle. enabled"
        
        response = client.get("/printers", headers=TEST_HEADERS)
        assert response.status_code == 200
        
        data = response.json()
        assert "printers" in data
        assert "total_count" in data
        assert len(data["printers"]) > 0
    
    @patch('server.get_available_printers')
    @patch('server.check_printer_status')
    def test_get_printer_status_success(self, mock_check_status, mock_get_printers):
        """프린터 상태 확인 성공 테스트"""
        mock_get_printers.return_value = ["BIXOLON_SRP_330II"]
        mock_check_status.return_value = "printer BIXOLON_SRP_330II is idle. enabled"
        
        response = client.get("/printers/BIXOLON_SRP_330II/status", headers=TEST_HEADERS)
        assert response.status_code == 200
        
        data = response.json()
        assert data["printer_name"] == "BIXOLON_SRP_330II"
        assert "status" in data
        assert "available" in data
        assert "last_checked" in data
    
    def test_get_printer_status_invalid_printer(self):
        """허용되지 않은 프린터 상태 확인 테스트"""
        response = client.get("/printers/INVALID_PRINTER/status", headers=TEST_HEADERS)
        assert response.status_code == 403
        assert "허용되지 않은 프린터" in response.json()["detail"]


class TestPrintEndpoints:
    """출력 관련 엔드포인트 테스트"""
    
    def test_print_receipt_invalid_printer(self):
        """허용되지 않은 프린터로 출력 시도"""
        print_request = {
            "content": {"text": "Test print"},
            "preview": False
        }
        
        response = client.post(
            "/printers/INVALID_PRINTER/print",
            headers=TEST_HEADERS,
            json=print_request
        )
        assert response.status_code == 403
        assert "허용되지 않은 프린터" in response.json()["detail"]
    
    def test_print_receipt_preview_mode(self):
        """미리보기 모드 출력 테스트"""
        print_request = {
            "content": {"text": "Hello World Test"},
            "preview": True
        }
        
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            json=print_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "preview" in data
        assert "total_lines" in data
        assert isinstance(data["preview"], list)
    
    @patch('server.subprocess.run')
    @patch('server.tempfile.NamedTemporaryFile')
    def test_print_receipt_success(self, mock_temp_file, mock_subprocess):
        """실제 출력 성공 테스트"""
        # 임시 파일 모킹
        mock_file = MagicMock()
        mock_file.name = "/tmp/test_print_file.bin"
        mock_temp_file.return_value.__enter__.return_value = mock_file
        
        # subprocess 모킹
        mock_subprocess.return_value = MagicMock(
            returncode=0,
            stdout="request id is BIXOLON_SRP_330II-123",
            stderr=""
        )
        
        print_request = {
            "content": {"text": "Test print job"},
            "preview": False
        }
        
        with patch('server.os.unlink'):  # 파일 삭제 모킹
            response = client.post(
                "/printers/BIXOLON_SRP_330II/print",
                headers=TEST_HEADERS,
                json=print_request
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "출력 완료" in data["message"]
    
    @patch('server.subprocess.run')
    def test_print_receipt_printer_error(self, mock_subprocess):
        """프린터 오류 테스트"""
        mock_subprocess.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="lp: The printer or class does not exist."
        )
        
        print_request = {
            "content": {"text": "Test print job"},
            "preview": False
        }
        
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            json=print_request
        )
        assert response.status_code == 503  # Service Unavailable
        assert "출력 실패" in response.json()["detail"]
    
    def test_print_receipt_empty_content(self):
        """빈 내용 출력 시도 테스트"""
        print_request = {
            "content": {},
            "preview": False
        }
        
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            json=print_request
        )
        assert response.status_code == 400
        assert "출력할 내용이 없습니다" in response.json()["detail"]


class TestStructuredContent:
    """구조화된 내용 출력 테스트"""
    
    def test_print_structured_receipt_preview(self):
        """구조화된 영수증 미리보기 테스트"""
        print_request = {
            "content": {
                "header": "영수증",
                "items": [
                    {"name": "아메리카노", "quantity": 2, "price": 4500, "total": 9000},
                    {"name": "카페라떼", "quantity": 1, "price": 5000, "total": 5000}
                ],
                "footer": "감사합니다"
            },
            "preview": True
        }
        
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            json=print_request
        )
        assert response.status_code == 200
        
        data = response.json()
        assert "preview" in data
        assert len(data["preview"]) > 5  # 헤더, 항목들, 푸터 포함
    
    def test_print_items_only(self):
        """항목만 있는 영수증 테스트"""
        print_request = {
            "content": {
                "items": [
                    {"name": "테스트 항목", "quantity": 1}
                ]
            },
            "preview": True
        }
        
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            json=print_request
        )
        assert response.status_code == 200
        
        data = response.json()
        preview_text = "\n".join(data["preview"])
        assert "테스트 항목" in preview_text


class TestValidation:
    """입력 검증 테스트"""
    
    def test_invalid_json(self):
        """잘못된 JSON 형식 테스트"""
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            data="invalid json"
        )
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_missing_required_fields(self):
        """필수 필드 누락 테스트"""
        response = client.post(
            "/printers/BIXOLON_SRP_330II/print",
            headers=TEST_HEADERS,
            json={}  # content 필드 누락
        )
        assert response.status_code == 422


class TestErrorHandling:
    """에러 처리 테스트"""
    
    def test_http_exception_handler(self):
        """HTTP 예외 핸들러 테스트"""
        response = client.get("/printers", headers=INVALID_HEADERS)
        assert response.status_code == 401
        
        error_data = response.json()
        assert "error" in error_data
        assert "message" in error_data
        assert "troubleshooting" in error_data
    
    @patch('server.get_available_printers')
    def test_general_exception_handler(self, mock_get_printers):
        """일반 예외 핸들러 테스트"""
        mock_get_printers.side_effect = Exception("Test exception")
        
        response = client.get("/printers", headers=TEST_HEADERS)
        assert response.status_code == 500
        
        error_data = response.json()
        assert error_data["error"] == "InternalServerError"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])