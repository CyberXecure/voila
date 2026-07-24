from __future__ import annotations

from pathlib import Path

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"

if not web_app.exists():
    raise SystemExit("FAILED_WEB_APP_MISSING=" + str(web_app))

text = web_app.read_text(encoding="utf-8", errors="replace")

marker = "VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION"
if marker in text:
    print("V0.8.77 patch already applied")
    raise SystemExit(0)

append_block = r'''

# VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_START
def _voila_v0877_safe_identifier(value, max_len=160):
    text = str(value or "").strip()
    if not text or len(text) > max_len:
        return ""
    allowed = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-"
    if any(ch not in allowed for ch in text):
        return ""
    if text.startswith(".") or ".." in text:
        return ""
    return text


def _voila_v0877_trimmed_text(value, max_len):
    text = str(value or "").strip()
    if len(text) > max_len:
        return None
    return text


def _voila_v0877_safe_output_dir(course_id):
    from pathlib import Path as _VoilaV0877Path

    safe_course_id = _voila_v0877_safe_identifier(course_id)
    if not safe_course_id:
        return None

    repo_root = _VoilaV0877Path(__file__).resolve().parents[2]
    output_root = (repo_root / "data" / "output").resolve()
    candidate = (output_root / safe_course_id).resolve()

    try:
        candidate.relative_to(output_root)
    except Exception:
        return None

    if not candidate.exists() or not candidate.is_dir():
        return None

    return candidate


def _voila_v0877_read_json(path):
    import json as _voila_v0877_json

    try:
        if not path.exists() or not path.is_file():
            return None
        payload = _voila_v0877_json.loads(path.read_text(encoding="utf-8"))
        if isinstance(payload, dict):
            return payload
    except Exception:
        return None
    return None


def _voila_v0877_write_json_replace(path, payload):
    import json as _voila_v0877_json

    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(_voila_v0877_json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp_path.replace(path)


def _voila_v0877_load_visual_payload(output_dir):
    visual_dir = output_dir / "formula_visual_evidence"
    validated_path = visual_dir / "visual_items.bbox.validated.json"
    candidate_path = visual_dir / "visual_items.bbox.with-ocrmath-candidates.json"

    payload = _voila_v0877_read_json(validated_path)
    source_path = validated_path

    if not isinstance(payload, dict):
        payload = _voila_v0877_read_json(candidate_path)
        source_path = candidate_path

    if not isinstance(payload, dict):
        return None, None

    items = payload.get("items")
    if not isinstance(items, list):
        return None, None

    return payload, source_path


def _voila_v0877_count_decisions(items):
    counts = {
        "accepted_count": 0,
        "edited_count": 0,
        "ignored_count": 0,
        "pending_count": 0,
        "ready_for_study_count": 0,
    }

    for item in items:
        if not isinstance(item, dict):
            continue

        decision = str(item.get("user_decision") or "pending").strip()
        if decision == "accept":
            counts["accepted_count"] += 1
        elif decision == "edit":
            counts["edited_count"] += 1
        elif decision == "ignore":
            counts["ignored_count"] += 1
        else:
            counts["pending_count"] += 1

        if item.get("ready_for_study") is True:
            counts["ready_for_study_count"] += 1

    return counts


async def _voila_v0877_parse_save_form(request):
    from urllib.parse import parse_qs as _voila_v0877_parse_qs

    body = await request.body()
    if len(body) > 65536:
        return None, "Formularul este prea mare."

    try:
        parsed = _voila_v0877_parse_qs(
            body.decode("utf-8", errors="replace"),
            keep_blank_values=True,
            max_num_fields=12,
        )
    except Exception:
        return None, "Formularul nu poate fi citit."

    def one(name, max_len):
        values = parsed.get(name, [""])
        value = values[0] if values else ""
        value = str(value or "").strip()
        if len(value) > max_len:
            return None
        return value

    course_id = _voila_v0877_safe_identifier(one("course_id", 160))
    item_id = _voila_v0877_safe_identifier(one("item_id", 160))
    decision = one("decision", 20)
    corrected = _voila_v0877_trimmed_text(one("user_corrected_text", 4000), 4000)
    explanation = _voila_v0877_trimmed_text(one("user_explanation", 4000), 4000)

    if corrected is None or explanation is None:
        return None, "Textul introdus este prea lung."

    form = {
        "course_id": course_id,
        "item_id": item_id,
        "decision": str(decision or "").strip(),
        "user_corrected_text": corrected or "",
        "user_explanation": explanation or "",
    }

    return form, ""


def _voila_v0877_html_result(message, status_code=200, course_id=""):
    from starlette.responses import HTMLResponse as _VoilaV0877HTMLResponse

    safe_message = _voila_v0874_escape(message)
    safe_course_id = _voila_v0877_safe_identifier(course_id)
    link = ""
    if safe_course_id:
        link = (
            '<p><a href="/review-document/'
            + _voila_v0874_escape(safe_course_id)
            + '">Înapoi la Revizuire document</a></p>'
        )

    html = (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<title>Validare vizuală</title></head><body>"
        "<main><h1>Validare vizuală</h1><p>"
        + safe_message
        + "</p>"
        + link
        + "</main></body></html>"
    )

    return _VoilaV0877HTMLResponse(content=html, status_code=status_code)


from starlette.requests import Request as _VoilaV0877Request


@app.post("/review-document/visual-validation/save")
async def _voila_v0877_review_document_visual_validation_save_action(request: _VoilaV0877Request):
    form, form_error = await _voila_v0877_parse_save_form(request)
    if form is None:
        return _voila_v0877_html_result(form_error or "Formular invalid.", status_code=400)

    course_id = form["course_id"]
    item_id = form["item_id"]
    decision = form["decision"]

    if not course_id or not item_id:
        return _voila_v0877_html_result("Course ID sau item ID invalid.", status_code=400)

    if decision not in {"accept", "edit", "ignore"}:
        return _voila_v0877_html_result("Decizie invalidă.", status_code=400, course_id=course_id)

    output_dir = _voila_v0877_safe_output_dir(course_id)
    if output_dir is None:
        return _voila_v0877_html_result("Nu găsesc cursul local pentru validare.", status_code=404, course_id=course_id)

    payload, source_path = _voila_v0877_load_visual_payload(output_dir)
    if payload is None or source_path is None:
        return _voila_v0877_html_result("Nu există elemente vizuale pregătite pentru validare.", status_code=404, course_id=course_id)

    items = payload.get("items")
    target_item = None
    for item in items:
        if isinstance(item, dict) and str(item.get("item_id") or "").strip() == item_id:
            target_item = item
            break

    if target_item is None:
        return _voila_v0877_html_result("Elementul vizual nu a fost găsit.", status_code=404, course_id=course_id)

    crop_exists = target_item.get("crop_exists") is True
    crop_path = str(target_item.get("crop_path") or "").strip()
    candidate_text = str(target_item.get("ocr_math_candidate_text") or "").strip()
    corrected_text = form["user_corrected_text"]
    explanation_text = form["user_explanation"]

    if decision == "accept":
        if not crop_exists or not crop_path or not candidate_text:
            return _voila_v0877_html_result("Acceptarea necesită crop și text detectat.", status_code=400, course_id=course_id)
        target_item["user_decision"] = "accept"
        target_item["ocr_math_status"] = "validated_by_user"
        target_item["ready_for_study"] = True
        target_item["user_corrected_text"] = ""
        target_item["user_explanation"] = explanation_text

    elif decision == "edit":
        if not crop_exists or not crop_path or not corrected_text:
            return _voila_v0877_html_result("Corectarea necesită crop și text corectat.", status_code=400, course_id=course_id)
        target_item["user_decision"] = "edit"
        target_item["ocr_math_status"] = "validated_by_user"
        target_item["ready_for_study"] = True
        target_item["user_corrected_text"] = corrected_text
        target_item["user_explanation"] = explanation_text

    else:
        target_item["user_decision"] = "ignore"
        target_item["ocr_math_status"] = "not_applicable"
        target_item["ready_for_study"] = False
        target_item["user_corrected_text"] = ""
        target_item["user_explanation"] = explanation_text

    visual_dir = output_dir / "formula_visual_evidence"
    validated_path = visual_dir / "visual_items.bbox.validated.json"
    summary_path = visual_dir / "visual_items.bbox.validation-summary.json"

    payload["items"] = items
    _voila_v0877_write_json_replace(validated_path, payload)

    counts = _voila_v0877_count_decisions(items)
    summary = {
        "schema_version": "v0.8.77",
        "course_id": course_id,
        "updated_item_id": item_id,
        "decision": decision,
        "source_visual_items_path": source_path.name,
        "validated_visual_items_path": validated_path.name,
        "clean_study_write_performed": False,
        **counts,
    }
    _voila_v0877_write_json_replace(summary_path, summary)

    return _voila_v0877_html_result("DECIZIE_SALVATA=PASS", status_code=200, course_id=course_id)
# VOILA_V0_8_77_REVIEW_DOCUMENT_VISUAL_VALIDATION_SAVE_ACTION_END
'''

web_app.write_text(text.rstrip() + append_block + "\n", encoding="utf-8")
print("V0.8.77 patch applied to services/api/web_app.py")
