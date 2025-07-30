import os
import json
import logging
import time
import functools
from typing import Dict, Any, Optional, Callable, Union
from werkzeug.exceptions import HTTPException
from flask import jsonify, request
import traceback

# Configure logging
logger = logging.getLogger(__name__)

# Error codes and messages
class ErrorCodes:
    """Standard error codes for the application"""
    # File operations
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    FILE_INVALID_TYPE = "FILE_INVALID_TYPE"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
    FILE_PROCESSING_FAILED = "FILE_PROCESSING_FAILED"
    FILE_DELETE_FAILED = "FILE_DELETE_FAILED"
    
    # XML processing
    XML_PARSE_ERROR = "XML_PARSE_ERROR"
    XML_INVALID_STRUCTURE = "XML_INVALID_STRUCTURE"
    XML_TOO_MANY_EVENTS = "XML_TOO_MANY_EVENTS"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Data processing
    DATA_PROCESSING_ERROR = "DATA_PROCESSING_ERROR"
    PILOT_DATA_ERROR = "PILOT_DATA_ERROR"
    PROFILE_UPDATE_ERROR = "PROFILE_UPDATE_ERROR"
    
    # Discord integration
    DISCORD_WEBHOOK_ERROR = "DISCORD_WEBHOOK_ERROR"
    DISCORD_INVALID_DATA = "DISCORD_INVALID_DATA"
    
    # DCS Server Bot integration
    DCS_BOT_WEBHOOK_ERROR = "DCS_BOT_WEBHOOK_ERROR"
    DCS_BOT_INVALID_DATA = "DCS_BOT_INVALID_DATA"
    DCS_BOT_SIGNATURE_ERROR = "DCS_BOT_SIGNATURE_ERROR"
    DCS_BOT_DISABLED = "DCS_BOT_DISABLED"
    
    # DCS REST API integration
    DCS_REST_API_ERROR = "DCS_REST_API_ERROR"
    DCS_REST_API_DISABLED = "DCS_REST_API_DISABLED"
    DCS_REST_API_TIMEOUT = "DCS_REST_API_TIMEOUT"
    DCS_REST_API_AUTH_ERROR = "DCS_REST_API_AUTH_ERROR"
    
    # Configuration
    CONFIG_ERROR = "CONFIG_ERROR"
    ENV_VAR_MISSING = "ENV_VAR_MISSING"
    
    # General errors
    INTERNAL_ERROR = "INTERNAL_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    RATE_LIMIT_ERROR = "RATE_LIMIT_ERROR"

class ErrorMessages:
    """Standard error messages"""
    MESSAGES = {
        ErrorCodes.FILE_NOT_FOUND: "File not found",
        ErrorCodes.FILE_TOO_LARGE: "File too large",
        ErrorCodes.FILE_INVALID_TYPE: "Invalid file type",
        ErrorCodes.FILE_UPLOAD_FAILED: "File upload failed",
        ErrorCodes.FILE_PROCESSING_FAILED: "File processing failed",
        ErrorCodes.FILE_DELETE_FAILED: "Failed to delete file",
        ErrorCodes.XML_PARSE_ERROR: "XML parsing error",
        ErrorCodes.XML_INVALID_STRUCTURE: "Invalid XML structure",
        ErrorCodes.XML_TOO_MANY_EVENTS: "XML contains too many events",
        ErrorCodes.VALIDATION_ERROR: "Validation error",
        ErrorCodes.INVALID_INPUT: "Invalid input",
        ErrorCodes.MISSING_REQUIRED_FIELD: "Missing required field",
        ErrorCodes.DATA_PROCESSING_ERROR: "Data processing error",
        ErrorCodes.PILOT_DATA_ERROR: "Pilot data error",
        ErrorCodes.PROFILE_UPDATE_ERROR: "Profile update error",
        ErrorCodes.DISCORD_WEBHOOK_ERROR: "Discord webhook error",
        ErrorCodes.DISCORD_INVALID_DATA: "Invalid Discord data",
        ErrorCodes.DCS_BOT_WEBHOOK_ERROR: "DCS Server Bot webhook error",
        ErrorCodes.DCS_BOT_INVALID_DATA: "Invalid DCS Server Bot data",
        ErrorCodes.DCS_BOT_SIGNATURE_ERROR: "DCS Server Bot signature verification failed",
        ErrorCodes.DCS_BOT_DISABLED: "DCS Server Bot integration is disabled",
        ErrorCodes.DCS_REST_API_ERROR: "DCS REST API error",
        ErrorCodes.DCS_REST_API_DISABLED: "DCS REST API integration is disabled",
        ErrorCodes.DCS_REST_API_TIMEOUT: "DCS REST API request timeout",
        ErrorCodes.DCS_REST_API_AUTH_ERROR: "DCS REST API authentication error",
        ErrorCodes.CONFIG_ERROR: "Configuration error",
        ErrorCodes.ENV_VAR_MISSING: "Environment variable missing",
        ErrorCodes.INTERNAL_ERROR: "Internal server error",
        ErrorCodes.NETWORK_ERROR: "Network error",
        ErrorCodes.TIMEOUT_ERROR: "Request timeout",
        ErrorCodes.RATE_LIMIT_ERROR: "Rate limit exceeded"
    }

