from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

new_block = r'''
def crop_editor_is_running() -> bool:
    import socket

    try:
        with socket.create_connection(("127.0.0.1", 8790), timeout=0.5):
            return True
    except OSError:
        return False


def ensure_crop_editor_running() -> None:
    import subprocess
    import sys
    import time

    if crop_editor_is_running():
        return

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

    for _ in range(30):
        if crop_editor_is_running():
            return
        time.sleep(0.5)
'''

# Replace old ensure function area if present.
start = text.find("def ensure_crop_editor_running()")
if start != -1:
    # If crop_editor_is_running was already inserted before it, include it in replacement.
    previous = text.rfind("\ndef crop_editor_is_running()", 0, start)
    if previous != -1:
        start = previous + 1

    end = text.find("\n\napp = FastAPI(", start)
    if end == -1:
        raise SystemExit("Could not find end of crop editor helper block.")

    text = text[:start] + new_block + "\n\n" + text[end + 2:]
else:
    marker = "app = FastAPI("
    pos = text.find(marker)
    if pos == -1:
        raise SystemExit("Could not find FastAPI marker.")
    text = text[:pos] + new_block + "\n\n" + text[pos:]


new_route = r'''
@app.get("/edit-crops")
def edit_crops(pdf: str = ""):
    from fastapi.responses import HTMLResponse, RedirectResponse
    from urllib.parse import quote

    ensure_crop_editor_running()

    if not crop_editor_is_running():
        return HTMLResponse(
            """
            <h1>Crop Editor did not start</h1>
            <p>Port 8790 is not responding. Start it manually:</p>
            <pre>.\.venv\Scripts\python.exe -m uvicorn crop_editor_app:app --app-dir .\services\api --host 127.0.0.1 --port 8790</pre>
            """,
            status_code=503,
        )

    if pdf:
        return RedirectResponse("http://127.0.0.1:8790/?pdf=" + quote(pdf))

    return RedirectResponse("http://127.0.0.1:8790/")
'''

route_start = text.find('@app.get("/edit-crops")')
if route_start != -1:
    route_end = text.find("\n\n@app.", route_start + 1)
    if route_end == -1:
        route_end = len(text)
    text = text[:route_start] + new_route + text[route_end:]
else:
    text += "\n\n" + new_route

path.write_text(text, encoding="utf-8")
print("OK: /edit-crops route replaced with stable TCP-based launcher.")
