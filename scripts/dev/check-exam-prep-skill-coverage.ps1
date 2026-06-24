$ErrorActionPreference = "Stop"

cd "D:\dev\projects\voila"

Write-Host "=== EXAM PREP SAMPLE SKILL COVERAGE CHECK v0.4.29 ==="

$skillTreePath = ".\assets\exam_prep\bac\matematica_m1\skill_tree.json"

if (-not (Test-Path $skillTreePath)) {
    throw "Missing skill tree: $skillTreePath"
}

$pyPath = Join-Path $env:TEMP "check-exam-prep-skill-coverage-v0.4.29.py"

$py = @"
import json
import sys
import unicodedata
from pathlib import Path

skill_tree_path = Path(r"$skillTreePath")

def normalize(value):
    text = str(value or "")
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text.lower()

def walk_text(obj):
    if isinstance(obj, dict):
        fields = []
        for key in (
            "id",
            "slug",
            "label",
            "title",
            "name",
            "description",
            "short_description",
            "topic_group",
            "group",
            "category",
            "chapter",
            "unit",
            "domain",
            "strand",
        ):
            value = obj.get(key)
            if isinstance(value, (str, int, float)):
                fields.append(str(value))

        if fields:
            yield " ".join(fields)

        for value in obj.values():
            yield from walk_text(value)

    elif isinstance(obj, list):
        for value in obj:
            yield from walk_text(value)

data = json.loads(skill_tree_path.read_text(encoding="utf-8"))
corpus = "\\n".join(walk_text(data))
normalized = normalize(corpus)

expectations = {
    "Mulțimi": ["multimi", "multime"],
    "Funcții": ["functii", "functie"],
    "Derivate": ["derivate", "derivata"],
    "Integrale": ["integrale", "integrala"],
    "Geometrie": ["geometrie"],
}

all_ok = True

for label, needles in expectations.items():
    found = any(needle in normalized for needle in needles)
    safe_key = normalize(label).replace(" ", "_")
    print(f"coverage_has_{safe_key} {found}")
    if not found:
        all_ok = False

print(f"skill_tree_path {skill_tree_path}")
print(f"skill_tree_text_length {len(corpus)}")

if not all_ok:
    raise SystemExit("EXAM PREP SAMPLE SKILL COVERAGE CHECK FAILED")

print("EXAM PREP SAMPLE SKILL COVERAGE v0.4.29 PASS")
"@

Set-Content -Path $pyPath -Value $py -Encoding UTF8
python $pyPath
