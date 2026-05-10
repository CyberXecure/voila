from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# 1. Add display-time translator for Study questions.
if "def _study_question_display(" not in text:
    marker = '''def _ut(key: str, fallback: str) -> str:
    return str(_ui_texts().get(key) or fallback)
'''

    insert = marker + r'''

def _study_question_display(value: str) -> str:
    import re

    raw = str(value or "").strip()

    patterns = [
        r"^What technical point does the source state about\s+(.+?)\??$",
        r"^Under what condition or operating situation does the source describe\s+(.+?)\??$",
        r"^Name one key point supported by the source text in\s+['\"“”‘’](.+?)['\"“”‘’]\.?$",
        r"^Name one key point supported by the source text in\s+(.+?)\.?$",
        r"^What does the source state about\s+(.+?)\??$",
        r"^What does the text say about\s+(.+?)\??$",
        r"^What is stated about\s+(.+?)\??$",
        r"^What is the source saying about\s+(.+?)\??$",
    ]

    for pattern in patterns:
        match = re.match(pattern, raw, flags=re.IGNORECASE)

        if not match:
            continue

        concept = match.group(1).strip()
        concept = concept.rstrip(".?").strip()
        concept = concept.strip("'\"“”‘’")

        if concept:
            return f"Ce idee importantă susține sursa despre „{concept}”?"

    return raw
'''

    if marker not in text:
        raise SystemExit("Nu găsesc _ut helper pentru inserare.")

    text = text.replace(marker, insert, 1)


# 2. Replace Study question display.
old = '''<p style="font-size: 20px;"><strong>{html.escape(str(current.get("question")))}</strong></p>'''
new = '''<p style="font-size: 20px;"><strong>{html.escape(_study_question_display(str(current.get("question"))))}</strong></p>'''

if old in text:
    text = text.replace(old, new)


# 3. Patch any remaining hardcoded Correct / Incorrect buttons.
text = text.replace(
    '<button class="primary" type="submit">Correct</button>',
    '<button class="primary" type="submit">{_ut("correct", "Correct")}</button>'
)

text = text.replace(
    '<button type="submit">Correct</button>',
    '<button type="submit">{_ut("correct", "Correct")}</button>'
)

text = text.replace(
    '<button type="submit">Incorrect</button>',
    '<button type="submit">{_ut("incorrect", "Incorrect")}</button>'
)

path.write_text(text, encoding="utf-8")
print("OK: Study questions are translated at display time.")
