import re
import os
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Tuple, Union
from werkzeug.datastructures import FileStorage
import logging

logger = logging.getLogger(__name__)

# Validation constants
MAX_FILENAME_LENGTH = 255
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
MAX_PILOT_NAME_LENGTH = 100
MAX_CALLSIGN_LENGTH = 50
MAX_MISSION_NAME_LENGTH = 200
MAX_AIRCRAFT_NAME_LENGTH = 100
MAX_NOTE_LENGTH = 1000
MAX_CALLSIGNS_COUNT = 100

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.xml'}

# Valid aircraft types (whitelist for security)
VALID_AIRCRAFT_TYPES = {
    'F-16C', 'F-15E', 'F-15C', 'F/A-18C', 'AV-8B', 'A-10C', 'A-10A',
    'P-51D', 'MiG-21', 'MiG-29', 'Su-27', 'Su-33', 'Su-25', 'F-5E',
    'F-86F', 'MiG-15', 'Fw 190', 'Bf 109', 'Spitfire', 'Mosquito',
    'Corsair', 'Thunderbolt', 'Mustang', 'Viggen', 'Mirage F1',
    'M-2000C', 'L-39', 'C-101', 'Yak-52', 'Christen Eagle', 'JF-17',
    'I-16', 'MiG-19', 'Fw 190 A-8', 'Fw 190 D-9', 'Bf 109 K-4',
    'MB-339', 'AJS-37', 'AV-8B Night Attack', 'A-4 Skyhawk', 'A-4E Skyhawk',
    'Huey', 'Hip', 'Black Shark', 'Gazelle', 'Hind', 'Apache', 'Kiowa',
    'Havoc', 'Chinook', 'Black Hawk', 'Super Cobra', 'Viper', 'Venom',
    'Halo', 'Helix', 'Little Bird', 'Cayuse', 'Twin Huey', 'Super Stallion',
    'Sea Knight', 'Osprey'
}

# Valid platforms
VALID_PLATFORMS = {'DCS', 'BMS', 'IL2'}

# Regex patterns for validation
PILOT_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_|\.]+$')
CALLSIGN_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_|\.]+$')
MISSION_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.]+$')
AIRCRAFT_PATTERN = re.compile(r'^[a-zA-Z0-9\s\-_\.\/]+$')

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message: str, field: Optional[str] = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

