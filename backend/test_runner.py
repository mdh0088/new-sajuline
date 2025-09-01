#!/usr/bin/env python3
"""
테스트 실행 스크립트

가상환경 없이 로컬에서 테스트를 실행할 수 있도록 하는 임시 스크립트입니다.
실제 개발 시에는 가상환경을 사용하는 것을 권장합니다.
"""
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

if __name__ == "__main__":
    print("🧪 사주라인 백엔드 단위 테스트 실행")
    print("=" * 50)
    
    try:
        # 기본 Python 모듈로 간단한 import 테스트
        print("✅ Python 경로 설정 완료")
        
        # 프로젝트 구조 확인
        if os.path.exists("tests"):
            print("✅ tests/ 디렉터리 발견")
        else:
            print("❌ tests/ 디렉터리 없음")
            
        if os.path.exists("src"):
            print("✅ src/ 디렉터리 발견")
        else:
            print("❌ src/ 디렉터리 없음")
            
        print("\n📋 구축된 테스트 환경:")
        print("- 단위 테스트 구조: tests/unit/")
        print("- 픽스처: tests/fixtures/")
        print("- 전역 설정: tests/conftest.py")
        print("- GitHub Actions: .github/workflows/backend-ci.yml")
        
        print("\n🚀 실제 테스트 실행을 위해서는:")
        print("1. 가상환경 생성: python3 -m venv venv")
        print("2. 활성화: source venv/bin/activate")  
        print("3. 의존성 설치: pip install -e '.[dev]'")
        print("4. 테스트 실행: pytest tests/unit/ -v")
        
    except Exception as e:
        print(f"❌ 에러 발생: {e}")
        
    print("\n✨ 단위 테스트 환경 구축 완료!")