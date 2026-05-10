from pathlib import Path

path = Path("services/api/lesson_tools.py")
text = path.read_text(encoding="utf-8")

if "def _natural_key(" not in text:
    marker = '''def build_lessons(output_dir: Path | str) -> list[dict]:
'''
    insert = r'''

def _natural_key(value: str):
    import re

    parts = re.split(r"(\d+)", str(value or "").lower())

    return [
        int(part) if part.isdigit() else part
        for part in parts
    ]


'''
    text = text.replace(marker, insert + marker, 1)

old = '''    return lessons
'''

new = '''    lessons.sort(
        key=lambda item: (
            _natural_key(item.get("lesson_id") or ""),
            _natural_key(item.get("title") or ""),
        )
    )

    return lessons
'''

if old in text and "lessons.sort(" not in text:
    text = text.replace(old, new, 1)

path.write_text(text, encoding="utf-8")
print("OK: Lessons natural sort added.")
