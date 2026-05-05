from pathlib import Path

path = Path("services/api/figure_exporter_hybrid.py")
text = path.read_text(encoding="utf-8")

old = '''    for old_png in crops_dir.glob("figure_*.png"):
        old_png.unlink()

'''

new = '''    # Keep existing crops.
    # Important: partial runs must not delete previously generated figures.
    # Missing/invalid images can be repaired with repair_hybrid_figures.py.

'''

text = text.replace(old, new)

path.write_text(text, encoding="utf-8")
print("OK: figure_exporter_hybrid.py no longer deletes existing crop PNG files.")
