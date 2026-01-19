# 핸드폰 인증 모듈 테스트

이 디렉토리는 핸드폰 인증 모듈(`src/phone_verification`)의 종합적인 테스트 코드를 포함합니다.

## 📁 테스트 구조

```
tests/
├── conftest.py                           # pytest 설정 및 공통 픽스처
├── run_tests.py                          # 테스트 실행 스크립트
├── README.md                             # 이 파일
└── phone_verification/
    ├── __init__.py
    ├── test_domain.py                    # 도메인 계층 테스트
    ├── test_infrastructure.py           # 인프라스트럭처 계층 테스트
    ├── test_application.py              # 애플리케이션 계층 테스트
    ├── test_interface.py                # 인터페이스 계층 (API) 테스트
    └── test_integration.py              # 통합 테스트
```

## 🧪 테스트 범위

### 1. 도메인 계층 테스트 (`test_domain.py`)
- **PhoneVerificationRequest**: 입력 검증, 전화번호/생년월일 유효성
- **PhoneVerificationSession**: 세션 생성, 만료 확인
- **VerificationStatus**: 상태 전이 로직
- **KCPConfiguration**: 테스트/운영 설정
- **PhoneVerificationDomainService**: 도메인 서비스 로직
- **PhoneVerificationModel**: 데이터 모델 검증

### 2. 인프라스트럭처 계층 테스트 (`test_infrastructure.py`)
- **KCPService**: 해시 생성/검증, 암호화 데이터 복호화
- **KCPEncryptor**: 토큰 암호화/복호화
- **PhoneVerificationRepository**: 데이터베이스 CRUD 연산
- **만료 세션 정리**: 자동 정리 로직
- **중복 확인**: CI/DI 기반 중복 검사

### 3. 애플리케이션 계층 테스트 (`test_application.py`)
- **인증 시작**: 비즈니스 로직, 중복 방지
- **콜백 처리**: KCP 응답 처리, 보안 검증
- **상태 조회**: 세션 상태 관리
- **토큰 관리**: 생성/검증
- **에러 처리**: 다양한 예외 상황

### 4. 인터페이스 계층 테스트 (`test_interface.py`)
- **API 엔드포인트**: 모든 REST API 검증
- **요청/응답 검증**: 데이터 형식 확인
- **HTTP 상태 코드**: 적절한 응답 코드
- **에러 응답**: API 레벨 에러 처리
- **입력 유효성**: FastAPI 검증 로직

### 5. 통합 테스트 (`test_integration.py`)
- **전체 플로우**: 인증 시작 → 콜백 → 완료
- **실패 시나리오**: 다양한 실패 케이스
- **보안 검증**: 해시 변조 감지
- **사용자 이력**: 인증 이력 관리
- **정리 작업**: 만료 세션 처리

## 🚀 테스트 실행 방법

### 1. 환경 설정

```bash
# 개발 의존성 설치
cd backend
pip install -e ".[dev]"

# 또는 특정 패키지 설치
pip install pytest pytest-asyncio pytest-cov httpx
```

### 2. 전체 테스트 실행

```bash
# 자동화된 테스트 실행기 사용 (권장)
python tests/run_tests.py

# 또는 직접 pytest 실행
pytest tests/phone_verification/ -v
```

### 3. 특정 테스트 실행

```bash
# 도메인 계층만 테스트
pytest tests/phone_verification/test_domain.py -v

# 특정 테스트 클래스 실행
pytest tests/phone_verification/test_domain.py::TestPhoneVerificationRequest -v

# 특정 테스트 메서드 실행
pytest tests/phone_verification/test_domain.py::TestPhoneVerificationRequest::test_valid_phone_request_creation -v
```

### 4. 커버리지 측정

```bash
# 커버리지 리포트 생성
pytest tests/phone_verification/ --cov=src/phone_verification --cov-report=html --cov-report=term

# HTML 리포트 확인
open htmlcov/index.html
```

