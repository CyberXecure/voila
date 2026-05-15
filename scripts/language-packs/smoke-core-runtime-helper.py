#!/usr/bin/env python3
"""
Smoke test for Voila! core-first language pack runtime helper.

Scope:
- standard library only
- no application runtime import
- no UI changes
- verifies core-first lookup and sample fallback behavior
"""

from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parents[2] / "language-packs" / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from minimal_language_runtime import (  # noqa: E402
    MinimalLanguageRuntime,
    create_minimal_language_runtime,
    default_core_language_pack_dir,
    default_sample_language_pack_dir,
)


def write_pack(path: Path, language_code: str, value: str) -> None:
    path.write_text(
        json.dumps(
            {
                "manifest": {"language_code": language_code},
                "ui": {"button.save": value},
                "messages": {"lesson.progress": "Lesson {current} of {total}"},
                "feedback": {},
                "glossary": {},
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def assert_equal(actual: object, expected: object, message: str, errors: list[str]) -> None:
    if actual != expected:
        errors.append(f"{message}: expected {expected!r}, got {actual!r}")


def main() -> int:
    errors: list[str] = []

    core_dir = default_core_language_pack_dir()
    samples_dir = default_sample_language_pack_dir()

    if not core_dir.exists():
        errors.append(f"Core directory missing: {core_dir}")

    if not samples_dir.exists():
        errors.append(f"Samples directory missing: {samples_dir}")

    runtime = create_minimal_language_runtime()

    for language in ("ro", "en"):
        if language not in runtime.core_languages():
            errors.append(f"Missing core language: {language}")

        if language not in runtime.sample_languages():
            errors.append(f"Missing sample language: {language}")

    assert_equal(
        runtime.lookup_source("button.save", language="ro"),
        ("core", "ro"),
        "Romanian button.save should resolve from core",
        errors,
    )

    assert_equal(
        runtime.t("button.save", language="ro"),
        "Salvează",
        "Romanian button.save value",
        errors,
    )

    assert_equal(
        runtime.lookup_source("button.save", language="en"),
        ("core", "en"),
        "English button.save should resolve from core",
        errors,
    )

    assert_equal(
        runtime.t("button.save", language="en"),
        "Save",
        "English button.save value",
        errors,
    )

    assert_equal(
        runtime.lookup_source("button.save", language="fr"),
        ("core", "en"),
        "Unsupported language should fall back to English core",
        errors,
    )

    assert_equal(
        runtime.t("button.save", language="fr"),
        "Save",
        "Unsupported language fallback value",
        errors,
    )

    assert_equal(
        runtime.t("lesson.progress", language="ro", current=2, total=10),
        "Lecția 2 din 10",
        "Romanian lesson.progress placeholder replacement",
        errors,
    )

    assert_equal(
        runtime.t("missing.key", language="ro", default="Fallback OK"),
        "Fallback OK",
        "Missing key should use default",
        errors,
    )

    assert_equal(
        runtime.t("missing.key", language="ro"),
        "missing.key",
        "Missing key without default should return key",
        errors,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_samples = temp_path / "samples"
        temp_samples.mkdir()

        write_pack(
            temp_samples / "en.language-pack.sample.json",
            language_code="en",
            value="Sample Save",
        )

        sample_runtime = MinimalLanguageRuntime.from_core_and_samples(
            core_dir=temp_path / "missing-core",
            samples_dir=temp_samples,
        )

        assert_equal(
            sample_runtime.lookup_source("button.save", language="en"),
            ("sample", "en"),
            "Sample fallback source when core is missing",
            errors,
        )

        assert_equal(
            sample_runtime.t("button.save", language="en"),
            "Sample Save",
            "Sample fallback value when core is missing",
            errors,
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        temp_core = temp_path / "core"
        temp_samples = temp_path / "samples"
        temp_core.mkdir()
        temp_samples.mkdir()

        write_pack(
            temp_samples / "en.language-pack.sample.json",
            language_code="en",
            value="Sample Save",
        )

        write_pack(
            temp_core / "en.language-pack.json",
            language_code="en",
            value="Core Save",
        )

        core_runtime = MinimalLanguageRuntime.from_core_and_samples(
            core_dir=temp_core,
            samples_dir=temp_samples,
        )

        assert_equal(
            core_runtime.lookup_source("button.save", language="en"),
            ("core", "en"),
            "Core should override sample source",
            errors,
        )

        assert_equal(
            core_runtime.t("button.save", language="en"),
            "Core Save",
            "Core should override sample value",
            errors,
        )

    if errors:
        print("Core runtime helper smoke test failed.")
        print("")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Core runtime helper smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
