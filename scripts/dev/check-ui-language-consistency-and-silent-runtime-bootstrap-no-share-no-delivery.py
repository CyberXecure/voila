from __future__ import annotations

from copy import deepcopy
from html.parser import HTMLParser
from pathlib import Path
from unittest.mock import patch
import ast
import asyncio
import importlib
import re
import subprocess
import sys
import urllib.parse

import httpx

ROOT = Path(__file__).resolve().parents[2]
API_DIR = ROOT / "services" / "api"
BASE_HEAD = "79741947d75edd77e2057789717162b591aeb477"
BUILD_REL = "scripts/release/build-portable-runtime.ps1"
BUILD_PATH = ROOT / BUILD_REL
PDF_NAME = "03-pag-30-34-vectori-trigonometrie.pdf"
COURSE_ID = Path(PDF_NAME).stem
OUTPUT_DIR = ROOT / "data" / "output" / COURSE_ID
WEB_APP_PATH = API_DIR / "web_app.py"
I18N_PATH = API_DIR / "i18n.py"

OCR_EXPECTED = {
    API_DIR / "ocr_body_columns_tesseract_pages.py": 2,
    API_DIR / "ocr_columns_tesseract_pages.py": 1,
    API_DIR / "ocr_gate.py": 1,
    API_DIR / "ocr_tesseract_advanced.py": 1,
    API_DIR / "ocr_tesseract_pages.py": 1,
    API_DIR / "ocr_tsv_columns_tesseract_pages.py": 1,
}

sys.dont_write_bytecode = True
sys.path.insert(0, str(API_DIR))
failures: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{name}={'PASS' if ok else 'FAIL'}")
    if not ok:
        failures.append(name + (f": {detail}" if detail else ""))
        if detail:
            print(f"{name}_DETAIL={detail}")


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def snapshot(root: Path) -> dict:
    if not root.exists():
        return {}
    return {
        p.relative_to(root).as_posix(): (p.stat().st_size, p.stat().st_mtime_ns)
        for p in root.rglob("*")
        if p.is_file()
    }


def call_name(node: ast.Call) -> str:
    current = node.func
    parts: list[str] = []
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def canonical(raw: bytes) -> str:
    if raw.startswith(b"\xef\xbb\xbf"):
        raw = raw[3:]
    return raw.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n").rstrip("\n")


