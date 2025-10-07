"""
KCP 본인인증 유틸리티

KCP 바이너리 호출 및 데이터 처리를 위한 헬퍼 함수들
"""
import os
import platform
import subprocess
import hashlib
from typing import Optional, Dict

from src.config.settings import settings
from src.common.logging import get_logger_with_request_id


def get_kcp_binary_path() -> str:
    """시스템 아키텍처에 맞는 KCP 바이너리 경로 반환

    Returns:
        str: ct_cli 바이너리 절대 경로

    Raises:
        FileNotFoundError: 바이너리가 존재하지 않을 때
    """
    machine = platform.machine().lower()

    # 시스템 아키텍처 감지
    if machine in ['x86_64', 'amd64']:
        arch_dir = "64bit"
    elif machine in ['i386', 'i686', 'x86']:
        arch_dir = "32bit"
    else:
        arch_dir = "64bit"  # 기본값

    binary_path = os.path.join(settings.kcp_base_dir, arch_dir, "ct_cli")

    if not os.path.exists(binary_path):
        raise FileNotFoundError(f"KCP binary not found at {binary_path}")

    return binary_path


def get_kcp_site_cd() -> str:
    """현재 환경의 KCP 사이트 코드 반환"""
    return settings.kcp_test_site_cd if settings.kcp_test_mode else (settings.kcp_prod_site_cd or "")


def get_kcp_enc_key() -> str:
    """현재 환경의 KCP 암호화 키 반환"""
    return settings.kcp_test_enc_key if settings.kcp_test_mode else (settings.kcp_prod_enc_key or "")


def get_kcp_gateway_url() -> str:
    """KCP 인증 게이트웨이 URL 반환"""
    if settings.kcp_test_mode:
        return "https://testcert.kcp.co.kr/kcp_cert/cert_view.jsp"
    else:
        return "https://cert.kcp.co.kr/kcp_cert/cert_view.jsp"


def get_kcp_callback_url() -> str:
    """KCP 콜백 URL 반환"""
    return f"{settings.api_base_url}/api/v1/phone-verification/callback"


def get_kcp_web_siteid() -> str:
    """KCP 웹사이트 ID 반환"""
    return settings.kcp_web_siteid or ""


def make_hash_data(data: str) -> str:
    """해시 데이터 생성

    KCP ct_cli 바이너리 호출하여 해시 생성.
    바이너리 실행 실패 시 Python 폴백 구현 사용.

    Args:
        data: 해시를 생성할 데이터

    Returns:
        str: 생성된 해시 문자열
    """
    log = get_logger_with_request_id()
    enc_key = get_kcp_enc_key()

    try:
        ct_cli_path = get_kcp_binary_path()

        # KCP 바이너리 호출
        cmd = [
            ct_cli_path,
            "lf_CT_CLI__make_hash_data",
            enc_key,
            data
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        if result.returncode == 0:
            hash_value = result.stdout.strip()
            log.info("Hash generated via KCP binary", data_length=len(data))
            return hash_value
        else:
            log.warning("KCP binary failed, using Python fallback",
                       returncode=result.returncode,
                       stderr=result.stderr)
    except Exception as e:
        log.warning("Failed to call KCP binary, using Python fallback", error=str(e))

    # Python 폴백: SHA256 해시
    combined = f"{enc_key}{data}"
    hash_value = hashlib.sha256(combined.encode('utf-8')).hexdigest()
    log.info("Hash generated via Python fallback", data_length=len(data))

    return hash_value


def check_valid_hash(org_data: str, hash_data: str) -> bool:
    """해시 데이터 검증

    Args:
        org_data: 원본 데이터
        hash_data: 검증할 해시 데이터

    Returns:
        bool: 해시가 유효하면 True
    """
    log = get_logger_with_request_id()
    enc_key = get_kcp_enc_key()

    try:
        ct_cli_path = get_kcp_binary_path()

        # KCP 바이너리 호출
        cmd = [
            ct_cli_path,
            "lf_CT_CLI__check_valid_hash",
            enc_key,
            org_data,
            hash_data
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=10,
            check=False
        )

        if result.returncode == 0:
            is_valid = result.stdout.strip().lower() in ['true', '1', 'ok']
            log.info("Hash validated via KCP binary", is_valid=is_valid)
            return is_valid
        else:
            log.warning("KCP binary failed, using Python fallback",
                       returncode=result.returncode)
    except Exception as e:
        log.warning("Failed to call KCP binary, using Python fallback", error=str(e))

    # Python 폴백
    expected_hash = make_hash_data(org_data)
    is_valid = expected_hash == hash_data
    log.info("Hash validated via Python fallback", is_valid=is_valid)

    return is_valid


def decrypt_enc_cert(cert_no: str, enc_cert_data: str, opt: str = "0") -> Optional[Dict[str, str]]:
    """암호화된 인증 데이터 복호화

    Args:
        cert_no: 인증 번호
        enc_cert_data: 암호화된 인증 데이터
        opt: 옵션 (기본값: "0")

    Returns:
        Dict[str, str]: 복호화된 데이터 딕셔너리 또는 None
    """
    log = get_logger_with_request_id()
    site_cd = get_kcp_site_cd()
    enc_key = get_kcp_enc_key()

    try:
        ct_cli_path = get_kcp_binary_path()

        # KCP 바이너리 호출
        cmd = [
            ct_cli_path,
            "lf_CT_CLI__decrypt_enc_cert",
            enc_key,
            site_cd,
            cert_no,
            enc_cert_data,
            opt
        ]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=False,  # 바이너리 출력이므로 bytes로 받음
            timeout=15,
            check=False
        )

        if result.returncode == 0:
            # 인코딩 처리 (UTF-8 시도 → EUC-KR 시도)
            try:
                stdout_text = result.stdout.decode('utf-8', errors='ignore')
            except UnicodeDecodeError:
                try:
                    stdout_text = result.stdout.decode('euc-kr', errors='ignore')
                except UnicodeDecodeError:
                    stdout_text = result.stdout.decode('latin1', errors='ignore')

            # 데이터 파싱
            parsed_data = _parse_decrypted_data(stdout_text)
            log.info("Cert data decrypted via KCP binary",
                    cert_no=cert_no,
                    fields=list(parsed_data.keys()))
            return parsed_data
        else:
            log.error("KCP binary decryption failed",
                     cert_no=cert_no,
                     returncode=result.returncode,
                     stderr=result.stderr.decode('utf-8', errors='ignore'))
            return None

    except Exception as e:
        log.error("Failed to decrypt cert data", cert_no=cert_no, error=str(e))
        return None


