from pathlib import Path
import importlib.util
import json
import sys
from urllib.parse import quote

sys.path.insert(0, str(Path("services/api").resolve()))

builder_path = Path("scripts/dev/build-formula-visual-evidence-manifest.py")
spec = importlib.util.spec_from_file_location("v0792_formula_builder", builder_path)
builder = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(builder)

course_id = "03-pag-30-34-vectori-trigonometrie"
manifest = builder.build_manifest(course_id=course_id)

manifest_path = Path("data/output") / course_id / "formula_visual_evidence.manifest.json"
if not manifest_path.exists():
    raise SystemExit("FAILED_V0792_MANIFEST_NOT_WRITTEN")

data = json.loads(manifest_path.read_text(encoding="utf-8"))
candidates = data.get("candidates") if isinstance(data.get("candidates"), list) else []
quality_counts = data.get("quality_counts") if isinstance(data.get("quality_counts"), dict) else {}

if len(candidates) != data.get("candidate_count"):
    raise SystemExit("FAILED_V0792_CANDIDATE_COUNT_MISMATCH")

if len(candidates) != 43:
    raise SystemExit(f"FAILED_V0792_EXPECTED_43_CANDIDATES_GOT={len(candidates)}")

for item in candidates:
    if "quality_tier" not in item:
        raise SystemExit("FAILED_V0792_MISSING_QUALITY_TIER")
    if "quality_score" not in item:
        raise SystemExit("FAILED_V0792_MISSING_QUALITY_SCORE")
    if "noise_reasons" not in item:
        raise SystemExit("FAILED_V0792_MISSING_NOISE_REASONS")

tiers = [str(item.get("quality_tier") or "low") for item in candidates]
scores = [int(item.get("quality_score") or 0) for item in candidates]
noise_items = [item for item in candidates if item.get("noise_reasons")]

if not quality_counts:
    raise SystemExit("FAILED_V0792_MISSING_QUALITY_COUNTS")

if sum(int(quality_counts.get(k) or 0) for k in ["high", "medium", "low"]) != len(candidates):
    raise SystemExit("FAILED_V0792_QUALITY_COUNTS_SUM_MISMATCH")

if "low" not in tiers:
    raise SystemExit("FAILED_V0792_EXPECTED_LOW_TIER_FOR_NOISY_ITEMS")

if not noise_items:
    raise SystemExit("FAILED_V0792_EXPECTED_NOISE_REASONS")

from fastapi.testclient import TestClient
import web_app

client = TestClient(web_app.app)
viewer_url = f"/owner/formula-visual-evidence/{quote(course_id, safe='')}/view"
viewer = client.get(viewer_url)

if viewer.status_code != 200:
    raise SystemExit(f"FAILED_V0792_VIEWER_STATUS={viewer.status_code}")

viewer_text = viewer.text

required_viewer_terms = [
    "High:",
    "Medium:",
    "Low/noisy:",
    "Calitate:",
    "Zgomot:",
    "score",
    "Formula visual evidence",
]

for term in required_viewer_terms:
    if term not in viewer_text:
        raise SystemExit(f"FAILED_V0792_VIEWER_MISSING={term}")

source_builder = builder_path.read_text(encoding="utf-8")
source_web = Path("services/api/web_app.py").read_text(encoding="utf-8")
required_source_terms = [
    "VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_QUALITY_FILTER_START",
    "VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_QUALITY_FILTER_END",
    "VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_VIEWER_SORT_START",
    "VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_VIEWER_SORT_END",
    "quality_tier",
    "quality_score",
    "noise_reasons",
    "quality_counts",
]

for term in required_source_terms:
    if term not in source_builder and term not in source_web:
        raise SystemExit(f"FAILED_V0792_SOURCE_TERM_MISSING={term}")

summary = {
    "VOILA_V0_7_92_FORMULA_VISUAL_EVIDENCE_QUALITY_FILTER_CHECK": "PASS",
    "course_id": course_id,
    "candidate_count": len(candidates),
    "quality_counts": quality_counts,
    "high_count": int(quality_counts.get("high") or 0),
    "medium_count": int(quality_counts.get("medium") or 0),
    "low_count": int(quality_counts.get("low") or 0),
    "noise_item_count": len(noise_items),
    "min_quality_score": min(scores),
    "max_quality_score": max(scores),
    "viewer_status": viewer.status_code,
    "quality_tier_present": True,
    "quality_score_present": True,
    "noise_reasons_present": True,
    "viewer_quality_counts_visible": True,
    "viewer_quality_details_visible": True,
    "raw_candidates_preserved": True,
    "USES_LLM": data.get("policy", {}).get("uses_llm"),
    "USES_CLOUD": data.get("policy", {}).get("uses_cloud"),
    "OCR_REWRITE_PERFORMED": data.get("policy", {}).get("ocr_rewrite_performed"),
    "FORMULA_OCR_PERFORMED": data.get("policy", {}).get("formula_ocr_performed"),
    "BUILD_PERFORMED": data.get("policy", {}).get("build_performed"),
    "ZIP_CREATED": data.get("policy", {}).get("zip_created"),
    "SHARE_CREATED": data.get("policy", {}).get("share_created"),
    "DELIVERY_PERFORMED": data.get("policy", {}).get("delivery_performed"),
    "TESTER_READINESS": "LOCAL_FORMULA_VISUAL_EVIDENCE_QUALITY_FILTER_PASS_NOT_PACKAGED",
    "POLICY": "formula_visual_evidence_quality_filter_no_build_no_zip_no_share_no_delivery_no_distribution",
}

evidence = Path(r"D:\dev\tester-runs\v0792-formula-visual-evidence-quality-filter")
evidence.mkdir(parents=True, exist_ok=True)
out = evidence / "V0.7.92-FORMULA-VISUAL-EVIDENCE-QUALITY-FILTER-CHECK.json"
out.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

for k, v in summary.items():
    if isinstance(v, (str, bool, int)) or v is None:
        print(f"{k}={v}")
print("quality_counts=" + json.dumps(quality_counts, ensure_ascii=False))
print("EVIDENCE=" + str(out))
