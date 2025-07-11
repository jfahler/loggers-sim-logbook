# Security Features Documentation

This document describes the security features implemented in the Loggers DCS Squadron Logbook backend.

## Overview

The backend implements multiple layers of security to protect against common web application vulnerabilities:

1. **Rate Limiting** - Prevents abuse and DoS attacks
2. **CORS Configuration** - Controls cross-origin requests
3. **Request Size Validation** - Prevents large payload attacks
4. **Security Headers** - Protects against common web vulnerabilities
5. **Input Validation** - Sanitizes and validates all user inputs

## Rate Limiting

### Configuration

Rate limits are configured via environment variables or use sensible defaults:

```bash
# Environment variables (optional)
RATE_LIMIT_DEFAULT=100 per minute
RATE_LIMIT_UPLOAD=10 per minute
RATE_LIMIT_DISCORD=30 per minute
```

### Default Limits

- **Default**: 100 requests per minute (general endpoints)
- **Upload**: 10 requests per minute (XML file uploads)
- **Discord**: 30 requests per minute (Discord webhook endpoints)

### Implementation

Rate limiting is implemented using Flask-Limiter with the following features:

- **IP-based tracking**: Uses client IP address for rate limit tracking
- **Memory storage**: Uses in-memory storage for rate limit data
- **Exponential backoff**: Automatic retry with increasing delays
- **Custom error responses**: Standardized 429 responses with error codes

### Endpoints with Rate Limiting

| Endpoint | Method | Rate Limit | Purpose |
|----------|--------|------------|---------|
| `/upload_xml` | POST | 10/minute | File uploads |
| `/discord/pilot-stats` | POST | 30/minute | Discord webhooks |
| `/discord/flight-summary` | POST | 30/minute | Discord webhooks |
| `/squadron-callsigns` | POST | 100/minute | Configuration updates |
| `/pilots` | GET | 100/minute | Data retrieval |
| `/flights` | GET | 100/minute | Data retrieval |
| `/flights/<id>` | GET | 100/minute | Data retrieval |
| `/squadron-callsigns` | GET | 100/minute | Configuration retrieval |

## CORS Configuration

### Configuration

CORS is configured to allow only trusted origins:

```bash
# Environment variable (optional)
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000,https://yourdomain.com
```

### Default Configuration

- **Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Methods**: GET, POST, OPTIONS
- **Headers**: Content-Type, Authorization
- **Credentials**: Supported
- **Max Age**: 3600 seconds (1 hour)

### Security Features

- **Origin validation**: Only allows requests from configured origins
- **Method restriction**: Only allows necessary HTTP methods
- **Header restriction**: Only allows required headers
- **Credential support**: Supports authenticated requests

## Request Size Validation

### File Upload Limits

- **Maximum file size**: 50MB (configurable via `MAX_CONTENT_LENGTH`)
- **Allowed extensions**: `.xml` only
- **Allowed MIME types**: `application/xml`, `text/xml`

### JSON Request Limits

- **Maximum JSON size**: 1MB (configurable via `MAX_JSON_SIZE`)
- **Validation**: Applied to all JSON endpoints

### Implementation

```python
def validate_file_size(file):
    """Validate file size for uploads"""
    if file:
        file.seek(0, 2)  # Seek to end
        file_size = file.tell()
        file.seek(0)  # Reset to beginning
        
        if file_size > MAX_CONTENT_LENGTH:
            raise APIError(
                error_code=ErrorCodes.FILE_TOO_LARGE,
                message=f"File too large. Maximum size is {MAX_CONTENT_LENGTH // (1024*1024)}MB",
                status_code=413
            )

def validate_request_size():
    """Validate request size for JSON requests"""
    if request.is_json:
        content_length = request.content_length
        if content_length and content_length > MAX_JSON_SIZE:
            raise APIError(
                error_code=ErrorCodes.FILE_TOO_LARGE,
                message=f"Request too large. Maximum JSON size is {MAX_JSON_SIZE // (1024*1024)}MB",
                status_code=413
            )
```

## Security Headers

The application automatically adds the following security headers to all responses:

### Headers Implemented

