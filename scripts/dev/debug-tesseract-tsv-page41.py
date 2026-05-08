from pathlib import Path
import os
import subprocess
import tempfile
import fitz

project = Path(".").resolve()
pdf = project / "data" / "input" / "Manualul Instalatiilor Electrice.pdf"
out_dir = project / "data" / "output" / "Manualul Instalatiilor Electrice" / "_debug_tsv"
out_dir.mkdir(parents=True, exist_ok=True)

tesseract = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
tessdata = project / ".tessdata"

env = os.environ.copy()
if tessdata.exists():
    env["TESSDATA_PREFIX"] = str(tessdata)

doc = fitz.open(pdf)
page = doc.load_page(40)  # page 41, zero-based index
pix = page.get_pixmap(matrix=fitz.Matrix(2.8, 2.8), alpha=False)

png = out_dir / "page_041_zoom_2_8.png"
pix.save(str(png))

print("PNG:", png)
print("PNG exists:", png.exists(), "size:", png.stat().st_size if png.exists() else 0)

print("")
print("=== Tesseract version ===")
r = subprocess.run(
    [tesseract, "--version"],
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
)
print("returncode:", r.returncode)
print((r.stdout or r.stderr)[:1200])

print("")
print("=== Tesseract langs ===")
r = subprocess.run(
    [tesseract, "--list-langs"],
    text=True,
    encoding="utf-8",
    errors="replace",
    capture_output=True,
    env=env,
)
print("returncode:", r.returncode)
print((r.stdout or r.stderr)[:1200])

tests = [
    ("stdout_tsv", [tesseract, str(png), "stdout", "-l", "ron+eng", "--psm", "6", "tsv"]),
    ("file_tsv", [tesseract, str(png), str(out_dir / "ocr_file"), "-l", "ron+eng", "--psm", "6", "tsv"]),
    ("stdout_text", [tesseract, str(png), "stdout", "-l", "ron+eng", "--psm", "6"]),
]

for name, cmd in tests:
    print("")
    print("===", name, "===")
    print("CMD:", " ".join(cmd))

    r = subprocess.run(
        cmd,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        env=env,
    )

    print("returncode:", r.returncode)
    print("stdout chars:", len(r.stdout or ""))
    print("stderr chars:", len(r.stderr or ""))

    if r.stderr:
        print("STDERR preview:")
        print(r.stderr[:1000])

    if r.stdout:
        print("STDOUT preview:")
        print("\n".join(r.stdout.splitlines()[:12]))

tsv_file = out_dir / "ocr_file.tsv"
txt_file = out_dir / "ocr_file.txt"

print("")
print("=== Output files ===")
for p in [tsv_file, txt_file]:
    print(p.name, "exists:", p.exists(), "size:", p.stat().st_size if p.exists() else 0)
    if p.exists():
        content = p.read_text(encoding="utf-8", errors="replace")
        print("preview:")
        print("\n".join(content.splitlines()[:12]))

print("")
print("DONE")
