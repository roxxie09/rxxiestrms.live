#!/usr/bin/env python3
"""
update_clappr.py
----------------
Adds the iOS-friendly playback block

    playback: {
        playInline: true,
        recycleVideo: true
    }

to every `new Clappr.Player({ ... })` config it finds in your HTML files.

It is SAFE and CONSERVATIVE:
  * If a config already has recycleVideo  -> left alone (reported as "already").
  * If a config already has its own `playback:` object -> NOT touched,
    flagged for you to merge by hand (reported as "REVIEW").
  * If it can't find a safe spot to insert (no `autoPlay`) -> flagged "REVIEW".
  * Files with no Clappr player are skipped.
  * A .bak backup is written before any file is changed (unless --no-backup).
  * Run with --dry-run first to preview without writing anything.

Usage:
    python3 update_clappr.py                 # process *.html in current folder (recursive)
    python3 update_clappr.py /path/to/site   # process a folder
    python3 update_clappr.py file1.html ...  # process specific files
    python3 update_clappr.py --dry-run .     # preview only
    python3 update_clappr.py --no-backup .   # skip .bak files
"""

import os
import re
import sys

INSERT_PLAYINLINE = "playInline: true"
INSERT_RECYCLE = "recycleVideo: true"


def find_clappr_blocks(text):
    """Return list of (match_start, brace_start, brace_end, kind).
    brace_start/brace_end are indices of the '{' and matching '}' of the config.
    kind is 'ok', 'no-open-brace', or 'unbalanced'."""
    blocks = []
    for m in re.finditer(r'new\s+Clappr\.Player\s*\(', text):
        i = m.end()
        while i < len(text) and text[i] in ' \t\r\n':
            i += 1
        if i >= len(text) or text[i] != '{':
            blocks.append((m.start(), None, None, 'no-open-brace'))
            continue
        depth = 0
        j = i
        in_str = None
        esc = False
        end = None
        while j < len(text):
            c = text[j]
            if in_str:
                if esc:
                    esc = False
                elif c == '\\':
                    esc = True
                elif c == in_str:
                    in_str = None
            else:
                if c in '"\'`':
                    in_str = c
                elif c == '{':
                    depth += 1
                elif c == '}':
                    depth -= 1
                    if depth == 0:
                        end = j
                        break
            j += 1
        if end is None:
            blocks.append((m.start(), i, None, 'unbalanced'))
        else:
            blocks.append((m.start(), i, end, 'ok'))
    return blocks


def update_block(block_text):
    """block_text is the config object text including the outer braces.
    Returns (new_block_text, status, reason)."""
    if re.search(r'\brecycleVideo\b', block_text):
        return block_text, 'already', None
    if re.search(r'\bplayback\s*:', block_text):
        return block_text, 'review', 'config already has its own "playback" object'

    m = re.search(r'^([ \t]*)autoPlay[ \t]*:[ \t]*true[ \t]*(,?)[ \t]*$',
                  block_text, re.M)
    if not m:
        return block_text, 'review', 'no "autoPlay: true" line to anchor the insert'

    indent = m.group(1)
    new_autoplay = indent + "autoPlay: true,"
    insert = (
        "\n" + indent + "playback: {\n"
        + indent + "  " + INSERT_PLAYINLINE + ",\n"
        + indent + "  " + INSERT_RECYCLE + "\n"
        + indent + "},"
    )
    new_block = block_text[:m.start()] + new_autoplay + insert + block_text[m.end():]
    return new_block, 'updated', None


def process_text(text):
    """Return (new_text, results) where results is a list of (status, reason)."""
    blocks = find_clappr_blocks(text)
    results = []
    new_text = text
    # Process right-to-left so earlier indices stay valid.
    for (start, i, end, kind) in sorted(blocks, key=lambda b: b[0], reverse=True):
        if kind != 'ok':
            reason = ('opening "{" not found after new Clappr.Player('
                      if kind == 'no-open-brace'
                      else 'braces look unbalanced - could not parse the config')
            results.append(('review', reason))
            continue
        block_text = text[i:end + 1]
        updated, status, reason = update_block(block_text)
        results.append((status, reason))
        if status == 'updated':
            new_text = new_text[:i] + updated + new_text[end + 1:]
    results.reverse()  # back to source order
    return new_text, results


def gather_files(args):
    files = []
    paths = [a for a in args if not a.startswith('-')]
    if not paths:
        paths = ['.']
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, names in os.walk(p):
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
    dry_run = '--dry-run' in args
    no_backup = '--no-backup' in args

    files = gather_files(args)
    if not files:
        print("No .html files found.")
        return

    n_updated_files = 0
    n_blocks_updated = 0
    n_already = 0
    review = []          # (file, reason)
    no_clappr = []

    for path in files:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            review.append((path, f"could not read file: {e}"))
            continue

        if 'Clappr.Player' not in text:
            no_clappr.append(path)
            continue

        new_text, results = process_text(text)
        statuses = [s for s, _ in results]
        file_updated = new_text != text

        # Per-file line
        tag = []
        if statuses.count('updated'):
            tag.append(f"{statuses.count('updated')} updated")
        if statuses.count('already'):
            tag.append(f"{statuses.count('already')} already-ok")
        if statuses.count('review'):
            tag.append(f"{statuses.count('review')} NEEDS REVIEW")
        print(f"{path}: " + (", ".join(tag) if tag else "no Clappr config matched"))

        for s, reason in results:
            if s == 'review':
                review.append((path, reason))
        n_blocks_updated += statuses.count('updated')
        n_already += statuses.count('already')

        if file_updated:
            n_updated_files += 1
            if not dry_run:
                if not no_backup:
                    with open(path + '.bak', 'w', encoding='utf-8') as b:
                        b.write(text)
                with open(path, 'w', encoding='utf-8') as f:
                    f.write(new_text)

    print("\n" + "=" * 60)
    print("SUMMARY" + ("  (DRY RUN - nothing written)" if dry_run else ""))
    print("=" * 60)
    print(f"Files scanned          : {len(files)}")
    print(f"Files changed          : {n_updated_files}")
    print(f"Clappr configs updated : {n_blocks_updated}")
    print(f"Clappr configs already ok: {n_already}")
    print(f"Files with no Clappr   : {len(no_clappr)}")
    if review:
        print(f"\n!! NEEDS YOUR REVIEW ({len(review)}):")
        for path, reason in review:
            print(f"   - {path}: {reason}")
    else:
        print("\nNothing flagged for manual review.")


if __name__ == '__main__':
    main()