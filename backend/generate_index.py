# generate_index.py
import os
import json

def generate_index():
    folder = os.path.join(os.path.dirname(__file__), "pilot_profiles")
    slugs = [
        f.replace(".json", "")
        for f in os.listdir(folder)
        if f.endswith(".json") and f != "index.json"
    ]
    with open(os.path.join(folder, "index.json"), "w") as f:
        json.dump(slugs, f)

if __name__ == "__main__":
    generate_index()
