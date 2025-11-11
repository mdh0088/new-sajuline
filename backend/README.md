# Sajuline Backend

## KCP 본인인증 배포 시 필수 설정

### 1. KCP 바이너리 실행 권한 설정

**문제**: `Permission denied` 에러로 인증 실패

**원인**: 배포 시 바이너리 파일 실행 권한이 없어서 Python fallback으로 동작하여 KCP 인증 실패

**해결**:
```bash
cd /data/www/new-sajuline/backend

# 실행 권한 부여
chmod +x kcp_binaries/64bit/ct_cli
chmod +x kcp_binaries/32bit/ct_cli

# 재시작
pm2 restart fastapi-sajuline
```

**확인**:
```bash
# 로그에서 executable: true 확인
pm2 logs fastapi-sajuline | grep "executable"
```

### 2. API_BASE_URL 설정 (Nginx 프록시 환경)

**문제**: KCP 콜백 URL이 `localhost:8000`으로 설정되어 KCP 서버가 콜백을 보낼 수 없음

**해결**:
```bash
# .env.development 또는 .env.production 수정
API_BASE_URL=https://dev-client.sajuline.com  # 실제 프론트엔드 도메인

# 재시작
pm2 restart fastapi-sajuline
```

**설명**: Nginx에서 `/api/`를 `localhost:8000`으로 프록시하므로, API_BASE_URL은 프론트엔드 도메인을 사용해야 함