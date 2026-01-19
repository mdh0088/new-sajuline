"""
입력값 정제 및 XSS 방어 유틸리티
HTML 태그 제거 및 특수문자 이스케이프 처리
"""
import re
import html
from typing import Optional, Dict, Any


class Sanitizer:
    """입력값 정제 클래스"""
    
    # 허용할 HTML 태그 (기본적으로 모두 제거)
    ALLOWED_TAGS = []
    
    # 위험한 문자열 패턴
    DANGEROUS_PATTERNS = [
        r'javascript:',
        r'onerror\s*=',
        r'onclick\s*=',
        r'onload\s*=',
        r'onmouseover\s*=',
        r'onfocus\s*=',
        r'onblur\s*=',
        r'onchange\s*=',
        r'<script',
        r'</script',
        r'<iframe',
        r'</iframe',
        r'eval\s*\(',
        r'expression\s*\(',
        r'vbscript:',
        r'data:text/html',
    ]
    
    @staticmethod
    def sanitize_html(text: str, allowed_tags: Optional[list] = None) -> str:
        """
        HTML 태그 제거 및 XSS 방어
        
        Args:
            text: 입력 텍스트
            allowed_tags: 허용할 태그 리스트
            
        Returns:
            정제된 텍스트
        """
        if not text:
            return ""
        
        # HTML 특수문자 이스케이프
        text = html.escape(text)
        
        # 위험한 패턴 제거
        for pattern in Sanitizer.DANGEROUS_PATTERNS:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # 연속 공백 제거
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def sanitize_json(data: Dict[str, Any]) -> Dict[str, Any]:
        """
        JSON 데이터의 모든 문자열 값 정제
        
        Args:
            data: 입력 JSON 데이터
            
        Returns:
            정제된 JSON 데이터
        """
        if isinstance(data, dict):
            return {
                key: Sanitizer.sanitize_json(value) if isinstance(value, (dict, list))
                else Sanitizer.sanitize_html(value) if isinstance(value, str)
                else value
                for key, value in data.items()
            }
        elif isinstance(data, list):
            return [
                Sanitizer.sanitize_json(item) if isinstance(item, (dict, list))
                else Sanitizer.sanitize_html(item) if isinstance(item, str)
                else item
                for item in data
            ]
        elif isinstance(data, str):
            return Sanitizer.sanitize_html(data)
        else:
            return data
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        파일명 정제 (경로 탐색 공격 방어)
        
        Args:
            filename: 입력 파일명
            
        Returns:
            정제된 파일명
        """
        if not filename:
            return ""
        
        # 경로 구분자 제거
        filename = filename.replace('/', '').replace('\\', '')
        filename = filename.replace('..', '')
        
        # 특수문자 제거 (알파벳, 숫자, 일부 특수문자만 허용)
        filename = re.sub(r'[^a-zA-Z0-9_\-\.]', '', filename)
        
        # 최대 길이 제한
        max_length = 255
        if len(filename) > max_length:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
            if ext:
                name = name[:max_length - len(ext) - 1]
                filename = f"{name}.{ext}"
            else:
                filename = filename[:max_length]
        
        return filename
    
    @staticmethod
    def sanitize_sql_identifier(identifier: str) -> str:
        """
        SQL 식별자 정제 (SQL 인젝션 방어)
        
        Args:
            identifier: 테이블명, 컬럼명 등
            
        Returns:
            정제된 식별자
        """
        if not identifier:
            return ""
        
        # 알파벳, 숫자, 언더스코어만 허용
        return re.sub(r'[^a-zA-Z0-9_]', '', identifier)
    
    @staticmethod
    def sanitize_url(url: str) -> Optional[str]:
        """
        URL 정제 (오픈 리다이렉트 방어)
        
        Args:
            url: 입력 URL
            
        Returns:
            정제된 URL 또는 None
        """
        if not url:
            return None
        
        # 프로토콜 확인 (http, https만 허용)
        if not url.startswith(('http://', 'https://')):
            return None
        
        # javascript: 등 위험한 프로토콜 확인
        dangerous_protocols = ['javascript:', 'data:', 'vbscript:', 'file:']
        for protocol in dangerous_protocols:
            if protocol in url.lower():
                return None
        
        return url


# 편의 함수들
def clean_html(text: str) -> str:
    """HTML 태그 제거 편의 함수"""
    return Sanitizer.sanitize_html(text)


def clean_json(data: Dict[str, Any]) -> Dict[str, Any]:
    """JSON 데이터 정제 편의 함수"""
    return Sanitizer.sanitize_json(data)


def clean_filename(filename: str) -> str:
    """파일명 정제 편의 함수"""
    return Sanitizer.sanitize_filename(filename)


def clean_url(url: str) -> Optional[str]:
    """URL 정제 편의 함수"""
    return Sanitizer.sanitize_url(url)