#!/usr/bin/env python3
import re
import sys
from pathlib import Path

TARGET = "window.onload = function() {\nwindow.onload = function() {"
REPLACEMENT = "window.onload = function() {"


def patch_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')

    if 'id="toggleChat"' not in text:
        return 'no_toggle'
    if TARGET not in text:
        return 'no_change'

    new_text = text.replace(TARGET, REPLACEMENT, 1)
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        return 'patched'
    return 'no_change'


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    files = sorted(root.rglob('*.html'))
    if not files:
        print('No HTML files found.')
        return

    patched = 0
    unchanged = 0

    for f in files:
        result = patch_file(f)
        if result == 'patched':
            patched += 1
            print(f'PATCHED  {f}')
        else:
            unchanged += 1
            print(f'NOCHANGE {f}')

    print(f"\nDone. patched={patched} unchanged={unchanged}")


if __name__ == '__main__':
    main()