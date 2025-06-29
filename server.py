"""
FastAPI 백엔드 서버
프린터 제어를 위한 REST API 엔드포인트 제공
"""

import os
import shlex
import subprocess
import tempfile
from datetime import datetime
from typing import List, Optional

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import (
    ALLOWED_PRINTERS, DEFAULT_PRINTER, 
    SECURITY_HEADERS, DEBUG_MODE, MAX_LINES
)
from schemas import (
    PrintRequest, PrintResponse, PreviewResponse, 
    PrinterListResponse, PrinterInfo, StatusResponse, 
    ErrorResponse, ReceiptContent
)
from printer_utils import (
    get_available_printers, check_printer_status,
    prepare_print_content, create_esc_pos_content,
    wrap_text, center_text, get_text_width
)

app = FastAPI(
    title="BIXOLON Receipt Printer API",
    description="한국어 지원 영수증 프린터 제어 API",
    version="1.0.0",
    debug=DEBUG_MODE
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:*", "http://localhost:*"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# 보안 헤더 미들웨어
@app.middleware("http")
async def add_security_headers(request, call_next):
    response = await call_next(request)
    for header, value in SECURITY_HEADERS.items():
        response.headers[header] = value
    return response

# 로컬 MCP 서버이므로 API 키 인증 제거

def validate_printer_name(printer_name: str) -> str:
    """프린터 이름 검증 (화이트리스트 확인)"""
    if printer_name not in ALLOWED_PRINTERS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"허용되지 않은 프린터입니다: {printer_name}. 허용된 프린터: {', '.join(ALLOWED_PRINTERS)}"
        )
    return printer_name

def format_receipt_content(content: ReceiptContent, width: int = 40) -> List[str]:
    """ReceiptContent를 출력 가능한 텍스트 라인으로 변환"""
    lines = []
    
    # 헤더 추가
    if content.header:
        lines.append("")  # 위쪽 여백
        header_lines = wrap_text(content.header, width)
        for line in header_lines:
            lines.append(center_text(line, width))
        lines.append("")  # 구분선
    
    # 항목들 추가
    if content.items:
        for item in content.items:
            # 항목명과 수량
            if item.quantity and item.quantity > 1:
                item_text = f"{item.name} x{item.quantity}"
            else:
                item_text = item.name
            
            # 가격 정보가 있으면 추가
            if item.price is not None:
                if item.total is not None:
                    price_text = f"{int(item.total):,}원"
                else:
                    price_text = f"{int(item.price):,}원"
                
                # 항목명과 가격을 양쪽 정렬
                available_width = width - get_text_width(price_text)
                if get_text_width(item_text) > available_width - 1:
                    # 항목명이 너무 길면 줄바꿈
                    lines.extend(wrap_text(item_text, width))
                    lines.append(" " * (width - get_text_width(price_text)) + price_text)
                else:
                    # 한 줄에 맞춤
                    padding = available_width - get_text_width(item_text)
                    lines.append(item_text + " " * padding + price_text)
            else:
                # 가격 정보가 없으면 항목명만
                lines.extend(wrap_text(item_text, width))
        
        if content.footer:
            lines.append("")  # 구분선
    
    # 단순 텍스트 처리 (items가 없을 때만)
    elif content.text:
        if content.header:
            lines.append("-" * width)
        lines.extend(wrap_text(content.text, width))
    
    # 푸터 추가
    if content.footer:
        if not content.header and (content.items or content.text):
            lines.append("")  # 구분선
        footer_lines = wrap_text(content.footer, width)
        for line in footer_lines:
            lines.append(center_text(line, width))
        lines.append("")  # 아래쪽 여백
    
    return lines

@app.get("/", response_model=dict)
async def root():
    """API 루트 엔드포인트"""
    return {
        "name": "BIXOLON Receipt Printer API",
        "version": "1.0.0",
        "description": "한국어 지원 영수증 프린터 제어 API",
        "endpoints": {
            "GET /printers": "프린터 목록 조회",
            "GET /printers/{name}/status": "프린터 상태 확인", 
            "POST /printers/{name}/print": "영수증 출력"
        }
    }

