import re
from pathlib import Path

# 1) Regex for the atOptions <script> block (multiline)
atoptions_pattern = re.compile(
    r"<script[^>]*>\s*atOptions\s*=\s*\{[\s\S]*?\}\s*;\s*</script>\s*",
    re.IGNORECASE,
)

# 2) Regex for any <script> tag whose src contains monthspathsmug.com
adscript_pattern = re.compile(
    r"<script[^>]*src=['\"]?[^'\">]*monthspathsmug\.com[^>]*></script>\s*",
    re.IGNORECASE,
)

root = Path(".")  # change if needed, e.g. Path("/path/to/site")

for html_file in root.rglob("*.html"):
    text = html_file.read_text(encoding="utf-8")

    new_text = atoptions_pattern.sub("", text)
    new_text = adscript_pattern.sub("", new_text)

    if new_text != text:
        html_file.write_text(new_text, encoding="utf-8")
        print(f"Cleaned: {html_file}")
