from __future__ import annotations

from pathlib import Path

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"

if not web_app.exists():
    raise SystemExit("FAILED_WEB_APP_MISSING=" + str(web_app))

text = web_app.read_text(encoding="utf-8", errors="replace")

marker = "VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI"
if marker in text:
    print("V0.8.74 patch already applied")
    raise SystemExit(0)

append_block = r'''

# VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_START
def _voila_v0874_escape(value):
    import html as _voila_v0874_html

    return _voila_v0874_html.escape(str(value or ""), quote=True)


def _voila_v0874_safe_course_id(value):
    text = str(value or "").strip()
    if not text or len(text) > 160:
        return ""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if any(ch not in allowed for ch in text):
        return ""
    if text.startswith(".") or ".." in text:
        return ""
    return text


def _voila_v0874_course_id_from_review_request(request):
    path = str(getattr(getattr(request, "url", None), "path", "") or "")
    query_params = getattr(request, "query_params", {}) or {}

    pdf_name = str(query_params.get("pdf", "") or "").strip()
    if pdf_name:
        pdf_name = pdf_name.replace("\\", "/").split("/")[-1]
        lower_pdf = pdf_name.lower()
        if lower_pdf.endswith(".pdf"):
            return _voila_v0874_safe_course_id(pdf_name[:-4])

    prefix = "/review-document/"
    if path.startswith(prefix):
        candidate = path[len(prefix):].strip("/").split("/")[0]
        return _voila_v0874_safe_course_id(candidate)

    return ""


def _voila_v0874_find_output_dir(course_id):
    if not course_id:
        return None

    finder = globals().get("_voila_v0852_find_course_output_dir")
    if callable(finder):
        try:
            output_dir = finder(course_id)
        except Exception:
            return None
        if output_dir:
            try:
                if output_dir.exists() and output_dir.is_dir():
                    return output_dir
            except Exception:
                return None

    return None


def _voila_v0874_status_label(item):
    decision = str(item.get("user_decision") or "pending").strip()
    status = str(item.get("ocr_math_status") or "").strip()

    if decision == "accept":
        return "Acceptat"
    if decision == "edit":
        return "Corectat"
    if decision == "ignore":
        return "Ignorat"
    if status == "pending_user_validation":
        return "În așteptare"
    if status == "validated_by_user":
        return "Validat"
    if status == "failed":
        return "Necesită verificare"
    return "În așteptare"


def _voila_v0874_kind_label(kind):
    labels = {
        "formula": "formulă",
        "figure": "figură",
        "diagram": "diagramă",
        "table": "tabel",
        "symbol": "simbol",
        "mixed": "mixt",
        "unknown": "necunoscut",
    }
    return labels.get(str(kind or "").strip(), "necunoscut")


def _voila_v0874_load_visual_validation_items(course_id):
    import json as _voila_v0874_json

    output_dir = _voila_v0874_find_output_dir(course_id)
    if output_dir is None:
        return []

    visual_dir = output_dir / "formula_visual_evidence"
    candidate_paths = [
        visual_dir / "visual_items.bbox.with-ocrmath-candidates.json",
        visual_dir / "visual_items.bbox.validated.json",
    ]

    payload = None
    for candidate_path in candidate_paths:
        try:
            if candidate_path.exists() and candidate_path.is_file():
                loaded = _voila_v0874_json.loads(candidate_path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    payload = loaded
                    break
        except Exception:
            payload = None

    if not isinstance(payload, dict):
        return []

    raw_items = payload.get("items")
    if not isinstance(raw_items, list):
        return []

    items = []
    for raw_item in raw_items[:24]:
        if isinstance(raw_item, dict):
            items.append(raw_item)

    return items


def _voila_v0874_visual_validation_readonly_section(course_id):
    safe_course_id = _voila_v0874_safe_course_id(course_id)
    items = _voila_v0874_load_visual_validation_items(safe_course_id)

    cards = []
    for index, item in enumerate(items, start=1):
        page = item.get("page")
        if not isinstance(page, int) or page < 1:
            page = "?"
        kind_label = _voila_v0874_kind_label(item.get("kind"))
        candidate_text = str(item.get("ocr_math_candidate_text") or "").strip()
        corrected_text = str(item.get("user_corrected_text") or "").strip()
        explanation_text = str(item.get("user_explanation") or "").strip()
        crop_exists = item.get("crop_exists") is True
        decision = str(item.get("user_decision") or "pending").strip()
        ready = item.get("ready_for_study") is True

        visible_text = corrected_text if decision == "edit" and corrected_text else candidate_text
        if not visible_text:
            visible_text = "Nu există încă text detectat pentru acest element."

        crop_label = "disponibilă pentru verificare" if crop_exists else "nu este disponibilă încă"
        ready_label = "Gata pentru lecție" if ready else "Nu intră încă în lecție"
        status_label = _voila_v0874_status_label(item)

        cards.append(
            '<article class="card review-document-visual-validation-card">'
            f'<h3>Element vizual {index}</h3>'
            '<p class="muted">'
            f'Sursa: pagina {_voila_v0874_escape(page)} · '
            f'Tip: {_voila_v0874_escape(kind_label)} · '
            f'Status: {_voila_v0874_escape(status_label)}'
            '</p>'
            '<p><strong>Imagine extrasă din document:</strong> '
            f'{_voila_v0874_escape(crop_label)}</p>'
            '<p><strong>Text detectat:</strong></p>'
            f'<pre class="review-document-visual-validation-text">{_voila_v0874_escape(visible_text)}</pre>'
            '<p><strong>Explicație pe înțeles:</strong> '
            f'{_voila_v0874_escape(explanation_text or "Nu este completată încă.")}</p>'
            '<p><strong>Eligibilitate Clean Study:</strong> '
            f'{_voila_v0874_escape(ready_label)}</p>'
            '</article>'
        )

    if not cards:
        cards.append(
            '<article class="card review-document-visual-validation-card">'
            '<p>Nu există încă formule sau imagini pregătite pentru verificare vizuală.</p>'
            '<p class="muted">Această secțiune va afișa elementele după pașii locali de bbox, crop și OCR Math pe crop.</p>'
            '</article>'
        )

    return (
        '<section id="review-document-visual-validation-readonly-ui" class="card">'
        '<h2>Formule și imagini de verificat</h2>'
        '<p class="muted">Secțiune read-only. Nu salvează decizii și nu modifică lecția.</p>'
        + "".join(cards)
        + '<details class="muted"><summary>Diagnostic tehnic</summary>'
        '<p>v0.8.74 afișează doar date existente din artifactele locale validate anterior. '
        'Coordonatele bbox, numele brute de fișiere și căile locale absolute nu sunt afișate în cardurile principale.</p>'
        '</details>'
        '</section>'
    )


@app.middleware("http")
async def _voila_v0874_review_document_visual_validation_readonly_ui_middleware(request, call_next):
    response = await call_next(request)

    try:
        method = str(getattr(request, "method", "") or "").upper()
        path = str(getattr(getattr(request, "url", None), "path", "") or "")
        content_type = str(response.headers.get("content-type", "") or "").lower()

        if method != "GET":
            return response
        if not (path == "/review-document" or path.startswith("/review-document/")):
            return response
        if "text/html" not in content_type:
            return response

        body = b""
        async for chunk in response.body_iterator:
            body += chunk

        html_text = body.decode("utf-8", errors="replace")
        if "review-document-visual-validation-readonly-ui" in html_text:
            return response.__class__(content=body, status_code=response.status_code, headers=dict(response.headers))

        course_id = _voila_v0874_course_id_from_review_request(request)
        section = _voila_v0874_visual_validation_readonly_section(course_id)

        if "</main>" in html_text:
            html_text = html_text.replace("</main>", section + "\n</main>", 1)
        elif "</body>" in html_text:
            html_text = html_text.replace("</body>", section + "\n</body>", 1)
        else:
            html_text = html_text + section

        from starlette.responses import Response as _VoilaV0874Response

        headers = dict(response.headers)
        headers.pop("content-length", None)
        headers.pop("content-encoding", None)

        return _VoilaV0874Response(
            content=html_text.encode("utf-8"),
            status_code=response.status_code,
            headers=headers,
            media_type="text/html",
        )
    except Exception:
        return response
# VOILA_V0_8_74_REVIEW_DOCUMENT_VISUAL_VALIDATION_READONLY_UI_END
'''

web_app.write_text(text.rstrip() + append_block + "\n", encoding="utf-8")
print("V0.8.74 patch applied to services/api/web_app.py")
