from __future__ import annotations

from pathlib import Path

repo = Path(".").resolve()
web_app = repo / "services" / "api" / "web_app.py"

if not web_app.exists():
    raise SystemExit("FAILED_WEB_APP_MISSING=" + str(web_app))

text = web_app.read_text(encoding="utf-8", errors="replace")

marker = "VOILA_V0_8_78_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS"
if marker in text:
    print("V0.8.78 patch already applied")
    raise SystemExit(0)

old = '''            '<p><strong>Eligibilitate Clean Study:</strong> '
            f'{_voila_v0874_escape(ready_label)}</p>'
            '</article>'
        )
'''

new = '''            '<p><strong>Eligibilitate Clean Study:</strong> '
            f'{_voila_v0874_escape(ready_label)}</p>'
            '<div class="review-document-visual-validation-controls" '
            'data-voila-marker="VOILA_V0_8_78_REVIEW_DOCUMENT_VISUAL_VALIDATION_FORM_CONTROLS">'
            '<form method="post" action="/review-document/visual-validation/save">'
            f'<input type="hidden" name="course_id" value="{_voila_v0874_escape(safe_course_id)}">'
            f'<input type="hidden" name="item_id" value="{_voila_v0874_escape(str(item.get("item_id") or ""))}">'
            '<input type="hidden" name="decision" value="accept">'
            f'<input type="hidden" name="user_explanation" value="{_voila_v0874_escape(explanation_text)}">'
            '<button type="submit">Acceptă</button>'
            '</form>'
            '<form method="post" action="/review-document/visual-validation/save">'
            f'<input type="hidden" name="course_id" value="{_voila_v0874_escape(safe_course_id)}">'
            f'<input type="hidden" name="item_id" value="{_voila_v0874_escape(str(item.get("item_id") or ""))}">'
            '<input type="hidden" name="decision" value="edit">'
            '<label>Corectare</label>'
            f'<textarea name="user_corrected_text" rows="3">{_voila_v0874_escape(corrected_text or candidate_text)}</textarea>'
            '<label>Explicație pe înțeles</label>'
            f'<textarea name="user_explanation" rows="3">{_voila_v0874_escape(explanation_text)}</textarea>'
            '<button type="submit">Salvează corectarea</button>'
            '</form>'
            '<form method="post" action="/review-document/visual-validation/save">'
            f'<input type="hidden" name="course_id" value="{_voila_v0874_escape(safe_course_id)}">'
            f'<input type="hidden" name="item_id" value="{_voila_v0874_escape(str(item.get("item_id") or ""))}">'
            '<input type="hidden" name="decision" value="ignore">'
            f'<input type="hidden" name="user_explanation" value="{_voila_v0874_escape(explanation_text)}">'
            '<button type="submit">Ignoră</button>'
            '</form>'
            '</div>'
            '</article>'
        )
'''

if old not in text:
    raise SystemExit("FAILED_V0878_PATCH_TARGET_NOT_FOUND")

text = text.replace(old, new, 1)

old_doc_phrase = '<p class="muted">Secțiune read-only. Nu salvează decizii și nu modifică lecția.</p>'
new_doc_phrase = '<p class="muted">Deciziile se salvează local prin acțiuni explicite. Nu modifică direct lecția.</p>'

if old_doc_phrase not in text:
    raise SystemExit("FAILED_V0878_HEADER_TARGET_NOT_FOUND")

text = text.replace(old_doc_phrase, new_doc_phrase, 1)

web_app.write_text(text.rstrip() + "\n", encoding="utf-8")
print("V0.8.78 patch applied to services/api/web_app.py")