class VisibleParser(HTMLParser):
    SKIP = {"script", "style", "template", "noscript", "code"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[str] = []
        self.parts: list[str] = []
        self.links: list[str] = []

    def handle_starttag(self, tag, attrs):
        tag = str(tag).lower()
        self.stack.append(tag)
        if tag == "a":
            self.links.append(str(dict(attrs).get("href") or ""))

    def handle_endtag(self, tag):
        tag = str(tag).lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if any(tag in self.SKIP for tag in self.stack):
            return
        if "details" in self.stack and "summary" not in self.stack:
            return
        value = str(data or "").strip()
        if value:
            self.parts.append(value)


print("========== V0.8.91 DURABLE CHECK ==========")

paths = (I18N_PATH, *OCR_EXPECTED.keys(), WEB_APP_PATH)
sources: dict[Path, str] = {}
trees: dict[Path, ast.Module] = {}

for path in paths:
    check("PYTHON_FILE_" + path.stem.upper(), path.is_file(), str(path))
    if path.is_file():
        source = path.read_text(encoding="utf-8")
        sources[path] = source
        trees[path] = ast.parse(source, filename=str(path))
        print(f"PYTHON_AST_PARSE={path.relative_to(ROOT).as_posix()};PASS")

web_source = sources[WEB_APP_PATH]
web_tree = trees[WEB_APP_PATH]
i18n_source = sources[I18N_PATH]

markers = (
    "# VOILA_V0_8_91_SECONDARY_UI_LANGUAGE_BRIDGE_START",
    "# VOILA_V0_8_91_SECONDARY_UI_LANGUAGE_BRIDGE_END",
    "# VOILA_V0_8_91_RESOLVER_AUTO_FALLBACK_FIX_START",
    "# VOILA_V0_8_91_RESOLVER_AUTO_FALLBACK_FIX_END",
    "# VOILA_V0_8_91_FINAL_VISIBLE_RO_EN_COPY_CLEANUP_START",
    "# VOILA_V0_8_91_FINAL_VISIBLE_RO_EN_COPY_CLEANUP_END",
    "# VOILA_V0_8_91_EN_LAST_MILE_COPY_FIX_START",
    "# VOILA_V0_8_91_EN_LAST_MILE_COPY_FIX_END",
    "# VOILA_V0_8_91_COURSE_TOOLS_EN_FINAL_BRIDGE_START",
    "# VOILA_V0_8_91_COURSE_TOOLS_EN_FINAL_BRIDGE_END",
    "# VOILA_V0_8_91_COURSE_TOOLS_RO_FINAL_BRIDGE_START",
    "# VOILA_V0_8_91_COURSE_TOOLS_RO_FINAL_BRIDGE_END",
    "# VOILA_V0_8_91_CANONICAL_VISUAL_LEARNING_CONTRACT_START",
    "# VOILA_V0_8_91_CANONICAL_VISUAL_LEARNING_CONTRACT_END",
    "# VOILA_V0_8_91_REVIEW_DOCUMENT_CANONICAL_STAGE_STRUCTURE_START",
    "# VOILA_V0_8_91_REVIEW_DOCUMENT_CANONICAL_STAGE_STRUCTURE_END",
)

for marker in markers:
    check(
        "MARKER_" + re.sub(r"[^A-Z0-9]+", "_", marker.upper()).strip("_"),
        web_source.count(marker) == 1,
        f"count={web_source.count(marker)}",
    )

check("I18N_RO_EN_PRESENT", '"ro"' in i18n_source and '"en"' in i18n_source)

for field in (
    "visual_type", "short_title", "what_it_represents", "importance",
    "study_uses", "linked_concepts", "integration_status", "semantic_complete",
):
    check("SEMANTIC_FIELD_" + field.upper(), field in web_source)

ocr_total = 0
for path, expected in OCR_EXPECTED.items():
    source = sources[path]
    calls = []
    for node in ast.walk(trees[path]):
        if isinstance(node, ast.Call) and call_name(node).endswith("subprocess.run"):
            segment = ast.get_source_segment(source, node) or ""
            if "CREATE_NO_WINDOW" in segment:
                calls.append(segment)
    ocr_total += len(calls)
    check(
        "OCR_NO_CONSOLE_" + path.stem.upper(),
        len(calls) == expected and all("creationflags" in item for item in calls),
        f"expected={expected};actual={len(calls)}",
    )

check("OCR_NO_CONSOLE_TOTAL", ocr_total == 7, str(ocr_total))

web_calls = []
for node in ast.walk(web_tree):
    if isinstance(node, ast.Call):
        name = call_name(node)
        if name.endswith("subprocess.run") or name.endswith("subprocess.Popen"):
            segment = ast.get_source_segment(web_source, node) or ""
            if "CREATE_NO_WINDOW" in segment:
                web_calls.append(segment)

check("WEB_NO_CONSOLE_CALL_COUNT", len(web_calls) == 2, str(len(web_calls)))
check("CREATE_NEW_CONSOLE_REMOVED", "CREATE_NEW_CONSOLE" not in web_source)

blob = subprocess.run(
    ["git", "-C", str(ROOT), "cat-file", "blob", BASE_HEAD + ":" + BUILD_REL],
    cwd=str(ROOT),
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    check=False,
)
check("PORTABLE_RUNTIME_BASE_BLOB_READ", blob.returncode == 0, blob.stderr.decode(errors="replace"))

base_build = canonical(blob.stdout)
current_build = canonical(BUILD_PATH.read_bytes())
minimized = "-WindowStyle Minimized -PassThru"
hidden = "-WindowStyle Hidden -PassThru"
expected_build = base_build.replace(minimized, hidden)

check("PORTABLE_RUNTIME_BASE_MINIMIZED_2", base_build.count(minimized) == 2)
check("PORTABLE_RUNTIME_CURRENT_MINIMIZED_0", current_build.count(minimized) == 0)
check("PORTABLE_RUNTIME_CURRENT_HIDDEN_2", current_build.count(hidden) == 2)
check("PORTABLE_RUNTIME_EXACT_PIPELINE_REUSE", current_build == expected_build)

web_app = importlib.import_module("web_app")
output_before = snapshot(OUTPUT_DIR)


async def fetch_pages():
    transport = httpx.ASGITransport(app=web_app.app, raise_app_exceptions=True)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://voila.test",
        follow_redirects=False,
        timeout=30.0,
    ) as client:
        with patch.object(
            web_app,
            "ensure_crop_editor_running",
            side_effect=AssertionError("Legacy Crop Editor must not start."),
        ):
            return {
                "REVIEW_RO": await client.get("/review-document", params={"pdf": PDF_NAME, "lang": "ro"}),
                "REVIEW_EN": await client.get("/review-document", params={"pdf": PDF_NAME, "lang": "en"}),
                "COURSE_RO": await client.get("/course-tools", params={"pdf": PDF_NAME, "lang": "ro"}),
                "COURSE_EN": await client.get("/course-tools", params={"pdf": PDF_NAME, "lang": "en"}),
                "EDIT_RO": await client.get("/edit-crops", params={"pdf": PDF_NAME, "lang": "ro"}),
                "EDIT_EN": await client.get("/edit-crops", params={"pdf": PDF_NAME, "lang": "en"}),
            }


