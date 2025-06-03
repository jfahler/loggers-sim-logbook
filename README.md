<center><img src="loggers-logo.png" width="200px"></center>

# ✈️ Loggers: DCS Flight Logbook

_Loggers is a self-hosted, open-source flight logbook app for DCS World players and squadrons. Upload your Tacview files, extract mission stats, and optionally push automated summaries to Discord._

> **Flight logs. No lies.**

---

# THIS IS AN EARLY DEV BUILD - It probably doesn't work! 

## 🧩 What It Does

- 🔍 Parses Tacview `.xml` (and optionally `.acmi`) exports  
- 👤 Builds and updates pilot profiles from mission stats  
- 📊 Tracks kills, survivability (RTB, KIA, etc.), flight hours, and more  
- 🔁 CLI support for XML batch parsing and profile updates  
- 🌐 Includes a modern web frontend for browsing flight logs  
- 📣 Discord webhook integration (planned)

---

## ⚙️ Stack Overview

- **Frontend:** React (Vite + TailwindCSS + ShadCN + Radix UI)  
- **Backend:** Python (XML parsing and CLI tools)  
- **Old Backend (Legacy):** Encore / Leap (TypeScript, now deprecated)  
- **Hosting/Dev:** Bun, Docker, Xubuntu VM, or local

---

## 📂 Project Structure

```
loggers-sim-logbook/
├── backend/              # New XML-only Python backend
│   ├── update_profiles.py
│   ├── xml_parser.py
│   ├── nickname_matcher.py
│   ├── nicknames.json
│   └── pilot_profiles/   # Output profiles per pilot
├── backendOld/           # Archived Encore/Leap backend
├── frontend/             # React frontend
├── logs/                 # Your Tacview XML exports go here
├── public/               # Static assets (optional)
├── package.json          # Monorepo config
├── bun.lock              # Bun package lockfile
└── README.md             # You're reading it
```

---

## 🚀 Getting Started (Local Dev)

### 1. Clone the Repo

```bash
git clone https://github.com/jfahler/loggers-sim-logbook.git
cd loggers-sim-logbook
```

### 2. Python Backend (XML Parser)

```bash
cd backend
PYTHONPATH=. python3 update_profiles.py --xml ../logs/YourTacviewExport.xml --out pilot_profiles/
```

Output will appear in `pilot_profiles/` as `.json` files for each pilot.

### 3. React Frontend (Vite + Bun)

```bash
cd frontend
npm install
npm run dev
```

Visit [http://localhost:5173](http://localhost:5173)

---

## 🧠 Nickname Matching

Update `nicknames.json` to handle pilot aliasing (e.g. matching "WILDCAT 1-1 | BULLET" to `bullet`):

```json
{
  "bullet": ["wildcat", "bullet"],
  "drunkbonsai": ["drunk", "bonsai"]
}
```

---

## 📡 Deployment Options

- **Static Frontend:** Deploy via GitHub Pages, Vercel, or Netlify  
- **Backend:** Run via cron, script, or manual CLI  
- **Discord Support:** Coming soon (automated flight debriefing)

---

## 📎 TODO / Known Issues

- [ ] Add file upload from browser to backend parser  
- [ ] Merge legacy backend with new XML engine  
- [ ] Optimize pilot matching with user-defined rules  
- [ ] Tag missions by type or squadron  
- [ ] CORS handling for external API integration

---

## 🙏 Acknowledgments

- [Tacview](https://www.tacview.net/) for the flight data  
- [ShadCN UI](https://ui.shadcn.com/) for great React UI primitives  
- [Encore](https://encore.dev) and [Leap](https://leap.new) for early backend work  
- [DCS World](https://www.digitalcombatsimulator.com/) for all the bruises and glory

---

## 📜 License

MIT License — fork, remix, deploy, and fly.
