import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from nickname_matcher import resolve_fuzzy_nickname
import math
import re
import json

# Load player profiles for AI filtering
def load_player_profiles():
    """Load the player profiles from config/profiles.json"""
    try:
        with open('config/profiles.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('players', [])
    except (FileNotFoundError, json.JSONDecodeError):
        print("Warning: profiles.json not found or invalid, using empty player list")
        return []

# Cache the player profiles
_PLAYER_PROFILES = None

def get_player_profiles():
    """Get cached player profiles"""
    global _PLAYER_PROFILES
    if _PLAYER_PROFILES is None:
        _PLAYER_PROFILES = load_player_profiles()
    return _PLAYER_PROFILES

def is_known_player(pilot_name: str) -> bool:
    """Check if a pilot name matches any known player in profiles.json"""
    if not pilot_name:
        return False
    
    pilot_lower = pilot_name.lower()
    profiles = get_player_profiles()
    
    for profile in profiles:
        # Check callsign
        if profile.get('callsign', '').lower() == pilot_lower:
            return True
        
        # Check aliases
        aliases = profile.get('aliases', [])
        for alias in aliases:
            if alias.lower() == pilot_lower:
                return True
    
    return False

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
        
        # Initialize pilot mission data with enhanced tracking
        pilot_missions = defaultdict(lambda: {
            "date": mission_date,
            "mission": mission_name,
            "flight_minutes": int(mission_duration / 60),  # Convert seconds to minutes
            "aa_kills": 0, 
            "ag_kills": 0, 
            "frat_kills": 0, 
            "rtb": 0,
            "res": 0,  # Rescued
            "mia": 0,  # Missing in action 
            "kia": 0,  # Killed in action
            "ctd": 0,  # Crash to desktop
            "platform": detect_platform(root),  # DCS vs BMS vs IL2 detection
            "aircraft": "Unknown",
            "ejections": 0,
            "deaths": 0,
            "sorties": 1,  # At least one sortie if they appear in the file
            "total_kills": 0,
            "kd_ratio": "N/A",
            "nicknames": [],  # Track all known nicknames
            "profile_image": "",  # Profile image path
            "flight_times": [],  # Track individual flight sessions
            "stationary_periods": []  # Track stationary periods to filter out
        })
        
        # Track pilot positions and times for stationary detection
        pilot_positions = defaultdict(list)
        
        # Process all events
        for event in events.findall("Event"):
            process_event(event, pilot_missions, ground_types, pilot_positions)
        
        # Calculate actual flight hours (excluding stationary time)
        calculate_actual_flight_hours(pilot_missions, pilot_positions)
        
        # Post-process to clean up data
        return finalize_pilot_data(pilot_missions)
        
    except Exception as e:
        print(f"Error parsing Tacview XML: {e}")
        return {}

def calculate_actual_flight_hours(pilot_missions: dict, pilot_positions: dict):
    """Calculate actual flight hours excluding stationary time (>15 minutes)"""
    for pilot_name, positions in pilot_positions.items():
        if pilot_name not in pilot_missions:
            continue
            
        if not positions:
            continue
            
        # Sort positions by time
        positions.sort(key=lambda x: x['time'])
        
        total_flight_time = 0
        last_position = None
        stationary_start = None
        
        for pos in positions:
            if last_position is not None:
                time_diff = pos['time'] - last_position['time']
                distance = calculate_distance(last_position, pos)
                
                # If stationary for more than 15 minutes (900 seconds), don't count this time
                if distance < 100:  # Less than 100 meters movement
                    if stationary_start is None:
                        stationary_start = last_position['time']
                    elif pos['time'] - stationary_start > 900:  # 15 minutes
                        # Don't count this time as flight time
                        continue
                else:
                    # Moving, reset stationary timer
                    stationary_start = None
                
                total_flight_time += time_diff
            
            last_position = pos
        
        # Update flight hours
        pilot_missions[pilot_name]["flight_minutes"] = int(total_flight_time / 60)

def calculate_distance(pos1: dict, pos2: dict) -> float:
    """Calculate distance between two positions"""
    lat1, lon1 = pos1['lat'], pos1['lon']
    lat2, lon2 = pos2['lat'], pos2['lon']
    
    # Simple distance calculation (approximate)
    return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111000  # Convert to meters

def process_event(event, pilot_missions: dict, ground_types: set, pilot_positions: dict):
    """Process a single event from the XML"""
    action = event.findtext("Action")
    primary = event.find("PrimaryObject")
    secondary = event.find("SecondaryObject")
    
    if primary is None:
        return
    
    pilot = primary.findtext("Pilot", default="").strip()
    aircraft = primary.findtext("Name", default="Unknown")
    group = primary.findtext("Group", default="")
    
    # Skip if no pilot identified or not a player client
    if not pilot or pilot.lower() == "unknown":
        return
    
    # Only process player clients, not AI
    if not is_player_client(pilot, aircraft, group):
        return
    
    # Resolve nickname using fuzzy matching
    nickname = resolve_fuzzy_nickname(pilot)
    
    # Track all nicknames for this pilot
    if pilot not in pilot_missions[nickname]["nicknames"]:
        pilot_missions[nickname]["nicknames"].append(pilot)
    
    # Update aircraft info (last seen aircraft for this pilot)
    pilot_missions[nickname]["aircraft"] = aircraft
    
    # Track position for flight time calculation
    location = event.find("Location")
    if location is not None:
        lat = location.findtext("Latitude")
        lon = location.findtext("Longitude")
        time_elem = event.find("Time")
        time_val = float(time_elem.text) if time_elem is not None and time_elem.text else 0
        
        if lat and lon and time_val:
            pilot_positions[nickname].append({
                'lat': float(lat),
                'lon': float(lon),
                'time': time_val
            })
    
    # Process different event types
    if action == "HasBeenDestroyed":
        if secondary is not None:
            # Someone destroyed something
            attacker = secondary.findtext("Pilot", "").strip()
            if attacker and attacker.lower() != "unknown" and is_player_client(attacker, aircraft, group):
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
    """Detect if this is from DCS, BMS, IL2, or other sim"""
    # Look for platform indicators in the XML
    generator = root.get("generator", "").lower()
    source = root.findtext(".//Source", "").lower()
    
    # Check generator field
    if "dcs" in generator:
        return "DCS"
    elif "bms" in generator or "falcon" in generator:
        return "BMS"
    elif "il2" in generator or "il-2" in generator or "sturmovik" in generator:
        return "IL2"
    elif "tacview" in generator:
        return "Tacview"  # Generic
    
    # Check source field
    if "dcs" in source:
        return "DCS"
    elif "bms" in source or "falcon" in source:
        return "BMS"
    elif "il2" in source or "il-2" in source or "sturmovik" in source:
        return "IL2"
    
    # Check for DCS-specific elements
    if root.find(".//Mission") is not None:
        mission_elem = root.find(".//Mission")
        if mission_elem is not None:
            title = mission_elem.findtext("Title", "").lower()
            if any(keyword in title for keyword in ["dcs", "digital combat simulator"]):
                return "DCS"
    
    # Default to DCS if we can't determine
    return "DCS"

def format_duration_from_seconds(seconds: float) -> str:
    """Convert seconds to H:MM format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}"

def finalize_pilot_data(pilot_missions: dict) -> dict:
    """Clean up and validate pilot data before returning"""
    finalized = {}
    
    for nickname, data in pilot_missions.items():
        # Skip pilots with no activity
        total_activity = (data["aa_kills"] + data["ag_kills"] + 
                         data["frat_kills"] + data["rtb"] + data["kia"])
        
        if total_activity > 0 or data["flight_minutes"] > 0:
            # Calculate total kills
            data["total_kills"] = data["aa_kills"] + data["ag_kills"]
            
            # Calculate K/D ratio
            if data["deaths"] == 0:
                data["kd_ratio"] = "∞" if data["total_kills"] > 0 else "N/A"
            else:
                data["kd_ratio"] = f"{data['total_kills'] / data['deaths']:.2f}"
            
            # Ensure flight_minutes is an integer
            data["flight_minutes"] = int(data.get("flight_minutes", 0))
            
            finalized[nickname] = data
    
    return finalized

def is_player_client(pilot_name: str, aircraft_name: str, group: str = "") -> bool:
    """Determine if this is a player client (not AI)"""
    if not pilot_name or pilot_name.lower() == "unknown":
        return False
    
    # Check if this is a known player from profiles.json first
    if is_known_player(pilot_name):
        return True
    
    # Check group first - AI groups often have specific patterns
    if group:
        group_lower = group.lower()
        # AI group patterns
        ai_group_patterns = [
            r'.*iq.*',  # Groups with "IQ" (Intelligence Quotient) are often AI
            r'.*ai.*',  # Groups with "AI" 
            r'.*bot.*', # Groups with "bot"
            r'.*computer.*', # Groups with "computer"
            r'.*enemy.*', # Groups with "enemy"
            r'.*hostile.*', # Groups with "hostile"
        ]
        
        for pattern in ai_group_patterns:
            if re.search(pattern, group_lower):
                return False
    
    # Skip obvious AI units - use word boundaries for more precise matching
    ai_indicators = [
        "ai", "computer", "cpu", "bot", "enemy", "hostile",
        "springfield", "sting", "wizard", "arco", "shell", "colt",
        "hawk", "eagle", "falcon", "viper", "hornet", "tomcat",
        "flanker", "fulcrum", "frogfoot", "hokum", "hind", "shark",
        "apache", "blackhawk", "chinook", "osprey", "hercules",
        "ai_", "player_", "client_", "server_", "host_", "spectator",
        "observer", "referee", "admin", "moderator", "system"
    ]
    
    # AI squadron/group patterns - these indicate AI units
    ai_squadron_patterns = [
        r'^[a-z]+\d{1,2}$',  # word followed by 1-2 digits (e.g., pontiac61, dynamolabyrinth1)
        r'^[a-z]+\d{3}$',  # word followed by 3 digits (but exclude common player patterns)
        r'^\d{2}[a-z]+$',  # 2 digits followed by word
        r'^\d{3}[a-z]+$',  # 3 digits followed by word
        r'^[a-z]+\d{1,2}[a-z]+$',  # word + 1-2 digits + word
        r'^[a-z]+pilot\d+$',  # word + pilot + number (e.g., gudautastrike121pilot1)
        r'^[a-z]+cas\d+pilot\d+$',  # word + cas + number + pilot + number
        r'^[a-z]+barcap\d+pilot\d+$',  # word + barcap + number + pilot + number
        r'^[a-z]+sead\d+pilot\d+$',  # word + sead + number + pilot + number
        r'^[a-z]+strike\d+pilot\d+$',  # word + strike + number + pilot + number
    ]
    
    # Military unit patterns that indicate AI
    military_patterns = [
        r'^\d{4}\s*\|\s*(DDG|CG|FFG|LHA|LHD|CVN|SSN|SSBN|SSGN)',  # Ship identifiers
        r'^\d{4}\s*\|\s*(Tank|APC|IFV|MBT|SPG|MLRS|SAM|AAA)',     # Ground vehicle identifiers
        r'^\d{4}\s*\|\s*(F-16|F-18|F-15|F-22|F-35|A-10|B-1|B-2|B-52)',  # Aircraft with numbers
        r'^\d{4}\s*\|\s*(MiG|Su|Ka|Mi|Il|Tu|Yak)',                # Russian aircraft
        r'^\d{4}\s*\|\s*(Eurofighter|Rafale|Gripen|Typhoon)',     # European aircraft
        r'^\d{4}\s*\|\s*(Arleigh Burke|Ticonderoga|Nimitz|Ford)', # Ship classes
        r'^\d{4}\s*\|\s*(Abrams|Bradley|Stryker|Paladin)',        # Ground vehicle classes
        r'^\d+[a-z]+(bataillon|brigade|taskforce|airdefense|infantry)',  # Military units
        r'^\d+[a-z]+(division|regiment|squadron|wing|group)',     # Military units
    ]
    
    pilot_lower = pilot_name.lower()
    aircraft_lower = aircraft_name.lower() if aircraft_name else ""
    
    # Check for AI squadron patterns first, but exclude known player patterns
    for pattern in ai_squadron_patterns:
        if re.match(pattern, pilot_lower):
            # If it matches a known player, allow it
            if is_known_player(pilot_name):
                continue
            return False
    
    # Check for military unit patterns
    for pattern in military_patterns:
        if re.search(pattern, pilot_name, re.IGNORECASE):
            return False
    
    # Check pilot name against AI indicators with word boundaries
    for indicator in ai_indicators:
        # Use exact word matching to avoid false positives
        if (indicator == pilot_lower or 
            pilot_lower.startswith(indicator + "_") or 
            pilot_lower.startswith(indicator + " ") or
            pilot_lower.endswith("_" + indicator) or
            pilot_lower.endswith(" " + indicator) or
            " " + indicator + " " in " " + pilot_lower + " "):
            return False
    
    # Check aircraft name for AI indicators
    # REMOVED: This was causing false positives - real players can fly any aircraft type
    # for indicator in ai_indicators:
    #     if indicator in aircraft_lower:
    #         return False
    
    # Look for player patterns (callsign | name) - but be more careful
    if "|" in pilot_name:
        # Check if it's a military unit pattern first
        parts = pilot_name.split("|")
        if len(parts) == 2:
            left_part = parts[0].strip()
            right_part = parts[1].strip()
            
            # If left part is just numbers, likely AI
            if re.match(r'^\d+$', left_part):
                return False
            
            # If right part contains military identifiers, likely AI
            military_terms = ['DDG', 'CG', 'FFG', 'LHA', 'LHD', 'CVN', 'SSN', 'SSBN', 'SSGN', 
                            'Tank', 'APC', 'IFV', 'MBT', 'SPG', 'MLRS', 'SAM', 'AAA',
                            'Arleigh Burke', 'Ticonderoga', 'Nimitz', 'Ford',
                            'Abrams', 'Bradley', 'Stryker', 'Paladin']
            for term in military_terms:
                if term.lower() in right_part.lower():
                    return False
            
            # If it passes these checks, likely a real player
            return True
    
    # Look for player patterns (callsign - name)
    if " - " in pilot_name:
        return True
    
    # Look for player patterns (callsign name)
    if " " in pilot_name and not any(ai_indicator in pilot_lower for ai_indicator in ai_indicators):
        # Check if it looks like a real player name
        parts = pilot_name.split()
        if len(parts) >= 2:
            # If it has multiple parts and doesn't match AI patterns, likely a player
            return True
    
    # Additional checks for real player patterns
    # Look for callsigns that are likely real players (not AI)
    real_player_patterns = [
        # Common player name patterns
        r'^[A-Za-z0-9_]{2,20}$',  # Alphanumeric callsigns
        r'^[A-Za-z]+[0-9]+$',     # Letters followed by numbers
        r'^\d+[A-Za-z]+$',        # Numbers followed by letters
        r'^[A-Za-z]+_[A-Za-z0-9]+$',  # Underscore separated
        r'^[A-Za-z]+-[A-Za-z0-9]+$',  # Dash separated
    ]
    
    for pattern in real_player_patterns:
        if re.match(pattern, pilot_name):
            # Additional check: make sure it's not too generic
            if len(pilot_name) >= 3 and not pilot_name.isdigit():
                return True
    
    # If it's a simple word and not in AI indicators, likely a player
    if len(pilot_name) >= 3 and pilot_name.isalpha() and pilot_name.lower() not in ai_indicators:
        return True
    
    # If we can't determine, be conservative and assume it's AI
    return False
