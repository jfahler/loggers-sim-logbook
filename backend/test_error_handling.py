import unittest
import tempfile
import os
import json
import time
from unittest.mock import patch, MagicMock

from error_handling import (
    APIError, ErrorCodes, ErrorMessages, create_error_response, handle_api_error,
    retry_operation, safe_file_save, safe_file_read, safe_file_delete,
    safe_json_save, safe_json_read, validate_required_fields,
    validate_file_operation, log_operation_start, log_operation_success,
    log_operation_failure, ErrorHandler, error_handler
)

class TestErrorHandling(unittest.TestCase):
    """Test cases for error handling system"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_file = os.path.join(self.temp_dir, "test.txt")
        self.test_json_file = os.path.join(self.temp_dir, "test.json")
        
    def tearDown(self):
        """Clean up test environment"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_api_error_creation(self):
        """Test APIError creation with different parameters"""
        # Test with default parameters
        error = APIError(ErrorCodes.FILE_NOT_FOUND)
        self.assertEqual(error.error_code, ErrorCodes.FILE_NOT_FOUND)
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.message, "File not found")
        
        # Test with custom message
        error = APIError(ErrorCodes.FILE_NOT_FOUND, "Custom message")
        self.assertEqual(error.message, "Custom message")
        
        # Test with custom status code
        error = APIError(ErrorCodes.FILE_NOT_FOUND, status_code=404)
        self.assertEqual(error.status_code, 404)
        
        # Test with details and field
        error = APIError(
            ErrorCodes.VALIDATION_ERROR,
            details={"field": "test"},
            field="test_field"
        )
        self.assertEqual(error.details, {"field": "test"})
        self.assertEqual(error.field, "test_field")
    
    def test_create_error_response(self):
        """Test error response creation"""
        response = create_error_response(
            ErrorCodes.FILE_NOT_FOUND,
            "Test message",
            404,
            {"detail": "test"},
            "test_field",
            "req-123"
        )
        
        self.assertFalse(response["success"])
        self.assertEqual(response["error"]["code"], ErrorCodes.FILE_NOT_FOUND)
        self.assertEqual(response["error"]["message"], "Test message")
        self.assertEqual(response["error"]["status_code"], 404)
        self.assertEqual(response["error"]["details"], {"detail": "test"})
        self.assertEqual(response["error"]["field"], "test_field")
        self.assertEqual(response["request_id"], "req-123")
    
    def test_retry_operation_success(self):
        """Test retry operation with successful execution"""
        call_count = 0
        
        @retry_operation(max_attempts=3, delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 1)
    
    def test_retry_operation_failure_then_success(self):
        """Test retry operation that fails then succeeds"""
        call_count = 0
        
        @retry_operation(max_attempts=3, delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise OSError("Temporary failure")
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)
    
    def test_retry_operation_max_failures(self):
        """Test retry operation that fails all attempts"""
        call_count = 0
        
        @retry_operation(max_attempts=3, delay=0.1)
        def test_function():
            nonlocal call_count
            call_count += 1
            raise OSError("Persistent failure")
        
        with self.assertRaises(OSError):
            test_function()
        
        self.assertEqual(call_count, 3)
    
    def test_safe_file_operations(self):
        """Test safe file operations with retry mechanism"""
        # Test file save
        test_content = "Hello, World!"
        safe_file_save(self.test_file, test_content)
        self.assertTrue(os.path.exists(self.test_file))
        
        # Test file read
        content = safe_file_read(self.test_file)
        self.assertEqual(content, test_content)
        
        # Test file delete
        safe_file_delete(self.test_file)
        self.assertFalse(os.path.exists(self.test_file))
    
    def test_safe_json_operations(self):
        """Test safe JSON operations with retry mechanism"""
        test_data = {"name": "test", "value": 123}
        
        # Test JSON save
        safe_json_save(self.test_json_file, test_data)
        self.assertTrue(os.path.exists(self.test_json_file))
        
        # Test JSON read
        data = safe_json_read(self.test_json_file)
        self.assertEqual(data, test_data)
        
        # Test JSON delete
        safe_file_delete(self.test_json_file)
        self.assertFalse(os.path.exists(self.test_json_file))
    
    def test_validate_required_fields(self):
        """Test required field validation"""
        data = {"name": "test", "value": 123}
        
        # Test valid data
        validate_required_fields(data, ["name", "value"])
        
        # Test missing field
        with self.assertRaises(APIError) as cm:
            validate_required_fields(data, ["name", "value", "missing"])
        
        self.assertEqual(cm.exception.error_code, ErrorCodes.MISSING_REQUIRED_FIELD)
        self.assertEqual(cm.exception.field, "missing")
    
    def test_validate_file_operation(self):
        """Test file operation validation"""
        # Test read operation with non-existent file
        with self.assertRaises(APIError) as cm:
            validate_file_operation("/nonexistent/file.txt", "read")
        
        self.assertEqual(cm.exception.error_code, ErrorCodes.FILE_NOT_FOUND)
        
        # Test read operation with existing file
        safe_file_save(self.test_file, "test")
        validate_file_operation(self.test_file, "read")
        
        # Test write operation
        validate_file_operation(self.test_file, "write")
    
    def test_error_handler(self):
        """Test error handler functionality"""
        handler = ErrorHandler()
        
        # Test error handling
        error = APIError(ErrorCodes.FILE_NOT_FOUND)
        response, status_code = handler.handle_error(error)
        
        self.assertEqual(status_code, 400)
        self.assertFalse(response.json["success"])
        
        # Test error statistics
        stats = handler.get_error_stats()
        self.assertEqual(stats["APIError"], 1)
        
        # Test reset statistics
        handler.reset_error_stats()
        stats = handler.get_error_stats()
        self.assertEqual(len(stats), 0)
    
    def test_handle_api_error_function(self):
        """Test handle_api_error function"""
        from flask import Flask
        
        # Create a test Flask app
        app = Flask(__name__)
        
        with app.app_context():
            # Test APIError
            error = APIError(ErrorCodes.FILE_NOT_FOUND)
            response, status_code = handle_api_error(error)
            
            self.assertEqual(status_code, 400)
            self.assertFalse(response.json["success"])
            
            # Test HTTPException
            from werkzeug.exceptions import NotFound
            error = NotFound()
            response, status_code = handle_api_error(error)
            
            self.assertEqual(status_code, 404)
            self.assertFalse(response.json["success"])
            
            # Test unexpected error
            error = ValueError("Test error")
            response, status_code = handle_api_error(error)
            
            self.assertEqual(status_code, 500)
            self.assertFalse(response.json["success"])
    
    @patch('error_handling.logger')
    def test_logging_functions(self, mock_logger):
        """Test logging functions"""
        # Test operation start
        log_operation_start("test_operation", {"param": "value"})
        mock_logger.info.assert_called()
        
        # Test operation success
        log_operation_success("test_operation", {"result": "success"})
        mock_logger.info.assert_called()
        
        # Test operation failure
        error = ValueError("Test error")
        log_operation_failure("test_operation", error, {"param": "value"})
        mock_logger.error.assert_called()
    
    def test_error_codes_completeness(self):
        """Test that all error codes have corresponding messages"""
        for attr_name in dir(ErrorCodes):
            if not attr_name.startswith('_'):
                error_code = getattr(ErrorCodes, attr_name)
                message = ErrorMessages.MESSAGES.get(error_code)
                self.assertIsNotNone(message, f"No message found for error code: {error_code}")
    
    def test_file_operations_with_permissions(self):
        """Test file operations with permission issues"""
        # Create a read-only directory
        read_only_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(read_only_dir)
        
        # On Windows, we can't easily test read-only directories
        # So we'll test with a non-existent parent directory instead
        test_file = os.path.join(self.temp_dir, "nonexistent", "test.txt")
        
        # Test write operation to non-existent directory
        with self.assertRaises(OSError):
            safe_file_save(test_file, "test")
    
    def test_json_operations_with_invalid_data(self):
        """Test JSON operations with invalid data"""
        # Test saving non-serializable data
        class NonSerializable:
            pass
        
        with self.assertRaises(TypeError):
            safe_json_save(self.test_json_file, {"obj": NonSerializable()})
        
        # Test reading invalid JSON
        with open(self.test_json_file, 'w') as f:
            f.write("invalid json")
        
        with self.assertRaises(json.JSONDecodeError):
            safe_json_read(self.test_json_file)
    
    def test_retry_operation_with_different_exceptions(self):
        """Test retry operation with different exception types"""
        call_count = 0
        
        @retry_operation(max_attempts=2, delay=0.1, exceptions=(ValueError,))
        def test_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Temporary failure")
            return "success"
        
        result = test_function()
        self.assertEqual(result, "success")
        self.assertEqual(call_count, 2)
        
        # Test with exception not in retry list
        call_count = 0
        
        @retry_operation(max_attempts=2, delay=0.1, exceptions=(OSError,))
        def test_function2():
            nonlocal call_count
            call_count += 1
            raise ValueError("Should not retry")
        
        with self.assertRaises(ValueError):
            test_function2()
        
        self.assertEqual(call_count, 1)

if __name__ == '__main__':
    unittest.main() 