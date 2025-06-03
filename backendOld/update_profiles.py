import argparse
from pathlib import Path
from backend.xml_parser import parse_tacview_xml
from backend.profile_manager import load_profile, save_profile, update_profile

def update_profiles_from_xml(xml_path, profile_dir):
    pilot_missions = parse_tacview_xml(xml_path)
    profile_dir.mkdir(exist_ok=True)

    for nickname, mission_data in pilot_missions.items():
        aircraft = mission_data.get("aircraft", "Unknown")
        profile = load_profile(nickname, profile_dir)
        update_profile(profile, mission_data, flight_minutes=45, aircraft=aircraft)
        save_profile(nickname, profile, profile_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update pilot profiles from Tacview XML")
    parser.add_argument("--xml", required=True, help="Path to Tacview XML file")
    parser.add_argument("--out", default="pilot_profiles", help="Output directory for pilot profiles")

    args = parser.parse_args()
    xml_path = Path(args.xml)
    out_dir = Path(args.out)

    update_profiles_from_xml(xml_path, out_dir)
    print(f"✅ Profiles updated from {xml_path.name} into {out_dir}/")
