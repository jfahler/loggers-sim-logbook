# DCS Pilot Logbook Backend

A Python Flask backend for processing Tacview XML files and tracking pilot statistics for DCS, BMS, and other flight simulators.

## Features

- Parse Tacview XML export files
- Track pilot statistics (kills, deaths, flight hours, etc.)
- Generate pilot profiles and mission summaries
- Discord webhook integration for notifications
- RESTful API endpoints for frontend integration

## Setup

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables (optional):
```bash
# Discord webhook for notifications
export DISCORD_WEBHOOK_URL="your_discord_webhook_url"
```

3. Run the Flask application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- `GET /` - Health check and service info
- `POST /upload_xml` - Upload and process Tacview XML files
- `GET /pilots` - List all pilot profiles
- `GET /flights` - List all flight records
- `GET /flights/<id>` - Get specific flight details
- `POST /discord/pilot-stats` - Send pilot stats to Discord
- `POST /discord/flight-summary` - Send flight summary to Discord
- `GET /health` - Health check endpoint

## File Structure

- `app.py` - Main Flask application
- `xml_parser.py` - Tacview XML parsing logic
- `profile_manager.py` - Pilot profile management
- `webhook_helpers.py` - Discord webhook integration
- `pilot_profiles/` - Directory containing pilot JSON profiles
- `uploads/` - Temporary directory for uploaded files

## Development

The backend is built with Flask and uses standard Python libraries for XML parsing and file handling. All pilot data is stored as JSON files in the `pilot_profiles/` directory. 