def _parse_decrypted_data(raw_data: str) -> Dict[str, str]:
    """복호화된 데이터 파싱

    KCP는 chr(31) 구분자를 사용하여 key=value 쌍을 구분

    Args:
        raw_data: KCP 바이너리에서 출력된 원시 데이터

    Returns:
        Dict[str, str]: 파싱된 데이터
    """
    result = {}
    pairs = raw_data.split(chr(31))

    for pair in pairs:
        if "=" in pair:
            key, value = pair.split("=", 1)
            result[key.strip()] = value.strip()

    # sex_code 정규화 (KCP는 "01", "02" 형식 반환)
    if 'sex_code' in result and len(result['sex_code']) > 1:
        if result['sex_code'] == '01':
            result['sex_code'] = '1'
        elif result['sex_code'] == '02':
            result['sex_code'] = '2'

    return result


def get_kcp_lib_ver() -> str:
    """KCP 라이브러리 버전 조회

    Returns:
        str: KCP 라이브러리 버전 또는 "unknown"
    """
    log = get_logger_with_request_id()

    try:
        ct_cli_path = get_kcp_binary_path()

        cmd = [ct_cli_path, "lf_CT_CLI__get_lib_ver"]

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
            check=False
        )

        if result.returncode == 0:
            version = result.stdout.strip()
            log.info("KCP library version retrieved", version=version)
            return version
        else:
            log.warning("Failed to get KCP library version")
            return "unknown"

    except Exception as e:
        log.warning("Failed to call KCP binary for version", error=str(e))
        return "unknown"


def xor_encrypt(data: str, key: str = "verification_flag") -> str:
    """XOR 암호화 (간단한 인증 플래그 암호화용)

    Args:
        data: 암호화할 데이터
        key: 암호화 키 (기본값: "verification_flag")

    Returns:
        str: XOR 암호화된 hex 문자열
    """
    result = []
    for i, char in enumerate(data):
        result.append(chr(ord(char) ^ ord(key[i % len(key)])))
    return ''.join(result).encode('utf-8').hex()


def xor_decrypt(encrypted_hex: str, key: str = "verification_flag") -> str:
    """XOR 복호화

    Args:
        encrypted_hex: 암호화된 hex 문자열
        key: 복호화 키

    Returns:
        str: 복호화된 문자열
    """
    try:
        encrypted = bytes.fromhex(encrypted_hex).decode('utf-8')
        result = []
        for i, char in enumerate(encrypted):
            result.append(chr(ord(char) ^ ord(key[i % len(key)])))
        return ''.join(result)
    except Exception:
        return ""
