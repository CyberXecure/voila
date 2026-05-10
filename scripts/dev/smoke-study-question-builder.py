from pathlib import Path
import sys

PROJECT = Path(".").resolve()
sys.path.insert(0, str(PROJECT / "services" / "api"))

import study_questions

samples = [
    {
        "question": "What technical point does the source state about Partea IV?",
        "concept_title": "Partea IV",
    },
    {
        "question": "Under what condition or operating situation does the source describe Lipsa de gândire?",
        "concept_title": "Lipsa de gândire",
    },
    {
        "question": "Name one key point supported by the source text in 'PREFAŢA'.",
        "concept_title": "PREFAŢA",
    },
]

for item in samples:
    print(study_questions.build_study_question(PROJECT, "Manual-de-Supravietuire.pdf", item))
