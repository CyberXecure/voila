# Voila Complete Windows Runtime Source Helper Script Specification

Milestone:

```text
v0.3.51-voila-complete-windows-runtime-source-helper-script-plan
```

## Future script path

```text
scripts/release/create-complete-windows-runtime-source.ps1
```

## Inputs

```text
RuntimeSourceRoot
PythonStrategy
IncludeCropEditor
LanguageToolStrategy
OcrStrategy
Force
```

## Default strategy

```text
PythonStrategy: PackageVenv
IncludeCropEditor: false unless requested
LanguageToolStrategy: Deferred
OcrStrategy: Deferred
```

## Target root

```text
<RuntimeSourceRoot>\voila
```

## Required target structure

```text
voila/
  README-WINDOWS.txt
  RELEASE-NOTES.txt
  RUNTIME-SOURCE-SUMMARY.txt
  START-VOILA.bat
  STOP-VOILA.bat
  services/
    api/
      web_app.py
      requirements.txt
      *.py
  .venv/
    Scripts/
      python.exe
  scripts/
    start-voila.ps1
    stop-voila.ps1
    check-voila-health.ps1
  runtime/
    state/
    logs/
```

## Optional target structure

```text
services/api/crop_editor_app.py
runtime/java/
runtime/languagetool/
runtime/tesseract/
runtime/tessdata/
```

## Required validations

```text
[ ] RuntimeSourceRoot is not repository root
[ ] RuntimeSourceRoot is not docs/
[ ] RuntimeSourceRoot is not scripts/
[ ] RuntimeSourceRoot is not services/
[ ] services/api/web_app.py exists in source
[ ] services/api/web_app.py copied to target
[ ] .venv/Scripts/python.exe exists if PackageVenv selected
[ ] launcher files generated
[ ] launcher references web_app:app
[ ] launcher references services/api app-dir
[ ] Python import validation succeeds
[ ] forbidden file scan passes
[ ] RUNTIME-SOURCE-SUMMARY.txt created
```

## Exit behavior

Return non-zero on:

```text
unsafe target
missing web_app.py
missing package-local Python when required
copy failure
launcher generation failure
launcher alignment failure
import validation failure
forbidden file detection
```

## Expected success output

```text
Complete Windows runtime source created.
RuntimeSource: <RuntimeSourceRoot>\voila
Validation: PASS
```
