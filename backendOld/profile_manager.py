import json
from pathlib import Path

def load_profile(nickname, profile_dir):
    path = Path(profile_dir) / f"{nickname}.json"
    if not path.exists():
        return {
            "callsign": nickname,
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
    for key in ["aa_kills", "ag_kills", "frat_kills", "rtb", "res", "mia", "kia", "ctd"]:
        ms[key] += mission_data.get(key, 0)
        ms[f"{key.split('_')[0]}_avg"] = round(ms[key] / ms["logs_flown"], 2)

    profile["platform_hours"]["DCS"] = add_minutes(profile["platform_hours"]["DCS"], flight_minutes)
    profile["platform_hours"]["Total"] = add_minutes(profile["platform_hours"]["Total"], flight_minutes)

    if aircraft:
        prev = profile["aircraft_hours"].get(aircraft, "0:00")
        profile["aircraft_hours"][aircraft] = add_minutes(prev, flight_minutes)

    profile["missions"].append(mission_data)
