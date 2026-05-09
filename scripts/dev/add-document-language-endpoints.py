from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if '@app.get("/document-language")' not in text:
    block = r'''

@app.get("/document-language")
def voila_get_document_language(pdf: str = ""):
    from fastapi.responses import JSONResponse
    import document_language as dl

    return JSONResponse(
        dl.get_document_language(PROJECT_ROOT, pdf)
    )


@app.post("/document-language")
async def voila_set_document_language(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import document_language as dl

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    pdf = str(payload.get("pdf") or "")
    language = str(payload.get("language") or payload.get("document_language") or "auto")

    return JSONResponse(
        dl.set_document_language(PROJECT_ROOT, pdf, language)
    )
'''
    text = text.rstrip() + "\n\n" + block + "\n"

path.write_text(text, encoding="utf-8")
print("OK: document-language endpoints added.")
