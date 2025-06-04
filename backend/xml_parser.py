import xml.etree.ElementTree as ET
from collections import defaultdict
from backend.nickname_matcher import resolve_fuzzy_nickname

def parse_tacview_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()
    events = root.find("Events")

    ground_types = {"Infantry", "SAM/AAA", "Vehicle", "Tank", "Artillery"}
    pilot_missions = defaultdict(lambda: {
        "date": "2025-05-31",
        "mission": xml_path.stem,
        "flight_hours": "0:45",
        "aa_kills": 0, "ag_kills": 0, "frat_kills": 0, "rtb": 0,
        "res": 0, "mia": 0, "kia": 0, "ctd": 0,
        "platform": "DCS",
        "aircraft": "Unknown"
    })

    for event in events.findall("Event"):
        action = event.findtext("Action")
        primary = event.find("PrimaryObject")
        secondary = event.find("SecondaryObject")

        if primary is None:
            continue

        pilot = primary.findtext("Pilot", default="Unknown")
        aircraft = primary.findtext("Name", default="Unknown")

        if not pilot or pilot.strip().lower() == "unknown":
            continue

        nickname = resolve_fuzzy_nickname(pilot)
        pilot_missions[nickname]["aircraft"] = aircraft

        if action == "HasBeenDestroyed" and secondary is not None:
            attacker = secondary.findtext("Pilot")
            attacker_nick = resolve_fuzzy_nickname(attacker) if attacker else None
            destroyed_type = primary.findtext("Type", default="")
            if attacker_nick:
                if destroyed_type in ground_types:
                    pilot_missions[attacker_nick]["ag_kills"] += 1
                else:
                    pilot_missions[attacker_nick]["aa_kills"] += 1

        elif action == "HasLanded":
            pilot_missions[nickname]["rtb"] += 1

        elif action == "HasBeenDestroyed":
            victim_nick = resolve_fuzzy_nickname(pilot)
            pilot_missions[victim_nick]["kia"] += 1

    return pilot_missions
