#!/usr/bin/env python3
"""
통합 MCP 서버 시작 스크립트
FastAPI 서버와 MCP wrapper를 모두 관리
"""

import os
import sys
import asyncio
import subprocess
import signal
import time
from pathlib import Path

# 현재 스크립트의 디렉터리
PROJECT_DIR = Path(__file__).parent

class MCPServerManager:
    def __init__(self):
        self.fastapi_process = None
        self.running = True
        
    def start_fastapi_server(self):
        """FastAPI 서버 시작"""
        try:
            # 가상환경의 Python 사용
            python_path = PROJECT_DIR / ".venv" / "bin" / "python"
            server_path = PROJECT_DIR / "server.py"
            
            print(f"🚀 FastAPI 서버 시작: {server_path}")
            
            self.fastapi_process = subprocess.Popen(
                [str(python_path), str(server_path)],
                cwd=PROJECT_DIR,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy()
            )
            
            # 서버 시작 대기
            time.sleep(2)
            
            if self.fastapi_process.poll() is None:
                print("✅ FastAPI 서버가 시작되었습니다 (PID: {})".format(self.fastapi_process.pid))
                return True
            else:
                stdout, stderr = self.fastapi_process.communicate()
                print(f"❌ FastAPI 서버 시작 실패:")
                print(f"STDOUT: {stdout.decode()}")
                print(f"STDERR: {stderr.decode()}")
                return False
                
        except Exception as e:
            print(f"❌ FastAPI 서버 시작 오류: {e}")
            return False
    
    def stop_fastapi_server(self):
        """FastAPI 서버 종료"""
        if self.fastapi_process and self.fastapi_process.poll() is None:
            print("🛑 FastAPI 서버 종료 중...")
            self.fastapi_process.terminate()
            try:
                self.fastapi_process.wait(timeout=5)
                print("✅ FastAPI 서버가 정상 종료되었습니다")
            except subprocess.TimeoutExpired:
                print("⚠️ 강제 종료합니다...")
                self.fastapi_process.kill()
                self.fastapi_process.wait()
    
    def handle_signal(self, signum, frame):
        """시그널 처리 (Ctrl+C)"""
        print(f"\n🔔 시그널 {signum} 수신, 종료합니다...")
        self.running = False
        self.stop_fastapi_server()
        sys.exit(0)
    
    async def start_mcp_wrapper(self):
        """MCP wrapper 시작"""
        try:
            # MCP wrapper import 및 실행
            sys.path.insert(0, str(PROJECT_DIR))
            from mcp_wrapper import MCPServer
            
            print("🔗 MCP wrapper 시작...")
            async with MCPServer() as server:
                await server.run()
                
        except Exception as e:
            print(f"❌ MCP wrapper 오류: {e}")
            self.stop_fastapi_server()
            sys.exit(1)
    
    async def run(self):
        """전체 시스템 실행"""
        # 시그널 핸들러 등록
        signal.signal(signal.SIGINT, self.handle_signal)
        signal.signal(signal.SIGTERM, self.handle_signal)
        
        # FastAPI 서버 시작
        if not self.start_fastapi_server():
            print("❌ FastAPI 서버 시작 실패, 종료합니다.")
            sys.exit(1)
        
        try:
            # MCP wrapper 실행
            await self.start_mcp_wrapper()
        finally:
            self.stop_fastapi_server()

def main():
    print("🎯 MCP Receipt Printer Server 시작")
    print("=" * 50)
    
    # 프로젝트 디렉터리로 이동
    os.chdir(PROJECT_DIR)
    
    # 가상환경 확인
    venv_python = PROJECT_DIR / ".venv" / "bin" / "python"
    if not venv_python.exists():
        print("❌ 가상환경을 찾을 수 없습니다:")
        print(f"   {venv_python}")
        print("다음 명령으로 가상환경을 생성하세요:")
        print("   python3 -m venv .venv")
        print("   source .venv/bin/activate")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    
    # 매니저 실행
    manager = MCPServerManager()
    
    try:
        asyncio.run(manager.run())
    except KeyboardInterrupt:
        print("\n👋 사용자가 종료했습니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {e}")
        manager.stop_fastapi_server()
        sys.exit(1)

if __name__ == "__main__":
    main()