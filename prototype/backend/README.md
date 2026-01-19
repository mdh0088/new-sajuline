# Sajuline Backend

사주라인 리뉴얼 백엔드 (FastAPI)

## Quickstart
```bash
uvicorn src.main:app --reload
```

## Logging Quickstart
- 미들웨어/핸들러 등록은 `src/main.py`에서 완료되어 있습니다.
- 도메인 이벤트는 다음처럼 사용하세요:
```python
from src.common.logging.events import log_event
log_event("auth.login.success", domain="app.auth", user_id="u1", session_id="s1")
```
- 자세한 문서: `backend/docs/logging/` (ADR, How-to, Cookbook) 