from pathlib import Path
import re

path = Path("services/api/figure_exporter_visual_fallback.py")
text = path.read_text(encoding="utf-8")

text = re.sub(
    r'''patterns = \[
        r"\(\?m\)\^\\s\*\(\?:figura\|figure\|fig\\\.\?\)\\s\*\(\[IVXLCDM0-9\]\+\(\?:\[\.\\-\]\[0-9\]\+\)\+\)\\\.\?\\s\+\(\.\{3,180\}\)\$",
        r"\(\?m\)\^\\s\*\(\[0-9\]\{1,2\}\\\.\[0-9\]\{1,2\}\)\\\.\\s\+\(\.\{3,180\}\)\$",
    \]''',
    '''patterns = [
        r"(?m)^\\s*(?:figura|figure|fig\\.?)\\s*([IVXLCDM0-9]+(?:[.\\-][0-9]+)+)\\.?\\s+(.{3,180})$",
    ]''',
    text,
)

text = re.sub(
    r'''patterns = \[
        r"\(\?im\)\^\\s\*\(\?:fig\\\.\|figura\)\\s\*\[IVXLCDM0-9\]\+\(\?:\[\.\\-\]\\d\+\)\*",
        r"\(\?im\)\^\\s\*\\d\{1,2\}\\\.\\d\{1,2\}\\\.\\s\+\[A-ZĂÂÎȘȚ\]",
    \]''',
    '''patterns = [
        r"(?im)^\\s*(?:fig\\.|figura)\\s*[IVXLCDM0-9]+(?:[.\\-]\\d+)*",
    ]''',
    text,
)

# Fallback simple if regex replacement did not catch exact text.
text = text.replace(
'''    patterns = [
        r"(?im)^\\s*(?:fig\\.|figura)\\s*[IVXLCDM0-9]+(?:[.\\-]\\d+)*",
        r"(?im)^\\s*\\d{1,2}\\.\\d{1,2}\\.\\s+[A-ZĂÂÎȘȚ]",
    ]
''',
'''    patterns = [
        r"(?im)^\\s*(?:fig\\.|figura)\\s*[IVXLCDM0-9]+(?:[.\\-]\\d+)*",
    ]
'''
)

text = text.replace(
'''    patterns = [
        r"(?m)^\\s*(?:figura|figure|fig\\.?)\\s*([IVXLCDM0-9]+(?:[.\\-][0-9]+)+)\\.?\\s+(.{3,180})$",
        r"(?m)^\\s*([0-9]{1,2}\\.[0-9]{1,2})\\.\\s+(.{3,180})$",
    ]
''',
'''    patterns = [
        r"(?m)^\\s*(?:figura|figure|fig\\.?)\\s*([IVXLCDM0-9]+(?:[.\\-][0-9]+)+)\\.?\\s+(.{3,180})$",
    ]
'''
)

path.write_text(text, encoding="utf-8")
print("OK: figure fallback now requires explicit Fig./Figura caption.")
