import os

# Get the current working directory
folder = os.path.dirname(os.path.abspath(__file__))

# Loop through files in the current directory
for filename in os.listdir(folder):
    if filename.endswith(".html"):
        filepath = os.path.join(folder, filename)

        with open(filepath, 'r', encoding='utf-8') as file:
            content = file.read()

        # Replace all instances of "600.roxiestreams.live" with "600.tanjung.eu.org"
        updated_content = content.replace("6600.roxiestreams.live", "600.tanjung.eu.org")

        # Write the changes back to the file
        with open(filepath, 'w', encoding='utf-8') as file:
            file.write(updated_content)

        print(f"✅ Updated: {filename}")
