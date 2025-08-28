"""
Phone Verification Domain Models

핸드폰 인증 도메인 모델 (데이터베이스 테이블)
"""
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, Text, Enum as SQLEnum, Integer, Boolean, Index, JSON
from src.common.database.base import Base
from .entities import VerificationStatus, MobileCarrier, VerificationMethod


class PhoneVerification(Base):
    """핸드폰 인증 테이블"""
    __tablename__ = "phone_verifications"
    __table_args__ = (
        Index('idx_phone_verification_session_id', 'session_id'),
        Index('idx_phone_verification_user_id', 'user_id'),
        Index('idx_phone_verification_phone_no', 'phone_no'),
        Index('idx_phone_verification_status', 'status'),
        Index('idx_phone_verification_created_at', 'created_at'),
        {'comment': '핸드폰 본인인증 정보'}
    )
    
    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    
    # Session Info
    session_id = Column(String(40), unique=True, nullable=False, comment="세션 ID (요청번호)")
    user_id = Column(String(100), nullable=True, comment="사용자 ID (선택)")
    
    # Verification Status
    status = Column(
        SQLEnum(VerificationStatus, name='verification_status', create_type=True),
        nullable=False,
        default=VerificationStatus.PENDING,
        comment="인증 상태"
    )
    
    # Request Data
    user_name = Column(String(100), nullable=False, comment="사용자 이름")
    birth_date = Column(String(8), nullable=False, comment="생년월일 (YYYYMMDD)")
    phone_number = Column(String(11), nullable=False, comment="요청 휴대폰번호")
    carrier = Column(
        SQLEnum(MobileCarrier, name='mobile_carrier', create_type=True),
        nullable=False,
        comment="통신사"
    )
    gender = Column(String(1), nullable=False, comment="성별 (M/F)")
    local_code = Column(String(2), nullable=True, default="01", comment="내/외국인 (01:내국인, 02:외국인)")
    verification_method = Column(
        String(10),
        nullable=False,
        default="SMS",
        comment="인증방법"
    )
    
    # KCP Request/Response
    cert_no = Column(String(100), nullable=True, comment="인증 번호")
    enc_cert_data = Column(Text, nullable=True, comment="암호화된 인증 데이터")
    up_hash = Column(String(100), nullable=True, comment="요청 해시")
    dn_hash = Column(String(100), nullable=True, comment="응답 해시")
    
    # Verification Result
    comm_id = Column(String(10), nullable=True, comment="통신사 코드")
    phone_no = Column(String(11), nullable=True, comment="인증된 전화번호")
    verified_name = Column(String(100), nullable=True, comment="인증된 이름")
    verified_birth = Column(String(8), nullable=True, comment="인증된 생년월일")
    sex_code = Column(String(1), nullable=True, comment="성별 코드")
    ci = Column(String(200), nullable=True, comment="CI (연계정보)")
    di = Column(String(200), nullable=True, comment="DI (중복가입확인정보)")
    
    # Response Info
    res_cd = Column(String(10), nullable=True, comment="결과 코드")
    res_msg = Column(Text, nullable=True, comment="결과 메시지")
    
    # Additional Data (JSON)
    meta_data = Column(JSON, nullable=True, comment="추가 메타데이터")
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, comment="생성 시간")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, comment="수정 시간")
    verified_at = Column(DateTime, nullable=True, comment="인증 완료 시간")
    expires_at = Column(DateTime, nullable=False, comment="만료 시간")
    
    def __init__(self, **kwargs):
        """초기화 시 만료 시간 자동 설정 (60분)"""
        if 'expires_at' not in kwargs:
            kwargs['expires_at'] = datetime.utcnow() + timedelta(minutes=60)
        super().__init__(**kwargs)
    
    def is_expired(self) -> bool:
        """만료 여부 확인"""
        return datetime.utcnow() > self.expires_at
    
    def is_verified(self) -> bool:
        """인증 완료 여부 확인"""
        return self.status == VerificationStatus.COMPLETED
    
    def can_retry(self) -> bool:
        """재시도 가능 여부 확인"""
        return self.status in [VerificationStatus.PENDING, VerificationStatus.FAILED] and not self.is_expired()
    
    def __repr__(self):
        return f"<PhoneVerification(session_id={self.session_id}, status={self.status}, phone_no={self.phone_no})>"