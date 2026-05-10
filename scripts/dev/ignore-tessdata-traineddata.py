from pathlib import Path

path = Path(".gitignore")

text = path.read_text(encoding="utf-8") if path.exists() else ""

entries = [
    "",
    "# Local Tesseract language data",
    ".tessdata/*.traineddata",
    "!.tessdata/.gitkeep",
]

changed = False

for entry in entries:
    if entry and entry not in text:
        text += ("\n" if text and not text.endswith("\n") else "") + entry + "\n"
        changed = True

Path(".tessdata").mkdir(exist_ok=True)
Path(".tessdata/.gitkeep").write_text("", encoding="utf-8")

path.write_text(text, encoding="utf-8")

print("OK: .tessdata traineddata ignored, .gitkeep preserved.")
