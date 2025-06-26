#!/usr/bin/env python3
"""
빅솔론 프린터 간단 출력 스크립트 (CUPS 사용)
사용법: python3 print_text.py "출력할 텍스트"
"""

import sys
import subprocess
import tempfile
import argparse

def get_text_width(text):
    """텍스트의 실제 폭 계산 (한글=2, 영문=1)"""
    width = 0
    for char in text:
        if ord(char) > 127:  # 한글/특수문자
            width += 2
        else:  # 영문/숫자
            width += 1
    return width

def wrap_text(text, max_width=40):
    """텍스트를 지정된 폭으로 줄바꿈"""
    lines = []
    current_line = ""
    current_width = 0
    
    words = text.split()
    
    for word in words:
        word_width = get_text_width(word)
        space_width = 1 if current_line else 0
        
        # 현재 줄에 단어를 추가할 수 있는지 확인
        if current_width + space_width + word_width <= max_width:
            if current_line:
                current_line += " "
                current_width += 1
            current_line += word
            current_width += word_width
        else:
            # 현재 줄을 완성하고 새 줄 시작
            if current_line:
                lines.append(current_line)
            current_line = word
            current_width = word_width
    
    # 마지막 줄 추가
    if current_line:
        lines.append(current_line)
    
    return lines

def center_text(text, width=40):
    """텍스트를 가운데 정렬"""
    text_width = get_text_width(text)
    if text_width >= width:
        return text
    
    padding = (width - text_width) // 2
    return " " * padding + text

def prepare_print_content(text, min_lines=6):
    """출력할 내용 준비"""
    # 텍스트를 줄바꿈
    lines = wrap_text(text, max_width=40)
    
    # 위아래 여백 추가
    lines.insert(0, "")  # 위에 1줄 여백
    
    # 아래 여백 계산
    text_line_count = len(lines) - 1  # 위 여백 제외한 실제 텍스트 줄 수
    if text_line_count == 1:
        bottom_padding = 3
    elif text_line_count == 2:
        bottom_padding = 2
    else:
        bottom_padding = 1
    
    # 아래 여백 추가
    for _ in range(bottom_padding):
        lines.append("")
    
    return lines

def create_esc_pos_content(lines):
    """ESC/POS 명령어가 포함된 출력 내용 생성"""
    content = []
    
    # 프린터 초기화
    content.append(b'\x1B\x40')  # ESC @
    
    # 한글 지원을 위한 코드페이지 설정
    content.append(b'\x1B\x74\x12')  # ESC t 18 (CP949/EUC-KR)
    content.append(b'\x1C\x26')      # FS & (한글 모드)
    content.append(b'\x1C\x2E')      # FS . (취소 후 설정)
    
    # 가운데 정렬 설정
    content.append(b'\x1B\x61\x01')  # ESC a 1
    
    # 각 줄 추가
    for line in lines:
        try:
            # EUC-KR 인코딩 시도
            content.append(line.encode('euc-kr') + b'\n')
        except UnicodeEncodeError:
            # 실패시 UTF-8 사용
            content.append(line.encode('utf-8') + b'\n')
    
    # 추가 여백
    content.append(b'\n')
    
    # 좌측 정렬로 복귀
    content.append(b'\x1B\x61\x00')  # ESC a 0
    
    # 용지 절단
    content.append(b'\n\n\n')  # 추가 라인 피드
    content.append(b'\x1D\x56\x00')  # GS V 0 (풀 컷)
    
    return b''.join(content)

def get_available_printers():
    """사용 가능한 프린터 목록 가져오기"""
    try:
        result = subprocess.run(['lpstat', '-p'], capture_output=True, text=True)
        if result.returncode == 0:
            printers = []
            for line in result.stdout.split('\n'):
                if line.startswith('printer '):
                    printer_name = line.split()[1]
                    printers.append(printer_name)
            return printers
        return []
    except Exception:
        return []

def print_to_cups(text, printer_name="BIXOLON_SRP_330II"):
    """CUPS를 통해 프린터로 출력"""
    try:
        # 출력할 내용 준비
        lines = prepare_print_content(text)
        
        # ESC/POS 명령어 포함한 내용 생성
        print_content = create_esc_pos_content(lines)
        
        # 임시 파일 생성
        with tempfile.NamedTemporaryFile(delete=False, suffix='.bin') as temp_file:
            temp_file.write(print_content)
            temp_file_path = temp_file.name
        
        # lp 명령어로 출력
        cmd = ['lp', '-d', printer_name, '-o', 'raw', temp_file_path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # 임시 파일 삭제
        import os
        os.unlink(temp_file_path)
        
        if result.returncode == 0:
            print(f"✅ 출력 완료: {len(lines)}줄 → {printer_name}")
            if result.stdout.strip():
                print(f"📝 작업 ID: {result.stdout.strip()}")
            return True
        else:
            print(f"❌ 출력 실패: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 출력 오류: {e}")
        return False

def check_printer_status(printer_name):
    """프린터 상태 확인"""
    try:
        result = subprocess.run(['lpstat', '-p', printer_name], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return f"프린터 '{printer_name}'을 찾을 수 없습니다."
    except Exception as e:
        return f"상태 확인 실패: {e}"

def main():
    parser = argparse.ArgumentParser(description='빅솔론 프린터 텍스트 출력 (CUPS 사용)')
    parser.add_argument('text', nargs='?', help='출력할 텍스트')
    parser.add_argument('-p', '--printer', default='BIXOLON_SRP_330II', help='프린터 이름 (기본값: BIXOLON_SRP_330II)')
    parser.add_argument('--preview', action='store_true', help='출력 미리보기만 표시')
    parser.add_argument('--list-printers', action='store_true', help='사용 가능한 프린터 목록 표시')
    parser.add_argument('--status', action='store_true', help='프린터 상태 확인')
    
    args = parser.parse_args()
    
    # 프린터 목록 표시
    if args.list_printers:
        printers = get_available_printers()
        if printers:
            print("🖨️  사용 가능한 프린터:")
            for printer in printers:
                status = check_printer_status(printer)
                print(f"  - {printer}")
                print(f"    {status}")
        else:
            print("❌ CUPS에 등록된 프린터가 없습니다.")
            print("💡 다음 명령으로 프린터를 확인하세요: lpstat -p")
        return
    
    # 프린터 상태 확인
    if args.status:
        status = check_printer_status(args.printer)
        print(f"📊 프린터 상태: {args.printer}")
        print(status)
        return
    
    # 텍스트가 없으면 에러
    if not args.text:
        print("❌ 출력할 텍스트를 입력하세요.")
        print("💡 사용법: python3 print_text.py \"출력할 텍스트\"")
        return
    
    # 출력 미리보기
    if args.preview:
        lines = prepare_print_content(args.text)
        print("📄 출력 미리보기:")
        print("=" * 42)
        for line in lines:
            print(f"|{line:<40}|")
        print("=" * 42)
        print(f"총 {len(lines)}줄")
        return
    
    # 실제 출력
    success = print_to_cups(args.text, args.printer)
    
    if not success:
        print("\n🔧 문제 해결 방법:")
        print("1. 프린터가 CUPS에 등록되어 있는지 확인: --list-printers")
        print("2. 프린터 상태 확인: --status")
        print("3. 프린터 이름이 정확한지 확인: -p 프린터이름")
        print("4. CUPS 서비스 상태 확인: brew services list | grep cups")
        print("5. 미리보기로 내용 확인: --preview")

if __name__ == "__main__":
    main()