| Header | Value | Purpose |
|--------|-------|---------|
| `X-Content-Type-Options` | `nosniff` | Prevents MIME type sniffing |
| `X-Frame-Options` | `DENY` | Prevents clickjacking |
| `X-XSS-Protection` | `1; mode=block` | Enables XSS protection |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | Enforces HTTPS |
| `Content-Security-Policy` | `default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'` | Controls resource loading |

### Implementation

```python
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    security_headers = get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    return response
```

## Error Handling

### Standardized Error Responses

All errors return a consistent JSON format:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "status_code": 400
  },
  "request_id": "uuid-for-tracking"
}
```

### Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `FILE_TOO_LARGE` | 413 | File or request too large |
| `RATE_LIMIT_ERROR` | 429 | Rate limit exceeded |
| `FILE_NOT_FOUND` | 404 | Resource not found |
| `INVALID_INPUT` | 400 | Invalid input data |
| `VALIDATION_ERROR` | 400 | Validation failed |
| `INTERNAL_ERROR` | 500 | Internal server error |

## Monitoring and Logging

### Security Endpoints

- `/security-info` - Returns current security configuration
- `/error-stats` - Returns error statistics for monitoring

### Logging

All security events are logged with appropriate levels:

- **INFO**: Successful operations, configuration changes
- **WARNING**: Rate limit warnings, validation failures
- **ERROR**: Security violations, system errors

### Example Security Info Response

```json
{
  "success": true,
  "security_config": {
    "rate_limits": {
      "default": "100 per minute",
      "upload": "10 per minute",
      "discord": "30 per minute"
    },
    "cors": {
      "origins": ["http://localhost:3000"],
      "methods": ["GET", "POST", "OPTIONS"],
      "supports_credentials": true
    },
    "upload": {
      "max_file_size_mb": 50,
      "max_json_size_mb": 1,
      "allowed_extensions": [".xml"]
    },
    "security_headers": [
      "X-Content-Type-Options",
      "X-Frame-Options",
      "X-XSS-Protection",
      "Strict-Transport-Security",
      "Content-Security-Policy"
    ]
  },
  "timestamp": "2024-01-01T00:00:00Z"
}
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | CORS allowed origins |
| `RATE_LIMIT_DEFAULT` | `100 per minute` | Default rate limit |
| `RATE_LIMIT_UPLOAD` | `10 per minute` | Upload rate limit |
| `RATE_LIMIT_DISCORD` | `30 per minute` | Discord rate limit |
| `MAX_CONTENT_LENGTH` | `52428800` (50MB) | Maximum file size |
| `MAX_JSON_SIZE` | `1048576` (1MB) | Maximum JSON size |

### Production Recommendations

1. **HTTPS Only**: Use HTTPS in production and configure HSTS
2. **Restrict Origins**: Only allow your frontend domain in CORS
3. **Monitor Rate Limits**: Adjust limits based on usage patterns
4. **Log Security Events**: Monitor logs for security violations
5. **Regular Updates**: Keep dependencies updated for security patches

## Testing

Run the security test suite:

```bash
python test_security.py
```

The test suite covers:
- Rate limiting functionality
- CORS configuration
- Request size validation
- Security headers
- Configuration validation

## Security Best Practices

1. **Input Validation**: All user inputs are validated and sanitized
2. **File Upload Security**: Only XML files are accepted with size limits
3. **Rate Limiting**: Prevents abuse and DoS attacks
4. **CORS Protection**: Restricts cross-origin requests
5. **Security Headers**: Protects against common web vulnerabilities
6. **Error Handling**: No sensitive information leaked in errors
7. **Logging**: Comprehensive logging for security monitoring
8. **Configuration**: Environment-based configuration for flexibility

## Incident Response

In case of security incidents:

1. **Monitor Logs**: Check application logs for suspicious activity
2. **Check Rate Limits**: Review rate limit violations
3. **Verify Origins**: Ensure CORS is properly configured
4. **Review Errors**: Check error statistics for patterns
5. **Update Configuration**: Adjust security settings if needed

## Support

For security-related issues or questions:

1. Review this documentation
2. Check the security configuration
3. Monitor the `/security-info` endpoint
4. Review application logs
5. Contact the development team 