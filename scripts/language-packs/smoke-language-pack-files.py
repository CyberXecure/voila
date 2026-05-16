#!/usr/bin/env python3
"""
Smoke test for Voila! language pack files that future packaging should include.

Scope:
- standard library only
- checks files and JSON parseability
- no packaging changes
- no runtime changes
- no UI changes
"""

from __future__ import annotations

import json
from pathlib import Path


REQUIRED_JSON_FILES = (
    'language-packs/core/ro.language-pack.json',
    'language-packs/core/en.language-pack.json',
    'language-packs/samples/ro.language-pack.sample.json',
    'language-packs/samples/en.language-pack.sample.json',
    'language-packs/schema/language-pack.schema.json',
)


REQUIRED_TEXT_FILES = (
    'language-packs/runtime/minimal_language_runtime.py',
    'scripts/language-packs/validate-language-packs.py',
    'scripts/language-packs/test_language_pack_runtime.py',
    'scripts/language-packs/test_minimal_language_runtime.py',
    'scripts/language-packs/smoke-ui-language-endpoint.py',
    'scripts/language-packs/smoke-core-runtime-helper.py',
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding='utf-8'))


def check_json_file(root: Path, relative_path: str, errors: list[str]) -> None:
    path = root / relative_path

    if not path.exists():
        errors.append(f'Missing JSON file: {relative_path}')
        return

    try:
        data = load_json(path)
    except json.JSONDecodeError as exc:
        errors.append(f'Invalid JSON in {relative_path}: {exc}')
        return

    if not isinstance(data, dict):
        errors.append(f'JSON root must be an object: {relative_path}')
        return

    if relative_path.endswith('.language-pack.json') or relative_path.endswith('.language-pack.sample.json'):
        manifest = data.get('manifest')
        if not isinstance(manifest, dict):
            errors.append(f'Missing manifest object: {relative_path}')
            return

        language_code = manifest.get('language_code')
        if not isinstance(language_code, str) or not language_code:
            errors.append(f'Missing manifest.language_code: {relative_path}')


def check_text_file(root: Path, relative_path: str, errors: list[str]) -> None:
    path = root / relative_path

    if not path.exists():
        errors.append(f'Missing file: {relative_path}')
        return

    if path.stat().st_size <= 0:
        errors.append(f'File is empty: {relative_path}')


def main() -> int:
    root = repo_root()
    errors: list[str] = []

    for relative_path in REQUIRED_JSON_FILES:
        check_json_file(root, relative_path, errors)

    for relative_path in REQUIRED_TEXT_FILES:
        check_text_file(root, relative_path, errors)

    if errors:
        print('Language pack file smoke test failed.')
        print('')
        for error in errors:
            print(f'- {error}')
        return 1

    print('Language pack file smoke test passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
