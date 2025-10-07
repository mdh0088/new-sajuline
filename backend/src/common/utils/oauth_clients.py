"""
OAuth 2.0 소셜 로그인 클라이언트 (Kakao, Naver)
"""
import secrets
from typing import Dict, Optional
from urllib.parse import urlencode

import aiohttp

from src.config.settings import settings
from src.exceptions.custom_exceptions import ValidationError
from src.common.logging import get_logger_with_request_id


class KakaoOAuthClient:
    """Kakao OAuth 2.0 클라이언트

    특징:
    - client_secret 불필요 (client_id만 사용)
    - 토큰 요청: POST 방식
    - 사용자 정보 요청: POST 방식 (empty body)
    - user_id 형식: kko{kakao_id}
    """

    def __init__(self):
        self.client_id = settings.kakao_client_id
        self.auth_url = settings.kakao_auth_url
        self.token_url = settings.kakao_token_url
        self.user_info_url = settings.kakao_user_info_url
        self.redirect_uri = settings.kakao_redirect_uri

    def get_authorization_url(self, state: str) -> str:
        """OAuth 인증 URL 생성

        Args:
            state: CSRF 방지용 상태 값

        Returns:
            Kakao OAuth 인증 페이지 URL
        """
        log = get_logger_with_request_id()

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': state,
        }

        auth_url = f"{self.auth_url}?{urlencode(params)}"
        log.info("Generated Kakao OAuth URL", state=state)

        return auth_url

    async def get_access_token(self, code: str) -> Dict[str, any]:
        """인증 코드로 액세스 토큰 교환

        Kakao 특징: client_secret 불필요, POST 방식

        Args:
            code: OAuth 인증 코드

        Returns:
            토큰 정보 {'access_token': str, 'token_type': str, 'expires_in': int, ...}

        Raises:
            ValidationError: 토큰 요청 실패
        """
        log = get_logger_with_request_id()

        data = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'code': code
            # Kakao는 client_secret 불필요
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.token_url, data=data) as response:
                    result = await response.json()

                    if response.status != 200:
                        error_msg = result.get('error_description', result.get('error', 'Unknown error'))
                        log.error("Kakao token request failed",
                                 status=response.status,
                                 error=error_msg)
                        raise ValidationError(f"Kakao 토큰 요청 실패: {error_msg}")

                    log.info("Kakao access token obtained successfully")
                    return result

        except aiohttp.ClientError as e:
            log.error("Kakao token request network error", error=str(e))
            raise ValidationError("Kakao 토큰 요청 중 네트워크 오류가 발생했습니다")

    async def get_user_info(self, access_token: str) -> Dict[str, any]:
        """액세스 토큰으로 사용자 정보 조회

        Kakao 특징: POST 요청, empty body

        Args:
            access_token: OAuth 액세스 토큰

        Returns:
            사용자 정보 {
                'id': int,
                'kakao_account': {
                    'email': str,
                    'profile': {'nickname': str, 'profile_image_url': str}
                }
            }

        Raises:
            ValidationError: 사용자 정보 요청 실패
        """
        log = get_logger_with_request_id()

        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Kakao는 POST 요청 + empty body
                async with session.post(self.user_info_url, headers=headers, data={}) as response:
                    result = await response.json()

                    if response.status != 200:
                        error_msg = result.get('msg', 'Unknown error')
                        log.error("Kakao user info request failed",
                                 status=response.status,
                                 error=error_msg)
                        raise ValidationError(f"Kakao 사용자 정보 요청 실패: {error_msg}")

                    log.info("Kakao user info obtained", kakao_id=result.get('id'))
                    return result

        except aiohttp.ClientError as e:
            log.error("Kakao user info request network error", error=str(e))
            raise ValidationError("Kakao 사용자 정보 요청 중 네트워크 오류가 발생했습니다")


