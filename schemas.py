"""
Pydantic 스키마 정의
API 요청/응답을 위한 데이터 모델들
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, validator
from config import MAX_TEXT_LENGTH, MAX_LINES


class ReceiptItem(BaseModel):
    """영수증 항목 모델"""
    name: str = Field(..., max_length=30, description="항목명")
    quantity: Optional[int] = Field(1, ge=1, le=999, description="수량")
    price: Optional[float] = Field(None, ge=0, description="가격")
    total: Optional[float] = Field(None, ge=0, description="합계")
    
    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError('항목명은 비어있을 수 없습니다')
        return v.strip()


class ReceiptContent(BaseModel):
    """구조화된 영수증 내용 모델"""
    header: Optional[str] = Field(None, max_length=100, description="헤더 텍스트 (가운데 정렬)")
    items: List[ReceiptItem] = Field(default_factory=list, max_items=50, description="항목 목록")
    footer: Optional[str] = Field(None, max_length=100, description="푸터 텍스트 (가운데 정렬)")
    text: Optional[str] = Field(None, max_length=MAX_TEXT_LENGTH, description="단순 텍스트 (대체용)")
    
    @validator('text')
    def validate_text_length(cls, v):
        if v and len(v) > MAX_TEXT_LENGTH:
            raise ValueError(f'텍스트는 최대 {MAX_TEXT_LENGTH}자까지 가능합니다')
        return v
    
    @validator('header', 'footer')
    def validate_header_footer(cls, v):
        if v:
            return v.strip()
        return v


class PrintRequest(BaseModel):
    """출력 요청 모델"""
    content: ReceiptContent = Field(..., description="출력할 내용")
    preview: bool = Field(False, description="미리보기 모드")
    
    class Config:
        json_schema_extra = {
            "example": {
                "content": {
                    "header": "영수증",
                    "items": [
                        {"name": "아메리카노", "quantity": 2, "price": 4500, "total": 9000},
                        {"name": "카페라떼", "quantity": 1, "price": 5000, "total": 5000}
                    ],
                    "footer": "감사합니다"
                },
                "preview": False
            }
        }


class PrintResponse(BaseModel):
    """출력 응답 모델"""
    success: bool = Field(..., description="출력 성공 여부")
    message: str = Field(..., description="응답 메시지")
    job_id: Optional[str] = Field(None, description="출력 작업 ID")
    lines_printed: Optional[int] = Field(None, description="출력된 라인 수")


class PreviewResponse(BaseModel):
    """미리보기 응답 모델"""
    preview: List[str] = Field(..., description="미리보기 텍스트 라인들")
    total_lines: int = Field(..., description="총 라인 수")


class PrinterInfo(BaseModel):
    """프린터 정보 모델"""
    name: str = Field(..., description="프린터 이름")
    status: str = Field(..., description="프린터 상태")
    available: bool = Field(..., description="사용 가능 여부")


class PrinterListResponse(BaseModel):
    """프린터 목록 응답 모델"""
    printers: List[PrinterInfo] = Field(..., description="프린터 목록")
    total_count: int = Field(..., description="총 프린터 수")


class ErrorResponse(BaseModel):
    """에러 응답 모델"""
    error: str = Field(..., description="에러 유형")
    message: str = Field(..., description="에러 메시지")
    details: Optional[str] = Field(None, description="상세 정보")
    troubleshooting: Optional[List[str]] = Field(None, description="문제 해결 방법")


class StatusResponse(BaseModel):
    """상태 응답 모델"""
    printer_name: str = Field(..., description="프린터 이름")
    status: str = Field(..., description="상태 정보")
    available: bool = Field(..., description="사용 가능 여부")
    last_checked: str = Field(..., description="마지막 확인 시각")