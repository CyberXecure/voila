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
    progress = load_or_initialize_bac_matematica_m1_progress()
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
