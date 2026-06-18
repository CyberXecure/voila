from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from content_filter import should_exclude_study_item
except Exception:
    def should_exclude_study_item(**kwargs) -> bool:
        return False


TECHNICAL_KEYWORDS = [
    "se folosește", "se folosesc", "este utilizat", "sunt utilizate", "este destinat",
    "permite", "asigură", "reduce", "mărește", "crește", "scade", "trebuie", "necesar",
    "se recomandă", "se montează", "se alimentează", "funcționează", "comandă",
    "tensiune", "curent", "putere", "flux", "iluminare", "rezistență", "motor",
    "instalație", "protecție", "automatizare", "contact", "releu", "siguranță",
    "is used", "are used", "designed", "must", "should", "requires", "provides",
    "pressure", "temperature", "engine", "pump", "valve", "filter", "system",
]

RO_TOPIC_RULES = [
    ("sisteme de iluminat", ["sistem de iluminat", "sisteme de iluminat", "iluminat interior", "iluminat exterior"]),
    ("mărimi luminotehnice", ["flux luminos", "iluminare", "intensitate luminoasă", "luminanță"]),
    ("instalații electrice", ["instalații electrice", "instalația electrică", "alimentare cu energie"]),
    ("protecții electrice", ["protecție", "siguranță", "descărcări electrice", "supracurent"]),
    ("motoare electrice", ["motor electric", "motoare electrice", "rotor", "stator", "asincron", "sincron"]),
    ("sisteme de comandă automată", ["comandă automată", "releu", "contactor", "automatizare"]),
    ("măsurări electrice", ["măsurarea", "aparat de măsură", "voltmetru", "ampermetru", "wattmetru"]),
    ("surse de lumină", ["lămpi", "lampă", "fluorescente", "incandescență", "vapori de sodiu"]),
    ("corpuri de iluminat", ["corpuri de iluminat", "cil", "armătură de iluminat"]),
]

EN_TOPIC_RULES = [
    ("engine cycles", ["cycle", "diesel cycle", "indicator diagram"]),
    ("fuel injection", ["fuel injection", "injector", "atomized fuel"]),
    ("cooling systems", ["cooling", "coolant"]),
    ("lubricating oil systems", ["lubricating oil", "lube oil"]),
    ("filters and strainers", ["filter", "strainer"]),
    ("marine diesel engines", ["diesel engine", "propulsion", "bore", "stroke"]),
]


BAD_SENTENCE_PATTERNS = [
    r"^figure\s+",
    r"^fig\.\s+",
    r"^figura\s+",
    r"^table\s+",
    r"^tabel\s+",
    r"^\d+$",
    r"^chapter\s+\d+",
    r"^capitolul\s+\d+",
    r"^cuprins\b",
    r"^bibliografie\b",
]


def normalize_space(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normalize_key(value: str) -> str:
    return normalize_space(value).lower()


def is_noisy_concept_title(value: str) -> bool:
    title = normalize_space(value)
    lower = title.lower()

    if not title:
        return True

    if len(title) < 3:
        return True

    if len(title) > 90:
        return True

    if lower in {"prof", "prof.", "credit", "source", "figure", "fig.", "table"}:
        return True

    if any(
        phrase in lower
        for phrase in [
            "department of energy",
            "wikimedia commons",
            "nasa/ames",
            "ames research center",
            "modification of work",
            "credit a",
            "credit b",
            "credit c",
            "courtesy of",
        ]
    ):
        return True

    if re.search(r"^\s*(fig\.|figure|table|caption)\b", lower):
        return True

    letters = len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]", title))
    digits = len(re.findall(r"\d", title))

    if digits > letters and letters < 4:
        return True

    if len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]{3,}", title)) < 1:
        return True

    return False


def clean_concept_title(value: str, fallback: str = "") -> str:
    title = normalize_space(value)

    if " — " in title:
        title = title.split(" — ", 1)[1]

    title = re.sub(
        r"\([^)]*\b(credit|source|wikimedia|commons|nasa|ames|department of energy|modification of work)\b[^)]*\)",
        "",
        title,
        flags=re.IGNORECASE,
    )
    title = re.sub(r"\bcredit\s+[a-z]?\s*:.*$", "", title, flags=re.IGNORECASE)
    title = re.sub(r"\bmodification of work by\b.*$", "", title, flags=re.IGNORECASE)

    title = normalize_space(title)
    title = title.strip(" .,:;—–-()[]{}'\"“”‘’")
    title = re.sub(r"[\)\]\}]+$", "", title).strip(" .,:;—–-")

    if is_noisy_concept_title(title):
        return fallback

    return title[:90]


