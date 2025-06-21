from fastapi import FastAPI
from datetime import datetime
from backend.mock_stats import fetch_pilot_stats

app = FastAPI()

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/pilot/{ucid}")
def get_pilot(ucid: str):
    return fetch_pilot_stats(ucid)