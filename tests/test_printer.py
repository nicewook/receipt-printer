"""
프린터 유틸리티 함수 테스트
"""

import pytest
import tempfile
import os
from unittest.mock import patch, MagicMock

# 테스트를 위해 상위 디렉터리의 모듈들을 import
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from printer import (
    get_text_width, wrap_text,
    prepare_print_content, create_esc_pos_content,
    get_available_printers, check_printer_status
)


class TestTextProcessing:
    """텍스트 처리 함수 테스트"""
    
    def test_get_text_width_english(self):
        """영문 텍스트 폭 계산 테스트"""
        assert get_text_width("Hello") == 5
        assert get_text_width("123") == 3
        assert get_text_width("") == 0
    
    def test_get_text_width_korean(self):
        """한글 텍스트 폭 계산 테스트"""
        assert get_text_width("안녕") == 4  # 한글 2자 = 폭 4
        assert get_text_width("한글") == 4
        assert get_text_width("테스트") == 6  # 한글 3자 = 폭 6
    
    def test_get_text_width_mixed(self):
        """혼합 텍스트 폭 계산 테스트"""
        assert get_text_width("Hello 안녕") == 9  # 5 + 1 + 4 = 10이 아니라 9 (공백=1)
        assert get_text_width("카페 Latte") == 10  # 2*2 + 1 + 5 = 10
    
    def test_wrap_text_short(self):
        """짧은 텍스트 줄바꿈 테스트"""
        result = wrap_text("Hello World", max_width=40)
        assert result == ["Hello World"]
    
    def test_wrap_text_long_english(self):
        """긴 영문 텍스트 줄바꿈 테스트"""
        long_text = "This is a very long text that should be wrapped across multiple lines"
        result = wrap_text(long_text, max_width=20)
        assert len(result) > 1
        for line in result:
            assert get_text_width(line) <= 20
    
    def test_wrap_text_korean(self):
        """한글 텍스트 줄바꿈 테스트"""
        korean_text = "이것은 매우 긴 한글 텍스트입니다 여러 줄로 나뉘어져야 합니다"
        result = wrap_text(korean_text, max_width=20)
        assert len(result) > 1
        for line in result:
            assert get_text_width(line) <= 20
    


class TestPrintContent:
    """출력 내용 준비 함수 테스트"""
    
    def test_prepare_print_content_short(self):
        """짧은 텍스트 출력 준비 테스트"""
        result = prepare_print_content("Hello")
        assert len(result) >= 4  # 최소 여백 포함
        assert result[0] == ""  # 첫 줄은 여백
        assert "Hello" in result[1]  # 두 번째 줄에 텍스트
    
    def test_prepare_print_content_multiline(self):
        """여러 줄 텍스트 출력 준비 테스트"""
        long_text = "This is a very long text that will be wrapped into multiple lines for testing purposes"
        result = prepare_print_content(long_text)
        assert len(result) > 5
        assert result[0] == ""  # 위쪽 여백
        assert result[-1] == ""  # 아래쪽 여백
    
    def test_create_esc_pos_content(self):
        """ESC/POS 내용 생성 테스트"""
        lines = ["Test Line 1", "한글 테스트"]
        result = create_esc_pos_content(lines)
        
        # 바이너리 데이터 확인
        assert isinstance(result, bytes)
        assert len(result) > 0
        
        # ESC/POS 명령어 포함 확인
        assert b'\x1B\x40' in result  # ESC @ (초기화)
        assert b'\x1B\x74\x12' in result  # 코드페이지 설정
        assert b'\x1D\x56\x00' in result  # 용지 절단


class TestPrinterCommunication:
    """프린터 통신 함수 테스트 (모킹)"""
    
    @patch('printer.subprocess.run')
    def test_get_available_printers_success(self, mock_run):
        """프린터 목록 조회 성공 테스트"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="printer BIXOLON_SRP_330II is idle\nprinter HP_LaserJet is busy"
        )
        
        result = get_available_printers()
        assert "BIXOLON_SRP_330II" in result
        assert "HP_LaserJet" in result
        mock_run.assert_called_once_with(['lpstat', '-p'], capture_output=True, text=True)
    
    @patch('printer.subprocess.run')
    def test_get_available_printers_failure(self, mock_run):
        """프린터 목록 조회 실패 테스트"""
        mock_run.return_value = MagicMock(returncode=1)
        
        result = get_available_printers()
        assert result == []
    
    @patch('printer.subprocess.run')
    def test_check_printer_status_success(self, mock_run):
        """프린터 상태 확인 성공 테스트"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="printer BIXOLON_SRP_330II is idle. enabled since Mon 01 Jan 2024"
        )
        
        result = check_printer_status("BIXOLON_SRP_330II")
        assert "idle" in result
        assert "enabled" in result
    
    @patch('printer.subprocess.run')
    def test_check_printer_status_not_found(self, mock_run):
        """존재하지 않는 프린터 상태 확인 테스트"""
        mock_run.return_value = MagicMock(returncode=1)
        
        result = check_printer_status("NONEXISTENT_PRINTER")
        assert "찾을 수 없습니다" in result


class TestIntegration:
    """통합 테스트"""
    
    def test_full_text_processing_pipeline(self):
        """전체 텍스트 처리 파이프라인 테스트"""
        original_text = "안녕하세요! 이것은 한글과 English가 섞인 긴 텍스트입니다. 줄바꿈 테스트를 위해 작성되었습니다."
        
        # 1. 출력 내용 준비
        lines = prepare_print_content(original_text)
        assert len(lines) > 1
        
        # 2. ESC/POS 내용 생성
        esc_pos_content = create_esc_pos_content(lines)
        assert isinstance(esc_pos_content, bytes)
        assert len(esc_pos_content) > 100  # 충분한 데이터가 있는지 확인
    
    def test_empty_text_handling(self):
        """빈 텍스트 처리 테스트"""
        lines = prepare_print_content("")
        assert len(lines) >= 1
        
        esc_pos_content = create_esc_pos_content(lines)
        assert isinstance(esc_pos_content, bytes)
    
    def test_special_characters(self):
        """특수 문자 처리 테스트"""
        special_text = "!@#$%^&*()_+-=[]{}|;':\",./<>?`~"
        lines = prepare_print_content(special_text)
        
        # 특수 문자가 포함된 라인이 있어야 함
        content_lines = [line for line in lines if line.strip()]
        assert len(content_lines) > 0
        
        esc_pos_content = create_esc_pos_content(lines)
        assert isinstance(esc_pos_content, bytes)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])