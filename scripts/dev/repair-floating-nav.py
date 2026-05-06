from pathlib import Path
import re

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

# Remove old floating nav CSS blocks if present
text = re.sub(
    r"\n\s*\.floating-nav\s*\{\{.*?@media\s*\(max-width:\s*760px\)\s*\{\{.*?\n\s*\}\}\s*\n",
    "\n",
    text,
    flags=re.DOTALL,
)

# Remove old floating nav HTML blocks if present
text = re.sub(
    r"\n\s*<div class=\"floating-nav\".*?</div>\s*\n",
    "\n",
    text,
    flags=re.DOTALL,
)

css = '''
    .floating-nav {{
      position: fixed;
      right: 22px;
      bottom: 22px;
      z-index: 9999;
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
      box-shadow: 0 14px 34px rgba(0,0,0,0.32);
      opacity: 0.96;
      font-weight: 800;
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

html_block = '''
    <div class="floating-nav" aria-label="Quick navigation">
      <button type="button" onclick="window.scrollTo({{ top: 0, behavior: 'smooth' }})">↑ Top</button>
      <button type="button" onclick="window.scrollTo({{ top: document.body.scrollHeight, behavior: 'smooth' }})">↓ Bottom</button>
    </div>
'''

if "</style>" not in text:
    raise SystemExit("Could not find </style> in web_app.py")

text = text.replace("</style>", css + "\n  </style>", 1)

if "</body>" not in text:
    raise SystemExit("Could not find </body> in web_app.py")

text = text.replace("</body>", html_block + "\n</body>", 1)

path.write_text(text, encoding="utf-8")

print("OK: floating Top / Bottom nav reinserted.")
