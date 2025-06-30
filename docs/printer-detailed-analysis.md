# printer.py 상세 분석 문서

## 개요

`printer.py`는 BIXOLON SRP-330II 영수증 프린터에 한글과 영문 텍스트(최대 200자)를 출력하는 핵심 모듈입니다. CUPS 시스템을 통해 ESC/POS 프로토콜로 프린터와 통신하며, 한글 문자 폭 계산과 정확한 텍스트 정렬을 지원합니다.

## 핵심 기능

### 1. 문자 폭 계산 (`get_text_width`)
**위치**: `printer.py:12-20`

```python
def get_text_width(text):
    """텍스트의 실제 폭 계산 (한글=2, 영문=1)"""
    width = 0
    for char in text:
        if ord(char) > 127:  # 한글/특수문자
            width += 2
        else:  # 영문/숫자
            width += 1
    return width
```

**기능 설명**:
- 한글/특수문자: 2 단위폭 (Unicode 127 초과)
- 영문/숫자: 1 단위폭 (ASCII 범위)
- 프린터의 실제 출력 폭과 일치하는 정확한 계산

### 2. 텍스트 래핑 (`wrap_text`)
**위치**: `printer.py:22-52`

**핵심 알고리즘**:
- **최대 폭**: 40자 (영문 기준)
- **단어 단위 래핑**: 공백 기준으로 단어를 분리하여 처리
- **동적 폭 계산**: 각 단어의 실제 폭을 계산하여 줄바꿈 결정

**처리 과정**:
1. 텍스트를 공백으로 단어 분리
2. 각 단어의 폭 계산 (`get_text_width` 호출)
3. 현재 줄 + 공백 + 새 단어가 40자 이내인지 확인
4. 초과시 새 줄로 이동, 이내시 현재 줄에 추가

### 3. 출력 내용 준비 (`prepare_print_content`)
**위치**: `printer.py:55-76`

**여백 관리 시스템**:
- **상단 여백**: 항상 1줄
- **하단 여백**: 텍스트 줄 수에 따른 동적 조정
  - 1줄: 3줄 여백
  - 2줄: 2줄 여백  
  - 3줄 이상: 1줄 여백

**목적**: 영수증의 미적 완성도와 가독성 향상

### 4. ESC/POS 명령어 생성 (`create_esc_pos_content`)
**위치**: `printer.py:78-112`

**초기화 시퀀스**:
```
\x1B\x40        # ESC @ (프린터 초기화)
\x1B\x74\x12    # ESC t 18 (CP949/EUC-KR 코드페이지)
\x1C\x26        # FS & (한글 모드 활성화)
\x1C\x2E        # FS . (설정 적용)
```

**정렬 제어**:
```
\x1B\x61\x01    # ESC a 1 (가운데 정렬)
\x1B\x61\x00    # ESC a 0 (좌측 정렬 복귀)
```

**용지 절단**:
```
\x1D\x56\x00    # GS V 0 (풀 컷)
```

**문자 인코딩 전략**:
1. **1차 시도**: EUC-KR 인코딩 (한글 최적화)
2. **2차 대안**: UTF-8 인코딩 (UnicodeEncodeError 발생시)

### 5. 프린터 관리 기능

#### 사용 가능한 프린터 목록 (`get_available_printers`)
**위치**: `printer.py:114-127`

```bash
lpstat -p
```
명령어 결과를 파싱하여 CUPS에 등록된 프린터 목록 반환

#### 프린터 상태 확인 (`check_printer_status`)
**위치**: `printer.py:164-173`

```bash
lpstat -p [프린터명]
```
특정 프린터의 현재 상태 (활성화/비활성화/오류) 확인

### 6. CUPS 출력 실행 (`print_to_cups`)
**위치**: `printer.py:129-162`

**실행 프로세스**:
1. 텍스트 내용 준비 (`prepare_print_content`)
2. ESC/POS 바이너리 생성 (`create_esc_pos_content`)
3. 임시 바이너리 파일 생성 (`tempfile.NamedTemporaryFile`)
4. CUPS `lp` 명령어 실행
5. 임시 파일 자동 정리

**CUPS 명령어**:
```bash
lp -d [프린터명] -o raw [파일경로]
```
- `-d`: 대상 프린터 지정
- `-o raw`: 원시 데이터 모드 (ESC/POS 바이너리 직접 전송)

## 명령줄 인터페이스 (CLI)

### 주요 옵션

