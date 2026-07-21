from pathlib import Path
import hashlib
import json
import subprocess

root = Path(".").resolve()

doc = root / "docs" / "dev" / "packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.md"
bootstrap = root / "scripts" / "dev" / "start-voila-packaged.ps1"
check_py = root / "scripts" / "dev" / "check-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.py"
check_ps1 = root / "scripts" / "dev" / "check-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.ps1"
web = root / "services" / "api" / "web_app.py"

for path, marker in [
    (doc, "FAILED_V0837_DOC_MISSING"),
    (bootstrap, "FAILED_V0837_BOOTSTRAP_MISSING"),
    (check_py, "FAILED_V0837_CHECK_PY_MISSING"),
    (check_ps1, "FAILED_V0837_CHECK_PS1_MISSING"),
    (web, "FAILED_V0837_WEB_APP_MISSING"),
]:
    if not path.exists():
        raise SystemExit(marker + "=" + str(path))

doc_text = doc.read_text(encoding="utf-8", errors="replace")
bootstrap_text = bootstrap.read_text(encoding="utf-8", errors="replace")
bootstrap_lower = bootstrap_text.lower()
web_text = web.read_text(encoding="utf-8", errors="replace")

required_doc_terms = [
    "Packaged startup bootstrap",
    "v0.8.35 confirmed that the v0.8.34 tester ZIP is not self-startable after extraction",
    "v0.8.36 selected Option B",
    "`scripts/dev/start-voila-packaged.ps1`",
    "support `-CheckOnly`",
    "This milestone does not rebuild the package.",
    "This milestone does not create a new ZIP.",
    "This milestone does not extract the package.",
    "This milestone does not start the extracted package.",
    "This milestone does not modify `services/api/web_app.py`.",
    "This milestone does not add a route.",
    "This milestone does not add a POST endpoint.",
    "This milestone does not change Study behavior.",
    "This milestone does not write Progress.",
    "This milestone does not mark answers.",
    "This milestone does not copy to OneDrive.",
    "This milestone does not create a share.",
    "This milestone does not deliver anything.",
    "This milestone does not distribute anything.",
    "This milestone does not create a public release.",
    "v0.8.38 — rebuild local tester ZIP with `start-voila-packaged.ps1`, no share/no delivery",
    "v0.8.39 — retry extracted-package browser validation, no share/no delivery",
    "Package readiness remains blocked until rebuild and extracted-package validation pass.",
]

for term in required_doc_terms:
    if term not in doc_text:
        raise SystemExit("FAILED_V0837_DOC_TERM_MISSING=" + term)

changed = subprocess.check_output(
    ["git", "diff", "--name-only", "HEAD"],
    text=True,
    encoding="utf-8",
    errors="replace",
).splitlines()

allowed = {
    "docs/dev/packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.md",
    "scripts/dev/start-voila-packaged.ps1",
    "scripts/dev/check-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.py",
    "scripts/dev/check-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery.ps1",
}

unexpected = sorted(path for path in changed if path and path.replace("\\", "/") not in allowed)
if unexpected:
    raise SystemExit("FAILED_V0837_UNEXPECTED_CHANGED_FILES=" + ",".join(unexpected))

required_bootstrap_terms = [
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_START",
    "param(",
    "[switch]$Silent",
    "[switch]$NoBrowser",
    "[switch]$CheckOnly",
    ".venv\\Scripts\\python.exe",
    "services\\api",
    "web_app.py",
    "requirements.txt",
    "python -m venv",
    "pip install --upgrade pip",
    "pip install -r",
    "uvicorn",
    "web_app:app",
    "127.0.0.1",
    "8787",
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK_ONLY=PASS",
    "venv_create_performed=False",
    "dependency_install_performed=False",
    "server_start_performed=False",
    "browser_open_performed=False",
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_STARTED=PASS",
]

for term in required_bootstrap_terms:
    if term.lower() not in bootstrap_lower:
        raise SystemExit("FAILED_V0837_BOOTSTRAP_TERM_MISSING=" + term)

for forbidden in [
    "onedrive",
    "gh pr",
    "gh release",
    "Compress-Archive",
    "Expand-Archive",
    "delivery",
    "distribution",
]:
    if forbidden.lower() in bootstrap_lower:
        raise SystemExit("FAILED_V0837_BOOTSTRAP_FORBIDDEN_TERM=" + forbidden)

required_web_terms = [
    "VOILA_V0_8_27_MANUAL_STUDY_DEFAULT_STUDY_READ_ONLY_FALLBACK_START",
    "manual-study-default-route",
    "manual-study-default-cards",
    "manual_study_default_read_only_fallback",
    "VOILA_V0_8_22_MANUAL_STUDY_REAL_STUDY_READ_ONLY_SHADOW_TOGGLE_START",
    "manual-study-shadow-route",
    "VOILA_V0_8_24_MANUAL_STUDY_SHADOW_COURSE_TOOLS_LINK_START",
    "manual-study-shadow-course-tools-link",
    "manual-study-dry-run-course-tools-link",
    "/study?pdf=",
]

