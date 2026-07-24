from __future__ import annotations

from pathlib import Path

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"

if not web_app.exists():
    raise SystemExit("FAILED_WEB_APP_MISSING=" + str(web_app))

text = web_app.read_text(encoding="utf-8", errors="replace")

marker = "VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL"
if marker in text:
    print("V0.8.82 patch already applied")
    raise SystemExit(0)

append_block = r'''

# VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_START
def _voila_v0882_clean_study_refresh_control_html(course_id):
    from html import escape as _voila_v0882_escape

    safe_course_id = _voila_v0877_safe_identifier(course_id)
    if not safe_course_id:
        return ""

    escaped_course_id = _voila_v0882_escape(safe_course_id, quote=True)
    clean_study_href = "/study-clean-preview/" + escaped_course_id

    return (
        '<section id="review-document-clean-study-refresh-control" '
        'data-voila-clean-study-refresh-control="1" '
        'style="margin-top: 1rem; padding: 1rem; border: 1px solid rgba(148,163,184,.35); border-radius: 14px;">'
        '<h2>Actualizează lecția curată</h2>'
        '<p>Elementele acceptate și corectate pot intra în lecție. '
        'Elementele ignorate sau încă nevalidate rămân în afara lecției.</p>'
        '<p>Actualizarea este locală. Nu modifică documentul original, nu scrie Progress, '
        'nu publică și nu partajează nimic.</p>'
        '<form method="post" action="/review-document/visual-validation/refresh-clean-study-preview" '
        'data-voila-clean-study-refresh-form="1">'
        '<input type="hidden" name="course_id" value="' + escaped_course_id + '">'
        '<button type="submit">Actualizează lecția curată</button>'
        '</form>'
        '<p><a href="' + clean_study_href + '">Deschide lecția curată</a></p>'
        '</section>'
    )


@app.middleware("http")
async def _voila_v0882_review_document_clean_study_refresh_ui_control_middleware(request, call_next):
    response = await call_next(request)

    try:
        if request.method.upper() != "GET":
            return response

        path = str(request.url.path or "")
        if path != "/review-document" and not path.startswith("/review-document/"):
            return response

        if getattr(response, "status_code", 0) != 200:
            return response

        content_type = str(response.headers.get("content-type") or "")
        if "text/html" not in content_type.lower():
            return response

        chunks = []
        async for chunk in response.body_iterator:
            chunks.append(chunk if isinstance(chunk, bytes) else bytes(chunk))

        body = b"".join(chunks)
        html = body.decode("utf-8", errors="replace")

        if "review-document-clean-study-refresh-control" in html:
            from starlette.responses import HTMLResponse as _VoilaV0882HTMLResponse
            return _VoilaV0882HTMLResponse(content=html, status_code=response.status_code)

        if "review-document-visual-validation-readonly-ui" not in html:
            from starlette.responses import HTMLResponse as _VoilaV0882HTMLResponse
            return _VoilaV0882HTMLResponse(content=html, status_code=response.status_code)

        course_id = _voila_v0874_course_id_from_review_request(request)
        course_id = _voila_v0877_safe_identifier(course_id)
        control = _voila_v0882_clean_study_refresh_control_html(course_id)
        if not control:
            from starlette.responses import HTMLResponse as _VoilaV0882HTMLResponse
            return _VoilaV0882HTMLResponse(content=html, status_code=response.status_code)

        if "</main>" in html:
            html = html.replace("</main>", control + "</main>", 1)
        elif "</body>" in html:
            html = html.replace("</body>", control + "</body>", 1)
        else:
            html = html + control

        from starlette.responses import HTMLResponse as _VoilaV0882HTMLResponse
        return _VoilaV0882HTMLResponse(content=html, status_code=response.status_code)
    except Exception:
        return response
# VOILA_V0_8_82_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_UI_CONTROL_END
'''

web_app.write_text(text.rstrip() + append_block + "\n", encoding="utf-8")
print("V0.8.82 patch applied to services/api/web_app.py")
