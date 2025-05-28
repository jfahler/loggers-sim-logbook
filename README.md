<img src="loggers-logo.png" alt="loggers logo" width="200"/>
# ✈️ Loggers: DCS Flight Logbook

**Loggers** is a self-hosted, open-source flight logbook system for DCS World and Tacview users.  
Upload your `.acmi` files, track detailed flight stats, and optionally push automated summaries to Discord.

> _Flight logs. No lies._

---

## 🧩 What It Does

- 🔍 Parses `.acmi` files exported from Tacview
- 🧠 Extracts pilot callsign, aircraft, mission, kills, duration, and more
- 📊 Displays flight data locally in a browser UI
- 📣 Sends flight summaries to Discord (via webhook)
- 💻 Easily self-hosted, no backend expertise required

---

## 📂 Repo Overview

```bash
loggers-sim-logbook/
├── frontend/         # Leap-based React frontend
├── backend/          # Leap/Encore backend functions (Node)
├── public/           # Static assets
├── .env.example      # Template for environment config
├── README.md         # You're reading it
└── LICENSE           # MIT License
