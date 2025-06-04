from flask import Flask, send_from_directory, request, jsonify
import os
from generate_index import generate_index
from xml_parser import parse_xml
from update_profiles import update_profiles
from webhook_helpers import send_pilot_stats, send_flight_summary

# Optional: enable this if accessing backend from a different port (like React dev server)
# from flask_cors import CORS

app = Flask(__name__)
# CORS(app)  # Enable if needed for frontend integration

PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'pilot_profiles')

# 📦 Initialize pilot index at startup
generate_index()

# 🌐 Root route (health check)
@app.route('/')
def root():
    return "✅ Loggers backend is running."

# 📁 Serve individual pilot JSON profiles
@app.route('/pilot_profiles/<path:filename>')
def serve_profile(filename):
    return send_from_directory(PROFILE_DIR, filename)

# 📤 Handle Tacview XML upload and processing
@app.route('/upload_xml', methods=['POST'])
def upload_xml():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    if not file.filename.endswith('.xml'):
        return jsonify({"error": "Only .xml files allowed"}), 400

    filepath = os.path.join(PROFILE_DIR, "temp_upload.xml")
    file.save(filepath)

    # Parse XML, update profiles, rebuild index
    parse_xml(filepath)
    update_profiles()
    generate_index()

    return jsonify({
        "status": "success",
        "message": "Tacview XML processed and pilot profiles updated."
    }), 200

# 📣 Send a pilot stat summary to Discord
@app.route('/discord/pilot-stats', methods=['POST'])
def post_pilot_stats():
    data = request.json
    result = send_pilot_stats(data)
    return jsonify(result)

@app.route('/discord/flight-summary', methods=['POST'])
def post_flight_summary():
    data = request.json
    result = send_flight_summary(data)
    return jsonify(result)

# 🚀 Run local server
if __name__ == '__main__':
    app.run(debug=True)