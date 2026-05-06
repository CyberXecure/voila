from pathlib import Path
import re

path = Path("services/api/crop_editor_app.py")
text = path.read_text(encoding="utf-8")

helper = r'''

def item_output_path(pdf: Path, item: dict) -> Path:
    raw_path = item.get("path")

    if raw_path:
        return Path(raw_path)

    rel = item.get("relative_path")

    if rel:
        output_path = OUTPUT_DIR / pdf.stem / "figures_hybrid" / rel
        item["path"] = str(output_path)
        return output_path

    raise KeyError("Figure item has neither 'path' nor 'relative_path'.")
'''

if "def item_output_path" not in text:
    text = text.replace(
        "def clamp_rect(rect: list[float], page: fitz.Page) -> list[float]:",
        helper + "\n\ndef clamp_rect(rect: list[float], page: fitz.Page) -> list[float]:",
    )

# Fix rerender_crop output path.
text = text.replace(
    '''    output_path = Path(item["path"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
''',
    '''    output_path = item_output_path(pdf, item)
    output_path.parent.mkdir(parents=True, exist_ok=True)
'''
)

# Fix editor mtime path access.
text = text.replace(
    '''        mtime = Path(item["path"]).stat().st_mtime if Path(item["path"]).exists() else time.time()
''',
    '''        image_path = item_output_path(pdf_path, item)
        mtime = image_path.stat().st_mtime if image_path.exists() else time.time()
'''
)

# Make load_manifest normalize missing path values.
text = text.replace(
    '''    return json.loads(manifest_path.read_text(encoding="utf-8"))
''',
    '''    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    for item in manifest.get("figure_crops", []):
        if "path" not in item and item.get("relative_path"):
            item["path"] = str(OUTPUT_DIR / pdf.stem / "figures_hybrid" / item["relative_path"])

    return manifest
'''
)

path.write_text(text, encoding="utf-8")

print("OK: crop_editor_app.py now supports manifests without item['path'].")