| 옵션 | 설명 | 예시 |
|------|------|------|
| `text` | 출력할 텍스트 | `python3 printer.py "안녕하세요"` |
| `-p, --printer` | 프린터 이름 지정 | `python3 printer.py "텍스트" -p MyPrinter` |
| `--preview` | 출력 미리보기 | `python3 printer.py "텍스트" --preview` |
| `--list-printers` | 프린터 목록 조회 | `python3 printer.py --list-printers` |
| `--status` | 프린터 상태 확인 | `python3 printer.py --status -p BIXOLON_SRP_330II` |

### 사용 예시

```bash
# 기본 출력
python3 printer.py "우유 사오기"

# 특정 프린터로 출력
python3 printer.py "회의 3시" -p RECEIPT_PRINTER

# 출력 미리보기
python3 printer.py "장보기 목록: 우유, 빵, 계란" --preview

# 프린터 목록 확인
python3 printer.py --list-printers

# 프린터 상태 확인
python3 printer.py --status -p BIXOLON_SRP_330II
```

## 에러 처리 및 사용자 피드백

### 성공 메시지
```
✅ 출력 완료: 3줄 → BIXOLON_SRP_330II
📝 작업 ID: job-123
```

### 실패시 문제 해결 가이드
```
🔧 문제 해결 방법:
1. 프린터가 CUPS에 등록되어 있는지 확인: --list-printers
2. 프린터 상태 확인: --status
3. 프린터 이름이 정확한지 확인: -p 프린터이름
4. CUPS 서비스 상태 확인: brew services list | grep cups
5. 미리보기로 내용 확인: --preview
```

## 기술적 특징

### 한글 지원 최적화
- **EUC-KR 우선 인코딩**: 한글 프린터 호환성 극대화
- **UTF-8 대안 지원**: 특수문자 호환성 보장
- **정확한 문자 폭 계산**: 한글(2단위) vs 영문(1단위)

### 메모리 효율성
- **임시 파일 자동 정리**: `os.unlink()` 호출
- **바이너리 스트림 처리**: 메모리 사용량 최소화

### 시스템 통합
- **CUPS 네이티브 지원**: 시스템 프린터 큐 활용
- **크로스 플랫폼**: macOS/Linux CUPS 호환

## 의존성

### Python 표준 라이브러리
- `sys`: 명령줄 인수 처리
- `subprocess`: CUPS 명령어 실행
- `tempfile`: 임시 파일 관리
- `argparse`: CLI 인터페이스
- `os`: 파일 시스템 작업

### 시스템 의존성
- **CUPS**: Common Unix Printing System
- **lpstat**: 프린터 상태 조회 유틸리티
- **lp**: 출력 명령어

## 성능 특성

### 처리 용량
- **최대 텍스트 길이**: 200자 (MCP 인터페이스 제한)
- **최대 출력 폭**: 40자 (영문 기준)
- **처리 속도**: 즉시 처리 (동기식)

### 리소스 사용량
- **메모리**: 최소 (임시 파일 기반)
- **CPU**: 낮음 (텍스트 처리만)
- **디스크**: 임시 파일 생성 후 즉시 삭제

## 확장성

### MCP 통합
`mcp_wrapper.py`를 통해 Claude Desktop과 연동:
- `print_receipt`: 직접 텍스트 출력
- `list_printers`: 프린터 목록 조회
- `get_printer_status`: 상태 확인

### 테스트 지원
`tests/test_printer.py`를 통한 단위 테스트:
- 텍스트 폭 계산 검증
- 래핑 알고리즘 테스트
- ESC/POS 명령어 생성 확인

## 한계사항

1. **CUPS 의존성**: CUPS가 설치되지 않은 시스템에서 동작 불가
2. **ESC/POS 전용**: ESC/POS 프로토콜을 지원하지 않는 프린터 호환성 제한
3. **동기식 처리**: 대량 출력시 블로킹 발생 가능
4. **제한된 서식**: 단순 텍스트만 지원 (이미지, 바코드 등 미지원)

## 보안 고려사항

### 입력 검증
- 200자 길이 제한 (MCP 레벨)
- SQL 인젝션 등 보안 위험 없음 (파일 기반 처리)

### 파일 시스템 보안
- 임시 파일 자동 정리
- 제한된 파일 시스템 접근 (temporary directory만)

### 권한 관리
- CUPS 프린터 접근 권한 필요
- 시스템 수준 프린터 설정 변경 불가