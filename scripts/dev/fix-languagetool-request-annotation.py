from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

pattern = r'\n@app\.post\("/check-ocr-languagetool"\)[\s\S]*?(?=\n@app\.|\Z)'

replacement = r'''

@app.post("/check-ocr-languagetool")
async def voila_check_ocr_languagetool(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import ocr_languagetool as lt

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    try:
        result = lt.check_text(
            text=str(payload.get("text") or ""),
            language=str(payload.get("language") or "ro-RO"),
        )
    except Exception as exc:
        result = {
            "ok": False,
            "provider": "LanguageTool",
            "matches": [],
            "message": "Eroare internă la verificarea LanguageTool.",
            "error": str(exc),
        }

    return JSONResponse(result)
'''

text, count = re.subn(pattern, replacement, text, count=1)

if count != 1:
    raise SystemExit("Nu am găsit endpoint-ul /check-ocr-languagetool de înlocuit.")

path.write_text(text, encoding="utf-8")
print("OK: LanguageTool endpoint fixed with Request annotation.")
