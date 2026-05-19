import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
CORE = ROOT / "language-packs" / "core"

PLANNED_ERROR_KEYS = {
    "error.missing_pdf_name",
    "error.no_ocr_pages_found",
    "error.course_html_not_found",
    "error.figures_html_not_found",
    "error.page_not_found",
    "error.pdf_not_found",
    "error.not_found",
    "error.only_pdf_files_supported",
    "error.save_title_override_failed",
    "error.save_ocr_text_failed",
}

PLANNED_STATUS_KEYS = {
    "status.rebuild_complete",
    "status.rebuild_failed",
}

PLANNED_MESSAGE_KEYS = {
    "message.run_ocr_first",
    "message.no_log_file_found_yet",
}

ALL_PLANNED_KEYS = PLANNED_ERROR_KEYS | PLANNED_STATUS_KEYS | PLANNED_MESSAGE_KEYS


def load_messages(lang: str) -> dict[str, str]:
    path = CORE / f"{lang}.language-pack.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("messages")
    if not isinstance(messages, dict):
        raise AssertionError(f"{path} has no messages object")
    return messages


class UiErrorStatusCoreKeyTests(unittest.TestCase):
    def test_ro_and_en_have_all_planned_keys(self) -> None:
        for lang in ("ro", "en"):
            messages = load_messages(lang)
            missing = sorted(ALL_PLANNED_KEYS - set(messages))
            self.assertEqual([], missing, f"{lang} missing planned keys")

    def test_ro_and_en_planned_key_sets_match(self) -> None:
        ro = load_messages("ro")
        en = load_messages("en")

        ro_keys = {key for key in ro if key in ALL_PLANNED_KEYS}
        en_keys = {key for key in en if key in ALL_PLANNED_KEYS}

        self.assertEqual(ro_keys, en_keys)

    def test_planned_values_are_non_empty_strings(self) -> None:
        for lang in ("ro", "en"):
            messages = load_messages(lang)
            for key in sorted(ALL_PLANNED_KEYS):
                value = messages.get(key)
                self.assertIsInstance(value, str, f"{lang}:{key} must be a string")
                self.assertTrue(value.strip(), f"{lang}:{key} must not be empty")

    def test_expected_representative_values(self) -> None:
        ro = load_messages("ro")
        en = load_messages("en")

        self.assertEqual("Nume PDF lipsă", ro["error.missing_pdf_name"])
        self.assertEqual("Missing PDF name", en["error.missing_pdf_name"])

        self.assertEqual("Nu au fost găsite pagini OCR", ro["error.no_ocr_pages_found"])
        self.assertEqual("No OCR pages found", en["error.no_ocr_pages_found"])

        self.assertEqual("Reconstruire completă", ro["status.rebuild_complete"])
        self.assertEqual("Rebuild complete", en["status.rebuild_complete"])

        self.assertEqual("Rulează OCR mai întâi", ro["message.run_ocr_first"])
        self.assertEqual("Run OCR first", en["message.run_ocr_first"])


if __name__ == "__main__":
    unittest.main(verbosity=2)