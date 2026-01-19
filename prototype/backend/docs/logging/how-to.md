# How-to: 표준 로깅 사용법

## 1) FastAPI 등록
```python
from src.common.middleware.logging import LoggingMiddleware
from src.common.exceptions.handlers import setup_exception_handlers

app.add_middleware(LoggingMiddleware)
setup_exception_handlers(app)
```

- CORS, TrustedHost 뒤에 두되, 보안 헤더 이전/이후 어느 위치에서도 동작합니다.
- 미들웨어는 `X-Request-ID`를 수용/생성하고 응답 헤더에 반영합니다.

## 2) 도메인 이벤트 로깅
```python
from src.common.logging.events import log_event

# 성공
log_event("auth.login.success", domain="app.auth", user_id="u1", session_id="s123", channel="password")

# 실패
log_event("payment.charge.fail", domain="app.payment", level="ERROR", user_id="u1", order_id="o1", amount=10000, error_code="PG_TIMEOUT", reason="gateway" )
```

- 레벨 기준: 성공=INFO, 경고상황=WARNING, 실패/예외=ERROR
- 표준 컨텍스트 키: `user_id, session_id, order_id, counselor_id, amount, currency, channel, referer`

## 3) 보안 체크리스트
- [ ] password/token/authorization/cookie/ssn/email 로그 금지(헬퍼/미들웨어 마스킹 내장)
- [ ] 대용량 페이로드(파일/multipart)는 로그 제외(미들웨어 자동)
- [ ] 사용자의 원문 입력을 그대로 남기지 않기

## 4) Uvicorn log_config 예시
`src/main.py`에서 이미 dictConfig를 사용합니다. 외부 실행 시:
```bash
uvicorn src.main:app --log-level info
```

## 5) 문제 해결
- JSON 출력: `LOG_JSON=true`
- 파일 출력: `LOG_TO_FILE=true` + `LOG_DIR`/`LOG_FILE_NAME`
- 콘솔만: `LOG_TO_STDOUT=true`
