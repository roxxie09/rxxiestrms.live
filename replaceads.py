#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

# Regex pattern to match the old atOptions script block
old_atoptions_pattern = re.compile(
    r'<script\s+type=["\']text/javascript["\']>\s*'
    r'atOptions\s*=\s*\{\s*'
    r"['\"]key['\"]\s*:\s*['\"]003d52b3a131567a085c68d8775f52a2['\"],\s*"
    r"['\"]format['\"]\s*:\s*['\"]iframe['\"],\s*"
    r"['\"]height['\"]\s*:\s*60,\s*"
    r"['\"]width['\"]\s*:\s*468,\s*"
    r"['\"]params['\"]\s*:\s*\{\}\s*"
    r'\};\s*</script\s*>',
    re.IGNORECASE | re.DOTALL
)

# Replacement text (new atOptions + script include)
new_atoptions_block = """<script type="text/javascript">
\tatOptions = {
\t\t'key' : '4fb9813602118af6e6ec2974670023c9',
\t\t'format' : 'iframe',
\t\t'height' : 60,
\t\t'width' : 468,
\t\t'params' : {}
\t};
</script>
<script type="text/javascript" src="//monthspathsmug.com/4fb9813602118af6e6ec2974670023c9/invoke.js"></script>"""

def replace_in_file(path: Path):
    """Replace the old atOptions block with the new one."""
    text = path.read_text(encoding='utf-8', errors='replace')
    new_text, count = old_atoptions_pattern.subn(new_atoptions_block, text)
    if count > 0:
        backup = path.with_suffix(path.suffix + '.bak')
        shutil.copy2(path, backup)
        path.write_text(new_text, encoding='utf-8')
        print(f"✅ Updated {path.name} (backup -> {backup.name}, {count} replacements)")
    else:
        print(f"✔ No changes in {path.name}")

def main():
    for file in os.listdir('.'):
        if file.endswith('.html'):
            replace_in_file(Path(file))
    print("\nAll done!")

if __name__ == "__main__":
    main()