def detect_language(text: str) -> str:
    lower = normalize_key(text)
    ro_markers = [
        " și ", " în ", " este ", " sunt ", " pentru ", " care ", " instala",
        "măsur", "funcție", "tensiune", "curent", "iluminat", "protecție",
        "ă", "î", "ș", "ț", "â",
    ]

    score = sum(1 for marker in ro_markers if marker in lower)

    return "ro" if score >= 2 else "en"


def split_sentences(text: str) -> list[str]:
    text = normalize_space(text)

    if not text:
        return []

    parts = re.split(r"(?<=[.!?])\s+(?=[A-ZĂÂÎȘȚ0-9])", text)
    out = []

    for part in parts:
        sentence = normalize_space(part)

        if 55 <= len(sentence) <= 420:
            out.append(sentence)

    return out


def extract_lessons(course_md: str) -> list[dict]:
    pattern = re.compile(r"^##\s+(L\d+)\s+—\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(course_md))
    lessons = []

    for idx, match in enumerate(matches):
        lesson_id = match.group(1).strip()
        title = match.group(2).strip()

        start = match.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(course_md)
        block = course_md[start:end]

        pages = []
        pages_match = re.search(r"Source PDF pages:\s*([0-9,\s]+)", block)

        if pages_match:
            pages = [
                int(item.strip())
                for item in pages_match.group(1).split(",")
                if item.strip().isdigit()
            ]

        text_match = re.search(
            r"### Cleaned source text\s*```text\s*(.*?)\s*```",
            block,
            flags=re.DOTALL,
        )

        source_text = text_match.group(1).strip() if text_match else block.strip()

        lessons.append(
            {
                "lesson_id": lesson_id,
                "title": title,
                "source_pdf_pages": pages,
                "source_text": source_text,
            }
        )

    return lessons


def sentence_is_bad(sentence: str) -> bool:
    value = normalize_key(sentence)

    for pattern in BAD_SENTENCE_PATTERNS:
        if re.search(pattern, value):
            return True

    bad_fragments = [
        "generated by voila",
        "source pdf pages",
        "word count",
        "isbn",
        "editura",
        "coordonator",
        "tehnoredactare",
        "all rights reserved",
    ]

    if any(fragment in value for fragment in bad_fragments):
        return True

    if len(re.findall(r"[A-Za-zĂÂÎȘȚăâîșț]", sentence)) < 30:
        return True

    return False


def technical_score(sentence: str) -> int:
    lower = normalize_key(sentence)
    score = 0

    for keyword in TECHNICAL_KEYWORDS:
        if keyword in lower:
            score += 1

    if re.search(r"\b\d+(?:[.,]\d+)?\s*(v|kv|a|ma|w|kw|lm|lx|cd|hz|°|%)\b", lower):
        score += 2

    if ";" in sentence:
        score += 1

    if re.search(r"\b(fig\.|figura)\s*[ivxlcdm0-9]", lower):
        score += 1

    return score


def infer_concept_title(lesson_title: str, sentence: str, language: str) -> str:
    lower = normalize_key(sentence + " " + lesson_title)
    rules = RO_TOPIC_RULES if language == "ro" else EN_TOPIC_RULES
    fallback = "noțiuni tehnice" if language == "ro" else "technical fundamentals"

    for topic, keywords in rules:
        if any(keyword in lower for keyword in keywords):
            return clean_concept_title(topic, fallback=fallback) or fallback

    title = clean_concept_title(lesson_title, fallback="")

    if title:
        return title[:90]

    return fallback


def question_from_sentence(sentence: str, concept: str, language: str) -> tuple[str, str]:
    lower = normalize_key(sentence)

    has_number_or_unit = bool(
        re.search(
            r"\b\d+(?:[.,]\d+)?\s*(m|cm|mm|km|kg|g|s|min|h|hz|khz|mhz|n|pa|j|w|kw|v|a|ma|mol|k|°c|°|%)\b",
            lower,
        )
        or re.search(r"\b10[\-−–]?\d+\b", lower)
        or re.search(r"×\s*10", sentence)
    )

    if language == "ro":
        if re.search(r"\b(fig\.|figură|figura|tabel|diagramă|grafic|caption|legendă)\b", lower):
            return f"Ce detaliu din figură sau tabel oferă sursa pentru {concept}?", "visual_interpretation"

        if has_number_or_unit:
            return f"Ce detaliu numeric sau măsurătoare oferă sursa pentru {concept}?", "numeric_check"

        if re.search(r"\b(se numește|reprezintă|este definit|se definește|înseamnă|se referă la)\b", lower):
            return f"Cum definește sursa {concept}?", "definition"

        if re.search(r"\b(comparativ cu|în comparație|spre deosebire|față de|decât)\b", lower):
            return f"Ce comparație face sursa despre {concept}?", "comparison"

        if re.search(r"\b(de exemplu|cum ar fi|precum|inclusiv|include)\b", lower):
            return f"Ce exemplu oferă sursa pentru {concept}?", "example"

        if re.search(r"\b(se compune|este alcătuit|sunt alcătuite|conține|cuprinde|include|este format)\b", lower):
            return f"Din ce este alcătuit sau ce cuprinde {concept}?", "components"

        if re.search(r"\b(mai întâi|apoi|după aceea|următorul pas|proces|secvență|etapă)\b", lower):
            return f"Ce proces sau secvență descrie sursa pentru {concept}?", "process"

        if re.search(r"\b(se folosește|se folosesc|este utilizat|sunt utilizate|servește|rolul|scopul|funcția)\b", lower):
            return f"Care este rolul sau scopul descris pentru {concept}?", "purpose"

        if re.search(r"\b(trebuie|este necesar|sunt necesare|se recomandă|obligatoriu|necesită)\b", lower):
            return f"Ce cerință sau recomandare menționează sursa pentru {concept}?", "requirement"

        if re.search(r"\b(când|dacă|în cazul|la pornire|în timpul|în condiții)\b", lower):
            return f"În ce condiție sau situație descrie sursa {concept}?", "condition"

        if re.search(r"\b(deoarece|pentru că|astfel|ca urmare|determină|produce|duce la|rezultă)\b", lower):
            return f"Ce cauză, motiv sau efect descrie sursa pentru {concept}?", "cause_effect"

        return f"Ce precizare tehnică face sursa despre {concept}?", "technical_fact"

    if re.search(r"\b(fig\.|figure|table|diagram|graph|caption)\b", lower):
        return f"What figure or table detail does the source provide for {concept}?", "visual_interpretation"

    if has_number_or_unit:
        return f"What numerical detail or measurement does the source give for {concept}?", "numeric_check"

    if re.search(r"\b(is defined as|defined as|is called|are called|means|refers to|is equal to|is a measure of|is designed to be|is an?|is the)\b", lower):
        return f"How does the source define {concept}?", "definition"

    if re.search(r"\b(compared with|compared to|whereas|while|unlike|in contrast|versus| vs\.? )\b", lower):
        return f"What comparison does the source make about {concept}?", "comparison"

    if re.search(r"\b(for example|for instance|such as|including|e\.g\.)\b", lower):
        return f"What example does the source give for {concept}?", "example"

    if re.search(r"\b(consists of|contains|includes|is made of|are made of|comprises|is composed of)\b", lower):
        return f"What parts or components does the source describe for {concept}?", "components"

    if re.search(r"\b(first|then|next|finally|step|steps|process|sequence|procedure|involves)\b", lower):
        return f"What process or sequence does the source describe for {concept}?", "process"

    if re.search(r"\b(used to|used for|is used|are used|purpose|function|role|in order to|so that)\b", lower):
        return f"What purpose does the source describe for {concept}?", "purpose"

    if re.search(r"\b(must|should|required|requires|necessary|recommended|need to|has to)\b", lower):
        return f"What requirement or recommendation does the source state for {concept}?", "requirement"

    if re.search(r"\b(when|if|during|in case of|under .*condition|provided that)\b", lower):
        return f"Under what condition or situation does the source describe {concept}?", "condition"

    if re.search(r"\b(because|therefore|due to|causes|caused by|results in|leads to|as a result|so that)\b", lower):
        return f"What cause, reason, or effect does the source describe for {concept}?", "cause_effect"

    return f"What technical point does the source state about {concept}?", "technical_fact"


def lesson_passes_page_filter(pages: list[int], min_page: int) -> bool:
    if min_page <= 1:
        return True

    if not pages:
        return False

    return max(pages) >= min_page


def build_questions(lessons: list[dict], max_per_lesson: int, max_total: int, min_page: int) -> list[dict]:
    questions = []

    full_text = "\n".join(lesson.get("source_text") or "" for lesson in lessons)
    course_language = detect_language(full_text)

    for lesson in lessons:
        if len(questions) >= max_total:
            break

        lesson_id = lesson["lesson_id"]
        title = lesson["title"]
        pages = lesson.get("source_pdf_pages", [])
        source_text = lesson.get("source_text") or ""

        if not lesson_passes_page_filter(pages, min_page):
            continue

        if should_exclude_study_item(title=title, source_text=source_text, lesson_id=lesson_id):
            continue

        lesson_language = detect_language(source_text) if source_text else course_language

        candidates = []

        for sentence in split_sentences(source_text):
            if sentence_is_bad(sentence):
                continue

            if should_exclude_study_item(
                title=title,
                question="",
                answer=sentence,
                source_text=sentence,
                lesson_id=lesson_id,
            ):
                continue

            score = technical_score(sentence)

            if score <= 0:
                continue

            concept = infer_concept_title(title, sentence, lesson_language)

            candidates.append(
                {
                    "sentence": sentence,
                    "score": score,
                    "concept": concept,
                    "language": lesson_language,
                }
            )

        candidates.sort(key=lambda item: item["score"], reverse=True)

        used = set()
        lesson_count = 0

        for candidate in candidates:
            if lesson_count >= max_per_lesson or len(questions) >= max_total:
                break

            answer = candidate["sentence"]
            concept = candidate["concept"]
            language = candidate["language"]
            question_text, qtype = question_from_sentence(answer, concept, language)

            key = normalize_key(question_text)

            if key in used:
                continue

            used.add(key)
            qid = f"SQ{len(questions) + 1:04d}"

            questions.append(
                {
                    "question_id": qid,
                    "lesson_id": lesson_id,
                    "concept_id": f"{lesson_id} — {concept}",
                    "concept_title": concept,
                    "lesson_title": clean_concept_title(title, fallback=concept) or concept,
                    "question_type": qtype,
                    "language": language,
                    "question": question_text,
                    "answer": answer,
                    "source_pdf_pages": pages,
                    "source_sentence": answer,
                    "generator": "study_quiz_builder_v0.4.0_localized",
                }
            )

            lesson_count += 1

    return questions


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! localized source-based study quiz builder")
    parser.add_argument("output_dir")
    parser.add_argument("--max-per-lesson", type=int, default=4)
    parser.add_argument("--max-total", type=int, default=500)
    parser.add_argument("--min-page", type=int, default=1)

    args = parser.parse_args()

    output_dir = Path(args.output_dir).resolve()
    course_path = output_dir / "course.cleaned.md"

    if not course_path.exists():
        raise FileNotFoundError(f"course.cleaned.md not found: {course_path}")

    course_md = course_path.read_text(encoding="utf-8", errors="ignore")
    lessons = extract_lessons(course_md)

    questions = build_questions(
        lessons=lessons,
        max_per_lesson=args.max_per_lesson,
        max_total=args.max_total,
        min_page=args.min_page,
    )

    quiz = {
        "version": "0.4.0",
        "mode": "source_only_localized",
        "generator": "study_quiz_builder_v0.4.0_localized",
        "question_count": len(questions),
        "questions": questions,
    }

    out = output_dir / "quiz.study.json"
    out.write_text(json.dumps(quiz, ensure_ascii=False, indent=2), encoding="utf-8")

    print("Voila! localized study quiz generated successfully.")
    print(f"Lessons parsed: {len(lessons)}")
    print(f"Questions generated: {len(questions)}")
    print(f"- {out}")


if __name__ == "__main__":
    main()
