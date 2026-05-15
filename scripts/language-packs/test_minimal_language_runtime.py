#!/usr/bin/env python3
"""
Tests for the minimal Voila! language pack runtime helper.

Scope:
- standard library only
- no application runtime import
- no UI integration
- verifies core-first loading with sample fallback
"""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


RUNTIME_DIR = Path(__file__).resolve().parents[2] / "language-packs" / "runtime"
if str(RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(RUNTIME_DIR))

from minimal_language_runtime import (  # noqa: E402
    MinimalLanguageRuntime,
    create_minimal_language_runtime,
    default_core_language_pack_dir,
    default_language_pack_dir,
    default_sample_language_pack_dir,
    load_pack,
    load_pack_safely,
    replace_placeholders,
)


class MinimalLanguageRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = create_minimal_language_runtime()

    def test_default_language_pack_dirs_exist(self) -> None:
        self.assertTrue(default_core_language_pack_dir().exists())
        self.assertTrue(default_sample_language_pack_dir().exists())
        self.assertTrue(default_language_pack_dir().exists())

    def test_languages_include_ro_and_en(self) -> None:
        self.assertIn("ro", self.runtime.languages())
        self.assertIn("en", self.runtime.languages())

    def test_core_languages_include_ro_and_en(self) -> None:
        self.assertIn("ro", self.runtime.core_languages())
        self.assertIn("en", self.runtime.core_languages())

    def test_sample_languages_include_ro_and_en(self) -> None:
        self.assertIn("ro", self.runtime.sample_languages())
        self.assertIn("en", self.runtime.sample_languages())

    def test_core_is_preferred_for_existing_key(self) -> None:
        self.assertEqual(
            self.runtime.lookup_source("button.save", language="ro"),
            ("core", "ro"),
        )

    def test_ro_lookup(self) -> None:
        self.assertEqual(
            self.runtime.t("button.save", language="ro"),
            "Salvează",
        )

    def test_en_lookup(self) -> None:
        self.assertEqual(
            self.runtime.t("button.save", language="en"),
            "Save",
        )

    def test_unsupported_language_falls_back_to_en_core(self) -> None:
        self.assertEqual(
            self.runtime.lookup_source("button.save", language="fr"),
            ("core", "en"),
        )
        self.assertEqual(
            self.runtime.t("button.save", language="fr"),
            "Save",
        )

    def test_missing_key_uses_default(self) -> None:
        self.assertEqual(
            self.runtime.t("missing.key", language="ro", default="Fallback OK"),
            "Fallback OK",
        )

    def test_missing_key_without_default_returns_key(self) -> None:
        self.assertEqual(
            self.runtime.t("missing.key", language="ro"),
            "missing.key",
        )

    def test_ro_placeholders(self) -> None:
        self.assertEqual(
            self.runtime.t("lesson.progress", language="ro", current=2, total=10),
            "Lecția 2 din 10",
        )

    def test_en_placeholders(self) -> None:
        self.assertEqual(
            self.runtime.t("lesson.progress", language="en", current=2, total=10),
            "Lesson 2 of 10",
        )

    def test_missing_placeholder_is_preserved(self) -> None:
        self.assertEqual(
            self.runtime.t("lesson.progress", language="en", current=2),
            "Lesson 2 of {total}",
        )

    def test_replace_placeholders_directly(self) -> None:
        self.assertEqual(
            replace_placeholders("Processed {count} items.", {"count": 3}),
            "Processed 3 items.",
        )

    def test_lookup_returns_none_for_missing_key(self) -> None:
        self.assertIsNone(
            self.runtime.lookup("missing.key", language="ro"),
        )

    def test_empty_directories_are_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = MinimalLanguageRuntime.from_core_and_samples(
                core_dir=Path(temp_dir) / "missing-core",
                samples_dir=Path(temp_dir) / "missing-samples",
            )

        self.assertEqual(runtime.languages(), [])
        self.assertEqual(runtime.t("button.save", language="en", default="Save"), "Save")

    def test_sample_fallback_when_core_missing(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            samples_dir = temp_path / "samples"
            samples_dir.mkdir()

            pack_path = samples_dir / "en.language-pack.sample.json"
            pack_path.write_text(
                json.dumps(
                    {
                        "manifest": {"language_code": "en"},
                        "ui": {"button.save": "Sample Save"},
                        "messages": {},
                        "feedback": {},
                        "glossary": {},
                    }
                ),
                encoding="utf-8",
            )

            runtime = MinimalLanguageRuntime.from_core_and_samples(
                core_dir=temp_path / "core",
                samples_dir=samples_dir,
            )

        self.assertEqual(runtime.lookup_source("button.save", language="en"), ("sample", "en"))
        self.assertEqual(runtime.t("button.save", language="en"), "Sample Save")

    def test_core_overrides_sample_when_both_exist(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            core_dir = temp_path / "core"
            samples_dir = temp_path / "samples"
            core_dir.mkdir()
            samples_dir.mkdir()

            sample_pack = {
                "manifest": {"language_code": "en"},
                "ui": {"button.save": "Sample Save"},
                "messages": {},
                "feedback": {},
                "glossary": {},
            }
            core_pack = {
                "manifest": {"language_code": "en"},
                "ui": {"button.save": "Core Save"},
                "messages": {},
                "feedback": {},
                "glossary": {},
            }

            (samples_dir / "en.language-pack.sample.json").write_text(
                json.dumps(sample_pack),
                encoding="utf-8",
            )
            (core_dir / "en.language-pack.json").write_text(
                json.dumps(core_pack),
                encoding="utf-8",
            )

            runtime = MinimalLanguageRuntime.from_core_and_samples(
                core_dir=core_dir,
                samples_dir=samples_dir,
            )

        self.assertEqual(runtime.lookup_source("button.save", language="en"), ("core", "en"))
        self.assertEqual(runtime.t("button.save", language="en"), "Core Save")

    def test_invalid_json_pack_is_ignored(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            invalid_pack = temp_path / "bad.language-pack.sample.json"
            invalid_pack.write_text("{ invalid json", encoding="utf-8")

            runtime = MinimalLanguageRuntime.from_directory(temp_path)

        self.assertEqual(runtime.languages(), [])

    def test_load_pack_safely_returns_none_for_invalid_pack(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            invalid_pack = temp_path / "bad.language-pack.sample.json"
            invalid_pack.write_text("{ invalid json", encoding="utf-8")

            self.assertIsNone(load_pack_safely(invalid_pack))

    def test_load_pack_reads_manifest_language_code(self) -> None:
        sample = default_core_language_pack_dir() / "en.language-pack.json"
        pack = load_pack(sample)

        self.assertEqual(pack.language_code, "en")
        self.assertEqual(pack.source, "core")
        self.assertIn("button.save", pack.translations)

    def test_custom_pack_directory_legacy_loader(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            pack_path = temp_path / "xx.language-pack.sample.json"
            pack_path.write_text(
                json.dumps(
                    {
                        "manifest": {"language_code": "xx"},
                        "ui": {"button.save": "Save XX"},
                        "messages": {},
                        "feedback": {},
                        "glossary": {},
                    }
                ),
                encoding="utf-8",
            )

            runtime = MinimalLanguageRuntime.from_directory(temp_path)

        self.assertEqual(runtime.languages(), ["xx"])
        self.assertEqual(runtime.t("button.save", language="xx"), "Save XX")


if __name__ == "__main__":
    unittest.main(verbosity=2)
