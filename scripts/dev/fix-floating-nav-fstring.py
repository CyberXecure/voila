from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

css_fixed = '''    .floating-nav {{
      position: fixed;
      right: 22px;
      bottom: 22px;
      z-index: 998;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .floating-nav button {{
      min-width: 104px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--accent);
      color: #fffaf0;
      box-shadow: 0 14px 34px rgba(0,0,0,0.28);
      opacity: 0.92;
    }}

    .floating-nav button:hover {{
      opacity: 1;
      transform: translateY(-1px);
    }}

    @media (max-width: 760px) {{
      .floating-nav {{
        right: 12px;
        bottom: 12px;
      }}

      .floating-nav button {{
        min-width: 84px;
        padding: 7px 10px;
        font-size: 12px;
      }}
    }}
'''

start = text.find("    .floating-nav {")
if start == -1:
    start = text.find("    .floating-nav {{")

if start != -1:
    end = text.find("  </style>", start)
    if end == -1:
        raise SystemExit("Could not find </style> after floating nav CSS.")

    text = text[:start] + css_fixed + "\n" + text[end:]

text = text.replace(
    "window.scrollTo({ top: 0, behavior: 'smooth' })",
    "window.scrollTo({{ top: 0, behavior: 'smooth' }})"
)

text = text.replace(
    "window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })",
    "window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }})"
)

path.write_text(text, encoding="utf-8")

print("OK: floating nav braces fixed for Python f-string.")
