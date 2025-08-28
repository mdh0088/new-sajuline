"""
KCP Service

KCP 인증 서비스와의 통신 담당
"""
import os
import subprocess
import hashlib
import json
from typing import Dict, Any, Optional, Tuple
from ..domain.entities import KCPConfiguration


class KCPService:
    """KCP 인증 서비스"""
    
    def __init__(self, config: KCPConfiguration):
        self.config = config
    
    def make_hash_data(self, data: str) -> str:
        """
        해시 데이터 생성
        
        KCP ct_cli 바이너리를 호출하여 해시 생성
        시스템 아키텍처에 맞는 바이너리 자동 선택
        """
        try:
            # KCP ct_cli 바이너리 실행 (실제 환경)
            ct_cli_path = os.path.join(self.config.home_dir, "ct_cli")
            
            if os.path.exists(ct_cli_path):
                cmd = [
                    ct_cli_path,
                    "lf_CT_CLI__make_hash_data",
                    self.config.enc_key,  # site_key 대신 enc_key 사용
                    data
                ]
                
                print(f"Executing KCP binary: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    hash_value = result.stdout.strip()
                    print(f"KCP hash generated: {hash_value[:10]}...")
                    return hash_value
                else:
                    print(f"KCP binary error (returncode: {result.returncode}): {result.stderr}")
            else:
                print(f"KCP binary not found: {ct_cli_path}")
            
            # Python 구현 (개발/테스트용 폴백)
            print("Using Python hash implementation as fallback")
            return self._python_hash_implementation(data)
            
        except subprocess.TimeoutExpired:
            print("KCP binary execution timeout")
            return self._python_hash_implementation(data)
        except Exception as e:
            print(f"Hash generation error: {e}")
            return self._python_hash_implementation(data)  # 에러 코드
    
    def check_valid_hash(self, hash_value: str, data: str) -> bool:
        """
        해시 유효성 검증
        
        KCP ct_cli 바이너리를 호출하여 해시 검증
        시스템 아키텍처에 맞는 바이너리 자동 선택
        """
        try:
            # KCP ct_cli 바이너리 실행 (실제 환경)
            ct_cli_path = os.path.join(self.config.home_dir, "ct_cli")
            
            if os.path.exists(ct_cli_path):
                cmd = [
                    ct_cli_path,
                    "lf_CT_CLI__check_valid_hash",
                    self.config.enc_key,  # site_key 대신 enc_key 사용
                    hash_value,
                    data
                ]
                
                print(f"Executing KCP hash validation: {' '.join(cmd[:3])}...")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    is_valid = result.stdout.strip() == "1"
                    print(f"KCP hash validation result: {is_valid}")
                    return is_valid
                else:
                    print(f"KCP binary validation error: {result.stderr}")
            else:
                print(f"KCP binary not found: {ct_cli_path}")
            
            # Python 구현 (개발/테스트용 폴백)
            print("Using Python hash validation as fallback")
            expected_hash = self._python_hash_implementation(data)
            return hash_value == expected_hash
            
        except subprocess.TimeoutExpired:
            print("KCP binary validation timeout")
            expected_hash = self._python_hash_implementation(data)
            return hash_value == expected_hash
        except Exception as e:
            print(f"Hash validation error: {e}")
            return False
    
    def decrypt_enc_cert(
        self,
        cert_no: str,
        enc_cert_data: str,
        opt: str = "0"
    ) -> Optional[Dict[str, str]]:
        """
        암호화된 인증 데이터 복호화
        
        KCP ct_cli 바이너리를 호출하여 복호화
        시스템 아키텍처에 맞는 바이너리 자동 선택
        """
        try:
            # KCP ct_cli 바이너리 실행 (실제 환경)
            ct_cli_path = os.path.join(self.config.home_dir, "ct_cli")
            
            if os.path.exists(ct_cli_path):
                cmd = [
                    ct_cli_path,
                    "lf_CT_CLI__decrypt_enc_cert",
                    self.config.enc_key,  # site_key 대신 enc_key 사용
                    self.config.site_cd,
                    cert_no,
                    enc_cert_data,
                    opt
                ]
                
                print(f"Executing KCP decryption: {ct_cli_path} with cert_no: {cert_no}")
                result = subprocess.run(cmd, capture_output=True, text=False, timeout=15)
                
                if result.returncode == 0:
                    # Decode binary output with error handling
                    try:
                        stdout_text = result.stdout.decode('utf-8', errors='ignore')
                    except UnicodeDecodeError:
                        # Try with different encodings
                        try:
                            stdout_text = result.stdout.decode('euc-kr', errors='ignore')
                        except UnicodeDecodeError:
                            stdout_text = result.stdout.decode('latin1', errors='ignore')
                    
                    decrypted_data = self._parse_decrypted_data(stdout_text)
                    print(f"KCP decryption successful: {len(decrypted_data)} fields")
                    return decrypted_data
                else:
                    stderr_text = result.stderr.decode('utf-8', errors='ignore') if result.stderr else "Unknown error"
                    print(f"KCP binary decryption error: {stderr_text}")
            else:
                print(f"KCP binary not found: {ct_cli_path}")
            
            # 개발/테스트용 더미 데이터 (폴백)
            if self.config.is_test_mode:
                print("Using test decrypted data as fallback")
                return self._get_test_decrypted_data()
            
            return None
            
        except subprocess.TimeoutExpired:
            print("KCP binary decryption timeout")
            if self.config.is_test_mode:
                return self._get_test_decrypted_data()
            return None
        except Exception as e:
            print(f"Decryption error: {e}")
            return None
    
    def get_kcp_lib_ver(self) -> str:
        """
        KCP 라이브러리 버전 조회
        시스템 아키텍처에 맞는 바이너리 자동 선택
        """
        try:
            # KCP ct_cli 바이너리 실행 (실제 환경)
            ct_cli_path = os.path.join(self.config.home_dir, "ct_cli")
            
            if os.path.exists(ct_cli_path):
                cmd = [ct_cli_path, "lf_CT_CLI__get_kcp_lib_ver"]
                
                print(f"Executing KCP version check: {ct_cli_path}")
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0:
                    version = result.stdout.strip()
                    print(f"KCP library version: {version}")
                    return version
                else:
                    print(f"KCP binary version error: {result.stderr}")
            else:
                print(f"KCP binary not found: {ct_cli_path}")
            
            # 개발/테스트용 기본값
            return "PHP_CT_CLI_1.0.1"
            
        except subprocess.TimeoutExpired:
            print("KCP binary version check timeout")
            return "PHP_CT_CLI_1.0.1"
        except Exception as e:
            print(f"Version check error: {e}")
            return "HS04"  # 에러 코드  # 에러 코드
    
    def _python_hash_implementation(self, data: str) -> str:
        """
        Python으로 구현한 해시 생성 (개발/테스트용)
        
        실제 KCP 해시 알고리즘과 다를 수 있음
        운영 환경에서는 ct_cli 바이너리 사용 필요
        """
        # SHA256 해시 생성 (예시)
        hash_input = f"{self.config.enc_key}{data}"
        return hashlib.sha256(hash_input.encode()).hexdigest().upper()
    
    def _parse_decrypted_data(self, raw_data: str) -> Dict[str, str]:
        """
        복호화된 데이터 파싱
        
        KCP는 chr(31) 구분자를 사용
        """
        result = {}
        pairs = raw_data.split(chr(31))
        
        for pair in pairs:
            if "=" in pair:
                key, value = pair.split("=", 1)
                result[key] = value
        
        # sex_code 정규화: '01' -> '1', '02' -> '2' 
        if 'sex_code' in result and len(result['sex_code']) > 1:
            if result['sex_code'] == '01':
                result['sex_code'] = '1'
            elif result['sex_code'] == '02':
                result['sex_code'] = '2'
            else:
                # 첫 번째 문자만 사용
                result['sex_code'] = result['sex_code'][-1]
        
        return result
    
    def _get_test_decrypted_data(self) -> Dict[str, str]:
        """
        테스트용 더미 복호화 데이터
        """
        return {
            "comm_id": "SKT",
            "phone_no": "01012345678",
            "user_name": "홍길동",
            "birth_day": "19900101",
            "sex_code": "1",
            "local_code": "01",
            "ci_url": "TEST_CI_" + hashlib.md5(b"test").hexdigest(),
            "di_url": "TEST_DI_" + hashlib.md5(b"test").hexdigest(),
            "web_siteid": self.config.web_siteid,
            "res_cd": "0000",
            "res_msg": "정상처리"
        }


class KCPEncryptor:
    """KCP 암호화 헬퍼 클래스"""
    
    @staticmethod
    def encrypt_phone_verification_flag(key: str = "mysajuro##") -> str:
        """
        핸드폰 인증 완료 플래그 암호화
        
        기존 PHP 코드: base64_encode("pchked" ^ $key)
        """
        # XOR 연산을 위한 바이트 변환
        text = "pchked"
        
        # 키를 텍스트 길이에 맞춰 반복
        key_repeated = (key * (len(text) // len(key) + 1))[:len(text)]
        
        # XOR 연산
        xored = bytes(a ^ b for a, b in zip(text.encode(), key_repeated.encode()))
        
        # Base64 인코딩
        import base64
        return base64.b64encode(xored).decode()
    
    @staticmethod
    def validate_phone_verification_flag(encrypted: str, key: str = "mysajuro##") -> bool:
        """
        핸드폰 인증 완료 플래그 검증
        """
        try:
            import base64
            # Base64 디코딩
            decoded = base64.b64decode(encrypted)
            
            # 키를 디코딩된 데이터 길이에 맞춰 반복
            key_repeated = (key * (len(decoded) // len(key) + 1))[:len(decoded)]
            
            # XOR 연산으로 원본 복구
            original = bytes(a ^ b for a, b in zip(decoded, key_repeated.encode()))
            
            # 원본 텍스트와 비교
            return original.decode() == "pchked"
        except:
            return False