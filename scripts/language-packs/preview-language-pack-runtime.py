#!/usr/bin/env python3
"""
Preview the isolated Voila! language pack runtime scaffold.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from language_pack_runtime import create_default_runtime  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Preview Voila! language pack runtime scaffold."
    )

    parser.add_argument(
        "--language",
        default="en",
        help="Selected language code, for example ro or en.",
    )

    parser.add_argument(
        "--key",
        default="app.title",
        help="Translation key to preview.",
    )

    parser.add_argument(
        "--default",
        default=None,
        help="Optional default text when the key is missing.",
    )

    parser.add_argument(
        "--current",
        default=None,
        help="Placeholder value for {current}.",
    )

    parser.add_argument(
        "--total",
        default=None,
        help="Placeholder value for {total}.",
    )

    parser.add_argument(
        "--count",
        default=None,
        help="Placeholder value for {count}.",
    )

    parser.add_argument(
        "--field",
        default=None,
        help="Placeholder value for {field}.",
    )

    parser.add_argument(
        "--list-languages",
        action="store_true",
        help="List available language codes.",
    )

    return parser.parse_args()


def main() -> int:
    args = parse_args()
    runtime = create_default_runtime()

    if args.list_languages:
        print("\n".join(runtime.available_languages()))
        return 0

    placeholders = {}

    for name in ("current", "total", "count", "field"):
        value = getattr(args, name)
        if value is not None:
            placeholders[name] = value

    result = runtime.translate(
        key=args.key,
        language=args.language,
        default=args.default,
        **placeholders,
    )

    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
