# app.py improvements

import os
import logging
from flask import Flask, send_from_directory, request, jsonify
import json
from werkzeug.utils import secure_filename
from generate_index import generate_index
from xml_parser import parse_xml
from update_profiles import update_profiles
from webhook_helpers import send_pilot_stats, send_flight_summary
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration from environment variables
PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'pilot_profiles')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))  # 16MB default

# Ensure directories exist
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize pilot index at startup
try:
    generate_index()
    logger.info("Pilot index initialized successfully")
except Exception as e:
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
def upload_xml():
    try:
        logger.info("Received XML upload request")
        
        if 'file' not in request.files:
            logger.warning("No file uploaded in request")
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        
        if file.filename == '':
            logger.warning("Empty filename in upload request")
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith('.xml'):
            logger.warning(f"Invalid file type uploaded: {file.filename}")
            return jsonify({"error": "Only XML files are allowed"}), 400

        # Use secure filename to prevent path traversal
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        logger.info(f"Saving uploaded file: {filename}")
        file.save(filepath)

        # Process the XML
        logger.info(f"Processing XML file: {filepath}")
        parse_result = parse_xml(filepath)
        
        # Clean up the uploaded file after processing
        try:
            os.remove(filepath)
            logger.debug(f"Cleaned up temporary file: {filepath}")
        except OSError as e:
            logger.warning(f"Failed to clean up temporary file {filepath}: {e}")
        
        if parse_result.get('success', True):
            logger.info(f"XML parsing successful, updating profiles for {parse_result.get('pilots_count', 'unknown')} pilots")
            update_profiles(filepath)
            generate_index()
            
            return jsonify({
                "status": "success",
                "message": "Tacview XML processed successfully",
                "pilots_updated": parse_result.get('pilots_count', 'unknown')
            }), 200
        else:
            error_msg = parse_result.get('error', 'Unknown error')
            logger.error(f"XML parsing failed: {error_msg}")
            return jsonify({
                "status": "error", 
                "message": f"XML parsing failed: {error_msg}"
            }), 400
            
    except Exception as e:
        logger.error(f"Upload processing failed: {str(e)}", exc_info=True)
        return jsonify({
            "status": "error",
            "message": f"Upload processing failed: {str(e)}"
        }), 500

@app.route('/discord/pilot-stats', methods=['POST'])
def post_pilot_stats():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Basic validation
        if 'pilotName' not in data:
            return jsonify({"error": "pilotName is required"}), 400
            
        result = send_pilot_stats(data)
        status_code = 200 if result.get('success') else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Error processing request: {str(e)}"
        }), 500

@app.route('/discord/flight-summary', methods=['POST'])
def post_flight_summary():
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type must be application/json"}), 400
            
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        if 'pilotName' not in data:
            return jsonify({"error": "pilotName is required"}), 400
            
        result = send_flight_summary(data)
        status_code = 200 if result.get('success') else 400
        
        return jsonify(result), status_code
        
    except Exception as e:
        return jsonify({
            "success": False, 
            "message": f"Error processing request: {str(e)}"
        }), 500

# Health check endpoint for monitoring
@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "discord_configured": bool(os.getenv("DISCORD_WEBHOOK_URL"))
    })

# Error handlers
@app.errorhandler(413)
def too_large(e):
    return jsonify({"error": "File too large. Maximum size is 16MB."}), 413

@app.errorhandler(500)
def internal_error(e):
    return jsonify({"error": "Internal server error occurred."}), 500

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
        if not fname.endswith('.json') or fname == 'index.json':
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
        total_time = parse_hhmm(prof.get('platform_hours', {}).get('Total', '0:00')) * 60
        aircraft_hours = prof.get('aircraft_hours', {})
        fav_aircraft = None
        most_time = -1
        for air, val in aircraft_hours.items():
            mins = parse_hhmm(val)
            if mins > most_time:
                fav_aircraft = air
                most_time = mins

        flights = summary.get('logs_flown', 0)
        avg_duration = int(total_time / flights) if flights else 0

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
def list_pilots():
    return jsonify({'pilots': aggregate_pilots()})


@app.route('/flights')
def list_flights():
    limit = int(request.args.get('limit', 20))
    offset = int(request.args.get('offset', 0))
    flights = collect_flights()
    return jsonify({'flights': flights[offset:offset + limit], 'total': len(flights)})


@app.route('/flights/<int:flight_id>')
def get_flight(flight_id: int):
    for flight in collect_flights():
        if flight['id'] == flight_id:
            return jsonify(flight)
    return jsonify({'error': 'Flight not found'}), 404


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)