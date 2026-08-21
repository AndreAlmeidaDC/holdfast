#!/usr/bin/env python3
"""
Local structural validator for the holdfast skill.

Checks integrity before a commit or PR:
- required files exist (per metadata.json's required_files list)
- SKILL.md has valid frontmatter, the expected name and the origin version check section
- metadata.json is valid JSON with the expected keys for this skill
- update_policy follows the object schema (not the vibecode-family string schema)
- declared_capabilities has the three surfaces, each explicitly true or false with a reason

Run from the repo root or via: python3 scripts/validate_skill.py
Exits 0 when valid, 1 when any check fails.
"""
from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[1]

errors = []
warnings = []

metadata_path = ROOT / "metadata.json"
skill = ROOT / "SKILL.md"
readme = ROOT / "README.md"

# metadata.json
metadata = {}
if metadata_path.exists():
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"metadata.json is not valid JSON: {exc}")
else:
    errors.append("Missing metadata.json")

expected_name = metadata.get("name", "")

if metadata:
    for key in ["name", "version", "origin_url", "default_branch",
                "update_policy", "declared_capabilities", "required_files"]:
        if key not in metadata:
            errors.append(f"metadata.json missing key: {key}")

    # update_policy: object schema (this skill is not part of the vibecode family)
    policy = metadata.get("update_policy")
    if not isinstance(policy, dict):
        errors.append(
            'metadata.json update_policy must be an object with '
            '"requires_user_consent" and "silent_self_update_allowed" '
            '(this skill uses the object schema, not the vibecode string schema)'
        )
    else:
        if policy.get("requires_user_consent") is not True:
            errors.append("update_policy.requires_user_consent must be true")
        if policy.get("silent_self_update_allowed") is not False:
            errors.append("update_policy.silent_self_update_allowed must be false")

    # declared_capabilities: three surfaces, each with expected (bool) and reason (str)
    caps = metadata.get("declared_capabilities", {})
    if isinstance(caps, dict):
        for surface in ["network_egress", "subprocess", "dependency_install"]:
            entry = caps.get(surface)
            if not isinstance(entry, dict):
                errors.append(f"declared_capabilities missing surface: {surface}")
                continue
            if "expected" not in entry or not isinstance(entry["expected"], bool):
                errors.append(f"declared_capabilities.{surface}.expected must be a boolean")
            if not entry.get("reason"):
                errors.append(f"declared_capabilities.{surface} must include a non-empty reason")
    else:
        errors.append("declared_capabilities must be an object")

    # required_files list must be present and every listed file must exist
    required_files = metadata.get("required_files", [])
    if not required_files:
        warnings.append("metadata.json required_files is empty or missing")
    for rel in required_files:
        if not (ROOT / rel).exists():
            errors.append(f"Missing required file (per metadata.json): {rel}")

# SKILL.md
if not skill.exists():
    errors.append("Missing SKILL.md")
else:
    text = skill.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        errors.append("SKILL.md must start with YAML frontmatter")
    if expected_name and f"name: {expected_name}" not in text:
        errors.append(
            f"SKILL.md frontmatter name must match metadata name ({expected_name})"
        )
    if "description:" not in text:
        errors.append("SKILL.md frontmatter must include description")
    if "## Origin version check" not in text:
        errors.append("SKILL.md must include the Origin version check section")
    if "never self-update" not in text.lower() and "silent self-update" not in text.lower():
        warnings.append("SKILL.md should state that it never self-updates silently")

# references/version-check.md must exist and point at this repo
vc = ROOT / "references" / "version-check.md"
if not vc.exists():
    errors.append("Missing references/version-check.md")
else:
    vc_text = vc.read_text(encoding="utf-8")
    origin = metadata.get("origin_url", "")
    if origin and origin not in vc_text:
        errors.append("references/version-check.md does not reference the canonical origin_url")

if not readme.exists():
    errors.append("Missing README.md")

# report
if warnings:
    print("Warnings:")
    for w in warnings:
        print(f"- {w}")

if errors:
    print("Validation failed:")
    for error in errors:
        print(f"- {error}")
    sys.exit(1)

print("Validation passed.")