### 5. 코드 품질 검사

```bash
# 포맷팅 검사
black --check src/phone_verification tests/phone_verification

# Import 순서 검사
isort --check-only src/phone_verification tests/phone_verification

# 스타일 검사
flake8 src/phone_verification

# 타입 검사
mypy src/phone_verification
```

## 🎯 테스트 마커 활용

```bash
# 단위 테스트만 실행
pytest -m unit tests/phone_verification/

# 통합 테스트만 실행
pytest -m integration tests/phone_verification/

# 느린 테스트 제외
pytest -m "not slow" tests/phone_verification/
```

## 📊 커버리지 목표

- **전체 커버리지**: 90% 이상
- **도메인 계층**: 95% 이상
- **애플리케이션 계층**: 90% 이상
- **인프라 계층**: 85% 이상
- **인터페이스 계층**: 90% 이상

## 🔧 테스트 픽스처

`conftest.py`에서 제공하는 주요 픽스처:

- `test_session`: 테스트용 데이터베이스 세션
- `test_client`: FastAPI 테스트 클라이언트
- `test_kcp_config`: 테스트용 KCP 설정
- `valid_phone_request`: 유효한 인증 요청
- `test_verification_session`: 테스트용 인증 세션
- `completed_verification`: 완료된 인증 데이터
- `expired_verification`: 만료된 인증 데이터

## 🐛 테스트 디버깅

### 실패한 테스트 분석
```bash
# 상세한 출력으로 실행
pytest tests/phone_verification/ -vvv

# 첫 번째 실패에서 중단
pytest tests/phone_verification/ -x

# 마지막 실패 부분만 표시
pytest tests/phone_verification/ --tb=short
```

### 특정 테스트 디버깅
```bash
# pdb 디버거 사용
pytest tests/phone_verification/test_domain.py::test_method_name -s --pdb
```

## 📝 테스트 작성 가이드

### 1. 명명 규칙
- 테스트 파일: `test_*.py`
- 테스트 클래스: `Test*`
- 테스트 메서드: `test_*`

### 2. 테스트 구조
```python
@pytest.mark.asyncio
async def test_feature_success_scenario(self, fixtures):
    \"\"\"기능 성공 시나리오 테스트\"\"\"
    # Given: 테스트 데이터 준비
    
    # When: 테스트 대상 실행
    
    # Then: 결과 검증
    assert expected == actual
```

### 3. Mock 사용
```python
with patch('module.ClassName.method_name') as mock_method:
    mock_method.return_value = expected_value
    # 테스트 실행
```

## 🔒 보안 테스트

- **해시 변조 감지**: dn_hash 검증 로직
- **입력 검증**: SQL 인젝션, XSS 방지
- **세션 보안**: 만료 처리, 권한 확인
- **토큰 보안**: 암호화/복호화 검증

## 🚨 CI/CD 통합

```yaml
# GitHub Actions 예시
- name: Run Tests
  run: |
    cd backend
    python tests/run_tests.py
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./backend/htmlcov/coverage.xml
```

## 📈 성능 테스트

현재는 기능 테스트 위주이며, 성능 테스트는 향후 추가 예정:

- **응답 시간 측정**: API 엔드포인트별 성능
- **동시성 테스트**: 다중 사용자 시나리오
- **메모리 사용량**: 리소스 사용 최적화
- **데이터베이스 성능**: 쿼리 최적화

## 🤝 기여 가이드

새로운 테스트 추가 시:

1. **적절한 계층의 테스트 파일에 추가**
2. **픽스처 활용으로 중복 코드 방지**
3. **명확한 테스트 이름과 문서화**
4. **다양한 시나리오 커버**
5. **커버리지 목표 달성 확인**

## 📞 문의

테스트 관련 문의사항은 개발팀에 연락해주세요.

---

*이 테스트 스위트는 핸드폰 인증 모듈의 안정성과 품질을 보장하기 위해 지속적으로 개선되고 있습니다.*