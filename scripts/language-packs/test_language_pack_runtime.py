#!/usr/bin/env python3
"""
Tests for the isolated Voila! language pack runtime scaffold.

Scope:
- standard library only
- does not import the application runtime
- validates fallback and placeholder behavior for sample packs
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from language_pack_runtime import (  # noqa: E402
    apply_placeholders,
    create_default_runtime,
    default_samples_dir,
    load_language_pack,
)


class LanguagePackRuntimeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.runtime = create_default_runtime()

    def test_samples_dir_exists(self) -> None:
        self.assertTrue(default_samples_dir().exists())

    def test_available_languages_include_ro_and_en(self) -> None:
        self.assertIn("ro", self.runtime.available_languages())
        self.assertIn("en", self.runtime.available_languages())

    def test_translate_ro_lesson_progress(self) -> None:
        result = self.runtime.translate(
            "lesson.progress",
            language="ro",
            current=2,
            total=10,
        )
        self.assertEqual(result, "Lecția 2 din 10")

    def test_translate_en_lesson_progress(self) -> None:
        result = self.runtime.translate(
            "lesson.progress",
            language="en",
            current=2,
            total=10,
        )
        self.assertEqual(result, "Lesson 2 of 10")

    def test_unsupported_language_falls_back_to_english(self) -> None:
        result = self.runtime.translate("button.save", language="fr")
        self.assertEqual(result, "Save")

    def test_missing_key_uses_default(self) -> None:
        result = self.runtime.translate(
            "missing.example",
            language="ro",
            default="Fallback OK",
        )
        self.assertEqual(result, "Fallback OK")

    def test_missing_key_without_default_returns_key(self) -> None:
        result = self.runtime.translate("missing.example", language="ro")
        self.assertEqual(result, "missing.example")

    def test_count_placeholder_ro(self) -> None:
        result = self.runtime.translate(
            "message.items_processed",
            language="ro",
            count=3,
        )
        self.assertEqual(result, "Au fost procesate 3 elemente.")

    def test_count_placeholder_en(self) -> None:
        result = self.runtime.translate(
            "message.items_processed",
            language="en",
            count=3,
        )
        self.assertEqual(result, "Processed 3 items.")

    def test_field_placeholder_ro(self) -> None:
        result = self.runtime.translate(
            "error.field_required",
            language="ro",
            field="Titlu",
        )
        self.assertEqual(result, "Titlu este obligatoriu.")

    def test_field_placeholder_en(self) -> None:
        result = self.runtime.translate(
            "error.field_required",
            language="en",
            field="Title",
        )
        self.assertEqual(result, "Title is required.")

    def test_missing_placeholder_is_preserved(self) -> None:
        result = self.runtime.translate(
            "lesson.progress",
            language="en",
            current=2,
        )
        self.assertEqual(result, "Lesson 2 of {total}")

    def test_lookup_returns_none_for_missing_key_without_default(self) -> None:
        result = self.runtime.lookup("missing.example", language="ro")
        self.assertIsNone(result)

    def test_glossary_translation_ro(self) -> None:
        result = self.runtime.translate("term.lesson", language="ro")
        self.assertEqual(result, "lecție")

    def test_glossary_translation_en(self) -> None:
        result = self.runtime.translate("term.lesson", language="en")
        self.assertEqual(result, "lesson")

    def test_apply_placeholders_directly(self) -> None:
        result = apply_placeholders(
            "Lesson {current} of {total}",
            {"current": 1, "total": 5},
        )
        self.assertEqual(result, "Lesson 1 of 5")

    def test_load_language_pack_manifest(self) -> None:
        sample_path = default_samples_dir() / "en.language-pack.sample.json"
        pack = load_language_pack(sample_path)

        self.assertEqual(pack.language_code, "en")
        self.assertEqual(pack.manifest["language_code"], "en")
        self.assertIn("button.save", pack.translations)


if __name__ == "__main__":
    unittest.main(verbosity=2)
