from pathlib import Path
import json
import unittest


ROOT = Path(__file__).resolve().parents[2]
RO_PATH = ROOT / "language-packs" / "core" / "ro.language-pack.json"
EN_PATH = ROOT / "language-packs" / "core" / "en.language-pack.json"

RO_EXPECTED = {
    "ui.upload_pdf": "Încarcă PDF",
    "ui.choose_file": "Alege fișier",
    "ui.generated": "Generat",
    "ui.source_mode": "Mod sursă",
    "ui.generate_course": "Generează curs",
    "ui.open_course": "Deschide cursul",
    "ui.figures": "Figuri",
    "ui.edit_crops": "Editează decupaje",
    "ui.study": "Studiază",
    "ui.review_weak": "Repetă punctele slabe",
    "ui.progress": "Progres",
    "ui.logs": "Jurnale",
    "ui.delete_from_library": "Șterge din bibliotecă",
}

EN_EXPECTED = {
    "ui.upload_pdf": "Upload PDF",
    "ui.choose_file": "Choose File",
    "ui.generated": "Generated",
    "ui.source_mode": "Source Mode",
    "ui.generate_course": "Generate course",
    "ui.open_course": "Open course",
    "ui.figures": "Figures",
    "ui.edit_crops": "Edit crops",
    "ui.study": "Study",
    "ui.review_weak": "Review weak",
    "ui.progress": "Progress",
    "ui.logs": "Logs",
    "ui.delete_from_library": "Delete from library",
}


def load_messages(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    messages = data.get("messages", {})
    if not isinstance(messages, dict):
        raise AssertionError(f"{path} messages section is not an object")
    return messages


def lookup_with_english_fallback(language: str, key: str):
    if language == "ro":
        messages = load_messages(RO_PATH)
    elif language == "en":
        messages = load_messages(EN_PATH)
    else:
        messages = {}

    if key in messages:
        return messages[key]

    return load_messages(EN_PATH).get(key)


class UiCoreKeyTests(unittest.TestCase):
    def test_ro_ui_core_keys_exist(self):
        messages = load_messages(RO_PATH)
        for key, value in RO_EXPECTED.items():
            self.assertEqual(messages.get(key), value)

    def test_en_ui_core_keys_exist(self):
        messages = load_messages(EN_PATH)
        for key, value in EN_EXPECTED.items():
            self.assertEqual(messages.get(key), value)

    def test_ro_and_en_have_same_ui_key_set(self):
        ro_messages = load_messages(RO_PATH)
        en_messages = load_messages(EN_PATH)

        ro_keys = {key for key in ro_messages if key.startswith("ui.")}
        en_keys = {key for key in en_messages if key.startswith("ui.")}

        self.assertEqual(ro_keys, en_keys)

    def test_unsupported_language_falls_back_to_english_ui_key(self):
        self.assertEqual(
            lookup_with_english_fallback("fr", "ui.upload_pdf"),
            "Upload PDF",
        )

    def test_missing_ui_key_returns_none(self):
        self.assertIsNone(
            lookup_with_english_fallback("ro", "ui.this_key_does_not_exist")
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
