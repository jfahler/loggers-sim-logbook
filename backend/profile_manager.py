import json
from pathlib import Path

def load_profile(nickname, profile_dir):
    path = Path(profile_dir) / f"{nickname}.json"
    if not path.exists():
        return {
            "callsign": nickname,
            "nicknames": [nickname],
            "profile_image": "",
            "platform_hours": {"DCS": 0, "BMS": 0, "IL2": 0, "Total": 0},
            "aircraft_hours": {},
            "mission_summary": {
                "logs_flown": 0, "aa_kills": 0, "aa_avg": 0.0, "ag_kills": 0, "ag_avg": 0.0,
                "frat_kills": 0, "frat_avg": 0.0, "rtb": 0, "rtb_avg": 0.0,
                "ejections": 0, "ejections_avg": 0.0, "res": 0, "res_avg": 0.0,
                "mia": 0, "mia_avg": 0.0, "kia": 0, "kia_avg": 0.0, 
                "ctd": 0, "ctd_avg": 0.0
            },
            "missions": [],
            "notes": ""
        }
    with open(path, 'r') as f:
        return json.load(f)

def save_profile(nickname, data, profile_dir):
    path = Path(profile_dir) / f"{nickname}.json"
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def add_minutes(time_str, minutes):
    hours, mins = map(int, time_str.split(":"))
    total = hours * 60 + mins + minutes
    return f"{total // 60}:{str(total % 60).zfill(2)}"

def update_profile(profile, mission_data, flight_minutes, aircraft):
    ms = profile["mission_summary"]
    ms["logs_flown"] += 1
    
    # Update all mission statistics
    for key in ["aa_kills", "ag_kills", "frat_kills", "rtb", "ejections", "res", "mia", "kia", "ctd"]:
        ms[key] += mission_data.get(key, 0)
        ms[f"{key.split('_')[0]}_avg"] = round(ms[key] / ms["logs_flown"], 2)

    # Update platform hours based on detected platform (in minutes)
    platform = mission_data.get("platform", "DCS")
    if platform in profile["platform_hours"]:
        profile["platform_hours"][platform] += flight_minutes
    profile["platform_hours"]["Total"] += flight_minutes

    # Update aircraft hours (in minutes)
    if aircraft and aircraft != "Unknown":
        if aircraft not in profile["aircraft_hours"]:
            profile["aircraft_hours"][aircraft] = 0
        profile["aircraft_hours"][aircraft] += flight_minutes

    # Update nicknames if new ones found
    if "nicknames" in mission_data:
        for nickname in mission_data["nicknames"]:
            if nickname not in profile["nicknames"]:
                profile["nicknames"].append(nickname)

    # Add mission to history (convert flight_hours to flight_minutes)
    mission_copy = mission_data.copy()
    if "flight_hours" in mission_copy:
        # Convert HH:MM string to minutes
        flight_hours_str = mission_copy["flight_hours"]
        if isinstance(flight_hours_str, str) and ":" in flight_hours_str:
            hours, minutes = map(int, flight_hours_str.split(":"))
            mission_copy["flight_minutes"] = hours * 60 + minutes
        else:
            mission_copy["flight_minutes"] = int(flight_hours_str) if flight_hours_str else 0
        del mission_copy["flight_hours"]
    
    profile["missions"].append(mission_copy)
