import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from nickname_matcher import resolve_fuzzy_nickname

def parse_xml(filepath: str) -> dict:
    """Main entry point for XML parsing - returns success/error status"""
    try:
        print(f"Parsing XML file at: {filepath}")
        
        # Basic file validation
        if not Path(filepath).exists():
            return {"success": False, "error": "File not found"}
        
        if not filepath.lower().endswith('.xml'):
            return {"success": False, "error": "Not an XML file"}
        
        # Parse the Tacview XML
        pilot_data = parse_tacview_xml(filepath)
        
        if not pilot_data:
            return {"success": False, "error": "No pilot data found in XML"}
        
        return {
            "success": True, 
            "pilots_count": len(pilot_data),
            "pilot_data": pilot_data
        }
        
    except ET.ParseError as e:
        return {"success": False, "error": f"XML parsing error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Unexpected error: {str(e)}"}

def parse_tacview_xml(xml_path: str) -> dict:
    """Parse Tacview XML and extract pilot mission data"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Extract mission metadata if available
        mission_name = extract_mission_name(root, xml_path)
        mission_date = extract_mission_date(root)
        mission_duration = extract_mission_duration(root)
        
        events = root.find("Events")
        if events is None:
            print("Warning: No Events section found in XML")
            return {}
        
        # Define ground target types (could be moved to config)
        ground_types = {
            "Infantry", "SAM/AAA", "Vehicle", "Tank", "Artillery", 
            "Ship", "Boat", "Structure", "Ground"  # Added more common types
        }
        
        # Initialize pilot mission data
        pilot_missions = defaultdict(lambda: {
            "date": mission_date,
            "mission": mission_name,
            "flight_hours": format_duration_from_seconds(mission_duration),
            "aa_kills": 0, 
            "ag_kills": 0, 
            "frat_kills": 0, 
            "rtb": 0,
            "res": 0,  # Rescued
            "mia": 0,  # Missing in action 
            "kia": 0,  # Killed in action
            "ctd": 0,  # Crash to desktop (maybe not relevant for Tacview)
            "platform": detect_platform(root),  # DCS vs BMS detection
            "aircraft": "Unknown",
            "ejections": 0,
            "deaths": 0,
            "sorties": 1  # At least one sortie if they appear in the file
        })
        
        # Process all events
        for event in events.findall("Event"):
            process_event(event, pilot_missions, ground_types)
        
        # Post-process to clean up data
        return finalize_pilot_data(pilot_missions)
        
    except Exception as e:
        print(f"Error parsing Tacview XML: {e}")
        return {}

def process_event(event, pilot_missions: dict, ground_types: set):
    """Process a single event from the XML"""
    action = event.findtext("Action")
    primary = event.find("PrimaryObject")
    secondary = event.find("SecondaryObject")
    
    if primary is None:
        return
    
    pilot = primary.findtext("Pilot", default="").strip()
    aircraft = primary.findtext("Name", default="Unknown")
    
    # Skip if no pilot identified
    if not pilot or pilot.lower() == "unknown":
        return
    
    # Resolve nickname using fuzzy matching
    nickname = resolve_fuzzy_nickname(pilot)
    
    # Update aircraft info (last seen aircraft for this pilot)
    pilot_missions[nickname]["aircraft"] = aircraft
    
    # Process different event types
    if action == "HasBeenDestroyed":
        if secondary is not None:
            # Someone destroyed something
            attacker = secondary.findtext("Pilot", "").strip()
            if attacker and attacker.lower() != "unknown":
                attacker_nick = resolve_fuzzy_nickname(attacker)
                destroyed_type = primary.findtext("Type", "")
                destroyed_coalition = primary.findtext("Coalition", "")
                attacker_coalition = secondary.findtext("Coalition", "")
                
                # Check for friendly fire
                if destroyed_coalition == attacker_coalition and destroyed_coalition:
                    pilot_missions[attacker_nick]["frat_kills"] += 1
                elif destroyed_type in ground_types:
                    pilot_missions[attacker_nick]["ag_kills"] += 1
                else:
                    pilot_missions[attacker_nick]["aa_kills"] += 1
        else:
            # Primary object was destroyed (pilot death)
            victim_nick = resolve_fuzzy_nickname(pilot)
            pilot_missions[victim_nick]["kia"] += 1
            pilot_missions[victim_nick]["deaths"] += 1
            
    elif action == "HasLanded":
        pilot_missions[nickname]["rtb"] += 1
        
    elif action == "HasEjected":
        pilot_missions[nickname]["ejections"] += 1
        
    elif action == "HasTakenOff":
        # Could track multiple sorties per pilot
        pass  # Already counting sorties in initialization

def extract_mission_name(root, xml_path: str) -> str:
    """Extract mission name from XML or filename"""
    # Try to find mission name in XML metadata
    mission_elem = root.find(".//Mission")
    if mission_elem is not None:
        name = mission_elem.get("name") or mission_elem.text
        if name:
            return name.strip()
    
    # Fall back to filename
    return Path(xml_path).stem

def extract_mission_date(root) -> str:
    """Extract mission date from XML"""
    # Try to find date in various places
    date_elem = root.find(".//Date")
    if date_elem is not None and date_elem.text:
        return date_elem.text.strip()
    
    # Try timestamp
    timestamp_elem = root.find(".//Timestamp")
    if timestamp_elem is not None and timestamp_elem.text:
        try:
            # Convert timestamp to date
            ts = float(timestamp_elem.text)
            return datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        except:
            pass
    
    # Default to today
    return datetime.now().strftime("%Y-%m-%d")

def extract_mission_duration(root) -> int:
    """Extract mission duration in seconds"""
    duration_elem = root.find(".//Duration")
    if duration_elem is not None and duration_elem.text:
        try:
            return int(float(duration_elem.text))
        except:
            pass
    
    # Try to calculate from events
    events = root.find("Events")
    if events is not None:
        timestamps = []
        for event in events.findall("Event"):
            time_elem = event.find("Time")
            if time_elem is not None and time_elem.text:
                try:
                    timestamps.append(float(time_elem.text))
                except:
                    continue
        
        if len(timestamps) >= 2:
            return int(max(timestamps) - min(timestamps))
    
    # Default duration (45 minutes)
    return 2700

def detect_platform(root) -> str:
    """Detect if this is from DCS, BMS, or other sim"""
    # Look for platform indicators in the XML
    generator = root.get("generator", "").lower()
    
    if "dcs" in generator:
        return "DCS"
    elif "bms" in generator or "falcon" in generator:
        return "BMS"
    elif "tacview" in generator:
        return "Tacview"  # Generic
    
    return "Unknown"

def format_duration_from_seconds(seconds: int) -> str:
    """Convert seconds to H:MM format"""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    return f"{hours}:{minutes:02d}"

def finalize_pilot_data(pilot_missions: dict) -> dict:
    """Clean up and validate pilot data before returning"""
    finalized = {}
    
    for nickname, data in pilot_missions.items():
        # Skip pilots with no activity
        total_activity = (data["aa_kills"] + data["ag_kills"] + 
                         data["frat_kills"] + data["rtb"] + data["kia"])
        
        if total_activity > 0:
            # Calculate total kills
            data["total_kills"] = data["aa_kills"] + data["ag_kills"]
            
            # Calculate K/D ratio
            if data["deaths"] == 0:
                data["kd_ratio"] = "∞" if data["total_kills"] > 0 else "N/A"
            else:
                data["kd_ratio"] = f"{data['total_kills'] / data['deaths']:.2f}"
            
            finalized[nickname] = data
    
    return finalized
