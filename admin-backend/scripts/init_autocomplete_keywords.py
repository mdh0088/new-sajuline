"""
자동완성 키워드 초기화 스크립트.

Stories: 4-3
AC3: 테이블/컬럼 이름을 자동완성에 포함

Usage:
    python scripts/init_autocomplete_keywords.py
"""
import asyncio
import redis.asyncio as redis

from src.config.settings import settings
from src.services.ai.services.autocomplete_service import AutocompleteService
from src.services.ai.tools.schema_loader import SchemaLoader


async def main():
    """자동완성 키워드 초기화."""
    print("자동완성 키워드 초기화 시작...")

    # Redis 연결
    redis_client = redis.from_url(
        settings.ai_redis_url, encoding="utf-8", decode_responses=True
    )

    try:
        # 스키마 로더로 테이블/컬럼 정보 로드
        schema_loader = SchemaLoader()

        # 모든 테이블의 스키마 정보 로드
        # TODO: 실제 allowed_tables는 config에서 가져와야 함
        all_tables = set([
            "admins",
            "members",
            "counselors",
            "payments",
            "point_transactions",
            "consultation_reviews",
            "banners",
            "notices",
            "inquiry",
            "grades",
            "mileage_products",
            "point_products",
        ])

        schema_info = await schema_loader.load_schema(all_tables)

        # 키워드 추출 (테이블명 + 컬럼명)
        keywords = []

        # 테이블명 추가
        keywords.extend(all_tables)

        # 컬럼명 추가
        for table_schema in schema_info.values():
            for column in table_schema.get("columns", []):
                column_name = column.get("name")
                if column_name:
                    keywords.append(column_name)

                    # 한글 별칭이 있으면 추가
                    korean_name = column.get("korean_name")
                    if korean_name:
                        keywords.append(korean_name)

        # 중복 제거
        keywords = list(set(keywords))

        print(f"총 {len(keywords)}개 키워드 추출")

        # 자동완성 서비스로 인덱싱
        autocomplete_service = AutocompleteService(
            redis_client=redis_client, encoding="utf-8"
        )
        await autocomplete_service.index_keywords(keywords)

        print(f"✅ 자동완성 키워드 초기화 완료: {len(keywords)}개")

        # 샘플 검색 테스트
        print("\n샘플 검색 테스트:")
        test_queries = ["mem", "pay", "admin", "user"]
        for query in test_queries:
            results = await autocomplete_service.suggest(query, limit=3)
            print(f"  '{query}' → {results}")

    finally:
        await redis_client.close()


if __name__ == "__main__":
    asyncio.run(main())