@app.get("/printers", response_model=PrinterListResponse)
async def list_printers():
    """허용된 프린터 목록 조회"""
    try:
        available_printers = get_available_printers()
        printer_infos = []
        
        for printer_name in ALLOWED_PRINTERS:
            status_info = check_printer_status(printer_name)
            is_available = printer_name in available_printers and "enabled" in status_info.lower()
            
            printer_infos.append(PrinterInfo(
                name=printer_name,
                status=status_info,
                available=is_available
            ))
        
        return PrinterListResponse(
            printers=printer_infos,
            total_count=len(printer_infos)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프린터 목록 조회 실패: {str(e)}"
        )

@app.get("/printers/{printer_name}/status", response_model=StatusResponse)
async def get_printer_status(printer_name: str):
    """특정 프린터 상태 확인"""
    validate_printer_name(printer_name)
    
    try:
        status_info = check_printer_status(printer_name)
        available_printers = get_available_printers()
        is_available = printer_name in available_printers and "enabled" in status_info.lower()
        
        return StatusResponse(
            printer_name=printer_name,
            status=status_info,
            available=is_available,
            last_checked=datetime.now().isoformat()
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"프린터 상태 확인 실패: {str(e)}"
        )

@app.post("/printers/{printer_name}/print")
async def print_receipt(
    printer_name: str,
    request: PrintRequest
):
    """영수증 출력"""
    validate_printer_name(printer_name)
    
    try:
        # 출력 내용 준비
        if request.content.items or request.content.header or request.content.footer:
            # 구조화된 내용 사용
            lines = format_receipt_content(request.content)
        elif request.content.text:
            # 단순 텍스트 사용
            lines = prepare_print_content(request.content.text)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="출력할 내용이 없습니다. text 또는 items를 제공해주세요."
            )
        
        # 라인 수 제한 확인
        if len(lines) > MAX_LINES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"출력 라인 수가 너무 많습니다. 최대 {MAX_LINES}줄까지 가능합니다."
            )
        
        # 미리보기 모드
        if request.preview:
            return PreviewResponse(
                preview=lines,
                total_lines=len(lines)
            )
        
        # 실제 출력
        print_content = create_esc_pos_content(lines)
        
        # 임시 파일 생성 및 출력
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
            temp_file.write(print_content)
            temp_file_path = temp_file.name
        
        try:
            # shlex.quote를 사용한 안전한 명령어 실행
            cmd = [
                'lp', 
                '-d', shlex.quote(printer_name), 
                '-o', 'raw', 
                shlex.quote(temp_file_path)
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                job_id = result.stdout.strip() if result.stdout.strip() else None
                return PrintResponse(
                    success=True,
                    message=f"출력 완료: {len(lines)}줄 → {printer_name}",
                    job_id=job_id,
                    lines_printed=len(lines)
                )
            else:
                error_msg = result.stderr.strip() if result.stderr.strip() else "알 수 없는 오류"
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=f"출력 실패: {error_msg}"
                )
        
        finally:
            # 임시 파일 정리
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    except HTTPException:
        raise
    except subprocess.TimeoutExpired:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail="출력 명령이 시간 초과되었습니다"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"출력 처리 중 오류 발생: {str(e)}"
        )

# 에러 핸들러
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """HTTP 예외 처리"""
    troubleshooting = []
    
    if exc.status_code == 503:  # Service Unavailable
        troubleshooting = [
            "프린터가 켜져 있고 연결되어 있는지 확인하세요",
            "CUPS 서비스가 실행 중인지 확인하세요: brew services list | grep cups",
            "프린터 상태를 확인하세요: GET /printers/{name}/status",
            "용지가 충분한지 확인하세요"
        ]
    elif exc.status_code == 401:  # Unauthorized
        troubleshooting = [
            "올바른 API 키를 Authorization 헤더에 포함하세요",
            "Bearer 토큰 형식을 사용하세요: Authorization: Bearer YOUR_API_KEY"
        ]
    elif exc.status_code == 403:  # Forbidden
        troubleshooting = [
            f"허용된 프린터만 사용할 수 있습니다: {', '.join(ALLOWED_PRINTERS)}",
            "프린터 목록을 확인하세요: GET /printers"
        ]
    
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.__class__.__name__,
            message=exc.detail,
            troubleshooting=troubleshooting if troubleshooting else None
        ).model_dump()
    )

@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """일반 예외 처리"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="InternalServerError",
            message="서버 내부 오류가 발생했습니다",
            details=str(exc) if DEBUG_MODE else None
        ).model_dump()
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8000,
        reload=DEBUG_MODE,
        access_log=DEBUG_MODE
    )