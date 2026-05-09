from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Add small static file route.
if '@app.get("/voila-static/{filename}")' not in text:
    block = r'''

@app.get("/voila-static/{filename}")
def voila_static_file(filename: str):
    from fastapi.responses import Response

    safe_name = Path(str(filename or "")).name
    static_path = PROJECT_ROOT / "services" / "api" / "static" / safe_name

    if not static_path.exists() or not static_path.is_file():
        return Response("Not found", status_code=404)

    suffix = static_path.suffix.lower()

    if suffix == ".js":
        media_type = "text/javascript; charset=utf-8"
    elif suffix == ".css":
        media_type = "text/css; charset=utf-8"
    else:
        media_type = "text/plain; charset=utf-8"

    return Response(
        static_path.read_text(encoding="utf-8"),
        media_type=media_type,
    )
'''
    text = text.rstrip() + "\n\n" + block + "\n"

# 2. Add LanguageTool API endpoint.
if '@app.post("/check-ocr-languagetool")' not in text:
    block = r'''

@app.post("/check-ocr-languagetool")
async def voila_check_ocr_languagetool(request: _VoilaRequest):
    import ocr_languagetool as lt

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    result = lt.check_text(
        text=str(payload.get("text") or ""),
        language=str(payload.get("language") or "ro-RO"),
    )

    return _VoilaJSONResponse(result)
'''
    text = text.rstrip() + "\n\n" + block + "\n"

# 3. Inject CSS/JS only into Correct OCR Review page.
route_start = text.find("def voila_review_ocr_corrected(")
if route_start == -1:
    raise SystemExit("Nu găsesc ruta voila_review_ocr_corrected.")

head_close = text.find("</head>", route_start)
if head_close == -1:
    raise SystemExit("Nu găsesc </head> în ruta OCR review.")

include = '''  <link rel="stylesheet" href="/voila-static/ocr_review_monaco.css">
  <script defer src="/voila-static/ocr_review_monaco.js"></script>
'''

segment = text[route_start:head_close]

if "/voila-static/ocr_review_monaco.js" not in segment:
    text = text[:head_close] + include + text[head_close:]

path.write_text(text, encoding="utf-8")
print("OK: web_app.py wired to static Monaco assets and LanguageTool endpoint.")
