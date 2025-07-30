import os
import json
import logging
from datetime import datetime
import uuid

from flask import Flask, request, jsonify, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

from xml_parser import parse_xml, load_squadron_callsigns, save_squadron_callsigns
from update_profiles import update_profiles_from_data
from generate_index import generate_index
from webhook_helpers import send_pilot_stats, send_flight_summary
from validation import (
    validate_file_upload, validate_xml_content, validate_discord_data,
    validate_callsigns_list, sanitize_string
)
from error_handling import (
    APIError, ErrorCodes, create_error_response, handle_api_error,
    log_operation_start, log_operation_success, log_operation_failure,
    safe_file_delete, validate_required_fields, error_handler
)
from security_config import (
    get_rate_limit, get_cors_origins, get_max_file_size, get_max_json_size,
    get_security_headers, validate_file_extension, validate_mime_type
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration from environment variables
PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'pilot_profiles')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')

# Security configuration
ALLOWED_ORIGINS = get_cors_origins()
RATE_LIMIT_DEFAULT = get_rate_limit('default')
RATE_LIMIT_UPLOAD = get_rate_limit('upload')
RATE_LIMIT_DISCORD = get_rate_limit('discord')
MAX_CONTENT_LENGTH = get_max_file_size()
MAX_JSON_SIZE = get_max_json_size()

# Ensure directories exist
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[RATE_LIMIT_DEFAULT],
    storage_uri="memory://"
)

# Configure CORS
CORS(app, 
     origins=ALLOWED_ORIGINS,
     methods=['GET', 'POST', 'OPTIONS'],
     allow_headers=['Content-Type', 'Authorization'],
     supports_credentials=True,
     max_age=3600)

# Add security headers middleware
@app.after_request
def add_security_headers(response):
    """Add security headers to all responses"""
    security_headers = get_security_headers()
    for header, value in security_headers.items():
        response.headers[header] = value
    return response

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

# Initialize pilot index at startup
try:
    log_operation_start("pilot_index_initialization")
    generate_index()
    log_operation_success("pilot_index_initialization")
    logger.info("Pilot index initialized successfully")
except Exception as e:
    log_operation_failure("pilot_index_initialization", e)
    logger.error(f"Failed to initialize pilot index: {e}")

@app.route('/')
def root():
    return jsonify({
        "status": "online",
        "service": "Loggers DCS Squadron Logbook",
        "version": "1.0.0",
        "description": "Tacview XML processing and pilot statistics tracking"
    })

@app.route('/upload_xml', methods=['POST'])
@limiter.limit(RATE_LIMIT_UPLOAD)
def upload_xml():
    request_id = str(uuid.uuid4())
    operation = "xml_upload"
    
    try:
        log_operation_start(operation, {"request_id": request_id})
        logger.info(f"Received XML upload request: {request_id}")
        
        # Validate request has file
        if 'file' not in request.files:
            raise APIError(
                error_code=ErrorCodes.FILE_UPLOAD_FAILED,
                message="No file uploaded",
                status_code=400
            )

        file = request.files['file']
        
        # Validate file size
        validate_file_size(file)
        
        # Validate file upload
        is_valid, error_msg = validate_file_upload(file)
        if not is_valid:
            raise APIError(
                error_code=ErrorCodes.FILE_INVALID_TYPE,
                message=error_msg,
                status_code=400
            )

        # Use secure filename to prevent path traversal
        filename = secure_filename(file.filename or '')
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        logger.info(f"Saving uploaded file: {filename}")
        file.save(filepath)

        # Validate XML content structure
        is_valid, error_msg = validate_xml_content(filepath)
        if not is_valid:
            # Clean up the uploaded file on validation error
            try:
                safe_file_delete(filepath)
                logger.debug(f"Cleaned up temporary file after validation error: {filepath}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {filepath}: {cleanup_error}")
            
            raise APIError(
                error_code=ErrorCodes.XML_INVALID_STRUCTURE,
                message=error_msg,
                status_code=400
            )

        # Process the XML
        logger.info(f"Processing XML file: {filepath}")
        parse_result = parse_xml(filepath)
        
        if parse_result.get('success', True):
            pilots_count = parse_result.get('pilots_count', 'unknown')
            logger.info(f"XML parsing successful, updating profiles for {pilots_count} pilots")
            
            # Update profiles with the parsed data
            pilot_data = parse_result.get('pilot_data', {})
            if pilot_data:
                update_profiles_from_data(pilot_data)
                generate_index()
            
            # Clean up the uploaded file after processing
            try:
                safe_file_delete(filepath)
                logger.debug(f"Cleaned up temporary file: {filepath}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {filepath}: {cleanup_error}")
            
            log_operation_success(operation, {
                "request_id": request_id,
                "pilots_updated": pilots_count
            })
            
            return jsonify({
                "success": True,
                "message": "Tacview XML processed successfully",
                "pilots_updated": pilots_count,
                "request_id": request_id
            }), 200
        else:
            # Clean up the uploaded file on error
            try:
                safe_file_delete(filepath)
                logger.debug(f"Cleaned up temporary file after error: {filepath}")
            except Exception as cleanup_error:
                logger.warning(f"Failed to clean up temporary file {filepath}: {cleanup_error}")
                
            error_msg = parse_result.get('error', 'Unknown error')
            raise APIError(
                error_code=ErrorCodes.XML_PARSE_ERROR,
                message=f"XML parsing failed: {error_msg}",
                status_code=400
            )
            
    except APIError:
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        log_operation_failure(operation, e, {"request_id": request_id})
        raise APIError(
            error_code=ErrorCodes.FILE_PROCESSING_FAILED,
            message=f"Upload processing failed: {str(e)}",
            status_code=500
        )

