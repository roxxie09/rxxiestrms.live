import re
from pathlib import Path

root = Path(".")

# Pattern matches the exact block you want to remove (multiline)
ad_block_pattern = re.compile(
    r"""
    <script>\s*
        atOptions\s*=\s*\{\s*
            'key'\s*:\s*'b1b8ec11c0dbedd922608bac17f740ee',\s*
            'format'\s*:\s*'iframe',\s*
            'height'\s*:\s*250,\s*
            'width'\s*:\s*300,\s*
            'params'\s*:\s*\{\s*\}\s*
        \};\s*
    </script>\s*
    <script\s+src="https://monthspathsmug\.com/b1b8ec11c0dbedd922608bac17f740ee/invoke\.js"></script>\s*
    <script\s+src="https://monthspathsmug\.com/39/5b/74/395b743c98df9f3269c808abb2b1d06a\.js"></script>
    """,
    re.VERBOSE | re.IGNORECASE
)

for html_file in root.rglob("*.html"):
    text = html_file.read_text(encoding="utf-8")
    
    # Only process if the specific key exists
    if 'b1b8ec11c0dbedd922608bac17f740ee' not in text:
        continue
    
    # Remove the entire block
    new_text = ad_block_pattern.sub("", text)
    
    # Clean up any extra blank lines left behind
    new_text = re.sub(r'\n\s*\n\s*\n', '\n\n', new_text)
    
    if new_text != text:
        html_file.write_text(new_text, encoding="utf-8")
        print(f"Removed ad block: {html_file}")
