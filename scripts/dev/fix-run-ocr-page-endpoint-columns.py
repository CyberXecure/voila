from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if 'columns = int(payload.get("columns") or 0)' not in text:
    text = text.replace(
'''    zoom = float(payload.get("zoom") or 3.0)
''',
'''    zoom = float(payload.get("zoom") or 3.0)
    columns = int(payload.get("columns") or 0)
'''
    )

if 'if columns > 1:' not in text:
    text = text.replace(
'''    ]

    try:
''',
'''    ]

    if columns > 1:
        cmd.extend(["--columns", str(columns)])

    try:
''',
        1
    )

path.write_text(text, encoding="utf-8")
print("OK: /run-ocr-page forwards columns to OCR script.")
