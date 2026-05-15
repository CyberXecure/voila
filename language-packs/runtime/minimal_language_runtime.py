#!/usr/bin/env python3
"""
Minimal Voila! language pack runtime helper.

Scope:
- standard library only
- local JSON language packs only
- prefers core packs when available
- falls back to sample packs
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
    source: str = "unknown"


class MinimalLanguageRuntime:
    def __init__(
        self,
        core_packs: dict[str, MinimalLanguagePack] | None = None,
        sample_packs: dict[str, MinimalLanguagePack] | None = None,
        fallback_languages: tuple[str, ...] = DEFAULT_FALLBACK_LANGUAGES,
    ) -> None:
        self.core_packs = core_packs or {}
        self.sample_packs = sample_packs or {}
        self.fallback_languages = fallback_languages

    @classmethod
    def from_directory(cls, directory: Path) -> "MinimalLanguageRuntime":
        """Legacy-compatible loader for a single language-pack directory."""
        return cls(core_packs=load_packs_from_directory(directory))

    @classmethod
    def from_core_and_samples(
        cls,
        core_dir: Path,
        samples_dir: Path,
    ) -> "MinimalLanguageRuntime":
        return cls(
            core_packs=load_packs_from_directory(core_dir),
            sample_packs=load_packs_from_directory(samples_dir),
        )

    def languages(self) -> list[str]:
        return sorted(set(self.core_packs.keys()) | set(self.sample_packs.keys()))

    def core_languages(self) -> list[str]:
        return sorted(self.core_packs.keys())

    def sample_languages(self) -> list[str]:
        return sorted(self.sample_packs.keys())

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
        for source, language_code in self._fallback_chain(language):
            pack = self._pack_for_source(source, language_code)

            if pack is None:
                continue

            value = pack.translations.get(key)

            if value is not None:
                return value

        return None

    def lookup_source(self, key: str, language: str | None = None) -> tuple[str, str] | None:
        for source, language_code in self._fallback_chain(language):
            pack = self._pack_for_source(source, language_code)

            if pack is None:
                continue

            if key in pack.translations:
                return source, language_code

        return None

    def _fallback_chain(self, language: str | None) -> list[tuple[str, str]]:
        languages: list[str] = []

        if language:
            languages.append(language)

        languages.extend(self.fallback_languages)

        unique_languages: list[str] = []
        for item in languages:
            if item not in unique_languages:
                unique_languages.append(item)

        chain: list[tuple[str, str]] = []

        for item in unique_languages:
            chain.append(("core", item))

        for item in unique_languages:
            chain.append(("sample", item))

        return chain

    def _pack_for_source(self, source: str, language_code: str) -> MinimalLanguagePack | None:
        if source == "core":
            return self.core_packs.get(language_code)

        if source == "sample":
            return self.sample_packs.get(language_code)

        return None


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def default_core_language_pack_dir() -> Path:
    return repo_root() / "language-packs" / "core"


def default_sample_language_pack_dir() -> Path:
    return repo_root() / "language-packs" / "samples"


def default_language_pack_dir() -> Path:
    """Legacy-compatible default directory used by older tests."""
    return default_sample_language_pack_dir()


def create_minimal_language_runtime(
    directory: Path | None = None,
) -> MinimalLanguageRuntime:
    if directory is not None:
        return MinimalLanguageRuntime.from_directory(directory)

    return MinimalLanguageRuntime.from_core_and_samples(
        core_dir=default_core_language_pack_dir(),
        samples_dir=default_sample_language_pack_dir(),
    )


def load_packs_from_directory(directory: Path) -> dict[str, MinimalLanguagePack]:
    packs: dict[str, MinimalLanguagePack] = {}

    if not directory.exists():
        return packs

    patterns = ("*.language-pack.json", "*.language-pack.sample.json")

    for pattern in patterns:
        for path in sorted(directory.glob(pattern)):
            pack = load_pack_safely(path)

            if pack is not None:
                packs[pack.language_code] = pack

    return packs


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

    return MinimalLanguagePack(
        language_code=language_code,
        translations=flatten_translations(data),
        source=classify_pack_source(path),
    )


def classify_pack_source(path: Path) -> str:
    parts = set(path.parts)

    if "core" in parts:
        return "core"

    if "samples" in parts:
        return "sample"

    return "unknown"


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