def get_error_message(error_code: str, custom_message: Optional[str] = None) -> str:
    """Get error message for a given error code"""
    if custom_message:
        return custom_message
    return ErrorMessages.MESSAGES.get(error_code, "Unknown error")

class APIError(Exception):
    """Custom API error class"""
    def __init__(self, 
                 error_code: str, 
                 message: Optional[str] = None, 
                 status_code: int = 400,
                 details: Optional[Dict[str, Any]] = None,
                 field: Optional[str] = None):
        self.error_code = error_code
        self.message = get_error_message(error_code, message)
        self.status_code = status_code
        self.details = details or {}
        self.field = field
        super().__init__(self.message)

def create_error_response(error_code: str, 
                         message: Optional[str] = None, 
                         status_code: int = 400,
                         details: Optional[Dict[str, Any]] = None,
                         field: Optional[str] = None,
                         request_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response
    
    Args:
        error_code: Standard error code
        message: Custom error message (optional)
        status_code: HTTP status code
        details: Additional error details
        field: Field name if validation error
        request_id: Request ID for tracking
        
    Returns:
        Standardized error response dictionary
    """
    response = {
        "success": False,
        "error": {
            "code": error_code,
            "message": get_error_message(error_code, message),
            "status_code": status_code
        }
    }
    
    if details:
        response["error"]["details"] = details
    
    if field:
        response["error"]["field"] = field
    
    if request_id:
        response["request_id"] = request_id
    
    return response

def log_error(error: Exception, 
              context: Optional[Dict[str, Any]] = None, 
              level: str = "ERROR") -> None:
    """
    Log error with context information
    
    Args:
        error: Exception to log
        context: Additional context information
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    log_data = {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "traceback": traceback.format_exc()
    }
    
    if context:
        log_data.update(context)
    
    # Add request information if available
    if request:
        log_data.update({
            "method": request.method,
            "url": request.url,
            "user_agent": request.headers.get("User-Agent"),
            "ip": request.remote_addr
        })
    
    log_message = f"Error: {error} | Context: {json.dumps(log_data, default=str)}"
    
    if level.upper() == "DEBUG":
        logger.debug(log_message)
    elif level.upper() == "INFO":
        logger.info(log_message)
    elif level.upper() == "WARNING":
        logger.warning(log_message)
    elif level.upper() == "CRITICAL":
        logger.critical(log_message)
    else:
        logger.error(log_message)

def retry_operation(max_attempts: int = 3, 
                   delay: float = 1.0, 
                   backoff_factor: float = 2.0,
                   exceptions: tuple = (OSError, IOError)) -> Callable:
    """
    Decorator to retry operations with exponential backoff
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff_factor: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay
            
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt < max_attempts - 1:
                        logger.warning(
                            f"Operation {func.__name__} failed (attempt {attempt + 1}/{max_attempts}): {e}. "
                            f"Retrying in {current_delay} seconds..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff_factor
                    else:
                        logger.error(
                            f"Operation {func.__name__} failed after {max_attempts} attempts: {e}"
                        )
            
            raise last_exception
        
        return wrapper
    return decorator

@retry_operation(max_attempts=3, delay=0.5)
def safe_file_save(file_path: str, content: Union[str, bytes], mode: str = 'w') -> None:
    """
    Safely save file with retry mechanism
    
    Args:
        file_path: Path to save the file
        content: Content to write
        mode: File mode ('w' for text, 'wb' for binary)
    """
    # Ensure directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    with open(file_path, mode) as f:
        f.write(content)

@retry_operation(max_attempts=3, delay=0.5)
def safe_file_read(file_path: str, mode: str = 'r') -> str:
    """
    Safely read file with retry mechanism
    
    Args:
        file_path: Path to read the file
        mode: File mode ('r' for text, 'rb' for binary)
        
    Returns:
        File content
    """
    with open(file_path, mode) as f:
        return f.read()

@retry_operation(max_attempts=3, delay=0.5)
def safe_file_delete(file_path: str) -> None:
    """
    Safely delete file with retry mechanism
    
    Args:
        file_path: Path to delete
    """
    if os.path.exists(file_path):
        os.remove(file_path)

@retry_operation(max_attempts=3, delay=0.5)
def safe_json_save(file_path: str, data: Dict[str, Any]) -> None:
    """
    Safely save JSON file with retry mechanism
    
    Args:
        file_path: Path to save the JSON file
        data: Data to save
    """
    safe_file_save(file_path, json.dumps(data, indent=2))

@retry_operation(max_attempts=3, delay=0.5)
def safe_json_read(file_path: str) -> Dict[str, Any]:
    """
    Safely read JSON file with retry mechanism
    
    Args:
        file_path: Path to read the JSON file
        
    Returns:
        Parsed JSON data
    """
    content = safe_file_read(file_path)
    return json.loads(content)

def handle_api_error(error: Exception) -> tuple:
    """
    Handle API errors and return standardized response
    
    Args:
        error: Exception to handle
        
    Returns:
        Tuple of (response, status_code)
    """
    if isinstance(error, APIError):
        response = create_error_response(
            error_code=error.error_code,
            message=error.message,
            status_code=error.status_code,
            details=error.details,
            field=error.field
        )
        log_error(error, level="WARNING")
        return jsonify(response), error.status_code
    
    elif isinstance(error, HTTPException):
        response = create_error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message=str(error),
            status_code=error.code
        )
        log_error(error, level="WARNING")
        return jsonify(response), error.code
    
    else:
        # Unexpected error
        response = create_error_response(
            error_code=ErrorCodes.INTERNAL_ERROR,
            message="An unexpected error occurred",
            status_code=500
        )
        log_error(error, level="ERROR")
        return jsonify(response), 500

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> None:
    """
    Validate that required fields are present in data
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        
    Raises:
        APIError: If required field is missing
    """
    for field in required_fields:
        if field not in data or data[field] is None:
            raise APIError(
                error_code=ErrorCodes.MISSING_REQUIRED_FIELD,
                message=f"Missing required field: {field}",
                field=field
            )

def validate_file_operation(file_path: str, operation: str = "read") -> None:
    """
    Validate file operation conditions
    
    Args:
        file_path: Path to validate
        operation: Operation type ("read", "write", "delete")
        
    Raises:
        APIError: If validation fails
    """
    if operation == "read":
        if not os.path.exists(file_path):
            raise APIError(
                error_code=ErrorCodes.FILE_NOT_FOUND,
                message=f"File not found: {file_path}"
            )
        if not os.access(file_path, os.R_OK):
            raise APIError(
                error_code=ErrorCodes.FILE_PROCESSING_FAILED,
                message=f"File not readable: {file_path}"
            )
    
    elif operation == "write":
        # Check if directory is writable
        directory = os.path.dirname(file_path)
        if directory and not os.access(directory, os.W_OK):
            raise APIError(
                error_code=ErrorCodes.FILE_PROCESSING_FAILED,
                message=f"Directory not writable: {directory}"
            )

def log_operation_start(operation: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log the start of an operation
    
    Args:
        operation: Operation name
        context: Additional context
    """
    log_data = {"operation": operation, "status": "started"}
    if context:
        log_data.update(context)
    
    logger.info(f"Operation started: {json.dumps(log_data, default=str)}")

def log_operation_success(operation: str, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log successful operation completion
    
    Args:
        operation: Operation name
        context: Additional context
    """
    log_data = {"operation": operation, "status": "completed"}
    if context:
        log_data.update(context)
    
    logger.info(f"Operation completed: {json.dumps(log_data, default=str)}")

def log_operation_failure(operation: str, error: Exception, context: Optional[Dict[str, Any]] = None) -> None:
    """
    Log operation failure
    
    Args:
        operation: Operation name
        error: Exception that occurred
        context: Additional context
    """
    log_data = {
        "operation": operation, 
        "status": "failed",
        "error": str(error)
    }
    if context:
        log_data.update(context)
    
    logger.error(f"Operation failed: {json.dumps(log_data, default=str)}")

class ErrorHandler:
    """Error handler class for managing error responses and logging"""
    
    def __init__(self):
        self.error_counts = {}
    
    def handle_error(self, error: Exception, context: Optional[Dict[str, Any]] = None) -> tuple:
        """
        Handle error and return standardized response
        
        Args:
            error: Exception to handle
            context: Additional context
            
        Returns:
            Tuple of (response, status_code)
        """
        # Increment error count
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
        
        # Log error with context
        log_error(error, context)
        
        # Return standardized response
        return handle_api_error(error)
    
    def get_error_stats(self) -> Dict[str, int]:
        """Get error statistics"""
        return self.error_counts.copy()
    
    def reset_error_stats(self) -> None:
        """Reset error statistics"""
        self.error_counts.clear()

# Global error handler instance
error_handler = ErrorHandler() 