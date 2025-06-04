from flask import Flask, send_from_directory, request, jsonify
import os
from generate_index import generate_index
from xml_parser import parse_xml
from update_profiles import update_profiles

app = Flask(__name__)
PROFILE_DIR = os.path.join(os.path.dirname(__file__), 'pilot_profiles')

# Run once at startup
generate_index()

@app.route('/')
def root():
    return "✅ Loggers backend is running."

@app.route('/pilot_profiles/<path:filename>')
def serve_profile(filename):
    return send_from_directory(PROFILE_DIR, filename)

@app.route('/upload_xml', methods=['POST'])
def upload_xml():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    
    file = request.files['file']
    
    if not file.filename.endswith('.xml'):
        return jsonify({"error": "Only .xml files allowed"}), 400

    filepath = os.path.join(PROFILE_DIR, "temp_upload.xml")
    file.save(filepath)

    # Parse XML and update profiles
    parse_xml(filepath)
    update_profiles()
    generate_index()

    return jsonify({"status": "success"}), 200

if __name__ == '__main__':
    app.run(debug=True)
