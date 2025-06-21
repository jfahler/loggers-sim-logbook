#!/usr/bin/env python3
"""
Production runner for the DCS Pilot Logbook Backend
"""

import os
from dotenv import load_dotenv
from app import app

# Load environment variables from .env file if it exists
load_dotenv()

if __name__ == '__main__':
    # Get configuration from environment variables
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    print(f"🚀 Starting DCS Pilot Logbook Backend")
    print(f"📍 Server: http://{host}:{port}")
    print(f"🔧 Debug mode: {debug}")
    
    app.run(
        host=host,
        port=port,
        debug=debug
    ) 