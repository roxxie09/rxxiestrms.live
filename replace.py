from pathlib import Path
import re

pattern = re.compile(
    r'\s*<li class="nav-item">\s*<a class="nav-link nav-link-march-madness"[^>]*>.*?<\/a>\s*<\/li>\s*',
    re.DOTALL
)

for file in Path(".").rglob("*.html"):
    text = file.read_text(encoding="utf-8")

    # remove the nav item cleanly
    new_text = pattern.sub("", text)

    # normalize extra blank lines (fix leftover spacing)
    new_text = re.sub(r'\n\s*\n\s*\n+', '\n\n', new_text)

    file.write_text(new_text, encoding="utf-8")

print("Done cleaning navbars")