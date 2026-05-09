from pathlib import Path

js_path = Path("services/api/static/ocr_review_monaco.js")
js = js_path.read_text(encoding="utf-8")

# 1. Monaco widgets outside editor clipping
if "fixedOverflowWidgets: true" not in js:
    js = js.replace(
'''        lightbulb: { enabled: true }''',
'''        lightbulb: { enabled: true },
        fixedOverflowWidgets: true'''
    )

# 2. Quick fix title: show replacement first, not LanguageTool prefix first.
js = js.replace(
'''                title: "LanguageTool: " + replacement,''',
'''                title: replacement + " — LanguageTool",'''
)

js_path.write_text(js, encoding="utf-8")


css_path = Path("services/api/static/ocr_review_monaco.css")
css = css_path.read_text(encoding="utf-8")

marker = "/* OCR_MONACO_WIDE_QUICK_FIX_V1 */"

if marker not in css:
    css += r'''

/* OCR_MONACO_WIDE_QUICK_FIX_V1 */

/* Quick Fix / Code Action widget wider, so suggestions are readable */
.monaco-editor .action-widget,
.monaco-editor .context-view,
.monaco-editor .monaco-menu,
.context-view,
.context-view .monaco-menu,
.monaco-menu-container {
  width: auto !important;
  min-width: 420px !important;
  max-width: min(760px, calc(100vw - 80px)) !important;
}

/* Do not ellipsis quick-fix labels too aggressively */
.monaco-editor .action-widget .action-label,
.monaco-editor .monaco-menu .action-label,
.context-view .action-label,
.monaco-menu-container .action-label {
  max-width: none !important;
  width: auto !important;
  overflow: visible !important;
  text-overflow: clip !important;
  white-space: nowrap !important;
}

/* Give the list itself enough room */
.monaco-editor .action-widget .action-list,
.monaco-editor .monaco-menu .actions-container,
.context-view .actions-container,
.monaco-menu-container .actions-container {
  width: auto !important;
  min-width: 420px !important;
}

/* If suggestion text is very long, allow a readable second line */
.monaco-editor .action-widget .monaco-list-row,
.monaco-editor .monaco-menu .monaco-list-row,
.context-view .monaco-list-row,
.monaco-menu-container .monaco-list-row {
  height: auto !important;
  min-height: 32px !important;
}
'''

css_path.write_text(css, encoding="utf-8")

print("OK: Monaco quick fix widget widened and labels improved.")
