"""
Security Configuration for Loggers DCS Squadron Logbook

This module contains security-related configuration settings and validation functions.
"""

import os
from typing import List, Dict, Any

# Rate Limiting Configuration
RATE_LIMITS = {
    'default': '100 per minute',
    'upload': '10 per minute',
    'discord': '30 per minute',
    'auth': '5 per minute'
}

# CORS Configuration
CORS_CONFIG = {
    'origins': ['http://localhost:3000', 'http://127.0.0.1:3000'],
    'methods': ['GET', 'POST', 'OPTIONS'],
    'allow_headers': ['Content-Type', 'Authorization'],
    'supports_credentials': True,
    'max_age': 3600
}

# File Upload Configuration
UPLOAD_CONFIG = {
    'max_file_size': 50 * 1024 * 1024,  # 50MB
    'max_json_size': 1 * 1024 * 1024,   # 1MB
    'allowed_extensions': ['.xml'],
    'allowed_mime_types': ['application/xml', 'text/xml']
}

# Security Headers
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
}

def get_rate_limit(limit_type: str = 'default') -> str:
    """Get rate limit configuration from environment or defaults"""
    env_key = f'RATE_LIMIT_{limit_type.upper()}'
    return os.getenv(env_key, RATE_LIMITS.get(limit_type, RATE_LIMITS['default']))

def get_cors_origins() -> List[str]:
    """Get CORS origins from environment or defaults"""
    origins = os.getenv('ALLOWED_ORIGINS')
    if origins:
        return [origin.strip() for origin in origins.split(',')]
    return CORS_CONFIG['origins']

def get_max_file_size() -> int:
    """Get maximum file size from environment or defaults"""
    return int(os.getenv('MAX_CONTENT_LENGTH', UPLOAD_CONFIG['max_file_size']))

def get_max_json_size() -> int:
    """Get maximum JSON size from environment or defaults"""
    return int(os.getenv('MAX_JSON_SIZE', UPLOAD_CONFIG['max_json_size']))

def validate_origin(origin: str) -> bool:
    """Validate if an origin is allowed"""
    allowed_origins = get_cors_origins()
    return origin in allowed_origins

def get_security_headers() -> Dict[str, str]:
    """Get security headers configuration"""
    return SECURITY_HEADERS.copy()

def validate_file_extension(filename: str) -> bool:
    """Validate file extension"""
    if not filename:
        return False
    
    ext = os.path.splitext(filename)[1].lower()
    return ext in UPLOAD_CONFIG['allowed_extensions']

def validate_mime_type(mime_type: str) -> bool:
    """Validate MIME type"""
    return mime_type in UPLOAD_CONFIG['allowed_mime_types']

def get_security_summary() -> Dict[str, Any]:
    """Get a summary of security configuration"""
    return {
        'rate_limits': {
            'default': get_rate_limit('default'),
            'upload': get_rate_limit('upload'),
            'discord': get_rate_limit('discord')
        },
        'cors': {
            'origins': get_cors_origins(),
            'methods': CORS_CONFIG['methods'],
            'supports_credentials': CORS_CONFIG['supports_credentials']
        },
        'upload': {
            'max_file_size_mb': get_max_file_size() // (1024 * 1024),
            'max_json_size_mb': get_max_json_size() // (1024 * 1024),
            'allowed_extensions': UPLOAD_CONFIG['allowed_extensions']
        },
        'security_headers': list(SECURITY_HEADERS.keys())
    } 