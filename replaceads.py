from pathlib import Path
import re

extra_script = """    <script src="https://monthspathsmug.com/39/5b/74/395b743c98df9f3269c808abb2b1d06a.js"></script>"""

root = Path(".")

for html_file in root.rglob("*.html"):
    text = html_file.read_text(encoding="utf-8")
    
    # Skip if this specific script already exists
    if '395b743c98df9f3269c808abb2b1d06a.js' in text:
        print(f"Already has extra script: {html_file}")
        continue
    
    # Find position: right after the invoke.js script (before </body>)
    invoke_pos = text.rfind('monthspathsmug.com/b1b8ec11c0dbedd922608bac17f740ee/invoke.js')
    
    if invoke_pos != -1:
        # Insert right after the invoke.js closing tag
        script_close_pos = text.find('</script>', invoke_pos) + 9  # +9 for </script> length
        new_text = text[:script_close_pos] + "\n" + extra_script + "\n" + text[script_close_pos:]
    else:
        print(f"No invoke.js found (skipping): {html_file}")
        continue
    
    html_file.write_text(new_text, encoding="utf-8")
    print(f"Added extra script: {html_file}")
