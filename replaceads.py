import re
from pathlib import Path

root = Path(".")

# Regex: from the awn-z10753238 div through the closing </noscript>
ad_block_pattern = re.compile(
    r'<div id="awn-z10753238"></div>[\s\S]*?</noscript>',
    re.IGNORECASE,
)

for html_file in root.rglob("*.html"):
    text = html_file.read_text(encoding="utf-8")

    if 'awn-z10753238' not in text:
        continue  # nothing to remove

    new_text = ad_block_pattern.sub("", text)

    if new_text != text:
        html_file.write_text(new_text, encoding="utf-8")
        print(f"Removed new ad block from: {html_file}")
