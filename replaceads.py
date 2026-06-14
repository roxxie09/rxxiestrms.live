#!/usr/bin/env python3
"""
add_mobile_layout.py
--------------------
Adds ONLY the mobile (portrait) layout media query to your stream pages:
 - stacks the layout, hides the chat in portrait,
 - makes the player tall (72vh),
 - lets the stream buttons wrap onto centered rows so none get cut off.

It changes nothing else. It is conservative:
 * Skips files that already have the block (idempotent).
 * Only edits a file whose <style> block has the expected classes
   (.fullplayer, #playerContainer, .embedchat, .streamchanger).
 * Anything unexpected is reported under "NEEDS REVIEW" and left untouched.

Usage:
    python3 add_mobile_layout.py /path/to/site             # apply to a folder
    python3 add_mobile_layout.py file1.html file2.html     # specific files
"""

import os
import re
import sys

MARKER = "Phones in PORTRAIT"

BLOCK = """        /* ---- Phones in PORTRAIT: hide chat, clean player, buttons wrap to fit ---- */
        @media (max-width: 768px) and (orientation: portrait) {
            .fullplayer {
                flex-direction: column;
                height: auto;
                margin-top: 12px;
            }
            #playerContainer {
                width: 100%;
                height: 72vh;
            }
            .embedchat {
                display: none;
            }
            .streamchanger {
                position: static;
                order: -1;
                top: auto;
                left: auto;
                width: 100%;
                margin: 0 0 10px;
                flex-wrap: wrap;
                justify-content: center;
                gap: 8px;
            }
            .streamchanger .streambutton {
                flex: 0 0 auto;
                white-space: nowrap;
                margin-right: 0;
                padding-left: 12px;
                padding-right: 12px;
            }
        }
"""

STYLE_RE = re.compile(r'(<style[^>]*>)(.*?)(</style>)', re.S | re.I)
REQUIRED = ['.fullplayer', '#playerContainer', '.embedchat', '.streamchanger']


def process(text):
    """Return (new_text, status, reason)."""
    if MARKER in text:
        return text, 'already', None

    # Find the <style> block that contains the player styles.
    target = None
    for m in STYLE_RE.finditer(text):
        if '.streamchanger' in m.group(2):
            target = m
            break
    if not target:
        return text, 'review', 'no <style> block containing .streamchanger found'

    css = target.group(2)
    missing = [c for c in REQUIRED if c not in css]
    if missing:
        return text, 'review', 'style block missing ' + ', '.join(missing)

    # Insert the block right before this style block's closing </style>.
    close_at = target.start(3)
    new_text = text[:close_at] + "\n" + BLOCK + "    " + text[close_at:]
    return new_text, 'updated', None


def gather_files(args):
    files = []
    paths = [a for a in args if not a.startswith('-')] or ['.']
    for p in paths:
        if os.path.isdir(p):
            for root, _d, names in os.walk(p):
                for n in names:
                    if n.lower().endswith(('.html', '.htm')):
                        files.append(os.path.join(root, n))
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"!! path not found: {p}")
    return sorted(set(files))


def main():
    args = sys.argv[1:]
    files = gather_files(args)
    if not files:
        print("No .html files found.")
        return

    updated = 0
    already = 0
    review = []

    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            review.append((path, f"could not read: {e}"))
            continue

        new_text, status, reason = process(text)
        if status == 'updated':
            updated += 1
            print(f"{path}: updated")
            with open(path, 'w', encoding='utf-8') as f:
                f.write(new_text)
        elif status == 'already':
            already += 1
            print(f"{path}: already has it")
        else:
            review.append((path, reason))
            print(f"{path}: NEEDS REVIEW - {reason}")

    print("\n" + "=" * 56)
    print("SUMMARY")
    print("=" * 56)
    print(f"Files scanned : {len(files)}")
    print(f"Updated       : {updated}")
    print(f"Already had it: {already}")
    if review:
        print(f"\n!! NEEDS REVIEW ({len(review)}):")
        for path, reason in review:
            print(f"   - {path}: {reason}")
    else:
        print("\nNothing flagged for review.")


if __name__ == '__main__':
    main()