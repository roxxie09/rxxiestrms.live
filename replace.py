import os

# Get the current working directory
folder = os.path.dirname(os.path.abspath(__file__))

# Loop through files in the current directory
for filename in os.listdir(folder):
    if filename.endswith(".html"):
        filepath = os.path.join(folder, filename)

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace all instances of "https://www.youtube.com/live_chat?v=K5tlSOUSRXY&amp;embed_domain=roxiestreams.info" with "https://www.youtube.com/live_chat?v=K5tlSOUSRXY&amp;embed_domain=roxiestreams.info&amp;dark_theme=1"
        updated_content = content.replace("https://www.youtube.com/live_chat?v=K5tlSOUSRXY&amp;embed_domain=roxiestreams.info", "https://www.youtube.com/live_chat?v=K5tlSOUSRXY&amp;embed_domain=roxiestreams.info&amp;dark_theme=1")

        # Write the changes back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print(f"✅ Updated: {filename}")