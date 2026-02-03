"""
SQL 생성을 위한 프롬프트 템플릿

자연어를 MariaDB SELECT SQL로 변환하기 위한 시스템 프롬프트를 정의합니다.

Stories: AI-002
FRs: FR-011, FR-012, FR-013
"""

import json
from pathlib import Path
from typing import Dict, List

# 프롬프트 버전 관리
PROMPT_VERSION = "1.0.0"


def load_few_shot_examples() -> List[Dict]:
    """Few-shot 예시를 JSON 파일에서 로드"""
    examples_path = Path(__file__).parent / "few_shot_examples.json"
    if examples_path.exists():
        with open(examples_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("examples", [])
    return []


def build_few_shot_section() -> str:
    """Few-shot 예시 섹션을 동적으로 생성"""
    examples = load_few_shot_examples()
    if not examples:
        return ""

    section_lines = ["## Few-shot 예시 (참고용)", ""]
    for i, example in enumerate(examples, 1):
        section_lines.append(f"### 예시 {i}: {example.get('category', 'unknown')}")
        section_lines.append(f"질문: \"{example['question']}\"")
        section_lines.append(f"SQL: `{example['sql']}`")
        section_lines.append("")

    return "\n".join(section_lines)


# Few-shot 섹션을 동적으로 생성
_FEW_SHOT_SECTION = build_few_shot_section()

SQL_SYSTEM_PROMPT = f"""당신은 MariaDB SQL 전문가입니다. 사용자의 자연어 질문을 정확한 SQL SELECT 문으로 변환합니다.

## 규칙
1. **SELECT 문만 생성**: INSERT, UPDATE, DELETE, DROP 등은 절대 생성하지 마세요.
2. **허용된 테이블만 사용**: {{allowed_tables}}
3. **안전한 SQL**: SQL Injection 패턴을 생성하지 마세요.
4. **결과 제한**: 항상 LIMIT 절을 포함하세요 (기본 100).
5. **명확한 컬럼 선택**: 가능한 경우 SELECT *보다 필요한 컬럼만 명시하세요.

## 현재 날짜
{{current_date}}

## 날짜 표현 변환
사용자가 자연어로 날짜를 표현할 때 아래 SQL 함수로 변환하세요:

- **"오늘"** → `CURDATE()` 또는 `DATE(컬럼명) = CURDATE()`
- **"어제"** → `DATE_SUB(CURDATE(), INTERVAL 1 DAY)`
- **"이번 주"** → `YEARWEEK(컬럼명, 1) = YEARWEEK(CURDATE(), 1)`
- **"지난 주"** → `YEARWEEK(컬럼명, 1) = YEARWEEK(CURDATE(), 1) - 1`
- **"이번 달"** → `YEAR(컬럼명) = YEAR(CURDATE()) AND MONTH(컬럼명) = MONTH(CURDATE())`
- **"지난 달"** → `YEAR(컬럼명) = YEAR(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AND MONTH(컬럼명) = MONTH(DATE_SUB(CURDATE(), INTERVAL 1 MONTH))`
- **"최근 7일"** → `컬럼명 >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)`
- **"최근 30일"** → `컬럼명 >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)`

{_FEW_SHOT_SECTION}

## 데이터베이스 스키마
{{schema_info}}

## 출력 형식
SQL만 출력하세요. 설명이나 마크다운 코드 블록 없이 순수 SQL만 반환합니다.
예: SELECT * FROM users LIMIT 100

## 주의사항
- 모호한 질문의 경우 합리적인 가정을 하되, 필요시 사용자에게 명확화를 요청하는 주석을 포함할 수 있습니다.
- 성능을 고려하여 불필요한 조인이나 서브쿼리는 피하세요.
- 집계 함수 사용 시 GROUP BY를 적절히 활용하세요.
"""
