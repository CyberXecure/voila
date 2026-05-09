from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

needle = '    corrected_text = oc.get_corrected_text(out_dir, page_number)\n'

replacement = '''    corrected_text = oc.get_corrected_text(out_dir, page_number)

    if not str(corrected_text or "").strip():
        try:
            import ocr_best_text as obt
            corrected_text = obt.get_best_page_text(out_dir, page_number)
        except Exception:
            pass
'''

if needle not in text:
    raise SystemExit("Nu găsesc linia corrected_text = oc.get_corrected_text(...). Nu modific web_app.py.")

if "import ocr_best_text as obt" not in text:
    text = text.replace(needle, replacement, 1)

path.write_text(text, encoding="utf-8")
print("OK: review-ocr-corrected now uses best OCR fallback when corrected text is empty.")
