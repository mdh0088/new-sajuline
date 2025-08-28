# Cookbook: 로깅 패턴 모음

## 도메인별 샘플
```python
# Auth 로그인
log_event("auth.login.success", domain="app.auth", user_id=uid, session_id=sid, channel="password")
log_event("auth.login.fail", domain="app.auth", level="ERROR", user_id=uid, error_code="INVALID_PASSWORD", reason="invalid_credentials")

# 포인트 충전/사용
log_event("payment.charge.success", domain="app.payment", user_id=uid, order_id=txn, amount=1000, currency="P", balance_after=11000)
log_event("payment.charge.fail", domain="app.payment", level="ERROR", user_id=uid, order_id=txn, amount=5000, error_code="POINTS_INSUFFICIENT", reason="insufficient_balance")

# 휴대폰 인증
log_event("phone.verify.send.success", domain="app.auth", channel="sms", referer="api")
log_event("phone.verify.send.fail", domain="app.auth", level="ERROR", error_code="VALIDATION_ERROR", reason="invalid_phone")
```

## Uvicorn/프로세스 실행
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --log-level info
```

## Docker Compose (요약)
```yaml
services:
  backend:
    build: ./backend
    environment:
      - LOG_JSON=true
      - LOG_LEVEL=INFO
      - LOG_TO_STDOUT=true
    volumes:
      - ./logs:/var/log/app
    ports:
      - "8000:8000"
```
