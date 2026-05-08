from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "data" / "output"

HYBRID = PROJECT_ROOT / "services" / "api" / "figure_exporter_hybrid.py"
VISUAL = PROJECT_ROOT / "services" / "api" / "figure_exporter_visual_fallback.py"
FIGURES_NAV = PROJECT_ROOT / "services" / "api" / "figures_nav_injector.py"


def figure_count(manifest_path: Path) -> int:
    if not manifest_path.exists():
        return 0

    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
        return len(data.get("figure_crops") or [])
    except Exception:
        return 0


def run_step(args: list[str], optional: bool = False) -> int:
    print("")
    print("RUN:", " ".join(args))

    result = subprocess.run(
        args,
        cwd=str(PROJECT_ROOT),
        text=True,
    )

    if result.returncode != 0 and not optional:
        raise SystemExit(result.returncode)

    return result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(description="Voila! smart figure exporter")
    parser.add_argument("pdf", help="Path to source PDF")
    parser.add_argument("--page-from", type=int, default=1)
    parser.add_argument("--page-to", type=int, default=0)
    parser.add_argument("--zoom", type=float, default=1.8)
    parser.add_argument("--max-items", type=int, default=180)
    parser.add_argument("--max-per-page", type=int, default=3)

    args = parser.parse_args()

    pdf_path = Path(args.pdf).resolve()

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    out_dir = OUTPUT_DIR / pdf_path.stem
    figures_dir = out_dir / "figures_hybrid"
    manifest_path = figures_dir / "figures_manifest.hybrid.json"
    figures_html = figures_dir / "figures_hybrid.html"

    print("=== Voila! smart figure export ===")
    print(f"PDF: {pdf_path}")

    print("")
    print("=== 1. Hybrid extraction ===")
    run_step(
        [
            sys.executable,
            str(HYBRID),
            str(pdf_path),
        ],
        optional=True,
    )

    count = figure_count(manifest_path)
    print(f"Hybrid figure count: {count}")

    if count == 0:
        print("")
        print("=== 2. Visual fallback extraction ===")

        visual_args = [
            sys.executable,
            str(VISUAL),
            str(pdf_path),
            "--page-from",
            str(args.page_from),
            "--zoom",
            str(args.zoom),
            "--max-items",
            str(args.max_items),
            "--max-per-page",
            str(args.max_per_page),
        ]

        if args.page_to > 0:
            visual_args.extend(["--page-to", str(args.page_to)])

        run_step(visual_args, optional=False)
    else:
        print("Visual fallback skipped because hybrid found figures.")

    if figures_html.exists():
        print("")
        print("=== 3. Inject figures navigation ===")
        run_step(
            [
                sys.executable,
                str(FIGURES_NAV),
                str(figures_html),
                pdf_path.name,
            ],
            optional=True,
        )
    else:
        print("")
        print("Figures HTML not found; navigation injection skipped.")

    final_count = figure_count(manifest_path)

    print("")
    print("Voila! smart figure export complete.")
    print(f"Final figure count: {final_count}")
    print(f"- {figures_html}")


if __name__ == "__main__":
    main()
