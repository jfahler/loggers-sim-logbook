#!/usr/bin/env python3

from xml_parser import is_player_client

# Test cases based on the XML structure we found
test_cases = [
    ("Static Armor RED-B-7-1", "Tank", ""),
    ("Static Armor RED-A-4", "Tank", ""),
    ("Static Armor RED-DECOY-B-4", "Infantry", ""),
    ("Ground-7-1", "Humvee", ""),
    ("Katana 1-1 Jediknight", "F-16C Fighting Falcon", ""),
    ("Gunner 1 | Machinegun817", "Mi-24P Hind-F", ""),
    ("(HHC/229) Six", "OH-58D Kiowa Warrior", ""),
]

print("Testing pilot filtering:")
print("=" * 50)

for pilot, aircraft, group in test_cases:
    result = is_player_client(pilot, aircraft, group)
    status = "PLAYER" if result else "AI"
    print(f"'{pilot}' -> {status}")

print("\nExpected results:")
print("- Static Armor* -> AI")
print("- Ground-* -> AI") 
print("- Real player names -> PLAYER") 