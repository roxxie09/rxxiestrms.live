import glob
import re
from pathlib import Path

# The \s* matches any newlines, tabs, or spaces inside the block
PATTERN = re.compile(
    r'<li\s+class="nav-item">\s*<a\s+class="[^"]*"\s+href="https://roxiestreams\.info/soccer">\s*Soccer\s*(?:\(WC\s*2026\))?\s*</a>\s*</li>',
    re.IGNORECASE | re.DOTALL
)

TARGET_HTML = '<li class="nav-item"><a class="nav-link" href="https://roxiestreams.info/soccer">Soccer</a></li>'

html_files = glob.glob("*.html")
updated_files = 0
already_correct = 0

for file_path in html_files:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    
    # Perform regex sub
    new_content, count = PATTERN.subn(TARGET_HTML, content)
    
    if count > 0 and new_content != content:
        path.write_text(new_content, encoding="utf-8")
        updated_files += 1
        print(f"Updated: {path.name}")
    elif TARGET_HTML in content:
        already_correct += 1

print(f"\nFinal Scan Complete!")
print(f"• Files updated now: {updated_files}")
print(f"• Files already matching clean target: {already_correct}")
print(f"• Total files scanned: {len(html_files)}")