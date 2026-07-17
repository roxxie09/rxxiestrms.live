#!/usr/bin/env python3
"""
apply-pink-theme.py
-------------------------------------------------------------------
Adds the pink Clappr theme to every .html file in the SAME folder as
this script. For each file it does two things:

  1. Inserts  <script src="js/clappr-pink-theme.js"></script>
     right after the Clappr CDN <script> tag.

  2. Inserts  mediacontrol: ClapprPinkTheme.mediacontrol,
     into every  new Clappr.Player({ ... })  config
     (right after the  autoPlay: true,  line).

It is SAFE to run more than once - it skips anything already themed,
so it will never double-insert.

A .bak backup of each changed file is written next to it the first
time that file is modified.

USAGE
-----
  Put this file (and clappr-pink-theme.js) in the folder with your
  HTML files, then run:

      python3 apply-pink-theme.py

  Or preview without changing anything:

      python3 apply-pink-theme.py --dry-run
-------------------------------------------------------------------
"""

import os
import re
import sys

# ---- config: change these if your paths/anchors ever differ --------
THEME_TAG = '<script src="js/clappr-pink-theme.js"></script>'
CLAPPR_TAG = '<script src="https://cdn.jsdelivr.net/npm/clappr@latest/dist/clappr.min.js"></script>'
MEDIACONTROL_LINE = 'mediacontrol: ClapprPinkTheme.mediacontrol,'
# --------------------------------------------------------------------

DRY_RUN = '--dry-run' in sys.argv

# Match the indentation + "autoPlay: true," line, but ONLY when it is
# not already followed by the mediacontrol line (so re-runs are safe).
autoplay_re = re.compile(
    r'([ \t]*)autoPlay:\s*true,[ \t]*\n(?![ \t]*mediacontrol:\s*ClapprPinkTheme)'
)


def add_mediacontrol(match):
    indent = match.group(1)
    return (
        f'{indent}autoPlay: true,\n'
        f'{indent}{MEDIACONTROL_LINE}\n'
    )


def process(content):
    """Return (new_content, added_tag, mediacontrol_count)."""
    added_tag = False
    mc_count = 0

    # 1) Insert the theme <script> tag after the Clappr CDN tag (once).
    if THEME_TAG not in content and CLAPPR_TAG in content:
        content = content.replace(CLAPPR_TAG, CLAPPR_TAG + '\n' + THEME_TAG, 1)
        added_tag = True

    # 2) Insert mediacontrol into each player config that lacks it.
    content, mc_count = autoplay_re.subn(add_mediacontrol, content)

    return content, added_tag, mc_count


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    html_files = [f for f in os.listdir(here) if f.lower().endswith('.html')]

    if not html_files:
        print(f'No .html files found in {here}')
        return

    print(f'Scanning {len(html_files)} HTML file(s) in {here}')
    if DRY_RUN:
        print('--- DRY RUN: no files will be changed ---')
    print()

    changed = 0
    for name in sorted(html_files):
        path = os.path.join(here, name)
        with open(path, 'r', encoding='utf-8') as fh:
            original = fh.read()

        new_content, added_tag, mc_count = process(original)

        if new_content == original:
            print(f'  [skip]  {name} (already themed / nothing to do)')
            continue

        bits = []
        if added_tag:
            bits.append('added script tag')
        if mc_count:
            bits.append(f'added mediacontrol x{mc_count}')
        summary = ', '.join(bits)

        if DRY_RUN:
            print(f'  [would] {name}: {summary}')
        else:
            # Write a one-time backup only if it doesn't exist yet.
            backup = path + '.bak'
            if not os.path.exists(backup):
                with open(backup, 'w', encoding='utf-8') as bh:
                    bh.write(original)
            with open(path, 'w', encoding='utf-8') as fh:
                fh.write(new_content)
            print(f'  [done]  {name}: {summary}  (backup: {name}.bak)')
        changed += 1

    print()
    verb = 'would change' if DRY_RUN else 'changed'
    print(f'Finished. {verb} {changed} file(s).')


if __name__ == '__main__':
    main()