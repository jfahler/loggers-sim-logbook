<center><img src="loggers-logo.png" width="200px"></center>


# ✈️ Loggers: DCS Flight Logbook

_Loggers is a self-hosted, open-source flight logbook app for DCS World players and squadrons. Upload your Tacview files, extract mission stats, and optionally push automated summaries to Discord._

> **Flight logs. No lies.**

---

## 🧩 What It Does

- 🔍 Parses `.acmi` files exported from Tacview  
- 🧠 Extracts data such as pilot callsign, aircraft type, kills, mission duration, and more  
- 📊 Displays detailed flight logs in a browser-based UI  
- 📣 Supports Discord webhook integration for automated debrief summaries  
- 💻 Built for local development and self-hosting by DCS mission creators

---

## ⚙️ Stack Overview

- **Frontend:** React (with Vite, Tailwind, Radix UI)
- **Backend:** TypeScript (Encore / Leap Framework)
- **Data Parsing:** Encodes Tacview `.acmi` data for backend processing
- **Hosting/Dev:** Docker + Local VM (Xubuntu) or Leap Cloud

---

## 📂 Project Structure

```
loggers-sim-logbook/
├── backend/          # Leap/Encore backend services
├── frontend/         # React frontend (Vite)
├── public/           # Static assets (optional)
├── bun.lock          # Bun package lockfile
├── package.json      # Monorepo-level config
└── .gitignore        # Standard node/bun ignores
```

---

## 🚀 Getting Started (Local Dev on Linux VM)

### 1. Clone the Repo

```bash
git clone https://github.com/jfahler/loggers-sim-logbook.git
cd loggers-sim-logbook
```

### 2. Install Dependencies

Make sure you have **Bun**, **Docker**, and **Encore** installed.

```bash
bun install
cd frontend && bun install
cd ../backend && bun install
```

### 3. Run Locally

In the `backend/` folder:

```bash
encore run
```

Then in a new terminal tab, from the `frontend/` folder:

```bash
bun dev
```

Visit `http://localhost:3000` in your browser.

---

## 📡 Deployment

- **Leap Cloud:** Sync the repo to [leap.new](https://leap.new) and deploy from there.
- **Self-Hosting:** VM + Docker setup will support this stack with minimal tweaking.
- **CORS/Upload Limits:** Large `.acmi` files may trigger backend CORS issues or size restrictions — backend file streaming or preprocessing may be required for production.

---

## 📎 TODO / Known Issues

- [ ] Add streaming or chunked uploads for large `.acmi` files
- [ ] Improve `.acmi` parsing and reduce payload size
- [ ] Add user-friendly error messages
- [ ] Enable mission categorization or metadata tagging
- [ ] Optimize for server deployments with reverse proxy support

---

## 🙏 Acknowledgments

- [Tacview](https://www.tacview.net/) for flight data exports
- [Leap](https://leap.new) / [Encore](https://encore.dev) for backend framework
- [DCS World](https://www.digitalcombatsimulator.com/) for eating all our free time

---

## 📜 License

MIT License — free to fork, modify, and deploy.

