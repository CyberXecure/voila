from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

if "def ensure_crop_editor_running" not in text:
    insert = r'''
def ensure_crop_editor_running() -> None:
    import subprocess
    import sys
    import time
    import urllib.request

    url = "http://127.0.0.1:8790/"

    try:
        urllib.request.urlopen(url, timeout=1)
        return
    except Exception:
        pass

    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "crop_editor_app:app",
            "--app-dir",
            str(PROJECT_ROOT / "services" / "api"),
            "--host",
            "127.0.0.1",
            "--port",
            "8790",
            "--log-level",
            "info",
        ],
        cwd=str(PROJECT_ROOT),
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )

    for _ in range(20):
        try:
            urllib.request.urlopen(url, timeout=1)
            return
        except Exception:
            time.sleep(0.5)


'''

    marker = "app = FastAPI("
    pos = text.find(marker)

    if pos == -1:
        raise SystemExit("Could not find FastAPI app marker.")

    text = text[:pos] + insert + "\n" + text[pos:]

if '@app.get("/edit-crops")' not in text:
    route = r'''

@app.get("/edit-crops")
def edit_crops(pdf: str = ""):
    from fastapi.responses import RedirectResponse
    from urllib.parse import quote

    ensure_crop_editor_running()

    if pdf:
        return RedirectResponse(f"http://127.0.0.1:8790/?pdf={quote(pdf)}")

    return RedirectResponse("http://127.0.0.1:8790/")
'''

    text += route

path.write_text(text, encoding="utf-8")
print("OK: web_app.py now auto-starts Crop Editor from /edit-crops")
