from __future__ import annotations

from pathlib import Path

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"

if not web_app.exists():
    raise SystemExit("FAILED_WEB_APP_MISSING=" + str(web_app))

text = web_app.read_text(encoding="utf-8", errors="replace")

marker = "VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION"
if marker in text:
    print("V0.8.81 patch already applied")
    raise SystemExit(0)

append_block = r'''

# VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_START
def _voila_v0881_study_answer_for_visual_item(item):
    decision = str(item.get("user_decision") or "").strip()
    candidate = str(item.get("ocr_math_candidate_text") or "").strip()
    corrected = str(item.get("user_corrected_text") or "").strip()

    if decision == "edit":
        if not corrected:
            return ""
        return corrected

    if decision == "accept":
        if not candidate:
            return ""
        return candidate

    return ""


def _voila_v0881_prompt_for_visual_kind(kind, page):
    labels = {
        "formula": "Explică formula validată din document.",
        "figure": "Explică figura validată din document.",
        "diagram": "Explică diagrama validată din document.",
        "table": "Explică tabelul validat din document.",
        "symbol": "Explică simbolul validat din document.",
        "mixed": "Explică elementul vizual validat din document.",
        "unknown": "Explică elementul vizual validat din document.",
    }
    base = labels.get(str(kind or "").strip(), labels["unknown"])
    return f"{base} Sursa: pagina {page}."


def _voila_v0881_build_clean_study_payload(course_id, source_pdf, validated_path, items):
    clean_items = []
    excluded_items = []

    for item in items:
        if not isinstance(item, dict):
            excluded_items.append({"reason": "malformed_item"})
            continue

        item_id = str(item.get("item_id") or "").strip()
        decision = str(item.get("user_decision") or "pending").strip()
        ready = item.get("ready_for_study") is True
        crop_exists = item.get("crop_exists") is True
        crop_path = str(item.get("crop_path") or "").strip()
        page = item.get("page")
        kind = str(item.get("kind") or "unknown").strip() or "unknown"

        if not isinstance(page, int) or page < 1:
            excluded_items.append({
                "source_visual_item_id": item_id,
                "user_decision": decision or "pending",
                "ready_for_study": bool(ready),
                "reason": "invalid_page",
            })
            continue

        if not ready or decision not in {"accept", "edit"}:
            excluded_items.append({
                "source_visual_item_id": item_id,
                "user_decision": decision or "pending",
                "ready_for_study": bool(ready),
                "reason": "not_ready_or_not_accept_edit",
            })
            continue

        if not crop_exists or not crop_path:
            excluded_items.append({
                "source_visual_item_id": item_id,
                "user_decision": decision,
                "ready_for_study": bool(ready),
                "reason": "missing_crop",
            })
            continue

        answer = _voila_v0881_study_answer_for_visual_item(item)
        if not answer:
            excluded_items.append({
                "source_visual_item_id": item_id,
                "user_decision": decision,
                "ready_for_study": bool(ready),
                "reason": "missing_answer_text",
            })
            continue

        explanation = str(item.get("user_explanation") or "").strip()

        clean_items.append({
            "schema_version": "v0.8.81",
            "study_item_id": "visual-study-" + item_id,
            "source_visual_item_id": item_id,
            "source_pdf": source_pdf,
            "page": page,
            "kind": kind,
            "title": f"Element vizual validat — pagina {page}",
            "prompt": _voila_v0881_prompt_for_visual_kind(kind, page),
            "answer": answer,
            "explanation": explanation,
            "image": {
                "crop_path": crop_path,
                "alt": f"Element vizual validat din pagina {page}",
            },
            "learning_source": "validated_bbox_visual_item",
            "user_decision": decision,
            "ready_for_clean_study": True,
        })

    payload = {
        "schema_version": "v0.8.81",
        "course_id": course_id,
        "source_pdf": source_pdf,
        "source_visual_items_path": validated_path.name,
        "item_count": len(clean_items),
        "items": clean_items,
        "excluded_count": len(excluded_items),
        "excluded_items": excluded_items,
    }

    summary = {
        "schema_version": "v0.8.81",
        "course_id": course_id,
        "source_visual_items_path": validated_path.name,
        "clean_study_visual_items_path": "visual_items.clean-study.preview.json",
        "source_item_count": len(items),
        "clean_study_item_count": len(clean_items),
        "excluded_item_count": len(excluded_items),
        "accepted_count": sum(1 for item in clean_items if item.get("user_decision") == "accept"),
        "edited_count": sum(1 for item in clean_items if item.get("user_decision") == "edit"),
        "ignored_or_pending_excluded": len(excluded_items),
        "validated_visual_decisions_preserved": True,
        "study_route_changed": False,
        "progress_write_performed": False,
    }

    return payload, summary


async def _voila_v0881_parse_refresh_form(request):
    from urllib.parse import parse_qs as _voila_v0881_parse_qs

    body = await request.body()
    if len(body) > 8192:
        return "", "Formularul este prea mare."

    try:
        parsed = _voila_v0881_parse_qs(
            body.decode("utf-8", errors="replace"),
            keep_blank_values=True,
            max_num_fields=4,
        )
    except Exception:
        return "", "Formularul nu poate fi citit."

    values = parsed.get("course_id", [""])
    course_id = _voila_v0877_safe_identifier(values[0] if values else "")
    if not course_id:
        return "", "Course ID invalid."

    return course_id, ""


from starlette.requests import Request as _VoilaV0881Request


@app.post("/review-document/visual-validation/refresh-clean-study-preview")
async def _voila_v0881_review_document_clean_study_refresh_action(request: _VoilaV0881Request):
    course_id, form_error = await _voila_v0881_parse_refresh_form(request)
    if not course_id:
        return _voila_v0877_html_result(form_error or "Formular invalid.", status_code=400)

    output_dir = _voila_v0877_safe_output_dir(course_id)
    if output_dir is None:
        return _voila_v0877_html_result("Nu găsesc cursul local pentru actualizare.", status_code=404, course_id=course_id)

    visual_dir = output_dir / "formula_visual_evidence"
    validated_path = visual_dir / "visual_items.bbox.validated.json"
    clean_path = visual_dir / "visual_items.clean-study.preview.json"
    clean_summary_path = visual_dir / "visual_items.clean-study.preview-summary.json"

    payload = _voila_v0877_read_json(validated_path)
    if not isinstance(payload, dict):
        return _voila_v0877_html_result("Nu există decizii vizuale validate.", status_code=404, course_id=course_id)

    items = payload.get("items")
    if not isinstance(items, list):
        return _voila_v0877_html_result("Artifactul de validare este invalid.", status_code=400, course_id=course_id)

    source_pdf = str(payload.get("source_pdf") or "").strip()
    clean_payload, clean_summary = _voila_v0881_build_clean_study_payload(course_id, source_pdf, validated_path, items)

    _voila_v0877_write_json_replace(clean_path, clean_payload)
    _voila_v0877_write_json_replace(clean_summary_path, clean_summary)

    message = (
        "CLEAN_STUDY_REFRESH=PASS · Elemente adăugate în lecție: "
        + str(clean_summary["clean_study_item_count"])
        + " · Elemente rămase în afara lecției: "
        + str(clean_summary["excluded_item_count"])
    )

    return _voila_v0877_html_result(message, status_code=200, course_id=course_id)
# VOILA_V0_8_81_REVIEW_DOCUMENT_CLEAN_STUDY_REFRESH_ACTION_END
'''

web_app.write_text(text.rstrip() + append_block + "\n", encoding="utf-8")
print("V0.8.81 patch applied to services/api/web_app.py")
