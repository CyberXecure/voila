from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

EXAM_PREP_ASSET_ROOT = PROJECT_ROOT / "assets" / "exam_prep"
EXAM_PREP_DATA_ROOT = PROJECT_ROOT / "data" / "exam_prep"


def load_bac_matematica_m1_skill_tree() -> dict:
    path = EXAM_PREP_ASSET_ROOT / "bac" / "matematica_m1" / "skill_tree.json"
    return json.loads(path.read_text(encoding="utf-8"))


def bac_matematica_m1_progress_path() -> Path:
    return EXAM_PREP_DATA_ROOT / "bac" / "matematica_m1" / "progress.json"


def default_progress_from_skill_tree(skill_tree: dict) -> dict:
    skills = {}

    for skill in skill_tree.get("skills", []):
        skill_id = str(skill.get("id") or "").strip()
        if not skill_id:
            continue

        skills[skill_id] = {
            "attempts": 0,
            "correct": 0,
            "mastery": 0.0,
        }

    return {
        "version": "voila_exam_prep_progress_v1",
        "track": skill_tree.get("track", "exam_prep"),
        "exam": skill_tree.get("exam", "bacalaureat"),
        "subject": skill_tree.get("subject", "matematica_m1"),
        "skills": skills,
    }


def load_or_initialize_bac_matematica_m1_progress() -> dict:
    skill_tree = load_bac_matematica_m1_skill_tree()
    progress_path = bac_matematica_m1_progress_path()

    if progress_path.exists():
        return json.loads(progress_path.read_text(encoding="utf-8"))

    progress = default_progress_from_skill_tree(skill_tree)
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress_path.write_text(
        json.dumps(progress, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return progress


def bac_matematica_m1_dashboard() -> dict:
    skill_tree = load_bac_matematica_m1_skill_tree()
    progress = merged_bac_matematica_m1_progress()
    progress_skills = progress.get("skills", {})

    rows = []
    for skill in skill_tree.get("skills", []):
        skill_id = str(skill.get("id") or "")
        state = progress_skills.get(skill_id, {})
        rows.append(
            {
                "id": skill_id,
                "name": skill.get("name", skill_id),
                "description": skill.get("description", ""),
                "attempts": int(state.get("attempts") or 0),
                "correct": int(state.get("correct") or 0),
                "mastery": float(state.get("mastery") or 0.0),
            }
        )

    return {
        "title": skill_tree.get("title", "Bacalaureat Matematică M1"),
        "skills": rows,
    }

BAC_MATEMATICA_M1_SKILL_KEYWORDS = {
    "derivate": [
        "derivata", "derivată", "derivare", "f'", "f’", "tangenta", "tangentă",
        "monotonie", "punct critic", "maxim", "minim", "convex", "concav"
    ],
    "integrale": [
        "integrala", "integrală", "integrale", "primitiva", "primitivă",
        "aria", "∫", "antiderivata", "antiderivată"
    ],
    "limite_continuitate": [
        "limita", "limită", "continuitate", "continua", "continuă",
        "asimptota", "asimptotă", "tinde la", "lim "
    ],
    "functii": [
        "functie", "funcție", "functii", "funcții", "domeniu", "codomeniu",
        "grafic", "imaginea functiei", "imaginea funcției", "injectiva", "surjectiva",
        "bijectiva", "compunere"
    ],
    "ecuatii_inecuatii": [
        "ecuatie", "ecuație", "ecuatia", "ecuația", "ecuatii", "ecuații",
        "inecuatie", "inecuație", "inecuatia", "inecuația",
        "sistem", "radacina", "rădăcină", "solutie", "soluție"
    ],
    "probabilitati_combinatorica": [
        "probabilitate", "probabilitati", "probabilități", "combinari", "combinări",
        "aranjamente", "permutari", "permutări", "binomial", "eveniment"
    ],
    "geometrie": [
        "geometrie", "vector", "vectori", "dreapta", "plan", "distanta", "distanță",
        "unghi", "coordonate", "coliniar", "ortogonal", "perpendicular"
    ],
    "multimi": [
        "multime", "mulțime", "multimi", "mulțimi", "reuniune", "intersectie",
        "intersecție", "incluziune", "apartine", "aparține", "submultime", "submulțime"
    ],
}


def normalize_skill_text(value: str) -> str:
    return str(value or "").lower().replace("ţ", "ț").replace("ş", "ș")


def infer_bac_matematica_m1_skill_id_from_text(value: str) -> str | None:
    text = normalize_skill_text(value)

    if not text.strip():
        return None

    best_skill = None
    best_score = 0

    for skill_id, keywords in BAC_MATEMATICA_M1_SKILL_KEYWORDS.items():
        score = 0
        for keyword in keywords:
            needle = normalize_skill_text(keyword)
            if needle and needle in text:
                score += 1

        if score > best_score:
            best_skill = skill_id
            best_score = score

    return best_skill


def infer_bac_matematica_m1_skill_id_from_question(question: dict) -> str | None:
    parts = [
        question.get("concept_id"),
        question.get("concept_title"),
        question.get("lesson_title"),
        question.get("question"),
        question.get("answer"),
        question.get("source_sentence"),
    ]

    return infer_bac_matematica_m1_skill_id_from_text(" ".join(str(part or "") for part in parts))



def bac_matematica_m1_skill_name_by_id() -> dict:
    skill_tree = load_bac_matematica_m1_skill_tree()
    return {
        str(skill.get("id") or ""): str(skill.get("name") or skill.get("id") or "")
        for skill in skill_tree.get("skills", [])
        if skill.get("id")
    }


def tag_bac_matematica_m1_question(question: dict) -> dict:
    tagged = dict(question)
    skill_id = infer_bac_matematica_m1_skill_id_from_question(tagged)
    skill_names = bac_matematica_m1_skill_name_by_id()

    if skill_id:
        tagged["exam_prep_track"] = "exam_prep"
        tagged["exam_prep_exam"] = "bacalaureat"
        tagged["exam_prep_subject"] = "matematica_m1"
        tagged["exam_prep_skill_id"] = skill_id
        tagged["exam_prep_skill_name"] = skill_names.get(skill_id, skill_id)

    return tagged


def tag_bac_matematica_m1_questions(questions: list[dict]) -> list[dict]:
    return [tag_bac_matematica_m1_question(question) for question in questions]


OUTPUT_DIR = PROJECT_ROOT / "data" / "output"


def load_json_or_default(path: Path, default):
    try:
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default
    return default


def aggregate_bac_matematica_m1_progress_from_study_outputs(output_root: Path | None = None) -> dict:
    output_root = output_root or OUTPUT_DIR
    skill_tree = load_bac_matematica_m1_skill_tree()
    valid_skill_ids = {
        str(skill.get("id") or "")
        for skill in skill_tree.get("skills", [])
        if skill.get("id")
    }

    aggregate = {
        skill_id: {
            "attempts": 0,
            "correct": 0,
            "mastery": 0.0,
            "_weighted_mastery": 0.0,
        }
        for skill_id in valid_skill_ids
    }

    if not output_root.exists():
        return {
            skill_id: {
                "attempts": 0,
                "correct": 0,
                "mastery": 0.0,
            }
            for skill_id in valid_skill_ids
        }

    for output_dir in output_root.iterdir():
        if not output_dir.is_dir():
            continue

        quiz_path = output_dir / "quiz.study.json"
        state_path = output_dir / "study_state.json"

        if not quiz_path.exists() or not state_path.exists():
            continue

        quiz = load_json_or_default(quiz_path, {"questions": []})
        state = load_json_or_default(state_path, {"concepts": {}})

        questions = quiz.get("questions") or []
        concepts = state.get("concepts") or {}

        skill_to_concepts: dict[str, set[str]] = {}

        for question in questions:
            if not isinstance(question, dict):
                continue

            skill_id = str(question.get("exam_prep_skill_id") or "").strip()
            concept_id = str(question.get("concept_id") or "").strip()

            if not skill_id or skill_id not in valid_skill_ids or not concept_id:
                continue

            skill_to_concepts.setdefault(skill_id, set()).add(concept_id)

        for skill_id, concept_ids in skill_to_concepts.items():
            for concept_id in concept_ids:
                concept = concepts.get(concept_id)

                if not isinstance(concept, dict):
                    continue

                attempts = int(concept.get("attempts") or 0)
                correct = int(concept.get("correct") or 0)
                mastery = float(concept.get("mastery") or 0.0)

                aggregate[skill_id]["attempts"] += attempts
                aggregate[skill_id]["correct"] += correct
                aggregate[skill_id]["_weighted_mastery"] += mastery * attempts

    cleaned = {}

    for skill_id, item in aggregate.items():
        attempts = int(item.get("attempts") or 0)
        correct = int(item.get("correct") or 0)

        if attempts > 0:
            mastery = float(item.get("_weighted_mastery") or 0.0) / attempts
        else:
            mastery = 0.0

        cleaned[skill_id] = {
            "attempts": attempts,
            "correct": correct,
            "mastery": mastery,
        }

    return cleaned


def merged_bac_matematica_m1_progress() -> dict:
    progress = load_or_initialize_bac_matematica_m1_progress()
    aggregated = aggregate_bac_matematica_m1_progress_from_study_outputs()

    merged = dict(progress)
    merged_skills = dict(progress.get("skills", {}))

    for skill_id, state in aggregated.items():
        if int(state.get("attempts") or 0) > 0:
            merged_skills[skill_id] = state

    merged["skills"] = merged_skills
    return merged

# --- v0.4.6 hotfix: robust skill tree parser ---
def _v46_skill_items() -> list[dict]:
    tree = _v46_load_skill_tree()
    items = []
    seen = set()

    id_keys = (
        "id",
        "skill_id",
        "exam_prep_skill_id",
        "slug",
        "key",
        "code",
    )

    label_keys = (
        "name_ro",
        "title_ro",
        "label_ro",
        "display_name_ro",
        "skill_name_ro",
        "name",
        "title",
        "label",
        "display_name",
        "skill_name",
        "skill_label",
    )

    description_keys = (
        "description_ro",
        "summary_ro",
        "objective_ro",
        "description",
        "summary",
        "objective",
    )

    skip_ids = {
        "bac",
        "matematica",
        "matematica_m1",
        "bac_matematica_m1",
        "root",
        "exam_prep",
    }

    def pick_from_keys(item: dict, keys: tuple[str, ...]) -> str:
        for key in keys:
            if key in item:
                text = _v46_as_text(item.get(key))
                if text:
                    return text
        return ""

    for item in _v46_walk(tree):
        if not isinstance(item, dict):
            continue

        skill_id = pick_from_keys(item, id_keys)
        label = pick_from_keys(item, label_keys)
        description = pick_from_keys(item, description_keys)

        if not skill_id or not label:
            continue

        normalized_id = skill_id.strip()
        if normalized_id.lower() in skip_ids:
            continue

        if normalized_id in seen:
            continue

        seen.add(normalized_id)

        normalized = dict(item)
        normalized["id"] = normalized_id
        normalized.setdefault("name_ro", label)

        if description:
            normalized.setdefault("description_ro", description)
        else:
            normalized.setdefault(
                "description_ro",
                "Skill din planul de pregătire Bacalaureat Matematică M1. Progresul se actualizează pe baza întrebărilor lucrate în Study Mode.",
            )

        items.append(normalized)

    if items:
        return items

    # Safety fallback only if the JSON structure changes and no skill can be inferred.
    return [
        {
            "id": "derivate",
            "name_ro": "Derivate",
            "description_ro": "Reguli de derivare, monotonia funcțiilor și aplicații pentru Bacalaureat Matematică M1.",
        },
        {
            "id": "integrale",
            "name_ro": "Integrale",
            "description_ro": "Primitive, integrale definite și aplicații pentru Bacalaureat Matematică M1.",
        },
        {
            "id": "functii",
            "name_ro": "Funcții",
            "description_ro": "Funcții, grafice, proprietăți și interpretare pentru Bacalaureat Matematică M1.",
        },
        {
            "id": "geometrie",
            "name_ro": "Geometrie",
            "description_ro": "Elemente de geometrie relevante pentru Bacalaureat Matematică M1.",
        },
    ]
# --- end v0.4.6 hotfix: robust skill tree parser ---

# --- v0.4.8 stable Exam Prep skill detail helpers ---
from html import escape as _v48_escape
from pathlib import Path as _V48Path
from urllib.parse import quote as _v48_quote
import json as _v48_json


def _v48_repo_root() -> _V48Path:
    return _V48Path(__file__).resolve().parents[2]


def _v48_skill_tree_path() -> _V48Path:
    return _v48_repo_root() / "assets" / "exam_prep" / "bac" / "matematica_m1" / "skill_tree.json"


def _v48_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("ro", "en", "label", "name", "title", "text", "description"):
            found = _v48_text(value.get(key))
            if found:
                return found
        return ""
    return str(value).strip()


def _v48_walk(value):
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from _v48_walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _v48_walk(child)


def _v48_pick(item: dict, keys: tuple[str, ...]) -> str:
    for key in keys:
        if key in item:
            value = _v48_text(item.get(key))
            if value:
                return value
    return ""


def _v48_fallback_skills() -> list[dict]:
    return [
        {
            "id": "derivate",
            "label": "Derivate",
            "description": "Reguli de derivare, monotonia funcțiilor și aplicații pentru Bacalaureat Matematică M1.",
        },
        {
            "id": "integrale",
            "label": "Integrale",
            "description": "Primitive, integrale definite și aplicații pentru Bacalaureat Matematică M1.",
        },
        {
            "id": "functii",
            "label": "Funcții",
            "description": "Funcții, grafice, proprietăți și interpretare pentru Bacalaureat Matematică M1.",
        },
        {
            "id": "geometrie",
            "label": "Geometrie",
            "description": "Elemente de geometrie relevante pentru Bacalaureat Matematică M1.",
        },
    ]


def _v48_skill_catalog() -> list[dict]:
    path = _v48_skill_tree_path()

    if not path.exists():
        return _v48_fallback_skills()

    try:
        tree = _v48_json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return _v48_fallback_skills()

    id_keys = ("id", "skill_id", "exam_prep_skill_id", "slug", "key", "code")
    label_keys = (
        "name_ro",
        "title_ro",
        "label_ro",
        "display_name_ro",
        "skill_name_ro",
        "name",
        "title",
        "label",
        "display_name",
        "skill_name",
    )
    description_keys = (
        "description_ro",
        "summary_ro",
        "objective_ro",
        "description",
        "summary",
        "objective",
    )

    skip_ids = {
        "root",
        "bac",
        "bac_matematica_m1",
        "matematica",
        "matematica_m1",
        "exam_prep",
    }

    items = []
    seen = set()

    for node in _v48_walk(tree):
        if not isinstance(node, dict):
            continue

        skill_id = _v48_pick(node, id_keys)
        label = _v48_pick(node, label_keys)

        if not skill_id or not label:
            continue

        normalized_id = skill_id.strip()
        if normalized_id.lower() in skip_ids:
            continue

        if normalized_id in seen:
            continue

        seen.add(normalized_id)

        description = _v48_pick(node, description_keys)
        if not description:
            description = "Skill din planul de pregătire Bacalaureat Matematică M1. Progresul se actualizează pe baza întrebărilor lucrate în Study Mode."

        items.append(
            {
                "id": normalized_id,
                "label": label,
                "description": description,
            }
        )

    return items or _v48_fallback_skills()


def _v48_skill_by_id(skill_id: str) -> dict | None:
    wanted = (skill_id or "").strip()
    for skill in _v48_skill_catalog():
        if skill["id"] == wanted:
            return skill
    return None


def _v48_linked_question_count(skill_id: str) -> int:
    data_root = _v48_repo_root() / "data"
    if not data_root.exists():
        return 0

    count = 0
    for path in data_root.rglob("quiz.study.json"):
        try:
            data = _v48_json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        for item in _v48_walk(data):
            if isinstance(item, dict) and _v48_text(item.get("exam_prep_skill_id")) == skill_id:
                count += 1

    return count


def render_exam_prep_skill_links_html() -> str:
    links = []

    for skill in _v48_skill_catalog():
        href = "/exam-prep/skill/" + _v48_quote(skill["id"], safe="")
        label = _v48_escape(skill["label"])
        links.append(
            '<a style="display:block;border:1px solid #e5e7ef;border-radius:14px;'
            'padding:12px;text-decoration:none;color:#172033;background:#fff;font-weight:650;" '
            f'href="{href}">{label}</a>'
        )

    return (
        '<section class="exam-prep-skill-detail-links" style="margin-top:24px;background:#fff;'
        'border:1px solid #e5e7ef;border-radius:18px;padding:20px;">'
        '<h2>Detalii pe skill</h2>'
        '<p style="color:#667085;line-height:1.55;">'
        'Deschide un skill pentru descriere, progres și pașii de continuare în Modul Studiu.'
        '</p>'
        '<div class="skill-link-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:10px;margin-top:14px;">'
        + "".join(links)
        + '</div></section>'
    )


def render_exam_prep_skill_detail_page(skill_id: str) -> tuple[str, int]:
    skill = _v48_skill_by_id(skill_id)

    if skill is None:
        safe_id = _v48_escape(skill_id or "")
        html = (
            '<!doctype html><html lang="ro"><head><meta charset="utf-8">'
            '<title>Exam Prep - Skill indisponibil</title>'
            '</head><body>'
            '<main><h1>Skill indisponibil</h1>'
            f'<p>Nu am gasit skill-ul: {safe_id}</p>'
            '<p><a href="/exam-prep">Înapoi la Pregătire examene</a></p>'
            '</main></body></html>'
        )
        return html, 404

    label = _v48_escape(skill["label"])
    description = _v48_escape(skill["description"])
    linked_questions = _v48_linked_question_count(skill["id"])

    status_ro = "În progres" if linked_questions > 0 else "Nepornit"
    status_hint = "Consolidat după lucru suficient în Study Mode"

    html = (
        '<!doctype html><html lang="ro"><head><meta charset="utf-8">'
        f'<title>Exam Prep - {label}</title>'
        '<style>'
        'body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#f7f7fb;color:#172033;}'
        'main{max-width:980px;margin:0 auto;padding:32px 20px 56px;}'
        '.card{background:#fff;border:1px solid #e5e7ef;border-radius:18px;padding:22px;box-shadow:0 10px 32px rgba(23,32,51,.06);}'
        '.muted{color:#667085;line-height:1.55;}'
        '.actions{display:flex;flex-wrap:wrap;gap:10px;margin-top:20px;}'
        '.button{display:inline-flex;align-items:center;justify-content:center;border-radius:999px;padding:10px 14px;text-decoration:none;border:1px solid #cfd6e6;color:#172033;background:#fff;font-weight:650;}'
        '.button.primary{background:#172033;color:#fff;border-color:#172033;}'
        '.metric-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px;margin:18px 0;}'
        '.metric{background:#f8fafc;border:1px solid #e5e7ef;border-radius:14px;padding:14px;}'
        '.metric strong{display:block;font-size:1.35rem;margin-top:4px;}'
        '.study-entry{margin-top:22px;background:#f8fafc;border:1px solid #e5e7ef;border-radius:16px;padding:18px;}'
        '.study-entry h2{margin:0 0 10px;font-size:1.15rem;}'
        '.study-steps{margin:0;padding-left:22px;color:#344054;line-height:1.6;}'
        '.study-steps li{margin:6px 0;}'
        '</style></head><body><main><div class="card">'
        '<p class="muted">Pregătire examene - Bacalaureat - Matematică M1</p>'
        f'<h1>Detaliu skill: {label}</h1>'
        f'<p>{description}</p>'
        '<div class="metric-grid">'
        f'<div class="metric"><span>Stare consolidare</span><strong>{status_ro}</strong>'
        f'<small class="muted">{status_hint}</small></div>'
        '<div class="metric"><span>Scor progres</span><strong>-</strong>'
        '<small class="muted">read-only din Modul Studiu, unde există</small></div>'
        f'<div class="metric"><span>Întrebări asociate din Modul Studiu</span><strong>{linked_questions}</strong>'
        '<small class="muted">din quiz.study.json</small></div>'
        '</div>'
        '<section class="study-entry">'
        '<h2>Cum lucrezi acest skill?</h2>'
        '<ol class="study-steps">'
        '<li>Deschide un PDF generat din biblioteca Voila.</li>'
        '<li>Foloseste actiunea Study pentru intrebari legate de acest skill.</li>'
        '<li>Revino in Exam Prep pentru a vedea progresul actualizat din Study Mode.</li>'
        '</ol>'
        '<p class="muted">Obiectivul este sa ajungi treptat la nivel Consolidat, fara sa modificam motorul BKT existent.</p>'
        '</section>'
        '<div class="actions">'
        '<a class="button primary" href="/#library">Continuă în Modul Studiu</a>'
        '<a class="button" href="/exam-prep">Înapoi la Pregătire examene</a>'
        '<a class="button" href="/quick-tools">Quick Tools</a>'
        '</div>'
        '</div></main></body></html>'
    )

    return html, 200

# --- v0.4.9 skill detail study entry polish ---
# --- end v0.4.8 stable Exam Prep skill detail helpers ---

# --- v0.4.10 Exam Prep dashboard progress summary helpers ---
def _v410_skill_score_percent(skill_id: str) -> int | None:
    data_root = _v48_repo_root() / "data"
    if not data_root.exists():
        return None

    scores = []

    for path in data_root.rglob("study_state.json"):
        try:
            data = _v48_json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue

        for item in _v48_walk(data):
            if not isinstance(item, dict):
                continue

            item_skill_id = _v48_text(item.get("exam_prep_skill_id") or item.get("skill_id"))
            if item_skill_id != skill_id:
                continue

            for key in ("mastery", "p_mastery", "knowledge", "score"):
                raw_value = item.get(key)
                if raw_value is None:
                    continue

                try:
                    value = float(raw_value)
                except Exception:
                    continue

                if 0 <= value <= 1:
                    scores.append(value * 100)
                elif 1 < value <= 100:
                    scores.append(value)

    if not scores:
        return None

    return round(sum(scores) / len(scores))


def _v410_skill_status(skill_id: str) -> str:
    score = _v410_skill_score_percent(skill_id)
    linked_questions = _v48_linked_question_count(skill_id)

    if score is not None and score >= 85:
        return "Consolidat"

    if score is not None and score > 0:
        return "În progres"

    if linked_questions > 0:
        return "În progres"

    return "Nepornit"


def exam_prep_dashboard_progress_summary() -> dict:
    skills = _v48_skill_catalog()

    summary = {
        "total": len(skills),
        "nepornit": 0,
        "in_progres": 0,
        "consolidat": 0,
    }

    for skill in skills:
        status = _v410_skill_status(skill["id"])

        if status == "Consolidat":
            summary["consolidat"] += 1
        elif status == "În progres":
            summary["in_progres"] += 1
        else:
            summary["nepornit"] += 1

    return summary


def render_exam_prep_dashboard_progress_summary_html() -> str:
    summary = exam_prep_dashboard_progress_summary()

    total = summary["total"]
    nepornit = summary["nepornit"]
    in_progres = summary["in_progres"]
    consolidat = summary["consolidat"]

    return (
        '<section class="exam-prep-progress-summary-v0410" style="margin:0 0 24px;background:#fff;'
        'border:1px solid #e5e7ef;border-radius:18px;padding:20px;box-shadow:0 10px 32px rgba(23,32,51,.06);">'
        '<h2 style="margin:0 0 8px;">Rezumat progres</h2>'
        '<p style="color:#667085;line-height:1.55;margin:0 0 16px;">'
        'Sursa progres: Modul Studiu. Rezumatul este read-only și nu modifică motorul BKT existent.'
        '</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;">'
        '<div style="background:#f8fafc;border:1px solid #e5e7ef;border-radius:14px;padding:14px;">'
        '<span>Total skill-uri</span>'
        f'<strong style="display:block;font-size:1.45rem;margin-top:4px;">{total}</strong>'
        '</div>'
        '<div style="background:#f8fafc;border:1px solid #e5e7ef;border-radius:14px;padding:14px;">'
        '<span>Nepornit</span>'
        f'<strong style="display:block;font-size:1.45rem;margin-top:4px;">{nepornit}</strong>'
        '</div>'
        '<div style="background:#f8fafc;border:1px solid #e5e7ef;border-radius:14px;padding:14px;">'
        '<span>În progres</span>'
        f'<strong style="display:block;font-size:1.45rem;margin-top:4px;">{in_progres}</strong>'
        '</div>'
        '<div style="background:#f8fafc;border:1px solid #e5e7ef;border-radius:14px;padding:14px;">'
        '<span>Consolidat</span>'
        f'<strong style="display:block;font-size:1.45rem;margin-top:4px;">{consolidat}</strong>'
        '</div>'
        '</div>'
        '</section>'
    )
# --- end v0.4.10 Exam Prep dashboard progress summary helpers ---

# --- v0.4.11 Exam Prep dashboard skill cards helpers ---
def _v411_skill_status_for_card(skill_id: str) -> str:
    try:
        return _v410_skill_status(skill_id)
    except Exception:
        try:
            linked_questions = _v48_linked_question_count(skill_id)
        except Exception:
            linked_questions = 0
        return "În progres" if linked_questions > 0 else "Nepornit"


def render_exam_prep_dashboard_skill_cards_html() -> str:
    cards = []

    for skill in _v48_skill_catalog():
        skill_id = skill["id"]
        label = _v48_escape(skill["label"])
        description = _v48_escape(skill.get("description", ""))
        href = "/exam-prep/skill/" + _v48_quote(skill_id, safe="")
        raw_status = _v411_skill_status_for_card(skill_id)
        if raw_status == "În progres":
            raw_status = "În progres"
        status = _v48_escape(raw_status)

        cards.append(
            '<article style="background:#fff;border:1px solid #e5e7ef;border-radius:16px;'
            'padding:16px;box-shadow:0 8px 24px rgba(23,32,51,.05);">'
            f'<h3 style="margin:0 0 8px;">{label}</h3>'
            f'<p style="color:#667085;line-height:1.5;margin:0 0 12px;">{description}</p>'
            '<div style="display:flex;flex-wrap:wrap;align-items:center;gap:10px;justify-content:space-between;">'
            f'<span style="display:inline-flex;border:1px solid #cfd6e6;border-radius:999px;padding:6px 10px;font-weight:650;">Status: {status}</span>'
            f'<a href="{href}" style="display:inline-flex;border-radius:999px;padding:8px 12px;'
            'background:#172033;color:#fff;text-decoration:none;font-weight:650;">Vezi detalii</a>'
            '</div>'
            '</article>'
        )

    return (
        '<section class="exam-prep-skill-cards-v0411" style="margin:24px 0;background:#f8fafc;'
        'border:1px solid #e5e7ef;border-radius:18px;padding:20px;">'
        '<h2 style="margin:0 0 8px;">Skill-uri Exam Prep</h2>'
        '<p style="color:#667085;line-height:1.55;margin:0 0 16px;">'
        'Alege un skill pentru descriere, status și pașii de lucru în Modul Studiu.'
        '</p>'
        '<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:14px;">'
        + "".join(cards)
        + '</div></section>'
    )
# --- end v0.4.11 Exam Prep dashboard skill cards helpers ---

# --- v0.4.12 Romanian UI polish ---

# --- v0.4.15 related Modul Studiu questions display helpers ---
from html import escape as _v415_escape


def render_exam_prep_related_study_questions_html(skill_id: str) -> str:
    try:
        linked_questions = _v48_linked_question_count(skill_id)
    except Exception:
        linked_questions = 0

    if linked_questions == 1:
        count_text = "1 întrebare asociată detectată"
        helper_text = "Răspunde la întrebarea asociată în Modul Studiu, iar progresul se va actualiza aici."
    elif linked_questions > 1:
        count_text = f"{linked_questions} întrebări asociate detectate"
        helper_text = "Răspunde la întrebările asociate în Modul Studiu, iar progresul se va actualiza aici."
    else:
        count_text = "Nu există încă întrebări asociate detectate"
        helper_text = "Răspunde la întrebări în Modul Studiu, iar progresul se va actualiza aici."

    safe_count_text = _v415_escape(count_text)
    safe_helper_text = _v415_escape(helper_text)

    return (
        '<section class="exam-prep-related-study-questions-v0415" '
        'style="margin-top:22px;background:#fff;border:1px solid #e5e7ef;border-radius:16px;padding:18px;">'
        '<h2>Întrebări asociate din Modul Studiu</h2>'
        f'<p><strong>{safe_count_text}</strong></p>'
        f'<p>{safe_helper_text}</p>'
        '<p style="color:#667085;line-height:1.55;">'
        'Acest rezumat este read-only și folosește progresul existent din Modul Studiu.'
        '</p>'
        '<div class="actions" style="display:flex;flex-wrap:wrap;gap:10px;margin-top:14px;">'
        '<a class="button primary" href="/#library">Continuă în Modul Studiu</a>'
        '<a class="button" href="/exam-prep">Înapoi la Pregătire examene</a>'
        '</div>'
        '</section>'
    )


_v415_base_render_exam_prep_skill_detail_page = render_exam_prep_skill_detail_page


def render_exam_prep_skill_detail_page(skill_id: str) -> tuple[str, int]:
    html, status_code = _v415_base_render_exam_prep_skill_detail_page(skill_id)

    if status_code != 200:
        return html, status_code

    if "exam-prep-related-study-questions-v0415" in html:
        return html, status_code

    section = render_exam_prep_related_study_questions_html(skill_id)

    if '<div class="actions">' in html:
        html = html.replace('<div class="actions">', section + '<div class="actions">', 1)
    elif "</main>" in html:
        html = html.replace("</main>", section + "</main>", 1)
    elif "</body>" in html:
        html = html.replace("</body>", section + "</body>", 1)
    else:
        html = html + section

    return html, status_code
# --- end v0.4.15 related Modul Studiu questions display helpers ---

# --- v0.4.16 next recommended action display helpers ---
def _v416_skill_status_for_next_action(skill_id: str) -> str:
    try:
        return _v410_skill_status(skill_id)
    except Exception:
        try:
            linked_questions = _v48_linked_question_count(skill_id)
        except Exception:
            linked_questions = 0

        return "În progres" if linked_questions > 0 else "Nepornit"


def render_exam_prep_next_action_html(skill_id: str) -> str:
    raw_status = _v416_skill_status_for_next_action(skill_id)

    if raw_status == "In progres":
        raw_status = "În progres"

    if raw_status == "Consolidat":
        title = "Acțiune recomandată"
        action = "Menține skill-ul consolidat prin recapitulări scurte în Modul Studiu."
        note = "Poți reveni periodic la întrebările asociate pentru a păstra progresul stabil."
    elif raw_status == "În progres":
        title = "Acțiune recomandată"
        action = "Continuă cu întrebările asociate în Modul Studiu."
        note = "Răspunsurile noi vor actualiza treptat progresul afișat aici."
    else:
        title = "Acțiune recomandată"
        action = "Începe cu un PDF generat și răspunde la primele întrebări în Modul Studiu."
        note = "După primele răspunsuri, statusul skill-ului se va actualiza automat aici."

    safe_title = _v48_escape(title)
    safe_status = _v48_escape(raw_status)
    safe_action = _v48_escape(action)
    safe_note = _v48_escape(note)

    return (
        '<section class="exam-prep-next-action-v0416" '
        'style="margin-top:22px;background:#f8fafc;border:1px solid #d9e2f1;border-radius:16px;padding:18px;">'
        f'<h2>{safe_title}</h2>'
        f'<p><strong>Status curent: {safe_status}</strong></p>'
        f'<p>{safe_action}</p>'
        f'<p style="color:#667085;line-height:1.55;">{safe_note}</p>'
        '<div class="actions" style="display:flex;flex-wrap:wrap;gap:10px;margin-top:14px;">'
        '<a class="button primary" href="/#library">Continuă în Modul Studiu</a>'
        '<a class="button" href="/exam-prep">Înapoi la Pregătire examene</a>'
        '</div>'
        '</section>'
    )


_v416_base_render_exam_prep_skill_detail_page = render_exam_prep_skill_detail_page


def render_exam_prep_skill_detail_page(skill_id: str) -> tuple[str, int]:
    html, status_code = _v416_base_render_exam_prep_skill_detail_page(skill_id)

    if status_code != 200:
        return html, status_code

    if "exam-prep-next-action-v0416" in html:
        return html, status_code

    section = render_exam_prep_next_action_html(skill_id)

    if "exam-prep-related-study-questions-v0415" in html:
        marker = "</section>"
        start = html.find("exam-prep-related-study-questions-v0415")
        end = html.find(marker, start)
        if end != -1:
            end = end + len(marker)
            html = html[:end] + section + html[end:]
        else:
            html = html + section
    elif '<div class="actions">' in html:
        html = html.replace('<div class="actions">', section + '<div class="actions">', 1)
    elif "</main>" in html:
        html = html.replace("</main>", section + "</main>", 1)
    elif "</body>" in html:
        html = html.replace("</body>", section + "</body>", 1)
    else:
        html = html + section

    return html, status_code
# --- end v0.4.16 next recommended action display helpers ---

# --- v0.4.17 dashboard next action summary helpers ---
def _v417_first_recommended_skill() -> dict | None:
    skills = _v48_skill_catalog()

    for preferred_status in ("În progres", "In progres", "Nepornit"):
        for skill in skills:
            try:
                status = _v410_skill_status(skill["id"])
            except Exception:
                status = "Nepornit"

            if status == "In progres":
                status = "În progres"

            if status == preferred_status:
                return {
                    "id": skill["id"],
                    "label": skill["label"],
                    "description": skill.get("description", ""),
                    "status": status,
                }

    if skills:
        skill = skills[0]
        return {
            "id": skill["id"],
            "label": skill["label"],
            "description": skill.get("description", ""),
            "status": "Nepornit",
        }

    return None


def render_exam_prep_dashboard_next_action_html() -> str:
    skill = _v417_first_recommended_skill()

    if skill is None:
        return (
            '<section class="exam-prep-dashboard-next-action-v0417" '
            'style="margin:0 0 24px;background:#fff;border:1px solid #e5e7ef;border-radius:18px;padding:20px;">'
            '<h2>Ce să faci acum?</h2>'
            '<p>Nu există încă skill-uri disponibile pentru Pregătire examene.</p>'
            '</section>'
        )

    skill_id = skill["id"]
    label = _v48_escape(skill["label"])
    status = _v48_escape(skill["status"])
    href = "/exam-prep/skill/" + _v48_quote(skill_id, safe="")

    if skill["status"] == "Consolidat":
        action = "Menține progresul cu o recapitulare scurtă în Modul Studiu."
    elif skill["status"] == "În progres":
        action = "Continuă cu acest skill în Modul Studiu pentru a consolida progresul."
    else:
        action = "Începe cu acest skill și răspunde la primele întrebări în Modul Studiu."

    safe_action = _v48_escape(action)

    return (
        '<section class="exam-prep-dashboard-next-action-v0417" '
        'style="margin:0 0 24px;background:#fff;border:1px solid #d9e2f1;border-radius:18px;'
        'padding:20px;box-shadow:0 10px 32px rgba(23,32,51,.06);">'
        '<h2 style="margin:0 0 8px;">Ce să faci acum?</h2>'
        '<p style="color:#667085;line-height:1.55;margin:0 0 16px;">'
        'Recomandare simplă bazată pe statusul curent din Pregătire examene.'
        '</p>'
        '<div style="background:#f8fafc;border:1px solid #e5e7ef;border-radius:16px;padding:16px;">'
        f'<p style="margin:0 0 8px;"><strong>Skill recomandat: {label}</strong></p>'
        f'<p style="margin:0 0 8px;">Status curent: <strong>{status}</strong></p>'
        f'<p style="margin:0 0 14px;">{safe_action}</p>'
        f'<a href="{href}" style="display:inline-flex;border-radius:999px;padding:9px 13px;'
        'background:#172033;color:#fff;text-decoration:none;font-weight:650;">Vezi detalii</a>'
        '</div>'
        '</section>'
    )
# --- end v0.4.17 dashboard next action summary helpers ---

# --- v0.4.22b consolidated dashboard Romanian polish helper ---
def _v422b_polish_dashboard_ro_html(html: str) -> str:
    replacements = [
        ("Functii", "Funcții"),
        ("In progres", "În progres"),
        ("reprezentari", "reprezentări"),
        ("proprietati", "proprietăți"),
        ("interpretari", "interpretări"),
        ("Matematica M1", "Matematică M1"),
        ("Pregatire examene", "Pregătire examene"),
    ]

    for old, new in replacements:
        html = html.replace(old, new)

    return html
# --- end v0.4.22b consolidated dashboard Romanian polish helper ---

# --- v0.4.28 Exam Prep weak skill review entry helper ---
def render_exam_prep_weak_review_entry_html(context: str = "dashboard") -> str:
    safe_context = _v48_escape(str(context or "dashboard"))
    href = "/#library"

    if safe_context == "skill":
        intro = (
            "După ce ai lucrat întrebările din Modul Studiu, poți reveni la fluxul existent "
            "de revizuire pentru conceptele slabe detectate în cursuri."
        )
    else:
        intro = (
            "Folosește fluxul existent de revizuire pentru a relua conceptele slabe "
            "din cursurile generate și sesiunile de studiu."
        )

    safe_intro = _v48_escape(intro)

    return (
        '<section class="exam-prep-weak-review-entry-v0428" '
        f'data-context="{safe_context}" '
        'style="margin-top:18px;background:#fff;border:1px solid #e5e7ef;border-radius:16px;padding:18px;">'
        '<h2>Revizuire concepte slabe</h2>'
        f'<p style="color:#475467;line-height:1.55;margin:8px 0 14px;">{safe_intro}</p>'
        '<p style="color:#667085;line-height:1.55;margin:0 0 14px;">'
        'Această intrare este doar un link către funcționalitatea existentă. '
        'Nu schimbă algoritmul de progres sau modul de calcul al statusului.'
        '</p>'
        '<a href="/#library" '
        'style="display:inline-flex;border-radius:999px;padding:9px 13px;'
        'background:#172033;color:#fff;text-decoration:none;font-weight:650;">'
        'Deschide revizuirea conceptelor slabe'
        '</a>'
        '</section>'
    )
# --- end v0.4.28 Exam Prep weak skill review entry helper ---

# --- v0.4.22 consolidated Exam Prep dashboard rendering helper ---
def _v422_safe_dashboard_section(function_name: str) -> str:
    function = globals().get(function_name)

    if not callable(function):
        return ""

    try:
        html = function()
    except Exception:
        return ""

    if not isinstance(html, str):
        return ""

    return html.strip()


def render_exam_prep_dashboard_sections_html() -> str:
    sections = [
        _v422_safe_dashboard_section("render_exam_prep_dashboard_next_action_html"),
        _v422_safe_dashboard_section("render_exam_prep_dashboard_progress_summary_html"),
        _v422_safe_dashboard_section("render_exam_prep_dashboard_skill_cards_html"),
        render_exam_prep_weak_review_entry_html("dashboard"),
    ]

    sections = [section for section in sections if section]

    if not sections:
        return (
            '<div class="exam-prep-dashboard-consolidated-v0422 exam-prep-dashboard-order-v0418">'
            '<section><h2>Pregătire examene</h2>'
            '<p>Dashboard-ul Exam Prep nu are încă secțiuni disponibile.</p>'
            '</section></div>'
        )

    html = (
        '<div class="exam-prep-dashboard-consolidated-v0422 exam-prep-dashboard-order-v0418" '
        'style="display:grid;gap:18px;margin:0 0 24px;">'
        + "".join(sections)
        + "</div>"
    )

    return _v422b_polish_dashboard_ro_html(html)
# --- end v0.4.22 consolidated Exam Prep dashboard rendering helper ---

# --- v0.4.27 Exam Prep skill metadata display helper ---
def _v427_polish_metadata_ro_text(value: object) -> str:
    text = str(value or "").strip()

    replacements = [
        ("Functii", "Funcții"),
        ("functii", "funcții"),
        ("In progres", "În progres"),
        ("in progres", "în progres"),
        ("Matematica M1", "Matematică M1"),
        ("Pregatire examene", "Pregătire examene"),
        ("reprezentari", "reprezentări"),
        ("proprietati", "proprietăți"),
        ("interpretari", "interpretări"),
    ]

    for old, new in replacements:
        text = text.replace(old, new)

    return text


def _v427_skill_by_id(skill_id: str) -> dict:
    try:
        skills = _v48_skill_catalog()
    except Exception:
        skills = []

    for skill in skills:
        try:
            if str(skill.get("id", "")) == str(skill_id):
                return skill
        except Exception:
            continue

    return {"id": skill_id, "label": skill_id, "description": ""}


def _v427_first_existing_value(data: dict, keys: list[str], default: str = "") -> str:
    for key in keys:
        value = data.get(key)
        if value:
            return _v427_polish_metadata_ro_text(value)

    return default


def _v427_prerequisites_text(skill: dict) -> str:
    raw = (
        skill.get("prerequisites")
        or skill.get("prerequisite_ids")
        or skill.get("requires")
        or skill.get("depends_on")
        or []
    )

    if isinstance(raw, str):
        raw = [raw]

    if not isinstance(raw, list):
        return "Nu sunt definite condiții preliminare."

    cleaned = [_v427_polish_metadata_ro_text(item) for item in raw if str(item).strip()]

    if not cleaned:
        return "Nu sunt definite condiții preliminare."

    return ", ".join(cleaned)


def _v427_related_study_status(skill_id: str) -> str:
    try:
        status = _v416_skill_status_for_next_action(skill_id)
    except Exception:
        status = "Nepornit"

    status = _v427_polish_metadata_ro_text(status)

    try:
        linked_questions = _v48_linked_question_count(skill_id)
    except Exception:
        linked_questions = 0

    if linked_questions == 1:
        return f"{status} · 1 întrebare asociată"
    if linked_questions > 1:
        return f"{status} · {linked_questions} întrebări asociate"

    return f"{status} · fără întrebări asociate detectate"


def render_exam_prep_skill_metadata_html(skill_id: str) -> str:
    skill = _v427_skill_by_id(skill_id)

    label = _v427_polish_metadata_ro_text(skill.get("label") or skill_id)
    description = _v427_first_existing_value(
        skill,
        ["short_description", "description", "summary"],
        "Descriere scurtă indisponibilă momentan.",
    )
    topic_group = _v427_first_existing_value(
        skill,
        ["topic_group", "group", "category", "chapter", "unit", "domain", "strand"],
        "Matematică M1",
    )
    prerequisites = _v427_prerequisites_text(skill)
    study_status = _v427_related_study_status(skill_id)

    safe_label = _v48_escape(label)
    safe_description = _v48_escape(description)
    safe_topic_group = _v48_escape(topic_group)
    safe_prerequisites = _v48_escape(prerequisites)
    safe_study_status = _v48_escape(study_status)

    return (
        '<section class="exam-prep-skill-metadata-v0427" '
        'style="margin-top:22px;background:#fff;border:1px solid #e5e7ef;border-radius:16px;padding:18px;">'
        '<h2>Detalii skill</h2>'
        '<dl style="display:grid;grid-template-columns:minmax(120px,180px) 1fr;gap:10px 16px;margin:12px 0 0;">'
        '<dt style="font-weight:750;color:#344054;">Skill</dt>'
        f'<dd style="margin:0;">{safe_label}</dd>'
        '<dt style="font-weight:750;color:#344054;">Capitol</dt>'
        f'<dd style="margin:0;">{safe_topic_group}</dd>'
        '<dt style="font-weight:750;color:#344054;">Descriere</dt>'
        f'<dd style="margin:0;">{safe_description}</dd>'
        '<dt style="font-weight:750;color:#344054;">Condiții preliminare</dt>'
        f'<dd style="margin:0;">{safe_prerequisites}</dd>'
        '<dt style="font-weight:750;color:#344054;">Status Modul Studiu</dt>'
        f'<dd style="margin:0;">{safe_study_status}</dd>'
        '</dl>'
        '<p style="color:#667085;line-height:1.55;margin:14px 0 0;">'
        'Această secțiune este read-only și folosește skill tree-ul Exam Prep împreună cu progresul existent.'
        '</p>'
        '</section>'
    )
# --- end v0.4.27 Exam Prep skill metadata display helper ---

# --- v0.4.23 consolidated Exam Prep skill detail rendering helper ---
def _v423_safe_skill_detail_section(function_name: str, skill_id: str) -> str:
    function = globals().get(function_name)

    if not callable(function):
        return ""

    try:
        html = function(skill_id)
    except Exception:
        return ""

    if not isinstance(html, str):
        return ""

    return html.strip()


def _v423_polish_skill_detail_ro_html(html: str) -> str:
    replacements = [
        ("Functii", "Funcții"),
        ("In progres", "În progres"),
        ("Pregatire examene", "Pregătire examene"),
        ("Matematica M1", "Matematică M1"),
        ("Intrebari", "Întrebări"),
        ("Continua", "Continuă"),
        ("Inapoi", "Înapoi"),
    ]

    for old, new in replacements:
        html = html.replace(old, new)

    return html


def render_exam_prep_skill_detail_sections_html(skill_id: str) -> str:
    sections = [
        _v423_safe_skill_detail_section("render_exam_prep_skill_metadata_html", skill_id),
        _v423_safe_skill_detail_section("render_exam_prep_related_study_questions_html", skill_id),
        _v423_safe_skill_detail_section("render_exam_prep_next_action_html", skill_id),
        render_exam_prep_weak_review_entry_html("skill"),
    ]

    sections = [section for section in sections if section]

    if not sections:
        html = (
            '<div class="exam-prep-skill-detail-consolidated-v0423" '
            'style="display:grid;gap:18px;margin:22px 0;">'
            '<section><h2>Pregătire examene</h2>'
            '<p>Secțiunile pentru acest skill nu sunt încă disponibile.</p>'
            '</section></div>'
        )
        return _v423_polish_skill_detail_ro_html(html)

    html = (
        '<div class="exam-prep-skill-detail-consolidated-v0423" '
        'style="display:grid;gap:18px;margin:22px 0;">'
        + "".join(sections)
        + "</div>"
    )

    return _v423_polish_skill_detail_ro_html(html)
# --- end v0.4.23 consolidated Exam Prep skill detail rendering helper ---

# --- v0.4.24 Exam Prep wording wrapper cleanup checkpoint ---
# Legacy wording wrapper blocks were removed after dashboard/skill-detail rendering consolidation.
# The permanent smoke and health checkpoint remain the safety gate.
# --- end v0.4.24 Exam Prep wording wrapper cleanup checkpoint ---
