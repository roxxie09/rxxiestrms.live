#!/usr/bin/env python3
from pathlib import Path
import sys

TARGET = """        window.onload = function() {
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

            showPlayer('clappr', 'https://z.rowdydowdyhauling.com/morningstar.m3u8');
        };
    </script>"""

REPLACEMENT = """        window.onload = function() {
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

            showPlayer('clappr', 'https://z.rowdydowdyhauling.com/morningstar.m3u8');
        };
    </script>"""


def patch_file(path):
    text = path.read_text(encoding='utf-8', errors='ignore')
    if 'id="toggleChat"' not in text:
        return False
    if TARGET not in text:
        return False
    new_text = text.replace(TARGET, REPLACEMENT, 1)
    if new_text != text:
        path.write_text(new_text, encoding='utf-8')
        return True
    return False


def main():
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    count = 0
    for f in root.rglob('*.html'):
        if patch_file(f):
            print('PATCHED', f)
            count += 1
    print(f"\nDone. patched={count}")


if __name__ == '__main__':
    main()