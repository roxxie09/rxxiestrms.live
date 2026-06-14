#!/usr/bin/env python3
"""
add_iframe_player.py
--------------------
Adds support for embed buttons like:

    <button class="streambutton"
            onclick="playIframePlayer('https://roxiestreams.info/raw/peacock')">
        Tele (Peacock)
    </button>

to your Clappr-only stream pages, so the button actually plays.

It does two things per page (both needed):
 1. Inserts a self-contained playIframePlayer() function. It guards the Shaka
    cleanup with typeof, so it's safe on pages that have no Shaka variables, and
    it sizes the iframe inline so no extra CSS is required.
 2. Adds one line to showPlayer() so switching back to a Clappr stream removes
    the iframe (otherwise the iframe would stay on top of the new player).

Conservative behavior:
 * Skips files that already define playIframePlayer (idempotent).
 * Only edits files that have a showPlayer() with the standard
   `if (playerType === "clappr") {` branch.
 * Anything else is reported under "NEEDS REVIEW" and left untouched.

Usage:
    python3 add_iframe_player.py /path/to/site            # apply to a folder
    python3 add_iframe_player.py file1.html file2.html    # specific files
"""

import os
import re
import sys

MARKER = 'function playIframePlayer'

FUNC = """function playIframePlayer(src) {
  var container = document.getElementById('playerContainer');

  if (typeof clapprPlayer !== 'undefined' && clapprPlayer) {
    clapprPlayer.destroy();
    clapprPlayer = null;
  }
  if (typeof shakaPlayer !== 'undefined' && shakaPlayer) {
    shakaPlayer.destroy();
    shakaPlayer = null;
  }
  if (typeof shakaUI !== 'undefined' && shakaUI) {
    shakaUI.destroy();
    shakaUI = null;
  }

  // Rebuild the iframe each call so re-pressing the button reloads the stream
  container.innerHTML = '';
  var iframe = document.createElement('iframe');
  iframe.id = 'stream1pc-iframe';
  iframe.allowFullscreen = true;
  iframe.src = src;
  iframe.style.width = '100%';
  iframe.style.height = '100%';
  iframe.style.border = 'none';
  iframe.style.display = 'block';
  container.appendChild(iframe);
}"""

CLEANUP = """var __pcFrame = document.getElementById('stream1pc-iframe');
if (__pcFrame) __pcFrame.remove();"""

CLAPPR_IF_RE = re.compile(r'^([ \t]*)if \(playerType === "clappr"\) \{', re.M)
SHOWPLAYER_RE = re.compile(r'^([ \t]*)function showPlayer\b', re.M)


def indent_block(block, ind, nl):
    out = []
    for line in block.split("\n"):
        out.append(ind + line if line.strip() else "")
    return nl.join(out)


def process(text):
    if MARKER in text:
        return text, 'already', None

    nl = '\r\n' if '\r\n' in text else '\n'

    m_if = CLAPPR_IF_RE.search(text)
    if not m_if:
        return text, 'review', 'no showPlayer clappr branch (`if (playerType === "clappr") {`) found'
    m_fn = SHOWPLAYER_RE.search(text)
    if not m_fn:
        return text, 'review', 'no `function showPlayer` found'

    # 1) Insert the iframe cleanup right after the clappr-if line.
    if_indent = m_if.group(1)
    line_end = text.find('\n', m_if.end())
    if line_end == -1:
        return text, 'review', 'could not find end of clappr-if line'
    insert_pos = line_end + 1
    cleanup_text = indent_block(CLEANUP, if_indent + '  ', nl) + nl
    text = text[:insert_pos] + cleanup_text + text[insert_pos:]

    # 2) Insert the playIframePlayer function just before function showPlayer.
    m_fn = SHOWPLAYER_RE.search(text)  # re-find after first insert
    fn_indent = m_fn.group(1)
    func_text = indent_block(FUNC, fn_indent, nl) + nl + nl + fn_indent
    text = text[:m_fn.start()] + func_text + text[m_fn.start() + len(fn_indent):]

    return text, 'updated', None


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
    files = gather_files(sys.argv[1:])
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