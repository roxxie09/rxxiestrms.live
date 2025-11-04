#!/bin/bash

# Set the target repo slug for syncing (update as needed)
TARGET="roxxie09/roxxiestrms"

# Start the YAML file
echo "$TARGET:" > .github/sync.yml

# Add all .html and .js files at the root
find . -maxdepth 1 -type f \( -name '*.html' -o -name '*.js' \) | sed 's|^\./||' | awk '{print "  - "$1}' >> .github/sync.yml

# (Optional) Add folders at root
find . -maxdepth 1 -type d ! -name '.' ! -name '.github' ! -name '.git' | sed 's|^\./||' | awk '{print "  - "$1"/"}' >> .github/sync.yml
