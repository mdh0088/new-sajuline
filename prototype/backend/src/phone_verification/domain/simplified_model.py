"""
Simplified Phone Verification Model

KCP 본인인증 핵심 필드만 유지한 간소화된 모델.
Redis로 세션 관리를 하므로 DB에는 최소한의 정보만 저장.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Index
from src.common.database.base import Base


class SimplifiedPhoneVerification(Base):
    """
    간소화된 핸드폰 인증 테이블
    
    핵심 KCP 인증 정보만 저장:
    - CI/DI: 중복가입 확인 및 연계정보 (필수)
    - 인증 결과: 감사 및 추적용
    - 기본 정보: 최소한의 사용자 정보
    """
    __tablename__ = "simplified_phone_verifications"
    __table_args__ = (
        Index('idx_sph_phone', 'phone_no'),
        Index('idx_sph_ci', 'ci'),
        Index('idx_sph_di', 'di'),
        Index('idx_sph_created', 'created_at'),
        {'comment': 'KCP 핸드폰 본인인증 핵심 정보'}
    )
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    
    # 인증 기본 정보 (KCP 필수)
    phone_no = Column(String(11), nullable=False, comment="인증된 전화번호")
    user_name = Column(String(100), nullable=False, comment="인증된 이름")
    birth_date = Column(String(8), nullable=False, comment="인증된 생년월일 (YYYYMMDD)")
    
    # KCP 핵심 데이터 (중복가입 확인용)
    ci = Column(String(200), nullable=False, unique=True, comment="CI (연계정보) - 사용자 고유 식별")
    di = Column(String(200), nullable=False, comment="DI (중복가입확인정보) - 사이트별 고유")
    
    # KCP 인증 결과 (감사용)
    cert_no = Column(String(100), nullable=True, comment="KCP 인증 번호")
    res_cd = Column(String(10), nullable=False, default="0000", comment="KCP 결과 코드")
    
    # 추적 정보
    is_verified = Column(Boolean, nullable=False, default=True, comment="인증 완료 여부")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="인증 시간")
    
    def to_dict(self) -> dict:
        """엔티티를 딕셔너리로 변환"""
        return {
            "id": self.id,
            "phone_no": self.phone_no,
            "user_name": self.user_name, 
            "birth_date": self.birth_date,
            "ci": self.ci,
            "di": self.di,
            "cert_no": self.cert_no,
            "res_cd": self.res_cd,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

