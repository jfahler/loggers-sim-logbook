#!/usr/bin/env python3
"""
Setup script for DCS Pilot Logbook Backend
"""

import os
import sys
import subprocess
from pathlib import Path
from generate_index import generate_index

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        sys.exit(1)

def create_directories():
    """Create necessary directories"""
    print("📁 Creating directories...")
    directories = [
        "pilot_profiles",
        "uploads",
        "__pycache__"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")

def create_env_file():
    """Create .env file if it doesn't exist"""
    env_file = Path(".env")
    if not env_file.exists():
        print("🔧 Creating .env file...")
        with open(env_file, "w") as f:
            f.write("# Flask Configuration\n")
            f.write("FLASK_HOST=0.0.0.0\n")
            f.write("FLASK_PORT=5000\n")
            f.write("FLASK_DEBUG=False\n")
            f.write("\n")
            f.write("# Discord Webhook (optional)\n")
            f.write("DISCORD_WEBHOOK_URL=your_discord_webhook_url_here\n")
            f.write("\n")
            f.write("# File Upload Configuration\n")
            f.write("MAX_CONTENT_LENGTH=16777216  # 16MB in bytes\n")
        print("✅ Created .env file")
    else:
        print("✅ .env file already exists")

def initialize_pilot_index():
    """Initialize the pilot index"""
    print("👥 Initializing pilot index...")
    try:
        generate_index()
        print("✅ Pilot index initialized")
    except Exception as e:
        print(f"⚠️  Warning: Could not initialize pilot index: {e}")

def main():
    print("🚀 Setting up DCS Pilot Logbook Backend...")
    print("=" * 50)
    
    check_python_version()
    install_dependencies()
    create_directories()
    create_env_file()
    initialize_pilot_index()
    
    print("=" * 50)
    print("✅ Setup completed successfully!")
    print("\nTo start the development server:")
    print("  python dev.py")
    print("\nTo start the production server:")
    print("  python run.py")
    print("\nTo test the API:")
    print("  curl http://localhost:5000/")

if __name__ == "__main__":
    main() 