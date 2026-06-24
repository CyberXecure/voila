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
