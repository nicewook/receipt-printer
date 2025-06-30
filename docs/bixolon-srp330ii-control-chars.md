# BIXOLON SRP-330II ESC/POS 제어문자 특성 분석

## 개요

BIXOLON SRP-330II 영수증 프린터는 표준 ESC/POS 프로토콜을 지원하지만, 일반적인 줄바꿈 및 여백 제어 명령어들을 무시하는 특별한 동작 특성을 가지고 있습니다. 이 문서는 실제 테스트를 통해 확인된 제어문자들의 작동 여부를 정리합니다.

## 실험 환경

- **프린터 모델**: BIXOLON SRP-330II  
- **연결 방식**: CUPS (Common Unix Printing System)
- **출력 모드**: Raw mode (`lp -o raw`)
- **테스트 방법**: 다양한 ESC/POS 제어문자를 바이너리 파일로 전송하여 실제 출력 결과 확인

## 작동하지 않는 제어문자들 (❌)

### 1. 표준 줄바꿈 문자
```python
content.append(b'\n\n\n')           # 일반 개행 문자
content.append(b'' + b'\n\n\n')     # 바이트 문자열 연결을 통한 개행
```
**결과**: 프린터에서 무시됨. 실제 여백 추가 효과 없음.

### 2. ASCII 제어 코드 (LF)
```python
content.append(b'\x0A' * 3)         # 0x0A = Line Feed (LF)
```
**결과**: 직접적인 LF 코드 전송도 무효. 하드웨어 레벨에서 필터링되는 것으로 추정.

### 3. ESC/POS 라인 피드 명령
```python
content.append(b'\x1B\x64\x03')     # ESC d 3 (3줄 라인 피드)
```
**바이트 코드 분석**:
- `\x1B` = ESC (Escape character)
- `\x64` = 'd' (Line feed command)  
- `\x03` = 3 (Feed 3 lines)

**결과**: ESC/POS 표준 명령임에도 불구하고 무시됨.

## 작동하는 제어문자들 (✅)

### 1. 기본 용지 절단 명령
```python
content.append(b'\x1D\x56\x00')     # GS V 0 (Full cut)
```
**바이트 코드 분석**:
- `\x1D` = GS (Group Separator)
- `\x56` = 'V' (Paper cut command)
- `\x00` = 0 (Full cut mode)

**결과**: 정상 작동. 용지 절단 수행.

### 2. 피드 후 용지 절단 명령
```python
content.append(b'\x1D\x56\x42\x05') # GS V B 5 (Feed 5 lines then full cut)
```
**바이트 코드 분석**:
- `\x1D` = GS (Group Separator)
- `\x56` = 'V' (Paper cut command)
- `\x42` = 'B' (Feed before cut mode)
- `\x05` = 5 (Feed 5 lines)

**결과**: 정상 작동. 5줄 여백 추가 후 용지 절단.

### 3. 텍스트 정렬 명령
```python
content.append(b'\x1B\x61\x01')     # ESC a 1 (Center alignment)
content.append(b'\x1B\x61\x00')     # ESC a 0 (Left alignment)
```
**결과**: 정상 작동. 텍스트 정렬 변경 효과 확인.

### 4. 한글 지원 명령
```python
content.append(b'\x1B\x74\x12')     # ESC t 18 (CP949/EUC-KR codepage)
content.append(b'\x1C\x26')         # FS & (Korean mode)
content.append(b'\x1C\x2E')         # FS . (Cancel/Set)
```
**결과**: 정상 작동. 한글 출력 지원.

## 프린터 특성 분석

### 1. 용지 절약 최적화
BIXOLON SRP-330II는 **용지 절약을 위한 하드웨어 최적화**가 구현되어 있습니다:

- 연속적인 빈 줄 자동 압축
- 불필요한 라인 피드 명령 필터링
- 실제 텍스트 내용 기반 여백 결정

### 2. 선택적 ESC/POS 지원
표준 ESC/POS 명령어 중 일부만 선택적으로 지원:

**지원되는 명령 카테고리**:
- 텍스트 정렬 (ESC a)
- 문자 인코딩 (ESC t, FS &)
- 용지 절단 (GS V)
- 프린터 초기화 (ESC @)

**무시되는 명령 카테고리**:
- 단순 라인 피드 (LF, ESC d)
- 수동 여백 제어
- 연속 개행 문자

### 3. 하드웨어 레벨 필터링
소프트웨어에서 전송한 제어문자가 프린터 하드웨어에서 다음과 같이 처리됩니다:

1. **1차 필터링**: 연속된 `\n`, `\x0A` 문자 제거
2. **2차 필터링**: 불필요한 `ESC d` 명령 무시  
3. **3차 최적화**: 실제 출력에 필요한 최소 여백만 적용

## 개발 권장사항

### 1. 여백 제어 전략
```python
# ❌ 피해야 할 방식
content.append(b'\n\n\n')           # 무효
content.append(b'\x1B\x64\x03')     # 무효

# ✅ 권장하는 방식  
content.append(b'\x1D\x56\x42\x03') # 3줄 피드 후 절단
```

### 2. 텍스트 레벨 여백 관리
프린터 제어문자 대신 **텍스트 내용 자체에 여백을 포함**:

```python
def prepare_print_content(text):
    lines = wrap_text(text)
    lines.insert(0, "")        # 위 여백 (텍스트로)
    lines.append("")           # 아래 여백 (텍스트로)
    return lines
```

### 3. 이중 여백 방지
- 텍스트 레벨 여백과 프린터 명령 여백을 동시에 사용하지 않기
- 하나의 방식으로 통일하여 중복 방지

## 테스트 결과 요약

| 제어문자 | 바이트 코드 | 작동 여부 | 비고 |
|---------|------------|----------|------|
| 개행 문자 | `\n\n\n` | ❌ | 하드웨어에서 무시 |
| LF 직접 코드 | `\x0A * 3` | ❌ | ASCII 제어 코드 무시 |
| ESC 라인 피드 | `\x1B\x64\x03` | ❌ | 표준 ESC/POS 명령 무시 |
| GS 풀 컷 | `\x1D\x56\x00` | ✅ | 용지 절단 정상 |
| GS 피드 컷 | `\x1D\x56\x42\x05` | ✅ | 여백 추가 후 절단 |
| ESC 정렬 | `\x1B\x61\x01` | ✅ | 텍스트 정렬 정상 |
| 한글 모드 | `\x1B\x74\x12` | ✅ | 문자 인코딩 정상 |

## 기술적 함의

### 1. 프린터 펌웨어 특성
BIXOLON SRP-330II의 펌웨어는 **상업용 영수증 프린터**로서의 실용성을 우선시합니다:

- 용지 절약을 위한 적극적인 최적화
- 사용자 실수로 인한 과도한 용지 소모 방지
- 핵심 기능(절단, 정렬, 인코딩)에 집중

### 2. ESC/POS 표준과의 차이점
일반적인 ESC/POS 프린터와 달리 **선택적 명령 지원**:

- 모든 ESC/POS 명령을 지원하지 않음
- 프린터 제조사의 비즈니스 로직이 반영됨
- 하드웨어 최적화가 표준 준수보다 우선

### 3. 개발 시 고려사항
- **프린터별 테스트 필수**: 동일한 ESC/POS 명령도 프린터마다 다른 결과
- **대안 전략 준비**: 표준 명령이 무시될 경우를 대비한 우회 방법
- **실제 출력 확인**: 코드상 예상과 실제 출력 결과의 차이점 인지

## 결론

BIXOLON SRP-330II는 표준 ESC/POS 줄바꿈 명령을 무시하고, 특정 용지 제어 명령(`GS V B`)을 통해서만 여백 제어가 가능한 특별한 동작 특성을 보입니다. 이는 용지 절약을 위한 하드웨어 최적화 결과로 판단되며, 개발시에는 텍스트 레벨에서의 여백 관리나 특수 용지 제어 명령을 활용해야 합니다.

이러한 특성을 이해하고 적절히 대응하면, 효율적이고 안정적인 프린터 출력 시스템을 구축할 수 있습니다.