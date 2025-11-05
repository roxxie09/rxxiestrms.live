import os
import re

# Define the exact malicious script tag
malicious_script = (
    r'<script\s+src="https://richinfo\.co/richpartners/pops/js/richads-pu-ob\.js"'
    r'\s+data-pubid="991686"\s+data-siteid="376319"\s+async\s+data-cfasync="false">'
    r'</script>'
)

# Regex to find <head>...</head> content and remove malicious script inside
head_pattern = re.compile(
    rf'(<head[^>]*>)(.*?)({malicious_script})(.*?)(</head>)',
    re.DOTALL | re.IGNORECASE
)

def clean_html_files():
    for filename in os.listdir('.'):
        if filename.endswith('.html'):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()

            # Remove the malicious script if found inside <head>
            new_content = re.sub(
                malicious_script, '', content, flags=re.IGNORECASE
            )

            if new_content != content:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"✅ Cleaned: {filename}")
            else:
                print(f"✔ No changes: {filename}")

if __name__ == "__main__":
    clean_html_files()
