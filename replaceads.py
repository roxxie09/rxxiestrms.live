from bs4 import BeautifulSoup
import glob
import os

MULTIVIEW_LI = '''<ul class="navbar-nav ms-auto mb-2 mb-lg-0">
<li class="nav-item">
    <a class="nav-link d-flex align-items-center gap-1" href="https://roxiestreams.info/multiview">
        <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
            <path d="M0 1.5A1.5 1.5 0 0 1 1.5 0h13A1.5 1.5 0 0 1 16 1.5v13a1.5 1.5 0 0 1-1.5 1.5h-13A1.5 1.5 0 0 1 0 14.5v-13zM1.5 1a.5.5 0 0 0-.5.5V7h6V1H1.5zM7 8H1v6.5a.5.5 0 0 0 .5.5H7V8zm1 0v7h6.5a.5.5 0 0 0 .5-.5V8H8zm0-1h7V1.5a.5.5 0 0 0-.5-.5H8v6z"/>
        </svg>
        MultiView (NEW)
    </a>
</li>
</ul>'''

html_files = glob.glob("*.html")
updated = []
skipped = []

for filepath in html_files:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    soup = BeautifulSoup(content, "html.parser")

    # Skip if already injected
    if soup.find("a", href="https://roxiestreams.info/multiview"):
        skipped.append(filepath)
        continue

    # Find the navbar-collapse div and insert after the main ul
    main_ul = soup.find("ul", class_=lambda c: c and "navbar-nav" in c and "me-auto" in c)
    if not main_ul:
        skipped.append(filepath)
        continue

    new_ul = BeautifulSoup(MULTIVIEW_LI, "html.parser")
    main_ul.insert_after(new_ul)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(soup))

    updated.append(filepath)

print(f"Updated ({len(updated)}): {updated}")
print(f"Skipped ({len(skipped)}): {skipped}")