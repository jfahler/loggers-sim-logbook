#!/usr/bin/env python3
"""
Script to clean up AI profiles from the pilot_profiles directory.
This script will check each profile against the AI filter and remove those that are identified as AI.
"""

import os
import json
import shutil
from xml_parser import is_player_client

def cleanup_ai_profiles():
    """Clean up AI profiles from the pilot_profiles directory."""
    profile_dir = "pilot_profiles"
    
    if not os.path.exists(profile_dir):
        print(f"Profile directory {profile_dir} does not exist.")
        return
    
    # Get all JSON files in the profile directory
    json_files = [f for f in os.listdir(profile_dir) if f.endswith('.json') and f not in ['index.json', 'template.json']]
    
    print(f"Found {len(json_files)} profile files to check.")
    
    ai_profiles = []
    player_profiles = []
    
    for filename in json_files:
        filepath = os.path.join(profile_dir, filename)
        
        try:
            with open(filepath, 'r') as f:
                profile = json.load(f)
            
            callsign = profile.get('callsign', '')
            aircraft = profile.get('missions', [{}])[0].get('aircraft', '') if profile.get('missions') else ''
            
            # Check if this is an AI profile
            if is_player_client(callsign, aircraft):
                player_profiles.append(filename)
            else:
                ai_profiles.append(filename)
                
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue
    
    print(f"\nFound {len(player_profiles)} player profiles and {len(ai_profiles)} AI profiles.")
    
    if ai_profiles:
        print("\nAI profiles to be removed:")
        for filename in ai_profiles[:10]:  # Show first 10
            print(f"  - {filename}")
        if len(ai_profiles) > 10:
            print(f"  ... and {len(ai_profiles) - 10} more")
        
        # Ask for confirmation
        response = input(f"\nRemove {len(ai_profiles)} AI profiles? (y/N): ")
        
        if response.lower() == 'y':
            # Create backup directory
            backup_dir = "pilot_profiles_backup"
            if not os.path.exists(backup_dir):
                os.makedirs(backup_dir)
            
            # Move AI profiles to backup
            for filename in ai_profiles:
                src = os.path.join(profile_dir, filename)
                dst = os.path.join(backup_dir, filename)
                shutil.move(src, dst)
                print(f"Moved {filename} to backup")
            
            print(f"\nMoved {len(ai_profiles)} AI profiles to {backup_dir}/")
            print("You can restore them later if needed by moving them back.")
        else:
            print("Cleanup cancelled.")
    else:
        print("No AI profiles found to remove.")

if __name__ == "__main__":
    cleanup_ai_profiles() 