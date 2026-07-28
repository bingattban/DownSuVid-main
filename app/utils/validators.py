"""
Validation Utilities Module
"""

import re
from typing import Optional, Tuple
from pathlib import Path
import os


class Validators:
    """Utility class for validation functions"""
    
    @staticmethod
    def validate_url(url: str) -> bool:
        if not url: return False
        url_pattern = re.compile(
            r'^https?://'
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
            r'localhost|'
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
            r'(?::\d+)?'
            r'(?:/?|[/?]\S+)$',
            re.IGNORECASE
        )
        return bool(url_pattern.match(url))
    
    @staticmethod
    def validate_quality(quality: str) -> bool:
        if not quality or not quality.endswith('p'): return False
        try:
            height = int(quality.rstrip('p'))
            return 0 < height <= 4320
        except ValueError: return False
    
    @staticmethod
    def validate_file_path(path: str) -> bool:
        if not path or len(path) > 4096: return False
        dangerous_patterns = ['..', '~', '$', '`', '|', ';', '&']
        if any(pattern in path for pattern in dangerous_patterns): return False
        try:
            Path(path).resolve()
            return True
        except Exception: return False
    
    @staticmethod
    def validate_filename(filename: str) -> bool:
        if not filename or len(filename) > 255: return False
        invalid_chars = '<>:"/\\|?*'
        if any(char in filename for char in invalid_chars): return False
        reserved_names = [
            'CON', 'PRN', 'AUX', 'NUL', 'COM1', 'COM2', 'COM3', 'COM4', 'COM5', 'COM6', 'COM7', 'COM8', 'COM9',
            'LPT1', 'LPT2', 'LPT3', 'LPT4', 'LPT5', 'LPT6', 'LPT7', 'LPT8', 'LPT9',
        ]
        return os.path.splitext(filename)[0].upper() not in reserved_names
    
    @staticmethod
    def validate_language_code(code: str) -> bool:
        return bool(code and (len(code) in (2, 3)) and code.isalpha())
    
    @staticmethod
    def sanitize_text(text: str) -> str:
        if not text: return ""
        text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
        return re.sub(r'\s+', ' ', text).strip()
    
    @staticmethod
    def validate_sha256(hash_string: str) -> bool:
        return bool(hash_string and re.match(r'^[a-fA-F0-9]{64}$', hash_string))
    
    @staticmethod
    def validate_email(email: str) -> bool:
        if not email: return False
        return bool(re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email))
    
    @staticmethod
    def get_file_extension(filename: str) -> str:
        return os.path.splitext(filename)[1].lower()