responses = asyncio.run(fetch_pages())
parsed: dict[str, dict] = {}

for label in ("REVIEW_RO", "REVIEW_EN", "COURSE_RO", "COURSE_EN"):
    response = responses[label]
    expected_lang = "en" if label.endswith("_EN") else "ro"
    check(label + "_HTTP_200", response.status_code == 200)
    check(label + "_HTML_LANG", f'<html lang="{expected_lang}">' in response.text)
    check(label + "_NO_REPLACEMENT_CHARACTER", "\ufffd" not in response.text)
    parser = VisibleParser()
    parser.feed(response.text)
    parsed[label] = {
        "html": response.text,
        "visible": compact(" ".join(parser.parts)),
        "links": parser.links,
    }

for label, expected_lang in (("EDIT_RO", "ro"), ("EDIT_EN", "en")):
    response = responses[label]
    location = urllib.parse.urlsplit(str(response.headers.get("location") or ""))
    query = urllib.parse.parse_qs(location.query, keep_blank_values=True)
    check(label + "_REDIRECT_STATUS", response.status_code in {302, 303, 307, 308})
    check(label + "_REDIRECT_PATH", location.path == "/review-document")
    check(label + "_REDIRECT_PDF", query.get("pdf") == [PDF_NAME])
    check(label + "_REDIRECT_LANG", query.get("lang") == [expected_lang])
    check(label + "_REDIRECT_SECTION", query.get("section") == ["visual"])
    check(label + "_REDIRECT_FRAGMENT", location.fragment == "review-document-visual-validation-readonly-ui")
    check(label + "_NO_8790", "8790" not in location.geturl())

stage_contract = {
    "REVIEW_RO": ("Text și OCR", "Formule și zone din pagină", "Noțiuni de învățat"),
    "REVIEW_EN": ("Text & OCR", "Formulas and page regions", "Concepts to learn"),
}

for label, stages in stage_contract.items():
    positions = [parsed[label]["visible"].find(stage) for stage in stages]
    check(
        label + "_STAGE_ORDER",
        all(position >= 0 for position in positions) and positions[0] < positions[1] < positions[2],
        repr(positions),
    )
    html_text = parsed[label]["html"]
    sections = [
        html_text.find('id="review-document-text-ocr-stage"'),
        html_text.find('id="review-document-visual-validation-readonly-ui"'),
        html_text.find('id="review-document-concepts-stage"'),
    ]
    check(
        label + "_SECTION_ORDER",
        all(position >= 0 for position in sections) and sections[0] < sections[1] < sections[2],
        repr(sections),
    )

for label in ("REVIEW_RO", "REVIEW_EN", "COURSE_RO", "COURSE_EN"):
    forbidden = (
        "/edit-crops", "127.0.0.1:8790", "localhost:8790",
        "/owner/manual-learning-evidence/", "/owner/manual-study-preview/", "figures_hybrid",
    )
    hits = [href for href in parsed[label]["links"] if any(item in href for item in forbidden)]
    check(label + "_NO_LEGACY_LINKS", not hits, " | ".join(hits))
    check(label + "_NO_PORT_8790_HTML", "8790" not in parsed[label]["html"])

