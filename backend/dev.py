#!/usr/bin/env python3
"""
Development server for the DCS Pilot Logbook Backend
"""

import os
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file if it exists
load_dotenv()

if __name__ == '__main__':
    # Development configuration
    host = '127.0.0.1'
    port = 5000
    debug = True
    
    print(f"🚀 Starting DCS Pilot Logbook Backend (Development)")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    print(f"📁 Profile directory: {os.path.join(os.path.dirname(__file__), 'pilot_profiles')}")
    print(f"📁 Upload directory: {os.path.join(os.path.dirname(__file__), 'uploads')}")
    
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True
    ) 