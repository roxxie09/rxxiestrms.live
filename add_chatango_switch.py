#!/usr/bin/env python3
import re
import sys
from pathlib import Path

CHAT_CSS = """
        .embedchat {
            width: 30%;
            height: 100%;
            display: flex;
            flex-direction: column;
            margin-left: 10px;
            border: 1px solid rgba(255, 192, 203, 0.2);
            border-radius: 8px;
            overflow: hidden;
        }
        .chat-header {
            padding: 8px;
            background: #1a1a1a;
            border-bottom: 1px solid rgba(255, 192, 203, 0.1);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .chat-toggle-btn {
            background: rgba(255, 192, 203, 0.1);
            border: 1px solid rgba(255, 192, 203, 0.3);
            color: pink;
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 4px;
            cursor: pointer;
            text-transform: uppercase;
            font-weight: bold;
        }
        .chat-toggle-btn:hover {
            background: rgba(255, 192, 203, 0.2);
        }
        #chatContent {
            flex: 1;
            width: 100%;
            height: 100%;
        }
        #chatContent iframe {
            width: 100%;
            height: 100%;
            border: none;
        }
"""

CHAT_HTML = """
            <div class=\"embedchat\">
                <div class=\"chat-header\">
                    <span style=\"font-size: 10px; color: pink; font-weight: bold;\">LIVE CHAT</span>
                    <button class=\"chat-toggle-btn\" id=\"toggleChat\">Switch to Chatango</button>
                </div>
                <div id=\"chatContent\">
                    <iframe src=\"https://www.youtube.com/live_chat?v=mpwfjhmyEzw&amp;embed_domain=roxiestreams.info\"></iframe>
                </div>
            </div>
"""

TOGGLE_BLOCK = """
    window.onload = function() {
        var toggleBtn = document.getElementById('toggleChat');
        var chatContent = document.getElementById('chatContent');

        if (toggleBtn) {
            toggleBtn.onclick = function() {
                if (currentChat === 'yt') {
                    chatContent.innerHTML = '';

                    var script = document.createElement('script');
                    script.id = 'cid0020000123456789012';
                    script.async = true;
                    script.src = 'https://st.chatango.com/js/gz/emb.js';

                    var config = {
                        handle: 'roxiestreams',
                        arch: 'js',
                        styles: {
                            a: '1a1a1a',
                            b: 100,
                            c: 'ffffff',
                            d: 'ffffff',
                            e: '1a1a1a',
                            f: '000000',
                            g: 'ffffff',
                            h: '000000',
                            i: 100,
                            j: 'ffffff',
                            k: 'e573b5',
                            l: '1a1a1a',
                            m: 'ffffff',
                            n: 'ffffff',
                            q: '1a1a1a',
                            r: 100,
                            t: 0,
                            v: 0,
                            w: 0
                        }
                    };

                    script.innerHTML = JSON.stringify(config);
                    chatContent.appendChild(script);
                    toggleBtn.innerText = 'Switch to YouTube';
                    currentChat = 'chatango';
                } else {
                    chatContent.innerHTML = '<iframe src="https://www.youtube.com/live_chat?v=mpwfjhmyEzw&amp;embed_domain=roxiestreams.info"></iframe>';
                    toggleBtn.innerText = 'Switch to Chatango';
                    currentChat = 'yt';
                }
            };
        }
    };
"""


def patch_file(path: Path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    original = text

    if 'id="toggleChat"' in text and 'https://st.chatango.com/js/gz/emb.js' in text:
        return 'already_patched'

    text = re.sub(
        r'(var\s+clapprPlayer\s*;)',
        r"\1\nvar currentChat = 'yt';",
        text,
        count=1,
        flags=re.IGNORECASE
    )

    embedchat_pattern = re.compile(
        r'<div class="embedchat">\s*<iframe[^>]*></iframe>\s*</div>',
        re.IGNORECASE | re.DOTALL
    )
    text = embedchat_pattern.sub(CHAT_HTML.strip(), text, count=1)

    if '.chat-header {' not in text:
        text = re.sub(
            r'(#playerContainer\s*\{[^}]*\}\s*)',
            r'\1\n' + CHAT_CSS,
            text,
            count=1,
            flags=re.IGNORECASE | re.DOTALL
        )

    if 'window.onload = function() {' in text and 'toggleBtn.onclick' not in text:
        text = text.replace('window.onload = function() {', 'window.onload = function() {\n' + TOGGLE_BLOCK.strip() + '\n', 1)
    elif 'function showPlayer' in text and 'toggleBtn.onclick' not in text:
        text = re.sub(
            r'(function\s+showPlayer\s*\([^)]*\)\s*\{.*?\n\})',
            r"\1\n\n" + TOGGLE_BLOCK.strip(),
            text,
            count=1,
            flags=re.DOTALL
        )

    if text != original:
        path.write_text(text, encoding='utf-8')
        return 'patched'
    return 'no_change'


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    files = sorted(root.rglob('*.html'))
    if not files:
        print('No HTML files found.')
        return

    patched = 0
    skipped = 0
    unchanged = 0

    for f in files:
        result = patch_file(f)
        if result == 'patched':
            patched += 1
            print(f'PATCHED  {f}')
        elif result == 'already_patched':
            skipped += 1
            print(f'SKIPPED  {f}')
        else:
            unchanged += 1
            print(f'NOCHANGE {f}')

    print(f'\nDone. patched={patched} skipped={skipped} unchanged={unchanged}')


if __name__ == '__main__':
    main()
