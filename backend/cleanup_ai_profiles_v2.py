#!/usr/bin/env python3
"""
Cleanup script to remove AI pilot profiles that got through the previous filter.
This script identifies and removes AI profiles based on improved patterns.
"""

import os
import json
import re
from pathlib import Path

# Configuration
PROFILE_DIR = Path("pilot_profiles")
BACKUP_DIR = Path("ai_profiles_backup")

def is_ai_pilot(pilot_name: str) -> bool:
    """Determine if a pilot name indicates an AI unit"""
    if not pilot_name:
        return False
    
    pilot_lower = pilot_name.lower()
    
    # Known real players (whitelist)
    real_players = {
        'machinegun817', 'six', 'fatal', 'drunkbonsai', 'bones', 'bullet'
    }
    
    if pilot_lower in real_players:
        return False
    
    # AI squadron/group patterns
    ai_patterns = [
        r'^[a-z]+\d{1,2}$',  # word followed by 1-2 digits
        r'^[a-z]+\d{3}$',  # word followed by 3 digits
        r'^\d{2}[a-z]+$',  # 2 digits followed by word
        r'^\d{3}[a-z]+$',  # 3 digits followed by word
        r'^[a-z]+\d{1,2}[a-z]+$',  # word + 1-2 digits + word
        r'^[a-z]+pilot\d+$',  # word + pilot + number
        r'^[a-z]+cas\d+pilot\d+$',  # word + cas + number + pilot + number
        r'^[a-z]+barcap\d+pilot\d+$',  # word + barcap + number + pilot + number
        r'^[a-z]+sead\d+pilot\d+$',  # word + sead + number + pilot + number
        r'^[a-z]+strike\d+pilot\d+$',  # word + strike + number + pilot + number
    ]
    
    for pattern in ai_patterns:
        if re.match(pattern, pilot_lower):
            return True
    
    return False

def cleanup_ai_profiles():
    """Remove AI pilot profiles and move them to backup"""
    
    # Create backup directory if it doesn't exist
    BACKUP_DIR.mkdir(exist_ok=True)
    
    # Get all JSON files in profile directory
    profile_files = [f for f in PROFILE_DIR.glob("*.json") 
                    if f.name not in ['index.json', 'template.json']]
    
    ai_profiles = []
    real_profiles = []
    
    print(f"Scanning {len(profile_files)} profile files...")
    
    for profile_file in profile_files:
        try:
            with open(profile_file, 'r', encoding='utf-8') as f:
                profile_data = json.load(f)
            
            pilot_name = profile_data.get('callsign', '').split('|')[-1].strip()
            
            if is_ai_pilot(pilot_name):
                ai_profiles.append(profile_file)
                print(f"  AI: {pilot_name} ({profile_file.name})")
            else:
                real_profiles.append(profile_file)
                print(f"  Player: {pilot_name} ({profile_file.name})")
                
        except Exception as e:
            print(f"  Error reading {profile_file.name}: {e}")
    
    print(f"\nFound {len(ai_profiles)} AI profiles and {len(real_profiles)} real player profiles")
    
    if not ai_profiles:
        print("No AI profiles to clean up!")
        return
    
    # Ask for confirmation
    response = input(f"\nMove {len(ai_profiles)} AI profiles to backup? (y/N): ")
    if response.lower() != 'y':
        print("Cleanup cancelled.")
        return
    
    # Move AI profiles to backup
    moved_count = 0
    for profile_file in ai_profiles:
        try:
            backup_path = BACKUP_DIR / profile_file.name
            profile_file.rename(backup_path)
            moved_count += 1
            print(f"  Moved: {profile_file.name}")
        except Exception as e:
            print(f"  Error moving {profile_file.name}: {e}")
    
    print(f"\n✅ Successfully moved {moved_count} AI profiles to backup")
    print(f"📁 Backup location: {BACKUP_DIR.absolute()}")

if __name__ == "__main__":
    cleanup_ai_profiles() 