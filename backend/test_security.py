import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, MagicMock
from io import BytesIO

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

from security_config import (
    get_rate_limit, get_cors_origins, get_max_file_size, get_max_json_size,
    validate_origin, validate_file_extension, validate_mime_type,
    get_security_headers, get_security_summary
)

class TestSecurityConfig(unittest.TestCase):
    """Test cases for security configuration"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
    def test_get_rate_limit_default(self):
        """Test getting default rate limit"""
        limit = get_rate_limit('default')
        self.assertIsInstance(limit, str)
        self.assertIn('per minute', limit)
    
    def test_get_rate_limit_upload(self):
        """Test getting upload rate limit"""
        limit = get_rate_limit('upload')
        self.assertIsInstance(limit, str)
        self.assertIn('per minute', limit)
    
    def test_get_cors_origins(self):
        """Test getting CORS origins"""
        origins = get_cors_origins()
        self.assertIsInstance(origins, list)
        self.assertTrue(len(origins) > 0)
    
    def test_get_max_file_size(self):
        """Test getting max file size"""
        size = get_max_file_size()
        self.assertIsInstance(size, int)
        self.assertTrue(size > 0)
    
    def test_get_max_json_size(self):
        """Test getting max JSON size"""
        size = get_max_json_size()
        self.assertIsInstance(size, int)
        self.assertTrue(size > 0)
    
    def test_validate_origin(self):
        """Test origin validation"""
        origins = get_cors_origins()
        if origins:
            self.assertTrue(validate_origin(origins[0]))
            self.assertFalse(validate_origin('http://malicious.com'))
    
    def test_validate_file_extension(self):
        """Test file extension validation"""
        self.assertTrue(validate_file_extension('test.xml'))
        self.assertTrue(validate_file_extension('TEST.XML'))
        self.assertFalse(validate_file_extension('test.txt'))
        self.assertFalse(validate_file_extension('test'))
        self.assertFalse(validate_file_extension(''))
    
    def test_validate_mime_type(self):
        """Test MIME type validation"""
        self.assertTrue(validate_mime_type('application/xml'))
        self.assertTrue(validate_mime_type('text/xml'))
        self.assertFalse(validate_mime_type('text/plain'))
        self.assertFalse(validate_mime_type('application/json'))
    
    def test_get_security_headers(self):
        """Test getting security headers"""
        headers = get_security_headers()
        self.assertIsInstance(headers, dict)
        self.assertTrue(len(headers) > 0)
        
        # Check for common security headers
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection'
        ]
        for header in expected_headers:
            self.assertIn(header, headers)
    
    def test_get_security_summary(self):
        """Test getting security summary"""
        summary = get_security_summary()
        self.assertIsInstance(summary, dict)
        
        # Check required keys
        required_keys = ['rate_limits', 'cors', 'upload', 'security_headers']
        for key in required_keys:
            self.assertIn(key, summary)
        
        # Check rate limits
        rate_limits = summary['rate_limits']
        self.assertIn('default', rate_limits)
        self.assertIn('upload', rate_limits)
        self.assertIn('discord', rate_limits)
        
        # Check upload config
        upload = summary['upload']
        self.assertIn('max_file_size_mb', upload)
        self.assertIn('max_json_size_mb', upload)
        self.assertIn('allowed_extensions', upload)

class TestSecurityIntegration(unittest.TestCase):
    """Test security features integration"""
    
    def setUp(self):
        """Set up test Flask app with security features"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        
        # Initialize rate limiter
        self.limiter = Limiter(
            app=self.app,
            key_func=get_remote_address,
            default_limits=['10 per minute'],
            storage_uri="memory://"
        )
        
        # Configure CORS
        CORS(self.app, 
             origins=['http://localhost:3000'],
             methods=['GET', 'POST'],
             allow_headers=['Content-Type'])
        
        # Add test routes
        @self.app.route('/test')
        @self.limiter.limit('5 per minute')
        def test_route():
            return {'message': 'success'}
        
        @self.app.route('/test-cors')
        def test_cors():
            return {'message': 'cors test'}
        
        self.client = self.app.test_client()
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        # Make requests up to the limit
        for i in range(5):
            response = self.client.get('/test')
            self.assertEqual(response.status_code, 200)
        
        # Next request should be rate limited
        response = self.client.get('/test')
        self.assertEqual(response.status_code, 429)
    
    def test_cors_headers(self):
        """Test CORS headers are present"""
        response = self.client.get('/test-cors')
        self.assertEqual(response.status_code, 200)
        
        # Check for CORS headers
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        self.assertIn('Access-Control-Allow-Methods', response.headers)
    
    def test_security_headers_middleware(self):
        """Test security headers middleware"""
        # Add security headers middleware
        @self.app.after_request
        def add_security_headers(response):
            security_headers = get_security_headers()
            for header, value in security_headers.items():
                response.headers[header] = value
            return response
        
        response = self.client.get('/test-cors')
        
        # Check for security headers
        security_headers = get_security_headers()
        for header, value in security_headers.items():
            self.assertIn(header, response.headers)
            self.assertEqual(response.headers[header], value)

class TestRequestSizeValidation(unittest.TestCase):
    """Test request size validation"""
    
    def setUp(self):
        """Set up test environment"""
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_file_size_validation(self):
        """Test file size validation"""
        # Create a test file that's too large
        large_content = b'x' * (get_max_file_size() + 1024)
        large_file = BytesIO(large_content)
        large_file.filename = 'test.xml'
        
        # This would be tested in a real upload endpoint
        # For now, just test the validation function
        from app import validate_file_size
        
        with self.assertRaises(Exception):
            validate_file_size(large_file)
    
    def test_json_size_validation(self):
        """Test JSON size validation"""
        # Create large JSON data
        large_data = {'data': 'x' * (get_max_json_size() + 1024)}
        
        # This would be tested in a real endpoint
        # For now, just verify the size
        json_str = json.dumps(large_data)
        self.assertGreater(len(json_str), get_max_json_size())

if __name__ == '__main__':
    unittest.main() 