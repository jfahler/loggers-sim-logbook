<center><img src="loggers-logo.png" width="200px"></center>

# ✈️ Loggers: DCS Flight Logbook

_Loggers is a self-hosted, open-source flight logbook app for DCS World players and squadrons. Upload your Tacview files, extract mission stats, and optionally push automated summaries to Discord._

## 🏗️ Architecture

- **Backend**: Python Flask API for processing Tacview XML files
- **Frontend**: React/TypeScript with Vite and Tailwind CSS for the web interface
- **Data Storage**: JSON files for pilot profiles and mission data

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- npm or yarn

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
python -m pip install -r requirements.txt
```

3. Start the development server:
```bash
python dev.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

### Quick Development Launcher

Use the provided scripts to start both servers quickly:

**Windows (PowerShell):**
```powershell
.\start-dev.ps1
```

**Windows (Command Prompt):**
```cmd
start-dev.bat
```

## 📁 Project Structure

```
loggers-sim-logbook/
├── backend/                 # Python Flask API
│   ├── app.py              # Main Flask application
│   ├── xml_parser.py       # Tacview XML parsing
│   ├── profile_manager.py  # Pilot profile management
│   ├── webhook_helpers.py  # Discord integration
│   ├── pilot_profiles/     # Pilot data storage
│   ├── requirements.txt    # Python dependencies
│   ├── setup.py           # Setup script
│   ├── dev.py             # Development server
│   └── run.py             # Production server
├── frontend/               # React/TypeScript frontend
│   ├── src/               # Source code
│   ├── components/        # React components
│   ├── pages/            # Page components
│   ├── tailwind.config.js # Tailwind CSS configuration
│   ├── postcss.config.js  # PostCSS configuration
│   └── package.json      # Node dependencies
├── start-dev.ps1          # PowerShell development launcher
├── start-dev.bat          # Batch development launcher
└── pilot_profiles/        # Legacy pilot profiles
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False

# Discord Webhook (optional)
DISCORD_WEBHOOK_URL=your_discord_webhook_url_here

# File Upload Configuration
MAX_CONTENT_LENGTH=16777216  # 16MB in bytes
```

## 📊 Features

- **Tacview XML Processing**: Parse mission data from Tacview exports
- **Pilot Statistics**: Track kills, deaths, flight hours, and more
- **Multi-Platform Support**: DCS World, BMS, and other flight simulators
- **Discord Integration**: Automated mission summaries and pilot stats
- **Web Interface**: Modern React frontend with Tailwind CSS styling
- **RESTful API**: Clean API endpoints for integration
- **Responsive Design**: Works on desktop, tablet, and mobile

## 🛠️ Development

### Backend Development

```bash
cd backend
python dev.py  # Starts with auto-reload
```

### Frontend Development

```bash
cd frontend
npm run dev    # Starts Vite dev server with hot reload
```

### API Testing

Test the backend API:

```bash
# Health check
curl http://localhost:5000/health

# Upload XML file
curl -X POST -F "file=@mission.xml" http://localhost:5000/upload_xml

# Get pilot list
curl http://localhost:5000/pilots
```

## 📝 API Endpoints

- `GET /` - Service information
- `GET /health` - Health check
- `POST /upload_xml` - Upload Tacview XML file
- `GET /pilots` - List all pilots
- `GET /flights` - List all flights
- `GET /flights/<id>` - Get specific flight
- `POST /discord/pilot-stats` - Send pilot stats to Discord
- `POST /discord/flight-summary` - Send flight summary to Discord

## 🎨 UI Components

The frontend uses a modern component library with:
- **Tailwind CSS** for styling
- **Radix UI** for accessible components
- **Lucide React** for icons
- **React Query** for data fetching
- **React Router** for navigation

## 🤝 Contributing

This is an active development project. Contributions are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is open source. See LICENSE file for details.

---

**Status**: ✅ Fully functional with working CSS and API integration

