"""
사주 지식베이스 모델 테스트

Story 2.1: 사주 지식베이스 데이터 모델
- Task 1: 천간(SajuCheongan) 모델 (AC: 1, 2)
- Task 2: 지지(SajuJiji) 모델 (AC: 1, 3)
- Task 3: 십성 해석(SajuSipsungInterpretation) 모델 (AC: 1, 4)
- Task 4: 지지 관계(SajuJijiRelation) 모델 (AC: 1, 5)
- Task 5: 운세 이력(FortuneHistory) 모델 (AC: 6)
"""
import pytest
from sqlalchemy import inspect


class TestSajuCheonganModel:
    """천간 모델 테스트 (Task 1)"""

    def test_model_exists(self):
        """천간 모델이 존재하는지 확인"""
        from src.models.saju_cheongan_model import SajuCheongan
        assert SajuCheongan is not None

    def test_tablename(self):
        """테이블명이 saju_cheongan인지 확인"""
        from src.models.saju_cheongan_model import SajuCheongan
        assert SajuCheongan.__tablename__ == "saju_cheongan"

    def test_required_columns(self):
        """필수 컬럼이 존재하는지 확인"""
        from src.models.saju_cheongan_model import SajuCheongan

        mapper = inspect(SajuCheongan)
        columns = {col.key for col in mapper.columns}

        required_columns = {"id", "name", "hanja", "oheng", "yin_yang", "description"}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_column_types(self):
        """컬럼 타입이 올바른지 확인"""
        from src.models.saju_cheongan_model import SajuCheongan
        from sqlalchemy import Integer, String, Text

        mapper = inspect(SajuCheongan)
        columns = {col.key: col for col in mapper.columns}

        assert isinstance(columns["id"].type, Integer)
        assert isinstance(columns["name"].type, String)
        assert isinstance(columns["hanja"].type, String)
        assert isinstance(columns["oheng"].type, String)
        assert isinstance(columns["yin_yang"].type, String)
        assert isinstance(columns["description"].type, (String, Text))

    def test_primary_key(self):
        """id가 기본키인지 확인"""
        from src.models.saju_cheongan_model import SajuCheongan

        mapper = inspect(SajuCheongan)
        pk_columns = [col.key for col in mapper.primary_key]
        assert "id" in pk_columns


class TestSajuJijiModel:
    """지지 모델 테스트 (Task 2)"""

    def test_model_exists(self):
        """지지 모델이 존재하는지 확인"""
        from src.models.saju_jiji_model import SajuJiji
        assert SajuJiji is not None

    def test_tablename(self):
        """테이블명이 saju_jiji인지 확인"""
        from src.models.saju_jiji_model import SajuJiji
        assert SajuJiji.__tablename__ == "saju_jiji"

    def test_required_columns(self):
        """필수 컬럼이 존재하는지 확인"""
        from src.models.saju_jiji_model import SajuJiji

        mapper = inspect(SajuJiji)
        columns = {col.key for col in mapper.columns}

        required_columns = {"id", "name", "hanja", "oheng", "yin_yang", "animal", "month", "description"}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"


class TestSajuSipsungInterpretationModel:
    """십성 해석 모델 테스트 (Task 3)"""

    def test_model_exists(self):
        """십성 해석 모델이 존재하는지 확인"""
        from src.models.saju_sipsung_model import SajuSipsungInterpretation
        assert SajuSipsungInterpretation is not None

    def test_tablename(self):
        """테이블명이 saju_sipsung_interpretation인지 확인"""
        from src.models.saju_sipsung_model import SajuSipsungInterpretation
        assert SajuSipsungInterpretation.__tablename__ == "saju_sipsung_interpretation"

    def test_required_columns(self):
        """필수 컬럼이 존재하는지 확인"""
        from src.models.saju_sipsung_model import SajuSipsungInterpretation

        mapper = inspect(SajuSipsungInterpretation)
        columns = {col.key for col in mapper.columns}

        required_columns = {"id", "ilgan", "sipsung", "keywords", "positive_meaning", "negative_meaning", "daily_advice"}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_composite_index_exists(self):
        """복합 인덱스 idx_ilgan_sipsung이 존재하는지 확인"""
        from src.models.saju_sipsung_model import SajuSipsungInterpretation

        indexes = SajuSipsungInterpretation.__table__.indexes
        index_names = {idx.name for idx in indexes}

        assert "idx_ilgan_sipsung" in index_names


class TestSajuJijiRelationModel:
    """지지 관계 모델 테스트 (Task 4)"""

    def test_model_exists(self):
        """지지 관계 모델이 존재하는지 확인"""
        from src.models.saju_jiji_relation_model import SajuJijiRelation
        assert SajuJijiRelation is not None

    def test_tablename(self):
        """테이블명이 saju_jiji_relation인지 확인"""
        from src.models.saju_jiji_relation_model import SajuJijiRelation
        assert SajuJijiRelation.__tablename__ == "saju_jiji_relation"

    def test_required_columns(self):
        """필수 컬럼이 존재하는지 확인"""
        from src.models.saju_jiji_relation_model import SajuJijiRelation

        mapper = inspect(SajuJijiRelation)
        columns = {col.key for col in mapper.columns}

        required_columns = {"id", "relation_type", "jiji1", "jiji2", "name", "keywords", "meaning", "daily_impact"}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_relation_type_enum(self):
        """RelationType Enum이 올바르게 정의되어 있는지 확인"""
        from src.models.saju_jiji_relation_model import RelationType

        expected_values = {"합", "충", "형", "파", "해", "12운성"}
        actual_values = {e.value for e in RelationType}

        assert expected_values.issubset(actual_values), f"Missing enum values: {expected_values - actual_values}"

    def test_index_exists(self):
        """인덱스 idx_relation이 존재하는지 확인"""
        from src.models.saju_jiji_relation_model import SajuJijiRelation

        indexes = SajuJijiRelation.__table__.indexes
        index_names = {idx.name for idx in indexes}

        assert "idx_relation" in index_names


class TestFortuneHistoryModel:
    """운세 이력 모델 테스트 (Task 5)"""

    def test_model_exists(self):
        """운세 이력 모델이 존재하는지 확인"""
        from src.models.fortune_history_model import FortuneHistory
        assert FortuneHistory is not None

    def test_tablename(self):
        """테이블명이 fortune_histories인지 확인"""
        from src.models.fortune_history_model import FortuneHistory
        assert FortuneHistory.__tablename__ == "fortune_histories"

    def test_required_columns(self):
        """필수 컬럼이 존재하는지 확인 (AC6)"""
        from src.models.fortune_history_model import FortuneHistory

        mapper = inspect(FortuneHistory)
        columns = {col.key for col in mapper.columns}

        required_columns = {"id", "user_id", "fortune_type", "target_date", "content", "ai_model", "prompt_version", "created_at"}
        assert required_columns.issubset(columns), f"Missing columns: {required_columns - columns}"

    def test_fortune_type_enum(self):
        """FortuneType Enum이 올바르게 정의되어 있는지 확인"""
        from src.models.fortune_history_model import FortuneType

        expected_values = {"daily", "weekly", "monthly", "yearly"}
        actual_values = {e.value for e in FortuneType}

        assert expected_values == actual_values

    def test_composite_index_exists(self):
        """복합 인덱스 idx_user_type_date가 존재하는지 확인"""
        from src.models.fortune_history_model import FortuneHistory

        indexes = FortuneHistory.__table__.indexes
        index_names = {idx.name for idx in indexes}

        assert "idx_user_type_date" in index_names
