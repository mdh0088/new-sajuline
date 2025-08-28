#!/usr/bin/env python3
"""AI 운세 API 테스트 스크립트"""

import requests
import json
import time


def test_ai_fortune_api():
    """AI 운세 API 테스트"""
    
    # API 엔드포인트
    url = "http://localhost:8000/api/ai/fortune/demo"
    
    # 테스트 데이터
    test_data = {
        "user_info": {
            "name": "홍길동",
            "birth_date": "1990-01-01", 
            "birth_time": "14:30",
            "gender": "M",
            "calendar_type": "solar"
        }
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        print("🚀 AI 운세 API 테스트 시작...")
        print(f"URL: {url}")
        print(f"데이터: {json.dumps(test_data, ensure_ascii=False, indent=2)}")
        
        # API 호출
        start_time = time.time()
        response = requests.post(url, json=test_data, headers=headers, timeout=30)
        end_time = time.time()
        
        print(f"⏱️ 응답 시간: {(end_time - start_time):.2f}초")
        print(f"📊 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ API 호출 성공!")
            print(f"📄 응답 데이터:")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            
            # 응답 데이터 검증
            if result.get("success"):
                data = result.get("data", {})
                saju_result = data.get("saju_result", {})
                fortune_result = data.get("fortune_result", {})
                
                print("\n🔍 응답 데이터 검증:")
                print(f"- 사용자 요약: {data.get('user_summary')}")
                print(f"- 사주 기둥 수: {len(saju_result.get('pillars', []))}")
                print(f"- 오행 요소 수: {len(saju_result.get('elements', []))}")
                print(f"- 종합운 점수: {fortune_result.get('total', {}).get('score')}")
                print(f"- 연애운 점수: {fortune_result.get('love', {}).get('score')}")
                print(f"- 금전운 점수: {fortune_result.get('money', {}).get('score')}")
                print(f"- 직업운 점수: {fortune_result.get('work', {}).get('score')}")
                print(f"- 건강운 점수: {fortune_result.get('health', {}).get('score')}")
                
                print("\n✅ 모든 검증 통과!")
            else:
                print("❌ API 응답에서 success가 False입니다.")
                
        else:
            print(f"❌ API 호출 실패: {response.status_code}")
            print(f"에러 메시지: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.")
    except requests.exceptions.Timeout:
        print("❌ 요청 시간이 초과되었습니다.")
    except Exception as e:
        print(f"❌ 예상치 못한 오류: {str(e)}")


def test_health_check():
    """헬스 체크 테스트"""
    
    try:
        print("\n🏥 헬스 체크 테스트...")
        response = requests.get("http://localhost:8000/api/ai/health", timeout=10)
        
        print(f"📊 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 헬스 체크 성공!")
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(f"❌ 헬스 체크 실패: {response.text}")
            
    except Exception as e:
        print(f"❌ 헬스 체크 오류: {str(e)}")


def test_api_docs():
    """API 문서 테스트"""
    
    try:
        print("\n📚 API 문서 접근 테스트...")
        response = requests.get("http://localhost:8000/docs", timeout=10)
        
        print(f"📊 상태 코드: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API 문서 접근 성공!")
            print("🌐 브라우저에서 http://localhost:8000/docs 에서 확인 가능합니다.")
        else:
            print(f"❌ API 문서 접근 실패: {response.status_code}")
            
    except Exception as e:
        print(f"❌ API 문서 접근 오류: {str(e)}")


if __name__ == "__main__":
    print("=" * 60)
    print("🔮 사주라인 AI 운세 API 테스트")
    print("=" * 60)
    
    # 기본 헬스 체크
    test_health_check()
    
    # API 문서 테스트
    test_api_docs()
    
    # AI 운세 API 테스트
    test_ai_fortune_api()
    
    print("\n" + "=" * 60)
    print("🎉 테스트 완료!")
    print("=" * 60) 