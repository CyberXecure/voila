from pathlib import Path

path = Path("services/api/static/ocr_review_monaco.js")
text = path.read_text(encoding="utf-8")

# Add language detector after labelOf function.
if "function detectVoilaOcrLanguage" not in text:
    marker = '''  function labelOf(el) {
    return String((el && (el.textContent || el.value)) || "").trim().toLowerCase();
  }
'''
    insert = marker + r'''
  function detectVoilaOcrLanguage(value) {
    const text = String(value || "").toLowerCase();

    const roChars = /[ăâîșşțţ]/i.test(text) ? 4 : 0;

    const roWords = [
      "pentru", "este", "sunt", "care", "prin", "în", "din", "funcție",
      "tensiune", "curent", "lămpii", "instalații", "capitolul", "figura"
    ];

    const enWords = [
      "the", "and", "with", "from", "figure", "chapter", "valve",
      "engine", "fuel", "injection", "pressure", "temperature", "system"
    ];

    let roScore = roChars;
    let enScore = 0;

    roWords.forEach(function (word) {
      if (text.includes(word)) roScore += 1;
    });

    enWords.forEach(function (word) {
      if (text.includes(word)) enScore += 1;
    });

    if (enScore > roScore) return "en-US";
    return "ro-RO";
  }

'''
    if marker not in text:
        raise SystemExit("Nu găsesc locul pentru detectVoilaOcrLanguage.")

    text = text.replace(marker, insert)

# Replace hardcoded ro-RO in fetch body.
text = text.replace(
'''              language: "ro-RO"''',
'''              language: detectVoilaOcrLanguage(textarea.value || "")'''
)

# Improve status while checking.
text = text.replace(
'''        setStatus("<strong>LanguageTool:</strong> verific textul...");''',
'''        const detectedLanguage = detectVoilaOcrLanguage(textarea.value || "");
        setStatus("<strong>LanguageTool:</strong> verific textul cu limba " + detectedLanguage + "...");'''
)

# Make sure fetch body uses detectedLanguage if present.
text = text.replace(
'''              language: detectVoilaOcrLanguage(textarea.value || "")''',
'''              language: detectedLanguage'''
)

path.write_text(text, encoding="utf-8")
print("OK: Monaco LanguageTool now auto-detects ro-RO / en-US per manual text.")
