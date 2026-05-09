from pathlib import Path

path = Path("services/api/static/ocr_review_monaco.css")
text = path.read_text(encoding="utf-8")

if "#voilaDocumentLanguage" not in text:
    text += r'''

#voilaDocumentLanguage {
  padding: 7px 10px;
  font-size: 13px;
  line-height: 1.1;
  border-radius: 999px;
  border: 1px solid var(--line, #3b4b50);
  background: #111b1e;
  color: var(--text, #f4efe7);
}
'''

path.write_text(text, encoding="utf-8")
print("OK: language selector CSS added.")
