#!/usr/bin/env python3
import os
import re
import glob
from pathlib import Path

def remove_winter_olympics_nav(html_content):
    """Remove the Winter Olympics <li> from navbar using regex"""
    # Match the exact Winter Olympics li element
    pattern = r'<li class="nav-item"><a class="nav-link nav-link-winter-blue" href="https://roxiestreams\.info/olympics">Winter Olympics</a></li>'
    
    # Remove the line (including any whitespace/newlines around it)
    cleaned = re.sub(pattern + r'\s*\n?', '', html_content, flags=re.MULTILINE)
    
    # Also handle if there are extra newlines left behind
    cleaned = re.sub(r'\n\s*\n\s*\n', '\n\n', cleaned)
    
    return cleaned

def process_html_files(directory='.'):
    """Process all HTML files in the specified directory"""
    html_files = glob.glob(os.path.join(directory, '**/*.html'), recursive=True)
    
    if not html_files:
        print("No HTML files found in the directory.")
        return
    
    print(f"Found {len(html_files)} HTML files to process...\n")
    
    backup_dir = Path(directory) / "backups"
    backup_dir.mkdir(exist_ok=True)
    
    modified_count = 0
    
    for html_file in html_files:
        try:
            # Read original file
            with open(html_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if Winter Olympics nav item exists
            if 'nav-link-winter-blue' not in content:
                print(f"✓ {os.path.basename(html_file)} - No Winter Olympics item found")
                continue
            
            # Create backup
            backup_path = backup_dir / os.path.basename(html_file)
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Remove Winter Olympics item
            new_content = remove_winter_olympics_nav(content)
            
            # Write cleaned file
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            modified_count += 1
            print(f"✓ {os.path.basename(html_file)} - Winter Olympics removed (backup created)")
            
        except Exception as e:
            print(f"✗ Error processing {html_file}: {e}")
    
    print(f"\n✅ Completed! Modified {modified_count} files.")
    print(f"📁 Backups saved in: {backup_dir}")

if __name__ == "__main__":
    # Change this to your HTML files directory
    target_directory = input("Enter directory containing HTML files (press Enter for current directory): ").strip()
    if not target_directory:
        target_directory = '.'
    
    process_html_files(target_directory)
