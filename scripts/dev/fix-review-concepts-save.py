from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Ensure Form import exists.
text = re.sub(
    r"from fastapi import ([^\n]+)",
    lambda m: (
        "from fastapi import "
        + ", ".join(
            dict.fromkeys(
                [part.strip() for part in m.group(1).split(",")] + ["Form"]
            )
        )
    ),
    text,
    count=1,
)

new_route = r'''
@app.post("/review-concepts/save")
def save_review_concept(
    pdf: str = Form(...),
    lesson_id: str = Form(...),
    title: str = Form(...),
):
    from datetime import datetime, timezone
    from fastapi.responses import HTMLResponse, RedirectResponse
    from urllib.parse import quote
    import traceback

    try:
        pdf_name = _safe_pdf_name(pdf)
        output_dir = _output_dir_for_pdf_name(pdf_name)
        overrides_path = output_dir / "study_concept_overrides.json"

        payload = _load_json_file(
            overrides_path,
            {
                "version": "1.0",
                "overrides": {},
            },
        )

        clean_title = str(title or "").strip()

        if not clean_title:
            return HTMLResponse(
                "<h1>Empty title</h1><p>Concept title cannot be empty.</p>",
                status_code=400,
            )

        payload.setdefault("overrides", {})[lesson_id] = {
            "concept_title": clean_title,
            "lesson_title": clean_title,
            "source": "manual_ui",
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }

        _save_json_file(overrides_path, payload)

        try:
            from ocr_corrections_engine import apply_title_overrides
            apply_title_overrides(output_dir)
        except Exception:
            # Keep override saved even if rebuild/update fails.
            pass

        return RedirectResponse(
            "/review-concepts?pdf=" + quote(pdf_name),
            status_code=303,
        )

    except Exception:
        error = traceback.format_exc()
        return HTMLResponse(
            f"""
            <h1>Save title override failed</h1>
            <p>The correction was not saved because the server raised an exception.</p>
            <pre style="white-space: pre-wrap; background:#111; color:#f6ead7; padding:16px; border-radius:12px;">{error}</pre>
            <p><a href="/">Back to Voila</a></p>
            """,
            status_code=500,
        )
'''

start = text.find('@app.post("/review-concepts/save")')

if start == -1:
    text += "\n\n" + new_route
else:
    end = text.find("\n\n@app.", start + 1)
    if end == -1:
        end = len(text)

    text = text[:start] + new_route + text[end:]

path.write_text(text, encoding="utf-8")

print("OK: review-concepts save route fixed.")
