#!/bin/bash
#
# Counselor Status Sync Cron Script
# 상담사 상태 동기화 - tm60_member -> t_counselor
# Cron: * * * * * (1분마다 실행)
#

# 환경 설정
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_DIR="$BACKEND_DIR/logs"
LOG_FILE="$LOG_DIR/cs_status_scheduler.log"
API_URL="https://www.sajuline.com/api/v1/counselors/sync-status"
MAX_LOG_SIZE=10485760  # 10MB

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 로그 파일 크기 체크 및 로테이션
if [ -f "$LOG_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$LOG_FILE" 2>/dev/null || stat -f%z "$LOG_FILE" 2>/dev/null)
    if [ "$FILE_SIZE" -gt $MAX_LOG_SIZE ]; then
        mv "$LOG_FILE" "$LOG_FILE.$(date +%Y%m%d%H%M%S).bak"
    fi
fi

# 타임스탬프
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# API 호출 (nginx proxy 경유)
RESPONSE=$(curl -X POST "$API_URL" \
  -H "Content-Type: application/json" \
  --max-time 30 \
  -s -w "\nHTTP_CODE:%{http_code}" 2>&1)

HTTP_CODE=$(echo "$RESPONSE" | grep "HTTP_CODE:" | cut -d: -f2)
BODY=$(echo "$RESPONSE" | grep -v "HTTP_CODE:")

# 로그 기록
if [ "$HTTP_CODE" = "200" ]; then
    echo "[$TIMESTAMP] SUCCESS (HTTP $HTTP_CODE)" >> "$LOG_FILE"
else
    echo "[$TIMESTAMP] FAILED (HTTP $HTTP_CODE) - $BODY" >> "$LOG_FILE"
fi
