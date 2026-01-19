#!/usr/bin/env python3
"""
Test Runner for Phone Verification Module

핸드폰 인증 모듈 테스트 실행기
"""
import asyncio
import sys
import subprocess
from pathlib import Path


def run_command(command: str, description: str) -> bool:
    """명령어 실행 및 결과 출력"""
    print(f"\n{'='*60}")
    print(f"🔄 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            command.split(),
            capture_output=True,
            text=True,
            check=True
        )
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        
        print(f"✅ {description} - 성공")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} - 실패")
        print(f"Return code: {e.returncode}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False


def main():
    """테스트 실행 메인 함수"""
    # 프로젝트 루트 디렉토리로 이동
    backend_dir = Path(__file__).parent.parent
    print(f"📁 백엔드 디렉토리: {backend_dir}")
    
    # 테스트 명령어들
    test_commands = [
        # 코드 품질 검사
        ("black --check .", "Black 코드 포맷팅 검사"),
        ("isort --check-only .", "isort import 순서 검사"),
        ("flake8 src/phone_verification", "Flake8 코드 스타일 검사"),
        ("mypy src/phone_verification", "MyPy 타입 검사"),
        
        # 단위 테스트
        ("pytest tests/phone_verification/test_domain.py -v", "도메인 계층 테스트"),
        ("pytest tests/phone_verification/test_infrastructure.py -v", "인프라 계층 테스트"),
        ("pytest tests/phone_verification/test_application.py -v", "애플리케이션 계층 테스트"),
        ("pytest tests/phone_verification/test_interface.py -v", "인터페이스 계층 테스트"),
        
        # 통합 테스트
        ("pytest tests/phone_verification/test_integration.py -v", "통합 테스트"),
        
        # 전체 테스트 (커버리지 포함)
        ("pytest tests/phone_verification/ --cov=src/phone_verification --cov-report=html --cov-report=term", "전체 테스트 + 커버리지"),
    ]
    
    print("🚀 핸드폰 인증 모듈 테스트 실행")
    print(f"📍 작업 디렉토리: {backend_dir}")
    
    # 작업 디렉토리 변경
    import os
    os.chdir(backend_dir)
    
    success_count = 0
    total_count = len(test_commands)
    
    for command, description in test_commands:
        if run_command(command, description):
            success_count += 1
    
    # 결과 요약
    print(f"\n{'='*60}")
    print("📊 테스트 실행 결과 요약")
    print(f"{'='*60}")
    print(f"✅ 성공: {success_count}/{total_count}")
    print(f"❌ 실패: {total_count - success_count}/{total_count}")
    
    if success_count == total_count:
        print("🎉 모든 테스트가 성공적으로 완료되었습니다!")
        return 0
    else:
        print("⚠️ 일부 테스트가 실패했습니다. 위의 로그를 확인해주세요.")
        return 1


if __name__ == "__main__":
    sys.exit(main())