# app.py improvements

import os
from flask import Flask, send_from_directory, request, jsonify
from werkzeug.utils import secure_filename
from generate_index import generate_index
from xml_parser import parse_xml
from update_profiles import update_profiles
from webhook_helpers import send_pilot_stats, send_flight_summary

app = Flask(__name__)

# Configuration
PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'pilot_profiles')
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Ensure directories exist
os.makedirs(PROFILE_DIR, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize pilot index at startup
generate_index()

@app.route('/')
def root():
    return jsonify({
        "status": "online",
        "service": "Loggers DCS Squadron Logbook",
        "version": "1.0.0"
    })

@app.route('/upload_xml', methods=['POST'])
def upload_xml():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not file.filename.lower().endswith('.xml'):
            return jsonify({"error": "Only XML files are allowed"}), 400

        # Use secure filename to prevent path traversal
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        file.save(filepath)

        # Process the XML
        parse_result = parse_xml(filepath)
        
        # Clean up the uploaded file after processing
        try:
            os.remove(filepath)
        except OSError:
            pass  # File cleanup failed, but processing succeeded
        
        if parse_result.get('success', True):  # Assuming parse_xml returns success status
            update_profiles()
            generate_index()
            
            return jsonify({
                "status": "success",
                "message": "Tacview XML processed successfully",
                "pilots_updated": parse_result.get('pilots_count', 'unknown')
            }), 200
        else:
            return jsonify({
                "status": "error", 
                "message": f"XML parsing failed: {parse_result.get('error', 'Unknown error')}"
            }), 400
            
    except Exception as e:
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)