# KCP 바이너리 파일 관리

이 디렉토리는 KCP (Korea Cyber Payment) 핸드폰 인증을 위한 바이너리 파일들을 포함합니다.

## 📁 디렉토리 구조

```
kcp_binaries/
├── README.md          # 이 파일
├── 32bit/
│   └── ct_cli         # 32bit 시스템용 KCP 바이너리
└── 64bit/
    └── ct_cli         # 64bit 시스템용 KCP 바이너리
```

## 🎯 목적

- **아키텍처 자동 감지**: 시스템 아키텍처에 따라 적절한 바이너리 자동 선택
- **플랫폼 호환성**: 32bit/64bit 시스템 모두 지원
- **독립적 운영**: FastAPI 백엔드에서 KCP 기능 완전 구현

## ⚙️ 바이너리 정보

### 32bit (i386/i686)
- **파일**: `32bit/ct_cli`
- **아키텍처**: ELF 32-bit LSB executable, Intel 80386
- **크기**: ~519KB
- **용도**: 32bit Linux 시스템에서 KCP 암호화/복호화

### 64bit (x86_64)
- **파일**: `64bit/ct_cli`
- **아키텍처**: ELF 64-bit LSB executable, x86-64
- **크기**: ~572KB
- **용도**: 64bit Linux 시스템에서 KCP 암호화/복호화
- **버전**: CTCLI_C_1_0_8

## 🔧 자동 선택 로직

시스템에서 다음과 같이 자동으로 적절한 바이너리를 선택합니다:

```python
import platform

machine = platform.machine().lower()

if machine in ['x86_64', 'amd64']:
    # 64bit 시스템 → 64bit/ct_cli 사용
    arch_dir = "64bit"
elif machine in ['i386', 'i686', 'x86']:
    # 32bit 시스템 → 32bit/ct_cli 사용
    arch_dir = "32bit"
else:
    # 기본값으로 64bit 사용
    arch_dir = "64bit"
```

## 🚀 사용 방법

### 1. KCP 설정에서 자동 경로 설정
```python
from src.phone_verification.infrastructure.kcp_config import get_kcp_configuration

config = get_kcp_configuration()
print(config.home_dir)  # 자동으로 올바른 아키텍처 경로 반환
```

### 2. KCP 서비스에서 바이너리 실행
```python
from src.phone_verification.infrastructure.kcp_service import KCPService

service = KCPService(config)
hash_value = service.make_hash_data("test_data")  # 자동으로 올바른 바이너리 사용
```

## 🧪 테스트

바이너리가 올바르게 작동하는지 확인하려면:

```bash
cd backend
python test_kcp_integration.py
```

테스트 결과:
- ✅ 아키텍처 자동 감지
- ✅ 바이너리 존재 확인
- ✅ KCP 라이브러리 버전 조회
- ✅ 해시 생성 및 검증

## 🔐 KCP 바이너리 기능

### 지원하는 KCP 함수들:

1. **lf_CT_CLI__get_kcp_lib_ver**
   - KCP 라이브러리 버전 조회
   - 반환: `CTCLI_C_1_0_8`

2. **lf_CT_CLI__make_hash_data**
   - 데이터 해시 생성
   - 입력: 암호화키, 데이터
   - 반환: 해시값

3. **lf_CT_CLI__check_valid_hash**
   - 해시 유효성 검증
   - 입력: 암호화키, 해시값, 원본 데이터
   - 반환: 1 (유효) / 0 (무효)

4. **lf_CT_CLI__decrypt_enc_cert**
   - 암호화된 인증 데이터 복호화
   - 입력: 암호화키, 사이트코드, 인증번호, 암호화 데이터
   - 반환: 복호화된 사용자 정보

## 📋 원본 위치

이 바이너리들은 다음 위치에서 복사되었습니다:
- **32bit**: `/old-docs/config/kcp/bin/ct_cli`
- **64bit**: `/old-docs/config/kcp/bin/64bit/ct_cli`

## ⚠️ 주의사항

1. **권한 설정**: 바이너리 파일에 실행 권한이 필요합니다
2. **의존성**: Linux 환경에서만 동작합니다
3. **보안**: 암호화 키는 환경변수나 보안 저장소에서 관리하세요
4. **타임아웃**: 바이너리 실행 시 적절한 타임아웃을 설정하세요

## 🔄 업데이트

KCP에서 새로운 바이너리를 제공하는 경우:

1. 기존 바이너리 백업
2. 새 바이너리로 교체
3. 실행 권한 설정: `chmod +x ct_cli`
4. 통합 테스트 실행: `python test_kcp_integration.py`

---

*이 바이너리들은 KCP 핸드폰 인증 서비스의 핵심 구성요소로, 안전하고 신뢰할 수 있는 인증 서비스를 제공하기 위해 필수적입니다.*