# 작업 완료 시 수행해야 할 체크리스트

## 필수 체크리스트 (모든 작업 완료 후)

### 1. 코드 품질 검사

#### Backend (Python/FastAPI)
```bash
# 순서대로 실행 필수
cd backend

# 1. 코드 포매팅
black src/
isort src/

# 2. 린팅 검사
flake8 src/

# 3. 타입 체크
mypy src/

# 4. 테스트 실행
pytest
pytest --cov=src tests/  # 커버리지 포함
```

#### Frontend (TypeScript/Nuxt.js)  
```bash
cd frontend

# 1. 린팅 및 자동 수정
npm run lint:fix

# 2. 코드 포매팅
npm run format

# 3. 타입 체크
npm run type-check

# 4. 빌드 확인
npm run build
```

### 2. 테스트 확인
- [ ] 모든 단위 테스트 통과
- [ ] API 엔드포인트 동작 확인
- [ ] 프론트엔드 컴포넌트 렌더링 확인
- [ ] 통합 테스트 통과 (해당하는 경우)

### 3. 성능 검증
- [ ] API 응답 시간 확인 (p95 < 300ms)
- [ ] 페이지 로드 시간 확인 (LCP < 2.5s)
- [ ] 메모리 누수 체크
- [ ] 데이터베이스 쿼리 최적화 확인

### 4. 보안 점검
- [ ] 입력 검증 구현 여부
- [ ] 인증/인가 로직 확인
- [ ] 민감 정보 노출 방지 확인
- [ ] CORS 설정 적절성 확인

### 5. 문서화
- [ ] API 문서 업데이트 (Swagger)
- [ ] README 파일 업데이트 (필요시)
- [ ] 코드 주석 적절성 확인
- [ ] 변경 사항 CHANGELOG 기록

### 6. Git 워크플로
```bash
# 변경사항 확인
git status
git diff

# 적절한 커밋 메시지로 커밋
git add .
git commit -m "feat(domain): implement specific functionality

- Add new endpoint for user management
- Implement validation logic
- Update database schema

Closes #123"

# 푸시 전 최종 로그 확인
git log --oneline -3
```

## 배포 전 최종 점검

### 1. 환경별 설정 확인
- [ ] .env.development 설정 확인
- [ ] .env.production 설정 확인  
- [ ] Docker 환경 변수 확인
- [ ] 데이터베이스 마이그레이션 확인

### 2. 의존성 관리
- [ ] package.json / pyproject.toml 업데이트
- [ ] 보안 취약점 체크
- [ ] 라이선스 호환성 확인

### 3. 모니터링 준비
- [ ] 로그 레벨 적절성 확인
- [ ] Sentry 설정 확인 (에러 추적)
- [ ] 헬스체크 엔드포인트 동작 확인

## 코드 리뷰 전 자가 점검

### 1. 코드 품질
- [ ] DRY 원칙 준수
- [ ] SOLID 원칙 적용
- [ ] 함수 길이 20줄 이하
- [ ] 순환 복잡도 10 이하
- [ ] 네이밍 컨벤션 준수

### 2. 아키텍처 일관성
- [ ] 도메인별 레이어 분리 확인
- [ ] 의존성 방향성 확인
- [ ] 공통 컴포넌트 활용 확인

### 3. 테스트 커버리지
- [ ] 핵심 비즈니스 로직 테스트
- [ ] 에러 케이스 테스트
- [ ] 엣지 케이스 테스트
- [ ] 통합 시나리오 테스트

## 에러 대응 가이드

### 빌드 에러 발생 시
1. **Backend 에러**
   ```bash
   # 의존성 문제
   pip install -e ".[dev]" --upgrade
   
   # 타입 에러
   mypy src/ --show-error-codes
   
   # 테스트 실패
   pytest -vvs --tb=short
   ```

2. **Frontend 에러**
   ```bash
   # 의존성 문제  
   rm -rf node_modules package-lock.json
   npm install
   
   # 타입 에러
   npm run type-check -- --verbose
   
   # 빌드 에러
   npm run build -- --verbose
   ```

### 품질 검사 실패 시
1. **린팅 에러**: `npm run lint:fix` 또는 `black src/ && isort src/`
2. **타입 에러**: 타입 어노테이션 추가 및 수정
3. **테스트 실패**: 로직 수정 또는 테스트 케이스 보완

## CI/CD 파이프라인 준비

### GitHub Actions 기본 체크
```yaml
# .github/workflows/ci.yml 기본 구조
name: CI
on: [push, pull_request]
jobs:
  backend-test:
    # Backend 테스트 및 품질 검사
  frontend-test:
    # Frontend 테스트 및 빌드 검사
  integration-test:
    # Docker Compose 통합 테스트
```

### 배포 태그 생성
```bash
# 의미있는 버전 태깅
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 팀 협업 가이드

### 1. 브랜치 전략
- `main`: 프로덕션 레디 코드
- `develop`: 개발 통합 브랜치
- `feature/*`: 기능 개발 브랜치
- `hotfix/*`: 긴급 수정 브랜치

### 2. 풀 리퀘스트 체크리스트
- [ ] 위의 모든 품질 검사 통과
- [ ] 적절한 PR 제목 및 설명
- [ ] 관련 이슈 링크
- [ ] 스크린샷 첨부 (UI 변경 시)
- [ ] 테스트 계획 명시

### 3. 코드 리뷰 포인트
- [ ] 비즈니스 로직 정확성
- [ ] 성능 영향도
- [ ] 보안 고려사항
- [ ] 재사용 가능성
- [ ] 유지보수성