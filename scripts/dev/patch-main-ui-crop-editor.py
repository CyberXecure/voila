from pathlib import Path

path = Path("services/api/web_app.py")
text = path.read_text(encoding="utf-8")

text = text.replace(
'''        figures_html = out_dir / "figures" / "figures.html"
        log_file = out_dir / "last_run.log"
''',
'''        figures_html = out_dir / "figures" / "figures.html"
        hybrid_figures_html = out_dir / "figures_hybrid" / "figures_hybrid.html"
        hybrid_manifest = out_dir / "figures_hybrid" / "figures_manifest.hybrid.json"
        log_file = out_dir / "last_run.log"
'''
)

text = text.replace(
'''        if figures_html.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="{output_url(pdf.stem, "figures", "figures.html")}">Figures</a>'
            )
''',
'''        if hybrid_figures_html.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="{output_url(pdf.stem, "figures_hybrid", "figures_hybrid.html")}">Figures</a>'
            )

        elif figures_html.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="{output_url(pdf.stem, "figures", "figures.html")}">Figures</a>'
            )

        if hybrid_manifest.exists():
            actions.append(
                f'<a class="btn" target="_blank" href="http://127.0.0.1:8790/?pdf={quote(pdf.name)}">Edit crops</a>'
            )
'''
)

path.write_text(text, encoding="utf-8")
print("OK: web_app.py updated with Hybrid Figures and Edit crops button.")
