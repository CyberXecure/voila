#!/usr/bin/env python3
"""
Validate Voila! language pack sample files.

Scope:
- standard library only
- validates sample JSON files
- does not modify runtime behavior
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


SUPPORTED_LANGUAGE_CODES = {"ro", "en", "fr", "de", "ru", "it", "es", "pt"}
ALLOWED_STATUS_VALUES = {"draft", "planned", "review", "ready", "deprecated"}
ALLOWED_FALLBACK_VALUES = {"en", "ro"}

REQUIRED_TOP_LEVEL_SECTIONS = ["manifest", "ui", "messages", "feedback", "glossary"]
REQUIRED_MANIFEST_FIELDS = [
    "language_code",
    "language_name",
    "native_name",
    "version",
    "status",
    "fallback",
    "last_updated",
]

TRANSLATION_SECTIONS = ["ui", "messages", "feedback", "glossary"]

KEY_PATTERN = re.compile(r"^[a-z][a-z0-9_]*(\.[a-z][a-z0-9_]*)*$")
VERSION_PATTERN = re.compile(r"^[a-z]{2}-v[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$")
PLACEHOLDER_PATTERN = re.compile(r"\{[A-Za-z_][A-Za-z0-9_]*\}")


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path}: invalid JSON at line {exc.lineno}, column {exc.colno}: {exc.msg}") from exc


def placeholders(value: str) -> set[str]:
    return set(PLACEHOLDER_PATTERN.findall(value))


def validate_manifest(path: Path, data: dict[str, Any], errors: list[str]) -> str | None:
    manifest = data.get("manifest")

    if not isinstance(manifest, dict):
        errors.append(f"{path}: manifest must be an object")
        return None

    for field in REQUIRED_MANIFEST_FIELDS:
        if field not in manifest:
            errors.append(f"{path}: manifest missing required field: {field}")

    language_code = manifest.get("language_code")

    if not isinstance(language_code, str):
        errors.append(f"{path}: manifest.language_code must be a string")
        return None

    if language_code not in SUPPORTED_LANGUAGE_CODES:
        errors.append(f"{path}: unsupported language_code: {language_code}")

    filename_prefix = path.name.split(".", 1)[0]
    if filename_prefix != language_code:
        errors.append(
            f"{path}: filename prefix '{filename_prefix}' does not match manifest.language_code '{language_code}'"
        )

    for text_field in ["language_name", "native_name"]:
        value = manifest.get(text_field)
        if not isinstance(value, str) or len(value.strip()) < 2:
            errors.append(f"{path}: manifest.{text_field} must be a non-empty string")

    version = manifest.get("version")
    if not isinstance(version, str) or not VERSION_PATTERN.match(version):
        errors.append(f"{path}: manifest.version has invalid format: {version!r}")

    status = manifest.get("status")
    if status not in ALLOWED_STATUS_VALUES:
        errors.append(f"{path}: manifest.status has invalid value: {status!r}")

    fallback = manifest.get("fallback")
    if fallback not in ALLOWED_FALLBACK_VALUES:
        errors.append(f"{path}: manifest.fallback has invalid value: {fallback!r}")

    last_updated = manifest.get("last_updated")
    if not isinstance(last_updated, str):
        errors.append(f"{path}: manifest.last_updated must be a string")
    else:
        try:
            datetime.strptime(last_updated, "%Y-%m-%d")
        except ValueError:
            errors.append(f"{path}: manifest.last_updated must use YYYY-MM-DD format")

    for optional_field in ["author", "notes"]:
        if optional_field in manifest and not isinstance(manifest[optional_field], str):
            errors.append(f"{path}: manifest.{optional_field} must be a string when present")

    return language_code


def validate_translation_sections(path: Path, data: dict[str, Any], errors: list[str]) -> dict[str, str]:
    flattened: dict[str, str] = {}

    for section in TRANSLATION_SECTIONS:
        section_value = data.get(section)

        if not isinstance(section_value, dict):
            errors.append(f"{path}: {section} must be an object")
            continue

        for key, value in section_value.items():
            if not isinstance(key, str):
                errors.append(f"{path}: {section} contains a non-string key")
                continue

            if not KEY_PATTERN.match(key):
                errors.append(f"{path}: invalid translation key in {section}: {key!r}")

            if not isinstance(value, str):
                errors.append(f"{path}: value for {section}.{key} must be a string")
                continue

            full_key = f"{section}.{key}"
            flattened[full_key] = value

    return flattened


def validate_language_pack(path: Path) -> tuple[str | None, dict[str, str], list[str]]:
    errors: list[str] = []
    data = load_json(path)

    if not isinstance(data, dict):
        return None, {}, [f"{path}: root must be an object"]

    for section in REQUIRED_TOP_LEVEL_SECTIONS:
        if section not in data:
            errors.append(f"{path}: missing top-level section: {section}")

    extra_sections = sorted(set(data.keys()) - set(REQUIRED_TOP_LEVEL_SECTIONS))
    for section in extra_sections:
        errors.append(f"{path}: unexpected top-level section: {section}")

    language_code = validate_manifest(path, data, errors)
    flattened = validate_translation_sections(path, data, errors)

    return language_code, flattened, errors


def validate_placeholder_consistency(
    translations_by_language: dict[str, dict[str, str]],
    errors: list[str],
) -> None:
    all_keys: set[str] = set()

    for translations in translations_by_language.values():
        all_keys.update(translations.keys())

    for key in sorted(all_keys):
        placeholder_sets: dict[str, set[str]] = {}

        for language_code, translations in translations_by_language.items():
            if key not in translations:
                continue
            placeholder_sets[language_code] = placeholders(translations[key])

        non_empty_sets = {language: values for language, values in placeholder_sets.items() if values}

        if len(non_empty_sets) <= 1:
            continue

        reference_language = sorted(non_empty_sets.keys())[0]
        reference_placeholders = non_empty_sets[reference_language]

        for language_code, language_placeholders in non_empty_sets.items():
            if language_placeholders != reference_placeholders:
                errors.append(
                    "placeholder mismatch for "
                    f"{key}: {reference_language} has {sorted(reference_placeholders)}, "
                    f"{language_code} has {sorted(language_placeholders)}"
                )


def validate_language_pack_group(
    group_name: str,
    directory: Path,
    pattern: str,
    required: bool,
    errors: list[str],
) -> dict[str, dict[str, str]]:
    translations_by_language: dict[str, dict[str, str]] = {}

    if not directory.exists():
        if required:
            errors.append(f"Missing {group_name} directory: {directory}")
        return translations_by_language

    pack_paths = sorted(directory.glob(pattern))

    if not pack_paths:
        if required:
            errors.append(f"No {group_name} language packs found in: {directory}")
        return translations_by_language

    for pack_path in pack_paths:
        try:
            language_code, flattened, pack_errors = validate_language_pack(pack_path)
            errors.extend(pack_errors)

            if language_code:
                translations_by_language[language_code] = flattened
        except ValueError as exc:
            errors.append(str(exc))

    validate_placeholder_consistency(translations_by_language, errors)

    return translations_by_language


def main() -> int:
    root = repo_root()
    schema_path = root / "language-packs" / "schema" / "language-pack.schema.json"
    samples_dir = root / "language-packs" / "samples"
    core_dir = root / "language-packs" / "core"

    errors: list[str] = []

    if not schema_path.exists():
        errors.append(f"Missing schema file: {schema_path}")
    else:
        try:
            load_json(schema_path)
        except ValueError as exc:
            errors.append(str(exc))

    validate_language_pack_group(
        group_name="sample",
        directory=samples_dir,
        pattern="*.language-pack.sample.json",
        required=True,
        errors=errors,
    )

    validate_language_pack_group(
        group_name="core",
        directory=core_dir,
        pattern="*.language-pack.json",
        required=False,
        errors=errors,
    )

    if errors:
        print("Language pack validation failed.")
        print("")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Language pack validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
