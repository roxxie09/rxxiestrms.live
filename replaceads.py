import os
import re

# Script tag to insert (before closing </body>)
pop_script = """
<script type="text/javascript">
aclib.runPop({
zoneId: '10754426',
});
</script>"""

# Pattern to locate the closing </body> tag
body_close_pat = re.compile(r'</body\s*>', re.IGNORECASE)

# Ensure we only modify HTML files
html_exts = {'.html', '.htm', '.shtml', '.asp'}  # add more if needed

def process_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # If pop script already present, skip
    if 'aclib.runPop' in content:
        return False

    # Find the first </body> tag
    m_body = body_close_pat.search(content)
    if not m_body:
        # No body tag found; skip
        return False

    body_close_pos = m_body.start()
    # Insert script right before the </body> tag
    new_content = content[:body_close_pos] + pop_script + content[body_close_pos:]

    with open(path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return True

def main():
    cwd = os.getcwd()
    modified_files = []
    for fname in os.listdir(cwd):
        path = os.path.join(cwd, fname)
        if os.path.isfile(path):
            _, ext = os.path.splitext(fname)
            if ext.lower() in html_exts:
                if process_file(path):
                    modified_files.append(fname)

    if modified_files:
        print("Modified files:")
        for f in modified_files:
            print(f" - {f}")
    else:
        print("No files needed modification or no HTML files found.")

if __name__ == '__main__':
    main()
