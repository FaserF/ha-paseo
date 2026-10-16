"""Tests for versioning and SemVer compliance."""

import json
import re
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent


def test_semver_compliance():
    """Verify manifest.json uses strictly SemVer (Major.Minor.Patch)."""
    manifest_file = BASE_DIR / "custom_components" / "paseo" / "manifest.json"
    assert manifest_file.exists()

    with open(manifest_file, encoding="utf-8") as f:
        data = json.load(f)

    version = data.get("version")
    assert version is not None

    # Matches major.minor.patch or major.minor.patch-devN or major.minor.patchbN
    pattern = r"^\d+\.\d+\.\d+(?:(b|-dev)\d+)?$"
    assert re.match(pattern, version), f"Version '{version}' is not SemVer compliant"
