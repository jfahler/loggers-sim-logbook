import json
from pathlib import Path

PROFILE_DIR = Path("profiles")

def load_profile(callsign):
    path = PROFILE_DIR / f"{callsign.lower()}.json"
    if not path.exists():
        return {"callsign": callsign, "mission_summary": {}, "missions": []}
    with open(path, 'r') as f:
        return json.load(f)

def save_profile(callsign, data):
    path = PROFILE_DIR / f"{callsign.lower()}.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def update_with_mission(callsign, mission_data):
    profile = load_profile(callsign)
    profile["missions"].append(mission_data)
    # TODO: recalculate summary
    save_profile(callsign, profile)
