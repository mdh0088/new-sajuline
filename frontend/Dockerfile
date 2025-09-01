# 사주라인 Nuxt.js 4 Frontend Dockerfile
# 다단계 빌드로 개발/프로덕션 환경 최적화

# Base stage - 공통 설정
FROM node:22-alpine AS base
WORKDIR /app

# 필수 시스템 패키지 설치
RUN apk add --no-cache \
    curl \
    git \
    && rm -rf /var/cache/apk/*

# package.json과 package-lock.json 복사 (의존성 캐싱 최적화)
COPY package*.json ./

# Development stage - 개발 환경
FROM base AS development

# 개발 의존성 포함하여 설치
RUN npm ci --include=dev

# 소스 코드 복사
COPY . .

# Nuxt 준비 (타입 생성 등)
RUN npm run postinstall

# 개발 서버 포트 노출
EXPOSE 3000

# 개발 서버 실행
CMD ["npm", "run", "dev"]

# Dependencies stage - 프로덕션 의존성만 설치
FROM base AS dependencies

# 프로덕션 의존성만 설치
RUN npm ci --only=production && npm cache clean --force

# Build stage - 프로덕션 빌드
FROM base AS builder

# 개발 의존성 설치 (빌드용)
RUN npm ci --include=dev

# 소스 코드 복사
COPY . .

# 빌드 환경 변수
ENV NODE_ENV=production
ENV NUXT_TELEMETRY_DISABLED=1

# Nuxt 빌드 실행
RUN npm run build

# Production stage - 프로덕션 실행
FROM node:22-alpine AS production

WORKDIR /app

# 필수 런타임 패키지만 설치
RUN apk add --no-cache \
    curl \
    && rm -rf /var/cache/apk/*

# 프로덕션 의존성 복사
COPY --from=dependencies /app/node_modules ./node_modules

# 빌드된 파일들 복사
COPY --from=builder /app/.output ./.output
COPY --from=builder /app/package.json ./package.json

# 비root 유저 생성 및 권한 설정
RUN addgroup -g 1001 -S nuxt && \
    adduser -S nuxt -u 1001 && \
    chown -R nuxt:nuxt /app

USER nuxt

# 프로덕션 서버 포트 노출
EXPOSE 3000

# 환경 변수
ENV NODE_ENV=production
ENV NITRO_HOST=0.0.0.0
ENV NITRO_PORT=3000
ENV NUXT_TELEMETRY_DISABLED=1

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# 프로덕션 서버 실행
CMD ["node", ".output/server/index.mjs"]