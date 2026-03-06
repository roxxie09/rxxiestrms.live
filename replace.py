import re

with open('paste.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Arnold events parsed from paste.txt (names, times approximated from timestamps/context)
arnold_events = [
    ("Arnold Amateur Bodybuilding", "March 5, 2026 8:00 AM"),
    ("Armlifting Middleweight Men", "March 6, 2026 9:00 AM"),
    ("Animal Cage - Day 1", "March 6, 2026 9:30 AM"),
    ("Arnold Strongman Classic Day 1", "March 6, 2026 10:00 AM"),
    ("IFBB Pro Classic Physique Prejudging", "March 6, 2026 10:30 AM"),
    ("Ronnie Coleman Jay Cutler hosted", "March 6, 2026 11:00 AM"),
    ("Greg Doucette hosted", "March 6, 2026 11:30 AM"),
    ("Frank The Tank Matteo Jenks", "March 6, 2026 12:00 PM"),
    ("Chalkless With Tim Bush", "March 6, 2026 1:00 PM"),
    ("Friday Night Finals Arnold Mens Open", "March 6, 2026 2:00 PM")
]

# Build new table rows
table_rows = ''
for i, (name, time) in enumerate(arnold_events, 1):
    link = f'https://roxiestreams.info/arnold-{i}'
    # Format for data-end (next day) and data-start (same day)
    end_time = time.replace('AM', ':00 AM').replace('PM', ':00 PM')
    start_time = time.replace('AM', ':00 AM').replace('PM', ':00 PM')
    row = f'''<tr>
<td><a href="{link}">{name}</a></td>
<td>{time}</td>
<td><span class="countdown-timer" data-end="March 07, 2026 {end_time}" data-start="March 06, 2026 {start_time}"></span></td>
</tr>'''
    table_rows += row

# Replace table body and header
soccer_pattern = r'<tbody>.*?</table>'
arnold_table = f'<tbody>\n{table_rows}\n</tbody></table>'
new_content = content.replace('Upcoming Arnolds Events', 'Upcoming Arnold Events')
new_content = re.sub(soccer_pattern, arnold_table, new_content, flags=re.DOTALL)

with open('arnold_schedule.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Arnold schedule generated: arnold_schedule.html')
