from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

css = '''
    .floating-nav {
      position: fixed;
      right: 22px;
      bottom: 22px;
      z-index: 998;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .floating-nav button {
      min-width: 104px;
      border-radius: 999px;
      border: 1px solid var(--border);
      background: var(--accent);
      color: #fffaf0;
      box-shadow: 0 14px 34px rgba(0,0,0,0.28);
      opacity: 0.92;
    }

    .floating-nav button:hover {
      opacity: 1;
      transform: translateY(-1px);
    }

    @media (max-width: 760px) {
      .floating-nav {
        right: 12px;
        bottom: 12px;
      }

      .floating-nav button {
        min-width: 84px;
        padding: 7px 10px;
        font-size: 12px;
      }
    }
'''

if ".floating-nav" not in text:
    text = text.replace("</style>", css + "\n  </style>")

floating_html = '''
    <div class="floating-nav" aria-label="Quick navigation">
      <button type="button" onclick="window.scrollTo({ top: 0, behavior: 'smooth' })">↑ Top</button>
      <button type="button" onclick="window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' })">↓ Bottom</button>
    </div>
'''

if "Quick navigation" not in text:
    text = text.replace(
'''  </main>
</body>
</html>''',
'''  </main>
''' + floating_html + '''
</body>
</html>'''
    )

path.write_text(text, encoding="utf-8")
print("OK: floating Top / Bottom navigation added globally.")
