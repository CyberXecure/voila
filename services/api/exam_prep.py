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
        "title": skill_tree.get("title", "Bacalaureat Matematica M1"),
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
            "description": "Reguli de derivare, monotonia functiilor si aplicatii pentru Bacalaureat Matematica M1.",
        },
        {
            "id": "integrale",
            "label": "Integrale",
            "description": "Primitive, integrale definite si aplicatii pentru Bacalaureat Matematica M1.",
        },
        {
            "id": "functii",
            "label": "Functii",
            "description": "Functii, grafice, proprietati si interpretare pentru Bacalaureat Matematica M1.",
        },
        {
            "id": "geometrie",
            "label": "Geometrie",
            "description": "Elemente de geometrie relevante pentru Bacalaureat Matematica M1.",
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
            description = "Skill din planul de pregatire Bacalaureat Matematica M1. Progresul se actualizeaza pe baza intrebarilor lucrate in Study Mode."

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
        'Deschide un skill pentru descriere, progres si pasii de continuare in Study Mode.'
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
            '<p><a href="/exam-prep">Inapoi la Exam Prep</a></p>'
            '</main></body></html>'
        )
        return html, 404

    label = _v48_escape(skill["label"])
    description = _v48_escape(skill["description"])
    linked_questions = _v48_linked_question_count(skill["id"])

    status_ro = "In progres" if linked_questions > 0 else "Nepornit"
    status_hint = "Consolidat dupa lucru suficient in Study Mode"

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
        '<p class="muted">Pregatire examene - Bacalaureat - Matematica M1</p>'
        f'<h1>Detaliu skill: {label}</h1>'
        f'<p>{description}</p>'
        '<div class="metric-grid">'
        f'<div class="metric"><span>Stare consolidare</span><strong>{status_ro}</strong>'
        f'<small class="muted">{status_hint}</small></div>'
        '<div class="metric"><span>Scor progres</span><strong>-</strong>'
        '<small class="muted">read-only din Study Mode, unde exista</small></div>'
        f'<div class="metric"><span>Intrebari Study legate</span><strong>{linked_questions}</strong>'
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
        '<a class="button primary" href="/#library">Continua in Study Mode</a>'
        '<a class="button" href="/exam-prep">Inapoi la Exam Prep</a>'
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
        return "In progres"

    if linked_questions > 0:
        return "In progres"

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
        elif status == "In progres":
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
        'Sursa progres: Study Mode. Rezumatul este read-only si nu modifica motorul BKT existent.'
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
        '<span>In progres</span>'
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
