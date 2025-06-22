#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import os

def debug_xml_structure(xml_path):
    """Debug the XML structure to see what's happening"""
    print(f"Debugging XML file: {xml_path}")
    print("=" * 50)
    
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()
        
        # Find all Events
        events = root.find("Events")
        if events is None:
            print("No Events section found!")
            return
        
        print(f"Found {len(events.findall('Event'))} events")
        
        # Look at ALL events to understand structure
        pilot_names = set()
        ai_count = 0
        player_count = 0
        
        for i, event in enumerate(events.findall("Event")):  # ALL events
            primary = event.find("PrimaryObject")
            if primary is not None:
                pilot = primary.findtext("Pilot", "").strip()
                aircraft = primary.findtext("Name", "Unknown")
                group = primary.findtext("Group", "")
                
                if pilot and pilot.lower() != "unknown":
                    pilot_names.add(pilot)
                    
                    # Check if it looks like AI
                    is_ai = any(pattern in pilot for pattern in [
                        "Static Armor", "Ground-", "Static ", "AI ", "Computer "
                    ])
                    
                    if is_ai:
                        ai_count += 1
                    else:
                        player_count += 1
        
        print(f"\nSummary:")
        print(f"  Total unique pilots found: {len(pilot_names)}")
        print(f"  AI-like pilots: {ai_count}")
        print(f"  Player-like pilots: {player_count}")
        
        # Show all unique pilot names
        print(f"\nAll unique pilot names found:")
        for pilot in sorted(pilot_names):
            # Check if it looks like AI
            is_ai = any(pattern in pilot for pattern in [
                "Static Armor", "Ground-", "Static ", "AI ", "Computer "
            ])
            status = "AI" if is_ai else "Player"
            print(f"  '{pilot}' ({status})")
            
    except Exception as e:
        print(f"Error parsing XML: {e}")

if __name__ == "__main__":
    # Test with the XML file in the parent directory
    xml_path = "../testfile.xml"
    if os.path.exists(xml_path):
        debug_xml_structure(xml_path)
    else:
        print(f"XML file not found at: {xml_path}") 