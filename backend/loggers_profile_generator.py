import xml.etree.ElementTree as ET
import json
from collections import defaultdict
from pathlib import Path
import re
import logging
logger = logging.getLogger(__name__)

# === CONFIG ===
XML_INPUT_PATH = Path("testData.xml")  # Update this path
PROFILE_DIR = Path("pilot_profiles")
PROFILE_DIR.mkdir(exist_ok=True)

# === HELPER FUNCTIONS ===

def sanitize_filename(name):
    return re.sub(r"[^\w\s-]", "", name).strip().replace(" ", "_").lower()

def load_profile(callsign):
    filename = sanitize_filename(callsign) + ".json"
    path = PROFILE_DIR / filename
    if not path.exists():
        return {
            "callsign": callsign,
            "platform_hours": {"DCS": "0:00", "BMS": "0:00", "Total": "0:00"},
            "aircraft_hours": {},
            "mission_summary": {
                "logs_flown": 0, "aa_kills": 0, "aa_avg": 0.0, "ag_kills": 0, "ag_avg": 0.0,
                "frat_kills": 0, "frat_avg": 0.0, "rtb": 0, "rtb_avg": 0.0,
                "res": 0, "mia": 0, "kia": 0, "kia_avg": 0.0, "ctd": 0, "ctd_avg": 0.0
            },
            "missions": []
        }
    with open(path, 'r') as f:
        return json.load(f)

def save_profile(callsign, data):
    filename = sanitize_filename(callsign) + ".json"
    path = PROFILE_DIR / filename
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def add_minutes(time_str, minutes):
    hours, mins = map(int, time_str.split(":"))
    total = hours * 60 + mins + minutes
    return f"{total // 60}:{str(total % 60).zfill(2)}"

def update_profile(profile, mission_data, flight_minutes, aircraft):
    ms = profile["mission_summary"]
    ms["logs_flown"] += 1
    for key in ["aa_kills", "ag_kills", "frat_kills", "rtb", "res", "mia", "kia", "ctd"]:
        ms[key] += mission_data.get(key, 0)
        ms[f"{key.split('_')[0]}_avg"] = round(ms[key] / ms["logs_flown"], 2)

    profile["platform_hours"]["DCS"] = add_minutes(profile["platform_hours"]["DCS"], flight_minutes)
    profile["platform_hours"]["Total"] = add_minutes(profile["platform_hours"]["Total"], flight_minutes)

    if aircraft:
        prev = profile["aircraft_hours"].get(aircraft, "0:00")
        profile["aircraft_hours"][aircraft] = add_minutes(prev, flight_minutes)

    profile["missions"].append(mission_data)

# === PARSE XML ===
tree = ET.parse(XML_INPUT_PATH)
root = tree.getroot()
events = root.find("Events")

# A-G target types
ground_types = {"Infantry", "SAM/AAA", "Vehicle", "Tank", "Artillery"}

# Initialize per-pilot mission logs
pilot_missions = defaultdict(lambda: {
    "date": extract_date_from_xml(root) if root else "2025-05-31",  # TODO: extract from XML if needed
    "mission": "Final Strike",
    "flight_hours": "0:45",  # estimate
    "aa_kills": 0,
    "ag_kills": 0,
    "frat_kills": 0,
    "rtb": 1,
    "res": 0,
    "mia": 0,
    "kia": 0,
    "ctd": 0,
    "platform": "DCS"
})

# Build mission stats from events
for event in events.findall("Event"):
    action = event.findtext("Action")
    primary = event.find("PrimaryObject")
    secondary = event.find("SecondaryObject")

    if primary is None:
        continue

    pilot = primary.findtext("Pilot", default="Unknown")
    aircraft = primary.findtext("Name", default="Unknown")

    if action == "HasBeenDestroyed" and secondary is not None:
        attacker = secondary.findtext("Pilot")
        destroyed_type = primary.findtext("Type", default="")
        if destroyed_type in ground_types:
            pilot_missions[attacker]["ag_kills"] += 1
        else:
            pilot_missions[attacker]["aa_kills"] += 1

    elif action == "HasLanded":
        pilot_missions[pilot]["rtb"] += 1

    elif action == "HasBeenDestroyed":
        victim = primary.findtext("Pilot")
        pilot_missions[victim]["kia"] += 1

# Write profiles
for pilot, mission_data in pilot_missions.items():
    if not pilot or pilot.strip().lower() == "unknown":
        continue
    profile = load_profile(pilot)
    update_profile(profile, mission_data, flight_minutes=45, aircraft=profile.get("Aircraft", "F-16C Fighting Falcon"))
    save_profile(pilot, profile)

# === CLEANUP: Remove non-player unit profiles ===
non_player_keywords = {"infantry", "battalion", "brigade", "regiment", "air defense", "task force", "division"}
for profile_path in PROFILE_DIR.glob("*.json"):
    name = profile_path.stem
    if any(k in name.lower() for k in non_player_keywords):
        profile_path.unlink()

def extract_date_from_xml(xml):
    logger.info("extract_date_from_xml called, but not yet implemented.")
    # Placeholder for XML date extraction logic
    return "2025-05-31"
