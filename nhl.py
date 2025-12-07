import os

# Use the folder where your HTML files actually are
folder_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live"

nhl_item = '<li class="nav-item"><a class="nav-link" href="https://roxiestreams.live/nhl">NHL</a></li>\n'

after_tag = '<li class="nav-item"><a class="nav-link" href="https://roxiestreams.live/nfl">NFL</a></li>'
fallback_tag = '<li class="nav-item"><a class="nav-link" href="https://roxiestreams.live/fighting">Fighting</a></li>'

for filename in os.listdir(folder_path):
    if filename.endswith('.html'):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'href="https://roxiestreams.live/nhl"' in content:
            print(f'NHL section already exists in {filename}')
            continue

        if after_tag in content:
            content = content.replace(after_tag, after_tag + '\n' + nhl_item)
            print(f'Added NHL section after NFL in {filename}')
        elif fallback_tag in content:
            content = content.replace(fallback_tag, nhl_item + fallback_tag)
            print(f'Added NHL section before Fighting in {filename}')
        else:
            print(f'Could not find insertion point in {filename}')
            continue

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

print('All files processed.')
