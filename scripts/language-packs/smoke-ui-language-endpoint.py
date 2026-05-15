#!/usr/bin/env python3
"""
Smoke test for Voila! UI language aliases.

Scope:
- standard library only
- validates services/api/i18n.py alias behavior
- optionally validates a running /ui-language endpoint
- does not modify application state
"""

from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


ALIAS_TO_LEGACY = {
    "ui.language": "ui_language",
    "document.language": "document_language",
    "button.run_ocr_page": "run_ocr_page",
    "button.check_text": "check_text",
    "button.save": "save",
    "button.prev_issue": "prev_issue",
    "button.next_issue": "next_issue",
    "status.editor_loading": "editor_loading",
    "status.editor_ready": "editor_ready",
    "status.lt_checking": "lt_checking",
    "status.lt_no_issues": "lt_no_issues",
    "message.lt_apply_again": "lt_apply_again",
    "tooltip.run_ocr_page": "run_ocr_page_title",
    "tooltip.check_text": "check_text_title",
    "tooltip.save": "save_title",
}


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def import_i18n() -> Any:
    api_dir = repo_root() / "services" / "api"

    if str(api_dir) not in sys.path:
        sys.path.insert(0, str(api_dir))

    import i18n  # type: ignore

    return i18n


def check_i18n_module() -> list[str]:
    errors: list[str] = []
    root = repo_root()
    i18n = import_i18n()

    supported = getattr(i18n, "SUPPORTED_UI_LANGUAGES", {})
    translations = getattr(i18n, "TRANSLATIONS", {})

    expected_languages = {"ro", "en", "fr", "de", "ru", "it", "es", "pt"}

    missing_languages = sorted(expected_languages - set(supported.keys()))
    if missing_languages:
        errors.append(f"Missing supported UI languages: {missing_languages}")

    missing_translation_languages = sorted(expected_languages - set(translations.keys()))
    if missing_translation_languages:
        errors.append(f"Missing translation languages: {missing_translation_languages}")

    for language in sorted(expected_languages):
        values = translations.get(language)

        if not isinstance(values, dict):
            errors.append(f"{language}: translations must be a dict")
            continue

        for alias_key, legacy_key in ALIAS_TO_LEGACY.items():
            alias_value = values.get(alias_key)
            legacy_value = values.get(legacy_key)

            if legacy_value is None:
                errors.append(f"{language}: missing legacy key {legacy_key}")

            if alias_value is None:
                errors.append(f"{language}: missing alias key {alias_key}")

            if alias_value is not None and legacy_value is not None and alias_value != legacy_value:
                errors.append(
                    f"{language}: alias {alias_key} does not match legacy {legacy_key}"
                )

            translated = i18n.t(root, alias_key, language=language)
            if translated == alias_key:
                errors.append(f"{language}: i18n.t did not resolve alias key {alias_key}")

    default_response = i18n.get_ui_language(root)

    if not default_response.get("ok"):
        errors.append("get_ui_language response missing ok=true")

    default_translations = default_response.get("translations")
    if not isinstance(default_translations, dict):
        errors.append("get_ui_language translations must be a dict")
    else:
        for alias_key in ALIAS_TO_LEGACY:
            if alias_key not in default_translations:
                errors.append(f"get_ui_language missing alias key {alias_key}")

    return errors


def fetch_json(url: str) -> dict[str, Any]:
    with urllib.request.urlopen(url, timeout=10) as response:
        body = response.read().decode("utf-8")

    data = json.loads(body)

    if not isinstance(data, dict):
        raise ValueError("Endpoint response must be a JSON object")

    return data


def check_endpoint(url: str) -> list[str]:
    errors: list[str] = []

    try:
        data = fetch_json(url)
    except (OSError, urllib.error.URLError, json.JSONDecodeError, ValueError) as exc:
        return [f"Endpoint smoke test failed for {url}: {exc}"]

    if not data.get("ok"):
        errors.append("Endpoint response missing ok=true")

    translations = data.get("translations")

    if not isinstance(translations, dict):
        errors.append("Endpoint response translations must be a dict")
        return errors

    for alias_key in ALIAS_TO_LEGACY:
        if alias_key not in translations:
            errors.append(f"Endpoint response missing alias key {alias_key}")

    return errors


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Smoke test Voila! UI language alias behavior."
    )

    parser.add_argument(
        "--url",
        default=None,
        help="Optional running /ui-language endpoint URL to check.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = check_i18n_module()

    if args.url:
        errors.extend(check_endpoint(args.url))

    if errors:
        print("UI language smoke test failed.")
        print("")
        for error in errors:
            print(f"- {error}")
        return 1

    print("UI language smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
