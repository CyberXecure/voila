from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if '@app.post("/run-ocr-page")' not in text:
    block = r'''

@app.post("/run-ocr-page")
async def voila_run_ocr_page(request: _VoilaRequest):
    from fastapi.responses import JSONResponse
    import subprocess
    import sys

    try:
        payload = await request.json()
    except Exception:
        payload = {}

    pdf = str(payload.get("pdf") or "").strip()
    page = int(payload.get("page") or 1)
    psm = int(payload.get("psm") or 6)
    zoom = float(payload.get("zoom") or 3.0)

    if not pdf:
        return JSONResponse(
            {
                "ok": False,
                "message": "PDF lipsă.",
            },
            status_code=400,
        )

    script = PROJECT_ROOT / "scripts" / "dev" / "run-ocr-page.py"

    if not script.exists():
        return JSONResponse(
            {
                "ok": False,
                "message": f"Nu găsesc scriptul OCR: {script}",
            },
            status_code=500,
        )

    cmd = [
        sys.executable,
        str(script),
        "--pdf",
        pdf,
        "--page",
        str(page),
        "--lang",
        "auto",
        "--psm",
        str(psm),
        "--zoom",
        str(zoom),
    ]

    try:
        result = subprocess.run(
            cmd,
            cwd=str(PROJECT_ROOT),
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            timeout=240,
        )
    except subprocess.TimeoutExpired:
        return JSONResponse(
            {
                "ok": False,
                "message": "OCR a durat prea mult și a fost oprit.",
            },
            status_code=504,
        )
    except Exception as exc:
        return JSONResponse(
            {
                "ok": False,
                "message": "Eroare la pornirea OCR.",
                "error": str(exc),
            },
            status_code=500,
        )

    ok = result.returncode == 0

    return JSONResponse(
        {
            "ok": ok,
            "message": "OCR pagină finalizat." if ok else "OCR pagină a eșuat.",
            "returncode": result.returncode,
            "stdout": (result.stdout or "")[-4000:],
            "stderr": (result.stderr or "")[-4000:],
        },
        status_code=200 if ok else 500,
    )
'''
    text = text.rstrip() + "\n\n" + block + "\n"

path.write_text(text, encoding="utf-8")
print("OK: /run-ocr-page endpoint added.")
