#!/usr/bin/env python3

from xml_parser import parse_xml
from update_profiles import update_profiles_from_data

def format_minutes_to_hhmm(minutes):
    """Convert minutes to HH:MM format for display"""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours}:{mins:02d}"

def test_enhanced_parsing():
    print("Testing enhanced XML parsing...")
    result = parse_xml('testData.xml')
    
    if result.get('success'):
        pilots = result.get('pilot_data', {})
        print(f"Total pilots found: {len(pilots)}")
        
        for i, (pilot_name, pilot_data) in enumerate(pilots.items(), 1):
            flight_minutes = pilot_data.get('flight_minutes', 0)
            print(f"\n{i}. {pilot_name}:")
            print(f"   Platform: {pilot_data.get('platform', 'Unknown')}")
            print(f"   Aircraft: {pilot_data.get('aircraft', 'Unknown')}")
            print(f"   Nicknames: {pilot_data.get('nicknames', [])}")
            print(f"   Flight time: {flight_minutes} minutes ({format_minutes_to_hhmm(flight_minutes)})")
            print(f"   AA kills: {pilot_data.get('aa_kills', 0)}")
            print(f"   AG kills: {pilot_data.get('ag_kills', 0)}")
            print(f"   RTB: {pilot_data.get('rtb', 0)}")
            print(f"   Ejections: {pilot_data.get('ejections', 0)}")
            print(f"   KIA: {pilot_data.get('kia', 0)}")
        
        # Test profile generation
        print(f"\nGenerating profiles...")
        update_profiles_from_data(pilots)
        print("✅ Profiles generated successfully!")
        
        # Show sample profile data
        print(f"\nSample profile data (six.json):")
        import json
        with open('pilot_profiles/six.json', 'r') as f:
            profile = json.load(f)
            print(f"  Platform hours (minutes): {profile['platform_hours']}")
            print(f"  Aircraft hours (minutes): {profile['aircraft_hours']}")
            print(f"  Mission flight time: {profile['missions'][0]['flight_minutes']} minutes")
        
    else:
        print(f"Error: {result.get('error')}")

if __name__ == "__main__":
    test_enhanced_parsing() 