fake_item = {
    "item_id": "visual-001",
    "page": 4,
    "kind": "diagram",
    "crop_exists": True,
    "crop_path": "formula_visual_evidence/crops/mock.png",
    "ocr_math_candidate_text": "a = ax + ay",
    "user_decision": "pending",
    "ready_for_study": False,
}

with (
    patch.object(web_app, "_voila_v0874_load_visual_validation_items", return_value=[deepcopy(fake_item)]),
    patch.object(web_app, "_voila_v0874_find_output_dir", return_value=None),
):
    visual_ro = web_app._voila_v0874_visual_validation_readonly_section(COURSE_ID, ui_lang="ro")
    visual_en = web_app._voila_v0874_visual_validation_readonly_section(COURSE_ID, ui_lang="en")

for field in (
    'name="visual_type"', 'name="short_title"', 'name="what_it_represents"',
    'name="importance"', 'name="study_uses"', 'name="linked_concepts"',
):
    check(
        "VISUAL_FORM_" + re.sub(r"[^A-Z0-9]+", "_", field.upper()).strip("_"),
        field in visual_ro and field in visual_en,
    )

complete_item = {
    **fake_item,
    "visual_type": "diagram",
    "short_title": "Componentele unui vector",
    "what_it_represents": "Schema arată componentele unui vector.",
    "importance": "essential",
    "study_uses": ["explain", "question"],
    "linked_concepts": ["vector", "componente"],
    "user_decision": "accept",
    "ready_for_study": True,
    "integration_status": "eligible",
}
incomplete_item = {**complete_item, "item_id": "visual-002", "importance": ""}

check("SEMANTIC_COMPLETE_TRUE", web_app._voila_v091_visual_semantic_complete(complete_item) is True)
check("SEMANTIC_INCOMPLETE_FALSE", web_app._voila_v091_visual_semantic_complete(incomplete_item) is False)

clean_payload, clean_summary = web_app._voila_v0881_build_clean_study_payload(
    COURSE_ID,
    PDF_NAME,
    Path("visual_items.bbox.validated.json"),
    [complete_item, incomplete_item],
)

check("PREPARED_LESSON_ITEM_COUNT", clean_payload.get("item_count") == 1)
check("PREPARED_LESSON_EXCLUDED_COUNT", clean_payload.get("excluded_count") == 1)
clean_item = clean_payload["items"][0]
check("PREPARED_LESSON_SOURCE", clean_item.get("learning_source") == "validated_bbox_visual_item")
check(
    "PREPARED_LESSON_METADATA",
    clean_item.get("title") == "Componentele unui vector"
    and clean_item.get("importance") == "essential"
    and clean_item.get("study_uses") == ["explain", "question"]
    and clean_item.get("linked_concepts") == ["vector", "componente"],
)
check("PREPARED_LESSON_NO_PROGRESS_WRITE", clean_summary.get("progress_write_performed") is False)
check("OUTPUT_TREE_UNCHANGED", output_before == snapshot(OUTPUT_DIR))

print(f"FAILURE_COUNT={len(failures)}")
for index, failure in enumerate(failures, start=1):
    print(f"FAILURE_{index}={failure}")

if failures:
    print("V0_8_91_DURABLE_CHECK=FAIL")
    raise SystemExit(1)

print("V0_8_91_DURABLE_CHECK=PASS")
print("UI_LANGUAGE_RO_EN=PASS")
print("SILENT_RUNTIME=PASS")
print("CANONICAL_REVIEW_DOCUMENT_FLOW=PASS")
print("VISUAL_LEARNING_SEMANTIC_GATE=PASS")
print("PREPARED_LESSON_INTEGRATION_GATE=PASS")
print("LEGACY_CROP_EDITOR_DISABLED=PASS")
print("BUILD_EXECUTED=FALSE")
print("ZIP_CREATED=FALSE")
print("SHARE_PERFORMED=FALSE")
print("DELIVERY_PERFORMED=FALSE")
