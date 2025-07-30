import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from datetime import datetime
from nickname_matcher import resolve_fuzzy_nickname
import math
import re
import json
import os
from validation import (
    validate_pilot_name, validate_mission_name, validate_aircraft_name,
    validate_platform, validate_numeric_value, sanitize_string
)
from error_handling import (
    APIError, ErrorCodes, log_operation_start, log_operation_success,
    log_operation_failure, safe_json_save, safe_json_read
)
import logging

logger = logging.getLogger(__name__)

# Load player profiles for AI filtering
def load_player_profiles():
    """Load the player profiles from config/profiles.json"""
    try:
        with open('config/profiles.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data.get('players', [])
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        logger.warning(f"profiles.json not found or invalid, using empty player list: {e}")
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
    operation = "xml_parse"
    
    try:
        log_operation_start(operation, {"file_path": filepath})
        logger.info(f"Parsing XML file at: {filepath}")
        
        # Basic file validation
        if not Path(filepath).exists():
            raise APIError(
                error_code=ErrorCodes.FILE_NOT_FOUND,
                message="File not found",
                status_code=404
            )
        
        if not filepath.lower().endswith('.xml'):
            raise APIError(
                error_code=ErrorCodes.FILE_INVALID_TYPE,
                message="Not an XML file",
                status_code=400
            )
        
        # Parse the Tacview XML
        pilot_data = parse_tacview_xml(filepath)
        
        # Check if this was a duplicate mission
        if pilot_data and pilot_data.get("duplicate"):
            log_operation_success(operation, {
                "duplicate": True,
                "mission_name": pilot_data['mission_name'],
                "mission_date": pilot_data['mission_date']
            })
            return {
                "success": True,
                "duplicate": True,
                "message": f"Mission already processed: {pilot_data['mission_name']} on {pilot_data['mission_date']}",
                "pilots_count": 0,
                "pilot_data": {}
            }
        
        if not pilot_data:
            raise APIError(
                error_code=ErrorCodes.DATA_PROCESSING_ERROR,
                message="No pilot data found in XML",
                status_code=400
            )
        
        log_operation_success(operation, {
            "pilots_count": len(pilot_data),
            "file_path": filepath
        })
        
        return {
            "success": True, 
            "pilots_count": len(pilot_data),
            "pilot_data": pilot_data
        }
        
    except APIError:
        # Re-raise API errors
        raise
    except ET.ParseError as e:
        log_operation_failure(operation, e, {"file_path": filepath})
        raise APIError(
            error_code=ErrorCodes.XML_PARSE_ERROR,
            message=f"XML parsing error: {str(e)}",
            status_code=400
        )
    except Exception as e:
        log_operation_failure(operation, e, {"file_path": filepath})
        raise APIError(
            error_code=ErrorCodes.DATA_PROCESSING_ERROR,
            message=f"Unexpected error: {str(e)}",
            status_code=500
        )

def parse_tacview_xml(xml_path: str) -> dict:
    """Parse Tacview XML and extract pilot mission data"""
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Extract mission metadata if available
        mission_name = extract_mission_name(root, xml_path)
        mission_date = extract_mission_date(root)
        mission_duration = extract_mission_duration_safe(root)
        
        # Check for duplicate mission processing
        if is_mission_already_processed(mission_name, mission_date):
            logger.warning(f"Mission already processed: {mission_name} on {mission_date}")
            return {"duplicate": True, "mission_name": mission_name, "mission_date": mission_date}
        
        events = root.find("Events")
        if events is None:
            logger.warning("Warning: No Events section found in XML")
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
            "flight_minutes": int(mission_duration / 60) if mission_duration is not None else 45,  # Convert seconds to minutes, default to 45 if None
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
        
        # Mark mission as processed
        mark_mission_as_processed(mission_name, mission_date)
        
        # Post-process to clean up data
        return finalize_pilot_data(pilot_missions)
        
    except Exception as e:
        logger.error(f"Error parsing Tacview XML: {e}")
        return {}

def calculate_actual_flight_hours(pilot_missions: dict, pilot_positions: dict):
    """Calculate actual flight hours excluding stationary time (>15 minutes)"""
    try:
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
            pilot_missions[pilot_name]["flight_minutes"] = int(total_flight_time / 60) if total_flight_time is not None else 0
    except Exception as e:
        logger.warning(f"Warning: Could not calculate actual flight hours, using default: {e}")
        # Ensure all pilots have a default flight_minutes value
        for pilot_name in pilot_missions:
            if "flight_minutes" not in pilot_missions[pilot_name]:
                pilot_missions[pilot_name]["flight_minutes"] = 0

def calculate_distance(pos1: dict, pos2: dict) -> float:
    """Calculate distance between two positions"""
    try:
        lat1, lon1 = pos1['lat'], pos1['lon']
        lat2, lon2 = pos2['lat'], pos2['lon']
    
        # Simple distance calculation (approximate)
        return math.sqrt((lat2 - lat1)**2 + (lon2 - lon1)**2) * 111000  # Convert to meters
    except Exception as e:
        logger.warning(f"Warning: Could not calculate distance, returning 0: {e}")
        return 0.0

def process_event(event, pilot_missions: dict, ground_types: set, pilot_positions: dict):
    """Process a single event from the XML"""
    try:
        action = event.findtext("Action")
        primary = event.find("PrimaryObject")
        secondary = event.find("SecondaryObject")
    
        if primary is None:
            return
    
        pilot = primary.findtext("Pilot", default="").strip()
        aircraft = primary.findtext("Name", default="Unknown")
        group = primary.findtext("Group", default="")
    
        # Validate and sanitize pilot name
        if not pilot or pilot.lower() == "unknown":
            return
    
        # Validate pilot name
        is_valid, error = validate_pilot_name(pilot)
        if not is_valid:
            logger.warning(f"Invalid pilot name '{pilot}': {error}")
            return
    
        # Sanitize pilot name
        pilot = sanitize_string(pilot, 100)
    
        # Validate aircraft name
        is_valid, error = validate_aircraft_name(aircraft)
        if not is_valid:
            logger.warning(f"Invalid aircraft name '{aircraft}': {error}")
            aircraft = "Unknown"
    
        # Sanitize aircraft name
        aircraft = sanitize_string(aircraft, 100)
    
        # Debug: Log all pilots being checked
        logger.info(f"Checking pilot: '{pilot}' (aircraft: {aircraft}, group: {group})")
    
        # Only process player clients, not AI
        if not is_player_client(pilot, aircraft, group):
            logger.info(f"  -> FILTERED OUT (AI)")
            return
    
        logger.info(f"  -> ACCEPTED (Player)")
    
        # Resolve nickname using fuzzy matching
        nickname = resolve_fuzzy_nickname(pilot)
    
        # Validate nickname
        is_valid, error = validate_pilot_name(nickname)
        if not is_valid:
            logger.warning(f"Invalid nickname '{nickname}': {error}")
            return
    
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
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        # Continue processing other events even if one fails
        pass
    

def extract_mission_name(root, xml_path: str) -> str:
    """Extract mission name from XML or filename"""
    try:
        # Try to find mission name in XML metadata
        mission_elem = root.find(".//Mission")
        if mission_elem is not None:
            name = mission_elem.get("name") or mission_elem.text
            if name:
                name = name.strip()
                # Validate mission name
                is_valid, error = validate_mission_name(name)
                if is_valid:
                    return sanitize_string(name, 200)
        
        # Fall back to filename
        filename = Path(xml_path).stem
        return sanitize_string(filename, 200)
    except Exception as e:
        logger.warning(f"Warning: Could not extract mission name, using default: {e}")
        return "Unknown Mission"

def extract_mission_date(root) -> str:
    """Extract mission date from XML"""
    try:
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
    except Exception as e:
        logger.warning(f"Warning: Could not extract mission date, using default: {e}")
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


def extract_mission_duration_safe(root) -> int:
    """Extract mission duration in seconds with safety checks"""
    try:
        duration = extract_mission_duration(root)
        return duration if duration is not None else 2700
    except Exception:
        return 2700  # Default to 45 minutes

def detect_platform(root) -> str:
    """Detect if this is from DCS, BMS, IL2, or other sim"""
    try:
        # Look for platform indicators in the XML
        generator = root.get("generator", "").lower() if root.get("generator") else ""
        source = root.findtext(".//Source", "").lower() if root.findtext(".//Source") else ""
    
        # Check generator field
        if "dcs" in generator:
            platform = "DCS"
        elif "bms" in generator or "falcon" in generator:
            platform = "BMS"
        elif "il2" in generator or "il-2" in generator or "sturmovik" in generator:
            platform = "IL2"
        elif "tacview" in generator:
            platform = "Tacview"  # Generic
        else:
            # Check source field
            if "dcs" in source:
                platform = "DCS"
            elif "bms" in source or "falcon" in source:
                platform = "BMS"
            elif "il2" in source or "il-2" in source or "sturmovik" in source:
                platform = "IL2"
            else:
                # Check for DCS-specific elements
                if root.find(".//Mission") is not None:
                    mission_elem = root.find(".//Mission")
                    if mission_elem is not None:
                        title = mission_elem.findtext("Title", "").lower() if mission_elem.findtext("Title") else ""
                        if any(keyword in title for keyword in ["dcs", "digital combat simulator"]):
                            platform = "DCS"
                        else:
                            platform = "DCS"  # Default
                    else:
                        platform = "DCS"  # Default
                else:
                    platform = "DCS"  # Default
    
        # Validate platform
        is_valid, error = validate_platform(platform)
        if not is_valid:
            logger.warning(f"Invalid platform '{platform}': {error}, defaulting to DCS")
            platform = "DCS"
    
        return platform
    except Exception as e:
        logger.warning(f"Warning: Could not detect platform, defaulting to DCS: {e}")
        return "DCS"

def format_duration_from_seconds(seconds: float) -> str:
    """Convert seconds to H:MM format"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    return f"{hours}:{minutes:02d}"

def finalize_pilot_data(pilot_missions: dict) -> dict:
    """Clean up and validate pilot data before returning"""
    try:
        finalized = {}
    
        for nickname, data in pilot_missions.items():
            # Validate pilot data structure
            try:
                # Validate numeric fields
                numeric_fields = ['aa_kills', 'ag_kills', 'frat_kills', 'rtb', 'ejections', 'deaths', 'flight_minutes']
                for field in numeric_fields:
                    if field in data:
                        # Ensure the field value is not None
                        field_value = data[field] if data[field] is not None else 0
                        is_valid, error = validate_numeric_value(field_value, field, min_val=0, max_val=10000)
                        if not is_valid:
                            logger.warning(f"Invalid {field} for {nickname}: {error}")
                            data[field] = 0
            
                # Validate string fields
                if 'mission' in data:
                    mission_name = data['mission'] if data['mission'] is not None else "Unknown Mission"
                    is_valid, error = validate_mission_name(mission_name)
                    if not is_valid:
                        logger.warning(f"Invalid mission name for {nickname}: {error}")
                        data['mission'] = "Unknown Mission"
            
                if 'aircraft' in data:
                    aircraft_name = data['aircraft'] if data['aircraft'] is not None else "Unknown"
                    is_valid, error = validate_aircraft_name(aircraft_name)
                    if not is_valid:
                        logger.warning(f"Invalid aircraft for {nickname}: {error}")
                        data['aircraft'] = "Unknown"
            
                if 'platform' in data:
                    platform_name = data['platform'] if data['platform'] is not None else "DCS"
                    is_valid, error = validate_platform(platform_name)
                    if not is_valid:
                        logger.warning(f"Invalid platform for {nickname}: {error}")
                        data['platform'] = "DCS"
            
                # Sanitize string fields
                for field in ['mission', 'aircraft', 'platform']:
                    if field in data:
                        field_value = data[field] if data[field] is not None else ""
                        data[field] = sanitize_string(field_value, 200)
            
            except Exception as e:
                logger.error(f"Error validating pilot data for {nickname}: {e}")
                continue
        
            # Skip pilots with no activity
            total_activity = (data.get("aa_kills", 0) or 0) + (data.get("ag_kills", 0) or 0) + \
                             (data.get("frat_kills", 0) or 0) + (data.get("rtb", 0) or 0) + (data.get("kia", 0) or 0)
        
            if total_activity > 0 or (data.get("flight_minutes", 0) or 0) > 0:
                # Calculate total kills
                data["total_kills"] = (data.get("aa_kills", 0) or 0) + (data.get("ag_kills", 0) or 0)
            
                # Calculate K/D ratio
                deaths = data.get("deaths", 0) or 0
                total_kills = data.get("total_kills", 0) or 0
                if deaths == 0:
                    data["kd_ratio"] = "∞" if total_kills > 0 else "N/A"
                else:
                    data["kd_ratio"] = f"{total_kills / deaths:.2f}" if deaths > 0 else "N/A"
            
                # Ensure flight_minutes is an integer
                data["flight_minutes"] = int(data.get("flight_minutes", 0) or 0)
            
                finalized[nickname] = data
    
        return finalized
    except Exception as e:
        logger.error(f"Error finalizing pilot data: {e}")
        return {}

def is_player_client(pilot_name: str, aircraft_name: str, group: str = "") -> bool:
    """Determine if this is a player client (not AI)"""
    if not pilot_name or pilot_name.lower() == "unknown":
        return False
    
    # Check if this is a known player from profiles.json first
    if is_known_player(pilot_name):
        return True
    
    # Only accept pilots flying specific player aircraft
    player_aircraft = [
        # Full fidelity modules
        "DCS: F4U-1D Corsair",
        "DCS: F-5E Remastered", 
        "DCS: Flaming Cliffs 2024",
        "DCS: F-4E Phantom II",
        "DCS: F-15E",
        "DCS: MB-339",
        "DCS: Mirage F1",
        "DCS: Mosquito FB VI",
        "DCS: A-10C II Tank Killer",
        "DCS: P-47D Thunderbolt",
        "DCS: JF-17 Thunder",
        "DCS: F-16C Viper",
        "DCS: Fw 190 A-8",
        "DCS: I-16",
        "DCS: MiG-19P Farmer",
        "DCS: Christen Eagle II",
        "DCS: F-14 Tomcat",
        "DCS: Yak-52",
        "DCS: F/A-18C",
        "DCS: AV-8B Night Attack V/STOL",
        "DCS: AJS-37 Viggen",
        "DCS: Spitfire LF Mk. IX",
        "DCS: F-5E",
        "DCS: M-2000C",
        "DCS: L-39 Albatros",
        "DCS: C-101 Aviojet",
        "DCS: Bf 109 K-4 Kurfürst",
        "DCS: MiG-21bis",
        "DCS: Fw 190 D-9 Dora",
        "DCS: P-51D Mustang",
        "DCS: A-10C Warthog",
        "A-4 Skyhawk",
        "A-4E",
        
        # Helicopters
        "DCS: UH-1H Huey",
        "DCS: Mi-8MT Hip",
        "DCS: Ka-50 Black Shark",
        "DCS: SA342 Gazelle",
        "DCS: Mi-24P Hind",
        "DCS: AH-64D Apache",
        "DCS: OH-58D Kiowa Warrior",
        "DCS: AH-64E Apache",
        "DCS: Mi-28N Havoc",
        "DCS: Ka-50-3 Black Shark",
        "DCS: CH-47F Chinook",
        "DCS: UH-60L Black Hawk",
        "DCS: Mi-17 Hip",
        "DCS: AH-1W Super Cobra",
        "DCS: AH-1Z Viper",
        "DCS: UH-1Y Venom",
        "DCS: Mi-26 Halo",
        "DCS: Ka-27 Helix",
        "DCS: Ka-29 Helix",
        "DCS: Mi-35M Hind",
        "DCS: Mi-28 Havoc",
        "DCS: AH-6J Little Bird",
        "DCS: OH-6A Cayuse",
        "DCS: UH-1N Twin Huey",
        "DCS: CH-53E Super Stallion",
        "DCS: CH-46 Sea Knight",
        "DCS: V-22 Osprey",
        "DCS: Mi-8",
        "DCS: Ka-50",
        "DCS: AH-64",
        "DCS: UH-1",
        "DCS: Mi-24",
        "DCS: SA342",
        "DCS: OH-58D",
        "DCS: CH-47",
        "DCS: UH-60",
        "DCS: Mi-17",
        "DCS: AH-1",
        "DCS: Mi-26",
        "DCS: Ka-27",
        "DCS: Mi-35",
        "DCS: AH-6",
        "DCS: OH-6",
        "DCS: CH-53",
        "DCS: CH-46",
        "DCS: V-22",
        
        # Flaming Cliffs aircraft (simplified names)
        "MiG-15bis",
        "F-5E Flaming Cliffs",
        "F-86F Flaming Cliffs", 
        "MiG-29 Flaming Cliffs",
        "Su-33 Flaming Cliffs",
        "Su-27 Flaming Cliffs",
        "F-15C Flaming Cliffs",
        "Su-25 Flaming Cliffs",
        "A-10A Flaming Cliffs",
        "F-86F Sabre",
        
        # Alternative names that might appear
        "F-4E Phantom",
        "F-15E Strike Eagle",
        "F-16C",
        "F/A-18C Hornet",
        "AV-8B",
        "A-10C",
        "P-51D",
        "MiG-21",
        "MiG-29",
        "Su-27",
        "Su-33",
        "F-15C",
        "Su-25",
        "A-10A",
        "F-5E",
        "F-86F",
        "MiG-15",
        "Fw 190",
        "Bf 109",
        "Spitfire",
        "Mosquito",
        "Corsair",
        "Thunderbolt",
        "Mustang",
        "Viggen",
        "Mirage F1",
        "M-2000C",
        "L-39",
        "C-101",
        "Yak-52",
        "Christen Eagle",
        "JF-17",
        "I-16",
        "MiG-19",
        "Fw 190 A-8",
        "Fw 190 D-9",
        "Bf 109 K-4",
        "MB-339",
        "AJS-37",
        "AV-8B Night Attack",
        "A-4 Skyhawk",
        "A-4E Skyhawk",
        
        # Additional helicopter names
        "Huey",
        "Hip",
        "Black Shark",
        "Gazelle",
        "Hind",
        "Apache",
        "Kiowa",
        "Havoc",
        "Chinook",
        "Black Hawk",
        "Super Cobra",
        "Viper",
        "Venom",
        "Halo",
        "Helix",
        "Little Bird",
        "Cayuse",
        "Twin Huey",
        "Super Stallion",
        "Sea Knight",
        "Osprey"
    ]
    
    # Check if the aircraft is in our whitelist
    aircraft_lower = aircraft_name.lower() if aircraft_name else ""
    aircraft_allowed = False
    
    for allowed_aircraft in player_aircraft:
        if allowed_aircraft.lower() in aircraft_lower or aircraft_lower in allowed_aircraft.lower():
            aircraft_allowed = True
            break
    
    # If aircraft not in whitelist, it's AI
    if not aircraft_allowed:
        return False
    
    # Now check if pilot name matches squadron callsigns
    # Load squadron callsigns from config
    squadron_callsigns = load_squadron_callsigns_safe()
    
    if not squadron_callsigns:
        # If no squadron callsigns configured, accept all player aircraft pilots
        return True
    
    # Check if pilot name contains any squadron callsign
    pilot_lower = pilot_name.lower()
    
    for callsign in squadron_callsigns:
        callsign_lower = callsign.lower()
        
        # Direct match
        if callsign_lower in pilot_lower or pilot_lower in callsign_lower:
            return True
        
        # Check for FLIGHTCALLSIGN | PERSONALCALLSIGN pattern
        if "|" in pilot_name:
            parts = pilot_name.split("|")
            if len(parts) == 2:
                left_part = parts[0].strip().lower()
                right_part = parts[1].strip().lower()
                
                # Check if callsign appears in either part
                if callsign_lower in left_part or callsign_lower in right_part:
                    return True
        
        # Check for FLIGHTCALLSIGN - PERSONALCALLSIGN pattern
        if " - " in pilot_name:
            parts = pilot_name.split(" - ")
            if len(parts) == 2:
                left_part = parts[0].strip().lower()
                right_part = parts[1].strip().lower()
                
                # Check if callsign appears in either part
                if callsign_lower in left_part or callsign_lower in right_part:
                    return True
    
    # If we have squadron callsigns but pilot doesn't match any, it's likely AI
    return False

def load_squadron_callsigns() -> list:
    """Load squadron callsigns from config file"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), 'config', 'squadron_callsigns.json')
        if os.path.exists(config_path):
            data = safe_json_read(config_path)
            callsigns = data.get('callsigns', [])
            return callsigns if isinstance(callsigns, list) else []
    except Exception as e:
        logger.warning(f"Warning: Could not load squadron callsigns: {e}")
    
    return []

def load_squadron_callsigns_safe() -> list:
    """Load squadron callsigns from config file with safety checks"""
    try:
        callsigns = load_squadron_callsigns()
        return callsigns if isinstance(callsigns, list) else []
    except Exception as e:
        logger.warning(f"Warning: Could not load squadron callsigns safely: {e}")
        return []

def save_squadron_callsigns(callsigns: list):
    """Save squadron callsigns to config file"""
    try:
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        config_path = os.path.join(config_dir, 'squadron_callsigns.json')
        safe_json_save(config_path, {'callsigns': callsigns})
        
        return True
    except Exception as e:
        logger.error(f"Error saving squadron callsigns: {e}")
        return False

def is_mission_already_processed(mission_name: str, mission_date: str) -> bool:
    """Check if a mission has already been processed"""
    try:
        processed_file = os.path.join(os.path.dirname(__file__), 'config', 'processed_missions.json')
        if os.path.exists(processed_file):
            processed_missions = safe_json_read(processed_file)
            mission_key = f"{mission_name}_{mission_date}"
            return mission_key in processed_missions
    except Exception as e:
        logger.warning(f"Warning: Could not check processed missions: {e}")
    
    return False

def mark_mission_as_processed(mission_name: str, mission_date: str):
    """Mark a mission as processed to prevent duplicates"""
    try:
        config_dir = os.path.join(os.path.dirname(__file__), 'config')
        os.makedirs(config_dir, exist_ok=True)
        
        processed_file = os.path.join(config_dir, 'processed_missions.json')
        
        # Load existing processed missions
        processed_missions = {}
        if os.path.exists(processed_file):
            processed_missions = safe_json_read(processed_file)
        
        # Add this mission
        mission_key = f"{mission_name}_{mission_date}"
        processed_missions[mission_key] = {
            "mission_name": mission_name,
            "mission_date": mission_date,
            "processed_at": datetime.now().isoformat()
        }
        
        # Keep only last 100 missions to prevent file from growing too large
        if len(processed_missions) > 100:
            # Remove oldest entries
            sorted_missions = sorted(processed_missions.items(), 
                                   key=lambda x: x[1].get('processed_at', ''))
            processed_missions = dict(sorted_missions[-100:])
        
        # Save back to file
        safe_json_save(processed_file, processed_missions)
            
    except Exception as e:
        logger.warning(f"Warning: Could not mark mission as processed: {e}")
