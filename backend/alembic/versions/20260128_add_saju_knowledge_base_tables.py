"""add saju knowledge base tables

Revision ID: 20260128_saju_kb
Revises:
Create Date: 2026-01-28 23:05:14

Story 2.1: 사주 지식베이스 데이터 모델
- saju_cheongan (천간 10행)
- saju_jiji (지지 12행)
- saju_sipsung_interpretation (십성 해석 100행)
- saju_jiji_relation (지지 관계 30~50행)
- fortune_histories (운세 이력)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = '20260128_saju_kb'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### 천간 테이블 ###
    op.create_table(
        'saju_cheongan',
        sa.Column('id', sa.Integer(), nullable=False, comment='천간 ID (1~10)'),
        sa.Column('name', sa.String(2), nullable=False, comment='천간 이름 (갑~계)'),
        sa.Column('hanja', sa.String(4), nullable=False, comment='한자 (甲~癸)'),
        sa.Column('oheng', sa.String(4), nullable=False, comment='오행 (목, 화, 토, 금, 수)'),
        sa.Column('yin_yang', sa.String(4), nullable=False, comment='음양 (양, 음)'),
        sa.Column('description', sa.Text(), nullable=False, comment='천간 설명 및 특성'),
        sa.PrimaryKeyConstraint('id'),
        comment='천간 (天干) 기초 데이터'
    )

    # ### 지지 테이블 ###
    op.create_table(
        'saju_jiji',
        sa.Column('id', sa.Integer(), nullable=False, comment='지지 ID (1~12)'),
        sa.Column('name', sa.String(2), nullable=False, comment='지지 이름 (자~해)'),
        sa.Column('hanja', sa.String(4), nullable=False, comment='한자 (子~亥)'),
        sa.Column('oheng', sa.String(4), nullable=False, comment='오행 (목, 화, 토, 금, 수)'),
        sa.Column('yin_yang', sa.String(4), nullable=False, comment='음양 (양, 음)'),
        sa.Column('animal', sa.String(4), nullable=False, comment='12지신 동물 (쥐, 소, 호랑이, ...)'),
        sa.Column('month', sa.Integer(), nullable=False, comment='대응 음력월 (1~12, 자=11월)'),
        sa.Column('description', sa.Text(), nullable=False, comment='지지 설명 및 특성'),
        sa.PrimaryKeyConstraint('id'),
        comment='지지 (地支) 기초 데이터'
    )

    # ### 십성 해석 테이블 ###
    op.create_table(
        'saju_sipsung_interpretation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='해석 ID (AUTO_INCREMENT)'),
        sa.Column('ilgan', sa.String(2), nullable=False, comment='일간 (갑~계)'),
        sa.Column('sipsung', sa.String(10), nullable=False, comment='십성 (비견, 겁재, 식신, 상관, 정재, 편재, 정관, 편관, 정인, 편인)'),
        sa.Column('keywords', sa.JSON(), nullable=False, comment='핵심 키워드 배열'),
        sa.Column('positive_meaning', sa.Text(), nullable=False, comment='긍정적 의미 해석'),
        sa.Column('negative_meaning', sa.Text(), nullable=False, comment='부정적 의미 해석'),
        sa.Column('daily_advice', sa.Text(), nullable=False, comment='일일 운세 조언'),
        sa.PrimaryKeyConstraint('id'),
        comment='십성 해석 데이터 (일간×십성 100조합)'
    )
    op.create_index('idx_ilgan_sipsung', 'saju_sipsung_interpretation', ['ilgan', 'sipsung'], unique=False)

    # ### 지지 관계 테이블 ###
    op.create_table(
        'saju_jiji_relation',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False, comment='관계 ID (AUTO_INCREMENT)'),
        sa.Column('relation_type', sa.String(10), nullable=False, comment='관계 유형 (합, 충, 형, 파, 해, 12운성)'),
        sa.Column('jiji1', sa.String(2), nullable=False, comment='첫 번째 지지'),
        sa.Column('jiji2', sa.String(2), nullable=False, comment='두 번째 지지'),
        sa.Column('name', sa.String(20), nullable=False, comment='관계 이름 (예: 자축합, 자오충)'),
        sa.Column('keywords', sa.JSON(), nullable=False, comment='핵심 키워드 배열'),
        sa.Column('meaning', sa.Text(), nullable=False, comment='관계 의미 해석'),
        sa.Column('daily_impact', sa.Text(), nullable=False, comment='일일 운세에 미치는 영향'),
        sa.PrimaryKeyConstraint('id'),
        comment='지지 관계 데이터 (합, 충, 형, 파, 해)'
    )
    op.create_index('idx_relation', 'saju_jiji_relation', ['relation_type', 'jiji1'], unique=False)

    # ### 운세 이력 테이블 ###
    op.create_table(
        'fortune_histories',
        sa.Column('id', mysql.CHAR(36), nullable=False, comment='운세 이력 ID (UUID)'),
        sa.Column('user_id', sa.String(100), nullable=False, comment='사용자 ID'),
        sa.Column('fortune_type', sa.String(20), nullable=False, comment='운세 유형 (daily, weekly, monthly, yearly)'),
        sa.Column('target_date', sa.Date(), nullable=False, comment='운세 대상 날짜'),
        sa.Column('content', sa.Text(), nullable=False, comment='AI 생성 운세 내용'),
        sa.Column('ai_model', sa.String(50), nullable=False, comment='사용된 AI 모델 (예: gpt-4o-mini)'),
        sa.Column('prompt_version', sa.String(20), nullable=False, comment='프롬프트 버전 (예: v1.0.0)'),
        sa.Column('created_at', sa.DateTime(), nullable=False, comment='생성일시'),
        sa.PrimaryKeyConstraint('id'),
        comment='AI 운세 생성 이력'
    )
    op.create_index('idx_user_type_date', 'fortune_histories', ['user_id', 'fortune_type', 'target_date'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index('idx_user_type_date', table_name='fortune_histories')
    op.drop_table('fortune_histories')

    op.drop_index('idx_relation', table_name='saju_jiji_relation')
    op.drop_table('saju_jiji_relation')

    op.drop_index('idx_ilgan_sipsung', table_name='saju_sipsung_interpretation')
    op.drop_table('saju_sipsung_interpretation')

    op.drop_table('saju_jiji')
    op.drop_table('saju_cheongan')