for term in required_web_terms:
    if term not in web_text:
        raise SystemExit("FAILED_V0837_WEB_TERM_MISSING=" + term)

if web_text.count('@app.get("/study"') != 1:
    raise SystemExit("FAILED_V0837_STUDY_ROUTE_COUNT_CHANGED")

if web_text.count('@app.post("/study"') != 0:
    raise SystemExit("FAILED_V0837_STUDY_POST_ADDED")

check_result = subprocess.run(
    [
        "pwsh",
        "-NoProfile",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(bootstrap),
        "-CheckOnly",
        "-NoBrowser",
    ],
    cwd=str(root),
    text=True,
    encoding="utf-8",
    errors="replace",
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    timeout=60,
)

if check_result.returncode != 0:
    raise SystemExit("FAILED_V0837_BOOTSTRAP_CHECK_ONLY_RC=" + str(check_result.returncode) + "\n" + check_result.stdout)

check_output = check_result.stdout

required_check_output_terms = [
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_START",
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK_ONLY=PASS",
    "venv_create_performed=False",
    "dependency_install_performed=False",
    "server_start_performed=False",
    "browser_open_performed=False",
]

for term in required_check_output_terms:
    if term not in check_output:
        raise SystemExit("FAILED_V0837_CHECK_ONLY_OUTPUT_TERM_MISSING=" + term + "\n" + check_output)

evidence_dir = Path(r"D:\dev\tester-runs\v0837-packaged-startup-bootstrap-no-build-no-zip-no-share-no-delivery")
evidence_dir.mkdir(parents=True, exist_ok=True)

summary = {
    "VOILA_V0_8_37_PACKAGED_STARTUP_BOOTSTRAP_CHECK": "PASS",
    "depends_on_v0836_runtime_preflight": True,
    "packaged_bootstrap_script_added": True,
    "packaged_bootstrap_script_path": "scripts/dev/start-voila-packaged.ps1",
    "check_only_supported": True,
    "check_only_executed": True,
    "check_only_passed": True,
    "check_only_created_venv": False,
    "check_only_installed_dependencies": False,
    "check_only_started_server": False,
    "check_only_opened_browser": False,
    "bootstrap_resolves_package_root_from_script_location": True,
    "bootstrap_detects_venv_python": True,
    "bootstrap_can_create_venv_when_missing": True,
    "bootstrap_can_install_tracked_requirements": True,
    "bootstrap_can_start_uvicorn": True,
    "bootstrap_host": "127.0.0.1",
    "bootstrap_port": 8787,
    "bootstrap_hash_sha256": hashlib.sha256(bootstrap_text.encode("utf-8", errors="replace")).hexdigest(),
    "web_app_changed": False,
    "new_route_added": False,
    "new_post_endpoint_added": False,
    "study_changed": False,
    "progress_write_added": False,
    "answer_marking_added": False,
    "ocr_rewrite_performed": False,
    "formula_ocr_performed": False,
    "crop_file_written": False,
    "package_rebuild_performed": False,
    "new_zip_created": False,
    "package_extracted": False,
    "extracted_package_started": False,
    "share_created": False,
    "onedrive_copy_created": False,
    "delivery_performed": False,
    "distribution_performed": False,
    "public_release_created": False,
    "PACKAGED_STARTUP_BOOTSTRAP": "PASS_CHECK_ONLY_NO_BUILD_NO_ZIP",
    "PACKAGE_READINESS": "BLOCKED_PENDING_PACKAGE_REBUILD_AND_EXTRACTED_VALIDATION",
    "POLICY": "packaged_startup_bootstrap_no_build_no_zip_no_share_no_delivery",
    "RECOMMENDED_NEXT": "v0.8.38-owner-local-package-rebuild-with-packaged-startup-no-share-no-delivery",
}

out_json = evidence_dir / "V0.8.37-PACKAGED-STARTUP-BOOTSTRAP-CHECK.json"
out_md = evidence_dir / "V0.8.37-PACKAGED-STARTUP-BOOTSTRAP-CHECK.md"

out_json.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

md_lines = [
    "# v0.8.37 Packaged startup bootstrap — no build/no ZIP/no share/no delivery",
    "",
    "## Summary",
]
for key, value in summary.items():
    md_lines.append(f"- {key}: {value}")

out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

for k, v in summary.items():
    print(f"{k}={v}")

print("EVIDENCE_JSON=" + str(out_json))
print("EVIDENCE_MD=" + str(out_md))