@app.route('/discord/pilot-stats', methods=['POST'])
@limiter.limit(RATE_LIMIT_DISCORD)
def post_pilot_stats():
    request_id = str(uuid.uuid4())
    operation = "discord_pilot_stats"
    
    try:
        log_operation_start(operation, {"request_id": request_id})
        
        # Validate request size
        validate_request_size()
        
        if not request.is_json:
            raise APIError(
                error_code=ErrorCodes.INVALID_INPUT,
                message="Content-Type must be application/json",
                status_code=400
            )
            
        data = request.get_json()
        
        if not data:
            raise APIError(
                error_code=ErrorCodes.INVALID_INPUT,
                message="No JSON data provided",
                status_code=400
            )
        
        # Validate required fields
        validate_required_fields(data, ['pilotName'])
        
        # Validate Discord data
        is_valid, error_msg = validate_discord_data(data)
        if not is_valid:
            raise APIError(
                error_code=ErrorCodes.DISCORD_INVALID_DATA,
                message=error_msg,
                status_code=400
            )
            
        result = send_pilot_stats(data)
        
        if result.get('success'):
            log_operation_success(operation, {"request_id": request_id})
            return jsonify({
                "success": True,
                "message": result.get('message', 'Pilot stats sent successfully'),
                "request_id": request_id
            }), 200
        else:
            raise APIError(
                error_code=ErrorCodes.DISCORD_WEBHOOK_ERROR,
                message=result.get('message', 'Failed to send pilot stats'),
                status_code=400
            )
        
    except APIError:
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        log_operation_failure(operation, e, {"request_id": request_id})
        raise APIError(
            error_code=ErrorCodes.DISCORD_WEBHOOK_ERROR,
            message=f"Error processing request: {str(e)}",
            status_code=500
        )

@app.route('/discord/flight-summary', methods=['POST'])
@limiter.limit(RATE_LIMIT_DISCORD)
def post_flight_summary():
    request_id = str(uuid.uuid4())
    operation = "discord_flight_summary"
    
    try:
        log_operation_start(operation, {"request_id": request_id})
        
        # Validate request size
        validate_request_size()
        
        if not request.is_json:
            raise APIError(
                error_code=ErrorCodes.INVALID_INPUT,
                message="Content-Type must be application/json",
                status_code=400
            )
            
        data = request.get_json()
        
        if not data:
            raise APIError(
                error_code=ErrorCodes.INVALID_INPUT,
                message="No JSON data provided",
                status_code=400
            )
        
        # Validate required fields
        validate_required_fields(data, ['pilotName'])
        
        # Validate Discord data
        is_valid, error_msg = validate_discord_data(data)
        if not is_valid:
            raise APIError(
                error_code=ErrorCodes.DISCORD_INVALID_DATA,
                message=error_msg,
                status_code=400
            )
            
        result = send_flight_summary(data)
        
        if result.get('success'):
            log_operation_success(operation, {"request_id": request_id})
            return jsonify({
                "success": True,
                "message": result.get('message', 'Flight summary sent successfully'),
                "request_id": request_id
            }), 200
        else:
            raise APIError(
                error_code=ErrorCodes.DISCORD_WEBHOOK_ERROR,
                message=result.get('message', 'Failed to send flight summary'),
                status_code=400
            )
        
    except APIError:
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        log_operation_failure(operation, e, {"request_id": request_id})
        raise APIError(
            error_code=ErrorCodes.DISCORD_WEBHOOK_ERROR,
            message=f"Error processing request: {str(e)}",
            status_code=500
        )

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "discord_configured": bool(os.getenv("DISCORD_WEBHOOK_URL")),
    })

