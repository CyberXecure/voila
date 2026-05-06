from __future__ import annotations

import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
INPUT_DIR = PROJECT_ROOT / "data" / "input"
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"
INJECTOR = PROJECT_ROOT / "services" / "api" / "course_nav_injector.py"


def find_pdf_name_for_output_dir(output_dir: Path) -> str:
    expected_pdf = INPUT_DIR / f"{output_dir.name}.pdf"

    if expected_pdf.exists():
        return expected_pdf.name

    matching = list(INPUT_DIR.glob(f"{output_dir.name}*.pdf"))

    if matching:
        return matching[0].name

    return f"{output_dir.name}.pdf"


def main() -> None:
    html_files = sorted(OUTPUT_DIR.glob("*/course.cleaned.html"))

    if not html_files:
        print("No course.cleaned.html files found.")
        return

    updated = 0
    failed = 0

    for html_path in html_files:
        output_dir = html_path.parent
        pdf_name = find_pdf_name_for_output_dir(output_dir)

        print("")
        print(f"Course: {html_path}")
        print(f"PDF:    {pdf_name}")

        result = subprocess.run(
            [
                sys.executable,
                str(INJECTOR),
                str(html_path),
                pdf_name,
            ],
            cwd=str(PROJECT_ROOT),
            text=True,
            capture_output=True,
        )

        if result.returncode == 0:
            updated += 1
            print("OK")
        else:
            failed += 1
            print("FAILED")
            print(result.stdout)
            print(result.stderr)

    print("")
    print("Voila! bulk course navigation injection complete.")
    print(f"Updated: {updated}")
    print(f"Failed:  {failed}")


if __name__ == "__main__":
    main()
