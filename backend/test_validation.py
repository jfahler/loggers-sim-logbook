#!/usr/bin/env python3
"""
Test script for validation functions
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from validation import (
    validate_file_upload, validate_xml_content, validate_pilot_name,
    validate_callsign, validate_mission_name, validate_aircraft_name,
    validate_platform, validate_numeric_value, validate_callsigns_list,
    sanitize_string, validate_pilot_data, validate_discord_data
)
from werkzeug.datastructures import FileStorage
import tempfile
import xml.etree.ElementTree as ET

def test_pilot_name_validation():
    """Test pilot name validation"""
    print("Testing pilot name validation...")
    
    # Valid names
    valid_names = [
        "Pilot123",
        "Test Pilot",
        "Pilot-Name",
        "Pilot_Name",
        "Pilot.Name",
        "Pilot | Callsign",
        "Pilot - Callsign"
    ]
    
    for name in valid_names:
        is_valid, error = validate_pilot_name(name)
        if not is_valid:
            print(f"❌ Valid name '{name}' failed: {error}")
        else:
            print(f"✅ Valid name '{name}' passed")
    
    # Invalid names
    invalid_names = [
        "",  # Empty
        "A" * 101,  # Too long
        "Pilot<script>",  # Script injection
        "Pilot; DROP TABLE users;",  # SQL injection
    ]
    
    for name in invalid_names:
        is_valid, error = validate_pilot_name(name)
        if is_valid:
            print(f"❌ Invalid name '{name}' should have failed")
        else:
            print(f"✅ Invalid name '{name}' correctly rejected: {error}")

def test_callsign_validation():
    """Test callsign validation"""
    print("\nTesting callsign validation...")
    
    # Valid callsigns
    valid_callsigns = [
        "Alpha1",
        "Bravo-Two",
        "Charlie_3",
        "Delta.Four",
        "Echo | Foxtrot",
        "Golf - Hotel"
    ]
    
    for callsign in valid_callsigns:
        is_valid, error = validate_callsign(callsign)
        if not is_valid:
            print(f"❌ Valid callsign '{callsign}' failed: {error}")
        else:
            print(f"✅ Valid callsign '{callsign}' passed")
    
    # Invalid callsigns
    invalid_callsigns = [
        "",  # Empty
        "A" * 51,  # Too long
        "Callsign<script>",  # Script injection
    ]
    
    for callsign in invalid_callsigns:
        is_valid, error = validate_callsign(callsign)
        if is_valid:
            print(f"❌ Invalid callsign '{callsign}' should have failed")
        else:
            print(f"✅ Invalid callsign '{callsign}' correctly rejected: {error}")

def test_mission_name_validation():
    """Test mission name validation"""
    print("\nTesting mission name validation...")
    
    # Valid mission names
    valid_missions = [
        "Operation Desert Storm",
        "Mission_Alpha",
        "Test-Mission",
        "Mission.123"
    ]
    
    for mission in valid_missions:
        is_valid, error = validate_mission_name(mission)
        if not is_valid:
            print(f"❌ Valid mission '{mission}' failed: {error}")
        else:
            print(f"✅ Valid mission '{mission}' passed")
    
    # Invalid mission names
    invalid_missions = [
        "",  # Empty
        "A" * 201,  # Too long
        "Mission<script>",  # Script injection
    ]
    
    for mission in invalid_missions:
        is_valid, error = validate_mission_name(mission)
        if is_valid:
            print(f"❌ Invalid mission '{mission}' should have failed")
        else:
            print(f"✅ Invalid mission '{mission}' correctly rejected: {error}")

def test_aircraft_validation():
    """Test aircraft name validation"""
    print("\nTesting aircraft validation...")
    
    # Valid aircraft
    valid_aircraft = [
        "F-16C",
        "F-15E Strike Eagle",
        "F/A-18C Hornet",
        "MiG-21",
        "Su-27",
        "Unknown"
    ]
    
    for aircraft in valid_aircraft:
        is_valid, error = validate_aircraft_name(aircraft)
        if not is_valid:
            print(f"❌ Valid aircraft '{aircraft}' failed: {error}")
        else:
            print(f"✅ Valid aircraft '{aircraft}' passed")
    
    # Invalid aircraft
    invalid_aircraft = [
        "",  # Empty
        "A" * 101,  # Too long
        "Aircraft<script>",  # Script injection
    ]
    
    for aircraft in invalid_aircraft:
        is_valid, error = validate_aircraft_name(aircraft)
        if is_valid:
            print(f"❌ Invalid aircraft '{aircraft}' should have failed")
        else:
            print(f"✅ Invalid aircraft '{aircraft}' correctly rejected: {error}")

def test_platform_validation():
    """Test platform validation"""
    print("\nTesting platform validation...")
    
    # Valid platforms
    valid_platforms = ["DCS", "BMS", "IL2"]
    
    for platform in valid_platforms:
        is_valid, error = validate_platform(platform)
        if not is_valid:
            print(f"❌ Valid platform '{platform}' failed: {error}")
        else:
            print(f"✅ Valid platform '{platform}' passed")
    
    # Invalid platforms
    invalid_platforms = [
        "",  # Empty
        "Unknown",
        "DCS World",
        "BMS Falcon"
    ]
    
    for platform in invalid_platforms:
        is_valid, error = validate_platform(platform)
        if is_valid:
            print(f"❌ Invalid platform '{platform}' should have failed")
        else:
            print(f"✅ Invalid platform '{platform}' correctly rejected: {error}")

def test_numeric_validation():
    """Test numeric value validation"""
    print("\nTesting numeric validation...")
    
    # Valid numbers
    test_cases = [
        (0, "zero", 0, 100),
        (50, "fifty", 0, 100),
        (100, "hundred", 0, 100),
        ("25", "string_number", 0, 100),
        (1.5, "float", 0, 10),
    ]
    
    for value, name, min_val, max_val in test_cases:
        is_valid, error = validate_numeric_value(value, name, min_val, max_val)
        if not is_valid:
            print(f"❌ Valid number {value} failed: {error}")
        else:
            print(f"✅ Valid number {value} passed")
    
    # Invalid numbers
    invalid_cases = [
        (-1, "negative", 0, 100),
        (101, "too_high", 0, 100),
        ("abc", "not_number", 0, 100),
        ("", "empty", 0, 100),
    ]
    
    for value, name, min_val, max_val in invalid_cases:
        is_valid, error = validate_numeric_value(value, name, min_val, max_val)
        if is_valid:
            print(f"❌ Invalid number {value} should have failed")
        else:
            print(f"✅ Invalid number {value} correctly rejected: {error}")

def test_callsigns_list_validation():
    """Test callsigns list validation"""
    print("\nTesting callsigns list validation...")
    
    # Valid lists
    valid_lists = [
        ["Alpha", "Bravo", "Charlie"],
        ["Single"],
        []
    ]
    
    for callsigns in valid_lists:
        is_valid, error = validate_callsigns_list(callsigns)
        if not is_valid:
            print(f"❌ Valid callsigns list failed: {error}")
        else:
            print(f"✅ Valid callsigns list passed")
    
    # Invalid lists
    invalid_lists = [
        ["A" * 51],  # Too long callsign
        ["Alpha", ""],  # Empty callsign
        ["Alpha", "B" * 51],  # One too long
        ["A"] * 101,  # Too many callsigns
        "not_a_list",  # Not a list
    ]
    
    for callsigns in invalid_lists:
        is_valid, error = validate_callsigns_list(callsigns)
        if is_valid:
            print(f"❌ Invalid callsigns list should have failed")
        else:
            print(f"✅ Invalid callsigns list correctly rejected: {error}")

def test_sanitize_string():
    """Test string sanitization"""
    print("\nTesting string sanitization...")
    
    test_cases = [
        ("Normal string", "Normal string"),
        ("String with\nnewline", "String withnewline"),
        ("String with\x00null", "String withnull"),
        ("String with<script>", "String with<script>"),  # Should be handled by validation
        ("A" * 2000, "A" * 1000),  # Should be truncated
    ]
    
    for input_str, expected in test_cases:
        result = sanitize_string(input_str, 1000)
        if result == expected:
            print(f"✅ Sanitization passed: '{input_str}' -> '{result}'")
        else:
            print(f"❌ Sanitization failed: '{input_str}' -> '{result}' (expected: '{expected}')")

def test_pilot_data_validation():
    """Test pilot data validation"""
    print("\nTesting pilot data validation...")
    
    # Valid pilot data
    valid_data = {
        "date": "2024-01-01",
        "mission": "Test Mission",
        "aircraft": "F-16C",
        "platform": "DCS",
        "aa_kills": 2,
        "ag_kills": 1,
        "flight_minutes": 45
    }
    
    is_valid, error = validate_pilot_data(valid_data)
    if not is_valid:
        print(f"❌ Valid pilot data failed: {error}")
    else:
        print(f"✅ Valid pilot data passed")
    
    # Invalid pilot data
    invalid_data = {
        "date": "2024-01-01",
        "mission": "A" * 201,  # Too long
        "aircraft": "F-16C",
        "platform": "DCS",
        "aa_kills": -1,  # Negative
    }
    
    is_valid, error = validate_pilot_data(invalid_data)
    if is_valid:
        print(f"❌ Invalid pilot data should have failed")
    else:
        print(f"✅ Invalid pilot data correctly rejected: {error}")

def test_discord_data_validation():
    """Test Discord data validation"""
    print("\nTesting Discord data validation...")
    
    # Valid Discord data
    valid_data = {
        "pilotName": "Test Pilot",
        "pilotCallsign": "Alpha",
        "aircraftType": "F-16C",
        "totalFlights": 10,
        "totalFlightTime": 1200,
        "totalAaKills": 5,
        "totalAgKills": 3
    }
    
    is_valid, error = validate_discord_data(valid_data)
    if not is_valid:
        print(f"❌ Valid Discord data failed: {error}")
    else:
        print(f"✅ Valid Discord data passed")
    
    # Invalid Discord data
    invalid_data = {
        "pilotName": "",  # Empty
        "totalFlights": -1,  # Negative
    }
    
    is_valid, error = validate_discord_data(invalid_data)
    if is_valid:
        print(f"❌ Invalid Discord data should have failed")
    else:
        print(f"✅ Invalid Discord data correctly rejected: {error}")

def create_test_xml_file():
    """Create a test XML file for validation"""
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Tacview generator="DCS World">
    <Events>
        <Event>
            <Action>HasBeenDestroyed</Action>
            <Time>100.0</Time>
            <PrimaryObject>
                <Pilot>Test Pilot</Pilot>
                <Name>F-16C</Name>
                <Type>F-16C</Type>
                <Coalition>Blue</Coalition>
            </PrimaryObject>
            <SecondaryObject>
                <Pilot>Enemy Pilot</Pilot>
                <Name>MiG-29</Name>
                <Type>MiG-29</Type>
                <Coalition>Red</Coalition>
            </SecondaryObject>
            <Location>
                <Latitude>40.0</Latitude>
                <Longitude>-75.0</Longitude>
            </Location>
        </Event>
    </Events>
</Tacview>"""
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
        f.write(xml_content)
        return f.name

def test_xml_content_validation():
    """Test XML content validation"""
    print("\nTesting XML content validation...")
    
    # Create test XML file
    xml_file = create_test_xml_file()
    
    try:
        is_valid, error = validate_xml_content(xml_file)
        if not is_valid:
            print(f"❌ Valid XML content failed: {error}")
        else:
            print(f"✅ Valid XML content passed")
        
        # Test with non-existent file
        is_valid, error = validate_xml_content("nonexistent.xml")
        if is_valid:
            print(f"❌ Non-existent file should have failed")
        else:
            print(f"✅ Non-existent file correctly rejected: {error}")
            
    finally:
        # Clean up
        try:
            os.unlink(xml_file)
        except:
            pass

def main():
    """Run all validation tests"""
    print("🧪 Running validation tests...\n")
    
    test_pilot_name_validation()
    test_callsign_validation()
    test_mission_name_validation()
    test_aircraft_validation()
    test_platform_validation()
    test_numeric_validation()
    test_callsigns_list_validation()
    test_sanitize_string()
    test_pilot_data_validation()
    test_discord_data_validation()
    test_xml_content_validation()
    
    print("\n✅ All validation tests completed!")

if __name__ == "__main__":
    main() 