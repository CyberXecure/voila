from pathlib import Path
import json
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path("services/api").resolve()))

from fastapi.testclient import TestClient
import web_app

course_id = "03-pag-30-34-vectori-trigonometrie"
pdf_name = course_id + ".pdf"
manifest_path = Path("data/output") / course_id / "formula_visual_evidence.manifest.json"

if not manifest_path.exists():
    raise SystemExit("FAILED_V0791_MANIFEST_MISSING")

manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
candidate_count = manifest.get("candidate_count")

client = TestClient(web_app.app)

formula_viewer_url = f"/owner/formula-visual-evidence/{quote(course_id, safe='')}/view"
course_tools_url = f"/course-tools?pdf={quote(pdf_name, safe='')}"
ocr_math_url = f"/owner/ocr-math-report/{quote(course_id, safe='')}/view"
ocr_review_url = f"/owner/ocr-review/{quote(course_id, safe='')}"

course_tools = client.get(course_tools_url)
ocr_math = client.get(ocr_math_url)
ocr_review = client.get(ocr_review_url)
formula_viewer = client.get(formula_viewer_url)

if course_tools.status_code != 200:
    raise SystemExit(f"FAILED_V0791_COURSE_TOOLS_STATUS={course_tools.status_code}")
if ocr_math.status_code != 200:
    raise SystemExit(f"FAILED_V0791_OCR_MATH_STATUS={ocr_math.status_code}")
if ocr_review.status_code != 200:
    raise SystemExit(f"FAILED_V0791_OCR_REVIEW_STATUS={ocr_review.status_code}")
if formula_viewer.status_code != 200:
    raise SystemExit(f"FAILED_V0791_FORMULA_VIEWER_STATUS={formula_viewer.status_code}")

course_tools_link_visible = formula_viewer_url in course_tools.text
course_tools_card_visible = "Formula Visual Evidence" in course_tools.text and "Candidați vizuali: 43" in course_tools.text
ocr_math_report_link_visible = formula_viewer_url in ocr_math.text and "Formula visual evidence" in ocr_math.text
ocr_review_link_visible = formula_viewer_url in ocr_review.text and "Formula visual evidence" in ocr_review.text

source = Path("services/api/web_app.py").read_text(encoding="utf-8")
required_markers = [
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_MATH_LINK_START",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_MATH_LINK_END",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_LINK_START",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_LINK_END",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_AVAILABLE_START",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_COURSE_TOOLS_AVAILABLE_END",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_REVIEW_LINK_START",
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_OCR_REVIEW_LINK_END",
    "Formula Visual Evidence",
    "Formula evidence",
]

for marker in required_markers:
    if marker not in source:
        raise SystemExit(f"FAILED_V0791_SOURCE_MARKER_MISSING={marker}")

if not course_tools_link_visible:
    raise SystemExit("FAILED_V0791_COURSE_TOOLS_LINK_NOT_VISIBLE")
if not course_tools_card_visible:
    raise SystemExit("FAILED_V0791_COURSE_TOOLS_CARD_NOT_VISIBLE")
if not ocr_math_report_link_visible:
    raise SystemExit("FAILED_V0791_OCR_MATH_LINK_NOT_VISIBLE")
if not ocr_review_link_visible:
    raise SystemExit("FAILED_V0791_OCR_REVIEW_LINK_NOT_VISIBLE")

summary = {
    "VOILA_V0_7_91_FORMULA_VISUAL_EVIDENCE_LINKS_CHECK": "PASS",
    "course_id": course_id,
    "candidate_count": candidate_count,
    "COURSE_TOOLS_STATUS": course_tools.status_code,
    "OCR_MATH_REPORT_STATUS": ocr_math.status_code,
    "OCR_REVIEW_STATUS": ocr_review.status_code,
    "FORMULA_VIEWER_STATUS": formula_viewer.status_code,
    "COURSE_TOOLS_LINK_VISIBLE": course_tools_link_visible,
    "COURSE_TOOLS_CARD_VISIBLE": course_tools_card_visible,
    "OCR_MATH_REPORT_LINK_VISIBLE": ocr_math_report_link_visible,
    "OCR_REVIEW_LINK_VISIBLE": ocr_review_link_visible,
    "USES_LLM": manifest.get("policy", {}).get("uses_llm"),
    "USES_CLOUD": manifest.get("policy", {}).get("uses_cloud"),
    "OCR_REWRITE_PERFORMED": manifest.get("policy", {}).get("ocr_rewrite_performed"),
    "FORMULA_OCR_PERFORMED": manifest.get("policy", {}).get("formula_ocr_performed"),
    "BUILD_PERFORMED": False,
    "ZIP_CREATED": False,
    "SHARE_CREATED": False,
    "DELIVERY_PERFORMED": False,
    "TESTER_READINESS": "LOCAL_FORMULA_VISUAL_EVIDENCE_LINKS_PASS_NOT_PACKAGED",
    "POLICY": "formula_visual_evidence_links_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0791-formula-visual-evidence-links")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.91-FORMULA-VISUAL-EVIDENCE-LINKS-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    if isinstance(v, (str, bool, int)) or v is None:
        print(f"{k}={v}")

print("EVIDENCE=" + str(out))
