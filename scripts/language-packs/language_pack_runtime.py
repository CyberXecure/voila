#!/usr/bin/env python3
"""
Isolated Voila! language pack runtime scaffold.

Scope:
- standard library only
- loads local sample language packs
- provides fallback translation behavior
- not imported by the application runtime
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TRANSLATION_SECTIONS = ("ui", "messages", "feedback", "glossary")
DEFAULT_FALLBACK_ORDER = ("en", "ro")
PLACEHOLDER_PATTERN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass(frozen=True)
class LanguagePack:
    language_code: str
    manifest: dict[str, Any]
    translations: dict[str, str]


class LanguagePackRuntime:
    def __init__(
        self,
        packs: dict[str, LanguagePack],
        fallback_order: tuple[str, ...] = DEFAULT_FALLBACK_ORDER,
    ) -> None:
        self.packs = packs
        self.fallback_order = fallback_order

    @classmethod
    def from_samples_dir(cls, samples_dir: Path) -> "LanguagePackRuntime":
        packs: dict[str, LanguagePack] = {}

        for path in sorted(samples_dir.glob("*.language-pack.sample.json")):
            pack = load_language_pack(path)
            packs[pack.language_code] = pack

        return cls(packs=packs)

    def available_languages(self) -> list[str]:
        return sorted(self.packs.keys())

    def translate(
        self,
        key: str,
        language: str | None = None,
        default: str | None = None,
        **placeholders: Any,
    ) -> str:
        value = self.lookup(key=key, language=language)

        if value is None:
            value = default if default is not None else key

        return apply_placeholders(value, placeholders)

    def lookup(self, key: str, language: str | None = None) -> str | None:
        for language_code in self._candidate_languages(language):
            pack = self.packs.get(language_code)

            if not pack:
                continue

            value = pack.translations.get(key)

            if value is not None:
                return value

        return None

    def _candidate_languages(self, language: str | None) -> list[str]:
        candidates: list[str] = []

        if language:
            candidates.append(language)

        candidates.extend(self.fallback_order)

        unique: list[str] = []
        for item in candidates:
            if item not in unique:
                unique.append(item)

        return unique


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_samples_dir() -> Path:
    return repo_root() / "language-packs" / "samples"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a JSON object")

    return data


def flatten_translations(data: dict[str, Any]) -> dict[str, str]:
    translations: dict[str, str] = {}

    for section in TRANSLATION_SECTIONS:
        section_value = data.get(section, {})

        if not isinstance(section_value, dict):
            continue

        for key, value in section_value.items():
            if isinstance(key, str) and isinstance(value, str):
                translations[key] = value

    return translations


def load_language_pack(path: Path) -> LanguagePack:
    data = load_json(path)
    manifest = data.get("manifest")

    if not isinstance(manifest, dict):
        raise ValueError(f"{path}: manifest must be an object")

    language_code = manifest.get("language_code")

    if not isinstance(language_code, str) or not language_code:
        raise ValueError(f"{path}: manifest.language_code must be a non-empty string")

    return LanguagePack(
        language_code=language_code,
        manifest=manifest,
        translations=flatten_translations(data),
    )


def apply_placeholders(value: str, placeholders: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)

        if name not in placeholders:
            return match.group(0)

        return str(placeholders[name])

    return PLACEHOLDER_PATTERN.sub(replace, value)


def create_default_runtime() -> LanguagePackRuntime:
    return LanguagePackRuntime.from_samples_dir(default_samples_dir())
