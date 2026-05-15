#!/usr/bin/env python3
"""
Minimal Voila! language pack runtime helper.

Scope:
- standard library only
- local JSON language packs only
- safe fallback behavior
- no UI integration
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


TRANSLATION_SECTIONS = ("ui", "messages", "feedback", "glossary")
DEFAULT_FALLBACK_LANGUAGES = ("en", "ro")
PLACEHOLDER_PATTERN = re.compile(r"\{([A-Za-z_][A-Za-z0-9_]*)\}")


@dataclass(frozen=True)
class MinimalLanguagePack:
    language_code: str
    translations: dict[str, str]


class MinimalLanguageRuntime:
    def __init__(
        self,
        packs: dict[str, MinimalLanguagePack] | None = None,
        fallback_languages: tuple[str, ...] = DEFAULT_FALLBACK_LANGUAGES,
    ) -> None:
        self.packs = packs or {}
        self.fallback_languages = fallback_languages

    @classmethod
    def from_directory(cls, directory: Path) -> "MinimalLanguageRuntime":
        packs: dict[str, MinimalLanguagePack] = {}

        if not directory.exists():
            return cls(packs=packs)

        for path in sorted(directory.glob("*.language-pack.sample.json")):
            pack = load_pack_safely(path)

            if pack is not None:
                packs[pack.language_code] = pack

        return cls(packs=packs)

    def languages(self) -> list[str]:
        return sorted(self.packs.keys())

    def t(
        self,
        key: str,
        language: str | None = None,
        default: str | None = None,
        **values: Any,
    ) -> str:
        text = self.lookup(key=key, language=language)

        if text is None:
            text = default if default is not None else key

        return replace_placeholders(text, values)

    def lookup(self, key: str, language: str | None = None) -> str | None:
        for candidate in self._fallback_chain(language):
            pack = self.packs.get(candidate)

            if pack is None:
                continue

            value = pack.translations.get(key)

            if value is not None:
                return value

        return None

    def _fallback_chain(self, language: str | None) -> list[str]:
        result: list[str] = []

        if language:
            result.append(language)

        result.extend(self.fallback_languages)

        unique: list[str] = []
        for item in result:
            if item not in unique:
                unique.append(item)

        return unique


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_language_pack_dir() -> Path:
    return repo_root() / "language-packs" / "samples"


def create_minimal_language_runtime(
    directory: Path | None = None,
) -> MinimalLanguageRuntime:
    return MinimalLanguageRuntime.from_directory(directory or default_language_pack_dir())


def load_pack_safely(path: Path) -> MinimalLanguagePack | None:
    try:
        return load_pack(path)
    except (OSError, ValueError, json.JSONDecodeError):
        return None


def load_pack(path: Path) -> MinimalLanguagePack:
    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"{path}: root must be a JSON object")

    manifest = data.get("manifest")

    if not isinstance(manifest, dict):
        raise ValueError(f"{path}: manifest must be an object")

    language_code = manifest.get("language_code")

    if not isinstance(language_code, str) or not language_code:
        raise ValueError(f"{path}: manifest.language_code must be a non-empty string")

    translations = flatten_translations(data)

    return MinimalLanguagePack(
        language_code=language_code,
        translations=translations,
    )


def flatten_translations(data: dict[str, Any]) -> dict[str, str]:
    translations: dict[str, str] = {}

    for section in TRANSLATION_SECTIONS:
        section_value = data.get(section)

        if not isinstance(section_value, dict):
            continue

        for key, value in section_value.items():
            if isinstance(key, str) and isinstance(value, str):
                translations[key] = value

    return translations


def replace_placeholders(text: str, values: dict[str, Any]) -> str:
    def replace(match: re.Match[str]) -> str:
        name = match.group(1)

        if name not in values:
            return match.group(0)

        return str(values[name])

    return PLACEHOLDER_PATTERN.sub(replace, text)
