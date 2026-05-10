from pathlib import Path

path = Path(".gitignore")
text = path.read_text(encoding="utf-8") if path.exists() else ""

entries = [
    "",
    "# Local generated/trash data",
    "data/trash/",
]

for entry in entries:
    if entry and entry not in text:
        text += ("\n" if text and not text.endswith("\n") else "") + entry + "\n"

path.write_text(text, encoding="utf-8")
print("OK: data/trash ignored.")
