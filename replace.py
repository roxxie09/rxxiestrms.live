import os
import re

folder = os.path.dirname(os.path.abspath(__file__))

# Regular expression to detect URLs
url_pattern = re.compile(r'https?://[^\s"\']+')

def replace_discord(match):
    text = match.group(0)
    # Only replace 'discord' if it's not part of a URL
    if url_pattern.search(text):
        return text
    else:
        # Replace the exact word 'discord' with 'Stream Request (Discord)'
        # Use word boundaries to avoid partial matches
        return re.sub(r'\bdiscord\b', 'Stream Request (Discord)', text, flags=re.IGNORECASE)

for filename in os.listdir(folder):
    if filename.endswith(".html"):
        filepath = os.path.join(folder, filename)
        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # This pattern finds either URLs or 'discord' words in text
        # It uses a regex pattern to capture everything and safely decide what to replace
        pattern = re.compile(r'https?://[^\s"\']+|\bdiscord\b', flags=re.IGNORECASE)
        
        # Replace using a function that only replaces 'discord' if not part of URL
        updated_content = pattern.sub(lambda m: m.group(0) if url_pattern.match(m.group(0)) else 'Stream Request (Discord)', content)

        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print(f"✅ Updated: {filename}")