# Error statistics endpoint for monitoring
@app.route('/error-stats')
def error_stats():
    """Get error statistics for monitoring"""
    return jsonify({
        "success": True,
        "error_stats": error_handler.get_error_stats(),
        "timestamp": datetime.utcnow().isoformat()
    })

# Security configuration endpoint
@app.route('/security-info')
def security_info():
    """Get security configuration information"""
    from security_config import get_security_summary
    return jsonify({
        "success": True,
        "security_config": get_security_summary(),
        "timestamp": datetime.utcnow().isoformat()
    })

# Error handlers
@app.errorhandler(APIError)
def handle_api_error(error):
    """Handle custom API errors"""
    return error_handler.handle_error(error)

@app.errorhandler(413)
def too_large(e):
    """Handle file too large errors"""
    response = create_error_response(
        error_code=ErrorCodes.FILE_TOO_LARGE,
        message="File too large. Maximum size is 50MB.",
        status_code=413
    )
    return jsonify(response), 413

@app.errorhandler(429)
def rate_limit_exceeded(e):
    """Handle rate limit exceeded errors"""
    response = create_error_response(
        error_code=ErrorCodes.RATE_LIMIT_ERROR,
        message="Rate limit exceeded. Please try again later.",
        status_code=429
    )
    return jsonify(response), 429

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors"""
    response = create_error_response(
        error_code=ErrorCodes.INTERNAL_ERROR,
        message="Internal server error occurred.",
        status_code=500
    )
    return jsonify(response), 500

@app.errorhandler(404)
def not_found(e):
    """Handle not found errors"""
    response = create_error_response(
        error_code=ErrorCodes.FILE_NOT_FOUND,
        message="Resource not found.",
        status_code=404
    )
    return jsonify(response), 404

@app.errorhandler(405)
def method_not_allowed(e):
    """Handle method not allowed errors"""
    response = create_error_response(
        error_code=ErrorCodes.INVALID_INPUT,
        message="Method not allowed.",
        status_code=405
    )
    return jsonify(response), 405

@app.route('/pilot_profiles/<path:filename>')
def serve_profile(filename):
    return send_from_directory(PROFILE_DIR, filename)


def parse_hhmm(value: str) -> int:
    """Convert H:MM string to minutes."""
    try:
        hours, minutes = value.split(':')
        return int(hours) * 60 + int(minutes)
    except Exception:
        return 0


def load_profiles() -> list:
    profiles = []
    for fname in os.listdir(PROFILE_DIR):
        if not fname.endswith('.json') or fname in ['index.json', 'template.json']:
            continue
        with open(os.path.join(PROFILE_DIR, fname)) as f:
            profiles.append(json.load(f))
    return profiles


def aggregate_pilots() -> list:
    pilots = []
    for idx, prof in enumerate(load_profiles(), start=1):
        callsign = prof.get('callsign', '')
        if '|' in callsign:
            cs, name = [p.strip() for p in callsign.split('|', 1)]
        else:
            cs, name = None, callsign
        summary = prof.get('mission_summary', {})
        
        # Handle platform_hours as numbers (minutes) instead of HH:MM strings
        platform_hours = prof.get('platform_hours', {})
        total_time = platform_hours.get('Total', 0)  # Already in minutes
        
        aircraft_hours = prof.get('aircraft_hours', {})
        fav_aircraft = None
        most_time = -1
        for air, val in aircraft_hours.items():
            # Handle both string (HH:MM) and numeric (minutes) formats
            if isinstance(val, str):
                mins = parse_hhmm(val)
            else:
                mins = int(val) if val else 0
            if mins > most_time:
                fav_aircraft = air
                most_time = mins

        flights = summary.get('logs_flown', 0)
        # Ensure both values are integers for division
        total_time = int(total_time) if total_time else 0
        flights = int(flights) if flights else 0
        avg_duration = int(total_time / flights) if flights > 0 else 0

        pilots.append({
            'pilot': {
                'id': idx,
                'name': name,
                'callsign': cs,
                'createdAt': datetime.utcnow().isoformat(),
            },
            'totalFlights': flights,
            'totalFlightTime': total_time,
            'averageFlightDuration': avg_duration,
            'totalAaKills': summary.get('aa_kills', 0),
            'totalAgKills': summary.get('ag_kills', 0),
            'totalFratKills': summary.get('frat_kills', 0),
            'totalRtbCount': summary.get('rtb', 0),
            'totalEjections': summary.get('ejections', 0),
            'totalDeaths': summary.get('kia', 0),
            'favoriteAircraft': fav_aircraft,
        })
    return pilots


def collect_flights() -> list:
    flights = []
    idx = 1
    for prof in load_profiles():
        callsign = prof.get('callsign', '')
        if '|' in callsign:
            cs, name = [p.strip() for p in callsign.split('|', 1)]
        else:
            cs, name = None, callsign
        for mission in prof.get('missions', []):
            duration = parse_hhmm(mission.get('flight_hours', '0:00')) * 60
            flights.append({
                'id': idx,
                'pilotName': name,
                'pilotCallsign': cs,
                'aircraftType': mission.get('aircraft', 'Unknown'),
                'missionName': mission.get('mission'),
                'startTime': mission.get('date'),
                'durationSeconds': duration,
                'aaKills': mission.get('aa_kills', 0),
                'agKills': mission.get('ag_kills', 0),
                'fratKills': mission.get('frat_kills', 0),
                'rtbCount': mission.get('rtb', 0),
                'ejections': mission.get('ejections', 0),
                'deaths': mission.get('kia', 0),
            })
            idx += 1
    return flights


@app.route('/pilots')
@limiter.limit(RATE_LIMIT_DEFAULT)
def list_pilots():
    return jsonify({'pilots': aggregate_pilots()})


@app.route('/flights')
@limiter.limit(RATE_LIMIT_DEFAULT)
def list_flights():
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    flights = collect_flights()
    return jsonify({'flights': flights[offset:offset + limit], 'total': len(flights)})


@app.route('/flights/<int:flight_id>')
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_flight(flight_id: int):
    for flight in collect_flights():
        if flight['id'] == flight_id:
            return jsonify(flight)
    return jsonify({'error': 'Flight not found'}), 404


@app.route('/squadron-callsigns', methods=['GET'])
@limiter.limit(RATE_LIMIT_DEFAULT)
def get_squadron_callsigns():
    """Get current squadron callsigns"""
    callsigns = load_squadron_callsigns()
    return jsonify({'callsigns': callsigns})


@app.route('/squadron-callsigns', methods=['POST'])
@limiter.limit(RATE_LIMIT_DEFAULT)
def update_squadron_callsigns():
    """Update squadron callsigns"""
    request_id = str(uuid.uuid4())
    operation = "update_squadron_callsigns"
    
    try:
        log_operation_start(operation, {"request_id": request_id})
        
        # Validate request size
        validate_request_size()
        
        if not request.is_json:
            raise APIError(
                error_code=ErrorCodes.INVALID_INPUT,
                message="Content-Type must be application/json",
                status_code=400
            )
            
        data = request.get_json()
        
        if not data or 'callsigns' not in data:
            raise APIError(
                error_code=ErrorCodes.MISSING_REQUIRED_FIELD,
                message="callsigns array is required",
                field="callsigns",
                status_code=400
            )
        
        callsigns = data['callsigns']
        
        # Validate callsigns list
        is_valid, error_msg = validate_callsigns_list(callsigns)
        if not is_valid:
            raise APIError(
                error_code=ErrorCodes.VALIDATION_ERROR,
                message=error_msg,
                status_code=400
            )
        
        # Sanitize callsigns
        valid_callsigns = [sanitize_string(callsign.strip()) for callsign in callsigns if callsign.strip()]
        
        # Save to config file
        if save_squadron_callsigns(valid_callsigns):
            log_operation_success(operation, {
                "request_id": request_id,
                "callsigns_count": len(valid_callsigns)
            })
            return jsonify({
                "success": True,
                "message": f"Updated squadron callsigns: {', '.join(valid_callsigns)}",
                "callsigns": valid_callsigns,
                "request_id": request_id
            })
        else:
            raise APIError(
                error_code=ErrorCodes.CONFIG_ERROR,
                message="Failed to save squadron callsigns",
                status_code=500
            )
            
    except APIError:
        # Re-raise API errors to be handled by error handler
        raise
    except Exception as e:
        log_operation_failure(operation, e, {"request_id": request_id})
        raise APIError(
            error_code=ErrorCodes.CONFIG_ERROR,
            message=f"Error updating squadron callsigns: {str(e)}",
            status_code=500
        )


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)