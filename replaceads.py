from pathlib import Path

ad_snippet = """
    <script type="text/javascript">
        atOptions = {
            'key' : '4fb9813602118af6e6ec2974670023c9',
            'format' : 'iframe',
            'height' : 60,
            'width' : 468,
            'params' : {}
        };
    </script>
    <script type="text/javascript" src="//monthspathsmug.com/4fb9813602118af6e6ec2974670023c9/invoke.js"></script>
    <script type='text/javascript' src='//monthspathsmug.com/ab/1a/c2/ab1ac2d66efae0c6bc04e68156bc710e.js'></script>
"""

root = Path(".")  # or your project root

for html_file in root.rglob("*.html"):
    text = html_file.read_text(encoding="utf-8")

    # avoid duplicating if already present
    if "monthspathsmug.com" in text or "atOptions" in text:
        continue

    if "</body>" in text.lower():
        # find case-insensitive </body>
        lower = text.lower()
        idx = lower.rfind("</body>")
        new_text = text[:idx] + ad_snippet + "\n" + text[idx:]
    else:
        # if no </body>, just append
        new_text = text + ad_snippet

    html_file.write_text(new_text, encoding="utf-8")
    print(f"Injected ads into: {html_file}")
