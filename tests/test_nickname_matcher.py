import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.nickname_matcher import resolve_fuzzy_nickname, DEFAULT_FRAGMENTS, normalize_name


@pytest.mark.parametrize(
    "raw_name,expected",
    [
        ("Drunk Bonsai", "drunkbonsai"),
        ("HHC 229 Six", "six"),
        ("Machinegun 817 Gunner", "machinegun817"),
        ("Springfield Bones", "bones"),
        ("Fatal 101st", "fatal"),
    ],
)
def test_resolve_known_names(raw_name, expected):
    assert resolve_fuzzy_nickname(raw_name, DEFAULT_FRAGMENTS) == expected


def test_resolve_unknown_name_returns_normalized():
    raw = "Unknown Pilot"
    assert resolve_fuzzy_nickname(raw, DEFAULT_FRAGMENTS) == normalize_name(raw)
