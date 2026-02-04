"""
AI 에러 메시지 설정.

에러 코드별 사용자 친화적 메시지와 대안 제안 템플릿을 정의합니다.

Stories: STORY-4-2
FRs: FR20, FR21
"""

# 에러 코드별 사용자 메시지
ERROR_MESSAGES = {
    "AIBI_SQL_GEN_FAILED": "질문을 이해하지 못했어요. 다른 표현으로 질문해주세요.",
    "AIBI_TABLE_NOT_ALLOWED": "해당 데이터에 접근 권한이 없습니다.",
    "AIBI_LLM_TIMEOUT": "AI 응답이 지연되고 있어요. 잠시 후 다시 시도해주세요.",
    "AIBI_EMPTY_RESULT": "조회 결과가 없습니다.",
    "AIBI_TOO_MANY_RESULTS": "결과가 너무 많습니다. 조건을 좁혀주세요.",
    "AIBI_INVALID_QUERY": "질문 형식이 올바르지 않습니다.",
    "AIBI_DB_CONNECTION_ERROR": "데이터베이스 연결에 문제가 발생했습니다.",
    "AIBI_PERMISSION_DENIED": "권한이 없습니다.",
    "AIBI_RATE_LIMIT_EXCEEDED": "요청 횟수를 초과했습니다. 잠시 후 다시 시도해주세요.",
}

# 에러 유형별 안내 메시지
ERROR_TYPE_GUIDES = {
    "query_understanding": {
        "title": "질문 이해 오류",
        "description": "AI가 질문의 의도를 파악하지 못했습니다.",
        "tips": [
            "더 구체적으로 질문해주세요",
            "숫자나 기간을 명시해주세요",
            "예시: '이번 달 매출', '최근 7일 가입자'",
        ],
    },
    "permission": {
        "title": "권한 오류",
        "description": "요청한 데이터에 접근 권한이 없습니다.",
        "tips": [
            "조회 가능한 데이터 목록을 확인해주세요",
            "관리자에게 권한을 요청해주세요",
        ],
    },
    "timeout": {
        "title": "응답 지연",
        "description": "AI 처리 시간이 너무 오래 걸리고 있습니다.",
        "tips": [
            "잠시 후 다시 시도해주세요",
            "더 간단한 질문으로 나눠서 시도해보세요",
        ],
    },
    "data_access": {
        "title": "데이터 조회 오류",
        "description": "데이터 조회 중 문제가 발생했습니다.",
        "tips": [
            "조회 조건을 변경해보세요",
            "다른 기간으로 시도해보세요",
        ],
    },
}

# 에러 코드 → 에러 유형 매핑
ERROR_CODE_TO_TYPE = {
    "AIBI_SQL_GEN_FAILED": "query_understanding",
    "AIBI_INVALID_QUERY": "query_understanding",
    "AIBI_TABLE_NOT_ALLOWED": "permission",
    "AIBI_PERMISSION_DENIED": "permission",
    "AIBI_LLM_TIMEOUT": "timeout",
    "AIBI_EMPTY_RESULT": "data_access",
    "AIBI_TOO_MANY_RESULTS": "data_access",
    "AIBI_DB_CONNECTION_ERROR": "data_access",
    "AIBI_RATE_LIMIT_EXCEEDED": "timeout",
}


def get_error_guide(error_code: str) -> dict | None:
    """
    에러 코드에 대한 안내 정보 반환.

    Args:
        error_code: 에러 코드

    Returns:
        dict | None: 에러 안내 정보 (없으면 None)
    """
    error_type = ERROR_CODE_TO_TYPE.get(error_code)
    if error_type:
        return ERROR_TYPE_GUIDES.get(error_type)
    return None
