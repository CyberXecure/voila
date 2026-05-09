from pathlib import Path

path = Path("services/api/static/ocr_review_monaco.css")
text = path.read_text(encoding="utf-8")

marker = "/* OCR_MONACO_TOP_ROW_VISIBILITY_V1 */"

if marker not in text:
    text += r'''

/* OCR_MONACO_TOP_ROW_VISIBILITY_V1 */

/* Toolbar compact, ca să nu împingă/ascundă zona utilă */
#voilaMonacoToolbar {
  display: flex !important;
  gap: 6px !important;
  flex-wrap: wrap !important;
  align-items: center !important;
  margin: 6px 0 10px !important;
  position: relative !important;
  z-index: 20 !important;
}

#voilaMonacoToolbar button,
#voilaDocumentLanguage {
  padding: 6px 10px !important;
  font-size: 13px !important;
  line-height: 1.05 !important;
  min-height: 34px !important;
}

/* Editorul nu trebuie să taie widget-urile Monaco */
#voilaMonacoEditor {
  margin-top: 10px !important;
  overflow: visible !important;
  position: relative !important;
  z-index: 5 !important;
}

/* Monaco intern: lasă spațiu sus pentru primul rând + quick fix */
#voilaMonacoEditor .monaco-editor,
#voilaMonacoEditor .overflow-guard {
  border-radius: 14px !important;
}

#voilaMonacoEditor .monaco-scrollable-element {
  padding-top: 10px !important;
}

/* Widget-uri Monaco peste editor, nu sub header/buttons */
#voilaMonacoEditor .suggest-widget,
#voilaMonacoEditor .monaco-hover,
#voilaMonacoEditor .context-view,
#voilaMonacoEditor .quick-input-widget,
#voilaMonacoEditor .overflowingContentWidgets {
  z-index: 9999 !important;
}

/* Prima linie să nu stea lipită de marginea de sus */
#voilaMonacoEditor .view-lines {
  padding-top: 4px !important;
}
'''

path.write_text(text, encoding="utf-8")
print("OK: Monaco top row visibility CSS added.")