class NaverOAuthClient:
    """Naver OAuth 2.0 클라이언트

    특징:
    - client_secret 필수
    - 토큰 요청: GET 방식 (params)
    - 사용자 정보 요청: GET 방식
    - state 파라미터 필수 (CSRF 방지)
    - user_id 형식: email 그대로 사용
    """

    def __init__(self):
        self.client_id = settings.naver_client_id
        self.client_secret = settings.naver_client_secret
        self.auth_url = settings.naver_auth_url
        self.token_url = settings.naver_token_url
        self.user_info_url = settings.naver_user_info_url
        self.redirect_uri = settings.naver_redirect_uri

    def get_authorization_url(self, state: str) -> str:
        """OAuth 인증 URL 생성

        Args:
            state: CSRF 방지용 상태 값 (Naver는 필수)

        Returns:
            Naver OAuth 인증 페이지 URL
        """
        log = get_logger_with_request_id()

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'state': state,  # Naver는 state 필수
        }

        auth_url = f"{self.auth_url}?{urlencode(params)}"
        log.info("Generated Naver OAuth URL", state=state)

        return auth_url

    async def get_access_token(self, code: str, state: str) -> Dict[str, any]:
        """인증 코드로 액세스 토큰 교환

        Naver 특징: client_secret 필수, GET 방식, state 필요

        Args:
            code: OAuth 인증 코드
            state: CSRF 방지용 상태 값

        Returns:
            토큰 정보 {'access_token': str, 'token_type': str, 'expires_in': int, ...}

        Raises:
            ValidationError: 토큰 요청 실패
        """
        log = get_logger_with_request_id()

        params = {
            'grant_type': 'authorization_code',
            'client_id': self.client_id,
            'client_secret': self.client_secret,  # Naver는 client_secret 필수
            'redirect_uri': self.redirect_uri,
            'code': code,
            'state': state  # Naver는 state 필수
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Naver는 GET 요청
                async with session.get(self.token_url, params=params) as response:
                    result = await response.json()

                    if response.status != 200 or result.get('error'):
                        error_msg = result.get('error_description', result.get('error', 'Unknown error'))
                        log.error("Naver token request failed",
                                 status=response.status,
                                 error=error_msg)
                        raise ValidationError(f"Naver 토큰 요청 실패: {error_msg}")

                    log.info("Naver access token obtained successfully")
                    return result

        except aiohttp.ClientError as e:
            log.error("Naver token request network error", error=str(e))
            raise ValidationError("Naver 토큰 요청 중 네트워크 오류가 발생했습니다")

    async def get_user_info(self, access_token: str) -> Dict[str, any]:
        """액세스 토큰으로 사용자 정보 조회

        Naver 특징: GET 요청

        Args:
            access_token: OAuth 액세스 토큰

        Returns:
            사용자 정보 {
                'resultcode': '00',
                'message': 'success',
                'response': {
                    'email': str,
                    'name': str,
                    'profile_image': str
                }
            }

        Raises:
            ValidationError: 사용자 정보 요청 실패
        """
        log = get_logger_with_request_id()

        headers = {
            'Authorization': f'Bearer {access_token}'
        }

        try:
            async with aiohttp.ClientSession() as session:
                # Naver는 GET 요청
                async with session.get(self.user_info_url, headers=headers) as response:
                    result = await response.json()

                    if response.status != 200 or result.get('resultcode') != '00':
                        error_msg = result.get('message', 'Unknown error')
                        log.error("Naver user info request failed",
                                 status=response.status,
                                 error=error_msg)
                        raise ValidationError(f"Naver 사용자 정보 요청 실패: {error_msg}")

                    user_email = result.get('response', {}).get('email')
                    log.info("Naver user info obtained", email=user_email)
                    return result

        except aiohttp.ClientError as e:
            log.error("Naver user info request network error", error=str(e))
            raise ValidationError("Naver 사용자 정보 요청 중 네트워크 오류가 발생했습니다")


def generate_oauth_state() -> str:
    """OAuth state 파라미터 생성 (CSRF 방지)

    Returns:
        32자 랜덤 문자열
    """
    return secrets.token_urlsafe(32)
