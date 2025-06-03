import re
import json
from pathlib import Path

NICKNAME_JSON = Path("nicknames.json")

# Default fallback if no nickname JSON is found
DEFAULT_FRAGMENTS = {
    "drunkbonsai": ["drunk", "bonsai"],
    "six": ["hhc", "229", "six"],
    "machinegun817": ["machinegun", "817", "gunner"],
    "bones": ["bones", "springfield"],
    "fatal": ["fatal", "101st"]
}

def load_nickname_fragments():
    if NICKNAME_JSON.exists():
        with open(NICKNAME_JSON, "r") as f:
            return json.load(f)
    return DEFAULT_FRAGMENTS

def normalize_name(name):
    return re.sub(r"[^\w]", "", name).lower()

def resolve_fuzzy_nickname(raw_name, nickname_fragments=None):
    if nickname_fragments is None:
        nickname_fragments = load_nickname_fragments()

    norm = normalize_name(raw_name)
    for nickname, fragments in nickname_fragments.items():
        if all(fragment in norm for fragment in fragments):
            return nickname
    return normalize_name(raw_name)
