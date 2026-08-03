import glob
from pathlib import Path

# 1. Define exact old HTML and exact new HTML
OLD_HTML = '<li class="nav-item"><a class="nav-link" href="https://roxiestreams.info/soccer">Soccer (WC 2026)</a></li>'
NEW_HTML = '<li class="nav-item"><a class="nav-link" href="https://roxiestreams.info/soccer">Soccer</a></li>'

# 2. Find all .html files in current directory
html_files = glob.glob("*.html")

changed_count = 0

for file_path in html_files:
    path = Path(file_path)
    content = path.read_text(encoding="utf-8")
    
    # Check if the old string exists in the file
    if OLD_HTML in content:
        updated_content = content.replace(OLD_HTML, NEW_HTML)
        path.write_text(updated_content, encoding="utf-8")
        changed_count += 1
        print(f"Updated: {path.name}")

print(f"\nDone! Updated {changed_count} out of {len(html_files)} files.")