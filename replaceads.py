import os
import re
import glob

OLD_PATTERN = re.compile(
    r'(<a\s+class="nav-link"\s+href="https://roxiestreams\.info/soccer">)(Soccer(?:[^<]*)?)(</a>)',
    re.IGNORECASE
)

NEW_CLASS = 'nav-link nav-link-soccer'

def update_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()

    new_content, count = OLD_PATTERN.subn(
        lambda m: f'<a class="{NEW_CLASS}" href="https://roxiestreams.info/soccer">{m.group(2)}{m.group(3)}',
        content
    )

    if count > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ Updated: {filepath}")
    else:
        print(f"⏭️  Skipped: {filepath}")

directory = os.path.dirname(os.path.abspath(__file__))  # uses the script's own folder

html_files = glob.glob(os.path.join(directory, '**', '*.html'), recursive=True)
print(f"Scanning {len(html_files)} HTML file(s)...\n")
for filepath in sorted(html_files):
    update_file(filepath)