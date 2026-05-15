#!/usr/bin/env python3
"""
Tests for the minimal Voila! language pack runtime helper.

Scope:
- standard library only
- no application runtime import
- no UI integration
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
    default_language_pack_dir,
    load_pack,
    load_pack_safely,
    replace_placeholders,
)


class MinimalLanguageRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = create_minimal_language_runtime()

    def test_default_language_pack_dir_exists(self) -> None:
        self.assertTrue(default_language_pack_dir().exists())

    def test_languages_include_ro_and_en(self) -> None:
        self.assertIn("ro", self.runtime.languages())
        self.assertIn("en", self.runtime.languages())

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

    def test_unsupported_language_falls_back_to_en(self) -> None:
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

    def test_empty_directory_is_safe(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            runtime = MinimalLanguageRuntime.from_directory(Path(temp_dir))

        self.assertEqual(runtime.languages(), [])
        self.assertEqual(runtime.t("button.save", language="en", default="Save"), "Save")

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
        sample = default_language_pack_dir() / "en.language-pack.sample.json"
        pack = load_pack(sample)

        self.assertEqual(pack.language_code, "en")
        self.assertIn("button.save", pack.translations)

    def test_custom_pack_directory(self) -> None:
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
