"""Tests for translation files validity and parity."""

import json
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "custom_components" / "paseo"


def test_translations_validity():
    """Verify that strings.json and translation files parse as valid JSON."""
    strings_file = BASE_DIR / "strings.json"
    assert strings_file.exists()
    with open(strings_file, encoding="utf-8") as f:
        strings_data = json.load(f)

    en_file = BASE_DIR / "translations" / "en.json"
    assert en_file.exists()
    with open(en_file, encoding="utf-8") as f:
        en_data = json.load(f)

    de_file = BASE_DIR / "translations" / "de.json"
    assert de_file.exists()
    with open(de_file, encoding="utf-8") as f:
        de_data = json.load(f)

    assert "config" in strings_data
    assert "options" in strings_data
    assert "entity" in strings_data
    assert "services" in strings_data

    assert (
        strings_data["config"]["step"]["user"]["data"].keys()
        == en_data["config"]["step"]["user"]["data"].keys()
    )
    assert (
        strings_data["config"]["step"]["user"]["data"].keys()
        == de_data["config"]["step"]["user"]["data"].keys()
    )
