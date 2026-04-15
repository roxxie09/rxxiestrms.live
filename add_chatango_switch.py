#!/usr/bin/env python3
from pathlib import Path
import re
import sys

PATTERN = re.compile(
    r"""window\.onload\s*=\s*function\s*\(\)\s*\{\s*window\.onload\s*=\s*function\s*\(\)\s*\{(?P<toggle>.*?)\}\s*;\s*\n\s*showPlayer\('clappr',\s*'(?P<url>[^']+)'\);\s*\n\s*\}\s*;""",
    re.DOTALL
)


def replacer(match):
    toggle = match.group('toggle').rstrip()
    url = match.group('url')
    return (
        "showPlayer('clappr', '" + url + "');\n\n"
        "window.onload = function() {" + toggle + "\n    };"
    )


def patch_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    if 'id="toggleChat"' not in text:
        return 'no_toggle'
    if 'window.onload = function() {\nwindow.onload = function() {' not in text and 'window.onload = function() {\r\nwindow.onload = function() {' not in text:
        return 'no_change'

    new_text, count = PATTERN.subn(replacer, text, count=1)
    if count:
        path.write_text(new_text, encoding='utf-8')
        return 'patched'
    return 'no_change'


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    patched = 0
    unchanged = 0
    for f in sorted(root.rglob('*.html')):
        result = patch_file(f)
        if result == 'patched':
            patched += 1
            print(f'PATCHED  {f}')
        else:
            unchanged += 1
    print(f"\nDone. patched={patched} unchanged={unchanged}")


if __name__ == '__main__':
    main()