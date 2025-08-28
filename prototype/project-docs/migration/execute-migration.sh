#!/bin/bash

# MariaDB 마이그레이션 실행 스크립트
# Usage: ./execute-migration.sh

DB_HOST="localhost"
DB_USER="root"
DB_PASS="sajuline@2024"
DB_NAME="sajuline"

echo "========================================="
echo "사주라인 DB 마이그레이션 시작"
echo "========================================="

# 1. 백업 생성
echo "1. 기존 데이터베이스 백업 중..."
mysqldump -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME > backup_$(date +%Y%m%d_%H%M%S).sql
if [ $? -eq 0 ]; then
    echo "   ✅ 백업 완료"
else
    echo "   ❌ 백업 실패. 마이그레이션을 중단합니다."
    exit 1
fi

# 2. 데이터 정리 (중복 USER_ID 등)
echo "2. 데이터 정리 중..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < pre-migration-cleanup.sql
if [ $? -eq 0 ]; then
    echo "   ✅ 데이터 정리 완료"
else
    echo "   ⚠️  데이터 정리 중 오류 발생 (계속 진행)"
fi

# 3. 새로운 스키마 생성
echo "3. 개선된 스키마 적용 중..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < improved-schema.sql
if [ $? -eq 0 ]; then
    echo "   ✅ 스키마 생성 완료"
else
    echo "   ❌ 스키마 생성 실패. 마이그레이션을 중단합니다."
    exit 1
fi

# 4. 데이터 마이그레이션
echo "4. 데이터 마이그레이션 중..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < data-migration.sql
if [ $? -eq 0 ]; then
    echo "   ✅ 데이터 마이그레이션 완료"
else
    echo "   ❌ 데이터 마이그레이션 실패. 롤백을 고려하세요."
    exit 1
fi

# 5. 마이그레이션 후 검증
echo "5. 마이그레이션 검증 중..."
mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < post-migration-validation.sql
if [ $? -eq 0 ]; then
    echo "   ✅ 검증 완료"
else
    echo "   ⚠️  검증 중 경고 발생"
fi

echo "========================================="
echo "마이그레이션 완료!"
echo "========================================="
echo ""
echo "다음 단계:"
echo "1. 애플리케이션 연동 테스트"
echo "2. 평문 비밀번호 사용자 재설정 안내"
echo "3. 성능 모니터링"