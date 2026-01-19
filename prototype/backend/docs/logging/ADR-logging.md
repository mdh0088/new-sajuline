# ADR: 표준 로깅 시스템 채택 (FastAPI + JSON Structured Logging)

## 결정
- Python `logging` + `python-json-logger` 기반 구조화 로깅을 채택한다.
- 요청/응답/에러는 FastAPI 미들웨어와 전역 예외 핸들러가 자동 기록한다.
- 도메인 이벤트는 `log_event(event, *, domain, level, **context)` 헬퍼를 사용한다.

## 배경
- 마이크로서비스/모놀리식 혼합 환경에서 일관된 로그 스키마 필요
- 추적성(trace_id), 사용자 컨텍스트(user_id) 자동 주입 필요
- 보안(PII 마스킹)과 성능(바디 제한) 고려

## 상세
- 미들웨어: `X-Request-ID` 수용/생성, 2KB 이하 JSON 바디만 기록, multipart 제외
- 예외 핸들러: 4xx=WARNING, 5xx=ERROR, `exc_info=True` 스택트레이스 포함
- 컨텍스트: `trace_id`(요청), `user_id`(인증 의존성) ContextVar로 자동 주입
- 도메인 이벤트: `app.auth`, `app.payment` 등 네임스페이스 사용

## 환경변수
- `LOG_LEVEL` (DEBUG|INFO|WARNING|ERROR|CRITICAL)
- `LOG_JSON` (true|false) JSON 출력 토글
- `LOG_TO_STDOUT` (true|false), `LOG_TO_FILE` (true|false)
- `LOG_DIR`, `LOG_FILE_NAME`, `LOG_RETENTION_DAYS`
- `SERVICE_NAME`, `SERVICE_VERSION`, `ENV`

## 운영/퍼미션
- Linux: `/var/log/app/*.log` (서비스 사용자에 쓰기 권한)
- Windows: `C:\\var\\log\\app\\app.log`
- 로테이션: TimedRotating(midnight), 보관일수 `LOG_RETENTION_DAYS`

## Docker/Compose
```yaml
services:
  backend:
    environment:
      - LOG_JSON=true
      - LOG_LEVEL=INFO
      - LOG_TO_STDOUT=true
    volumes:
      - ./logs:/var/log/app
```

## 보안(PII)
- 마스킹 키: `password, token, authorization, cookie, ssn, email`
- 리뷰 체크리스트:
  - [ ] 민감정보 원문을 로그에 남기지 않는다
  - [ ] 대용량 페이로드 요약만 기록한다
  - [ ] 사용자 입력 그대로를 로깅하지 않는다

## 대안/트레이드오프
- OpenTelemetry 직접 도입은 초기 복잡도 증가로 보류
- 구조화 로그 → 이후 ELK/Grafana Loki 연동 용이

## 상태
- 승인, 구현 완료 (T-072, T-073)