def validate_file_upload(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file for security and format requirements
    
    Args:
        file: The uploaded file object
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if file exists
        if not file or file.filename == '':
            return False, "No file provided"
        
        # Validate filename length
        if len(file.filename) > MAX_FILENAME_LENGTH:
            return False, f"Filename too long (max {MAX_FILENAME_LENGTH} characters)"
        
        # Validate file extension
        file_ext = os.path.splitext(file.filename.lower())[1]
        if file_ext not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file type. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        
        # Validate file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer
        
        if file_size > MAX_FILE_SIZE:
            return False, f"File too large (max {MAX_FILE_SIZE // (1024*1024)}MB)"
        
        # Validate filename characters (basic security)
        if not re.match(r'^[a-zA-Z0-9\s\-_\.]+$', file.filename):
            return False, "Filename contains invalid characters"
        
        return True, None
        
    except Exception as e:
        logger.error(f"File validation error: {e}")
        return False, "File validation failed"

def validate_xml_content(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    Validate XML file content structure and security
    
    Args:
        file_path: Path to the XML file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check if file exists and is readable
        if not os.path.exists(file_path):
            return False, "File not found"
        
        if not os.access(file_path, os.R_OK):
            return False, "File not readable"
        
        # Try to parse XML
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
        except ET.ParseError as e:
            return False, f"Invalid XML format: {str(e)}"
        
        # Validate root element
        if root.tag != "Tacview":
            return False, "Invalid XML: Root element must be 'Tacview'"
        
        # Check for required elements
        events = root.find("Events")
        if events is None:
            return False, "Invalid XML: Missing 'Events' section"
        
        # Check for reasonable number of events (prevent DoS)
        event_count = len(events.findall("Event"))
        if event_count > 100000:  # Reasonable limit
            return False, "XML contains too many events (potential DoS)"
        
        # Validate event structure
        for i, event in enumerate(events.findall("Event")[:100]):  # Check first 100 events
            if not validate_event_structure(event):
                return False, f"Invalid event structure at index {i}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"XML content validation error: {e}")
        return False, f"XML validation failed: {str(e)}"

def validate_event_structure(event) -> bool:
    """Validate individual XML event structure"""
    try:
        # Check for required elements
        action = event.findtext("Action")
        if not action:
            return False
        
        # Validate action values
        valid_actions = {
            "HasBeenDestroyed", "HasLanded", "HasTakenOff", "HasEjected",
            "HasBeenRescued", "HasCrashed", "HasDespawned"
        }
        if action not in valid_actions:
            return False
        
        # Check for at least one object
        primary = event.find("PrimaryObject")
        if primary is None:
            return False
        
        return True
        
    except Exception:
        return False

def validate_pilot_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate pilot name for security and format
    
    Args:
        name: Pilot name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Pilot name is required"
    
    if len(name) > MAX_PILOT_NAME_LENGTH:
        return False, f"Pilot name too long (max {MAX_PILOT_NAME_LENGTH} characters)"
    
    if not PILOT_NAME_PATTERN.match(name):
        return False, "Pilot name contains invalid characters"
    
    return True, None

def validate_callsign(callsign: str) -> Tuple[bool, Optional[str]]:
    """
    Validate callsign for security and format
    
    Args:
        callsign: Callsign to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not callsign:
        return False, "Callsign is required"
    
    if len(callsign) > MAX_CALLSIGN_LENGTH:
        return False, f"Callsign too long (max {MAX_CALLSIGN_LENGTH} characters)"
    
    if not CALLSIGN_PATTERN.match(callsign):
        return False, "Callsign contains invalid characters"
    
    return True, None

def validate_mission_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate mission name for security and format
    
    Args:
        name: Mission name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Mission name is required"
    
    if len(name) > MAX_MISSION_NAME_LENGTH:
        return False, f"Mission name too long (max {MAX_MISSION_NAME_LENGTH} characters)"
    
    if not MISSION_NAME_PATTERN.match(name):
        return False, "Mission name contains invalid characters"
    
    return True, None

def validate_aircraft_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate aircraft name for security and format
    
    Args:
        name: Aircraft name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not name:
        return False, "Aircraft name is required"
    
    if len(name) > MAX_AIRCRAFT_NAME_LENGTH:
        return False, f"Aircraft name too long (max {MAX_AIRCRAFT_NAME_LENGTH} characters)"
    
    if not AIRCRAFT_PATTERN.match(name):
        return False, "Aircraft name contains invalid characters"
    
    # Check against whitelist for security
    if name not in VALID_AIRCRAFT_TYPES:
        logger.warning(f"Unknown aircraft type: {name}")
        # Don't reject, just log warning
    
    return True, None

def validate_platform(platform: str) -> Tuple[bool, Optional[str]]:
    """
    Validate platform name
    
    Args:
        platform: Platform name to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not platform:
        return False, "Platform is required"
    
    if platform not in VALID_PLATFORMS:
        return False, f"Invalid platform. Allowed: {', '.join(VALID_PLATFORMS)}"
    
    return True, None

def validate_numeric_value(value: Union[int, float, str], field_name: str, 
                          min_val: Optional[Union[int, float]] = None,
                          max_val: Optional[Union[int, float]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate numeric values
    
    Args:
        value: Value to validate
        field_name: Name of the field for error messages
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if isinstance(value, str):
            num_value = float(value)
        else:
            num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False, f"{field_name} must be at least {min_val}"
        
        if max_val is not None and num_value > max_val:
            return False, f"{field_name} must be at most {max_val}"
        
        return True, None
        
    except (ValueError, TypeError):
        return False, f"{field_name} must be a valid number"

def validate_callsigns_list(callsigns: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate list of callsigns
    
    Args:
        callsigns: List of callsigns to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(callsigns, list):
        return False, "Callsigns must be an array"
    
    if len(callsigns) > MAX_CALLSIGNS_COUNT:
        return False, f"Too many callsigns (max {MAX_CALLSIGNS_COUNT})"
    
    for i, callsign in enumerate(callsigns):
        is_valid, error = validate_callsign(callsign)
        if not is_valid:
            return False, f"Callsign {i+1}: {error}"
    
    return True, None

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input by removing dangerous characters and limiting length
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not value:
        return ""
    
    # Remove null bytes and control characters (including newlines)
    sanitized = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F\n\r]', '', str(value))
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized.strip()

def validate_pilot_data(pilot_data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate pilot mission data structure
    
    Args:
        pilot_data: Pilot data dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        required_fields = ['date', 'mission', 'aircraft', 'platform']
        
        for field in required_fields:
            if field not in pilot_data:
                return False, f"Missing required field: {field}"
        
        # Validate individual fields
        is_valid, error = validate_mission_name(pilot_data['mission'])
        if not is_valid:
            return False, f"Mission name: {error}"
        
        is_valid, error = validate_aircraft_name(pilot_data['aircraft'])
        if not is_valid:
            return False, f"Aircraft: {error}"
        
        is_valid, error = validate_platform(pilot_data['platform'])
        if not is_valid:
            return False, f"Platform: {error}"
        
        # Validate numeric fields
        numeric_fields = ['aa_kills', 'ag_kills', 'frat_kills', 'rtb', 'ejections', 'deaths', 'flight_minutes']
        for field in numeric_fields:
            if field in pilot_data:
                is_valid, error = validate_numeric_value(pilot_data[field], field, min_val=0, max_val=10000)
                if not is_valid:
                    return False, f"{field}: {error}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Pilot data validation error: {e}")
        return False, f"Data validation failed: {str(e)}"

def validate_discord_data(data: Dict) -> Tuple[bool, Optional[str]]:
    """
    Validate Discord webhook data
    
    Args:
        data: Discord data dictionary to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        if not isinstance(data, dict):
            return False, "Data must be a JSON object"
        
        if 'pilotName' not in data:
            return False, "pilotName is required"
        
        # Validate pilot name
        is_valid, error = validate_pilot_name(data['pilotName'])
        if not is_valid:
            return False, f"pilotName: {error}"
        
        # Validate optional fields
        optional_fields = ['pilotCallsign', 'aircraftType', 'missionName']
        for field in optional_fields:
            if field in data and data[field]:
                if field == 'pilotCallsign':
                    is_valid, error = validate_callsign(data[field])
                elif field == 'aircraftType':
                    is_valid, error = validate_aircraft_name(data[field])
                elif field == 'missionName':
                    is_valid, error = validate_mission_name(data[field])
                
                if not is_valid:
                    return False, f"{field}: {error}"
        
        # Validate numeric fields
        numeric_fields = ['totalFlights', 'totalFlightTime', 'averageFlightDuration', 
                         'totalAaKills', 'totalAgKills', 'totalFratKills', 
                         'totalRtbCount', 'totalEjections', 'totalDeaths']
        for field in numeric_fields:
            if field in data:
                is_valid, error = validate_numeric_value(data[field], field, min_val=0, max_val=100000)
                if not is_valid:
                    return False, f"{field}: {error}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Discord data validation error: {e}")
        return False, f"Data validation failed: {str(e)}" 