import re

with open('paste.txt', 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# Exact Arnold events/times from your list (kept duplicates, used start times)
arnold_events = [
    ("Animal Cage - Day 1", "March 6, 2026 7:00 AM"),
    ("Arnold Strongman Classic & Arnold Strongwoman Classic - Day 1", "March 6, 2026 8:00 AM"),
    ("Friday Night Finals (Arnold Men's Open Prejudging + Classic Physique, Fitness & Wellness Finals)", "March 6, 2026 4:00 PM"),
    ("High Five Armwrestling - Day 1", "March 7, 2026 6:00 AM"),
    ("Arnold Strongman Classic & Arnold Strongwoman Classic - Day 2", "March 7, 2026 7:00 AM"),
    ("Animal Cage - Day 2", "March 7, 2026 7:00 AM"),
    ("IFBB Pro Wheelchair Prejudging & Finals + Arnold Men's Physique & Bikini Prejudging", "March 7, 2026 7:00 AM"),
    ("Angel Fashion Show", "March 7, 2026 9:15 AM"),
    ("World's Strongest Firefighter", "March 7, 2026 10:15 AM"),
    ("Joey Swoll hosted by Siddique Farooqui", "March 7, 2026 1:15 PM"),
    ("Saturday Night Finals (Arnold Classic Men's Open, Men's Physique & Bikini)", "March 7, 2026 4:00 PM"),
    ("Arnold Showcase", "March 8, 2026 6:30 AM"),
    ("Animal Cage - Day 3", "March 8, 2026 7:00 AM"),
    ("Amateur Strongman Finals", "March 8, 2026 7:00 AM"),
    ("Sam Sulek", "March 8, 2026 9:30 AM"),
    ("Amateur Strongman Finals", "March 8, 2026 10:00 AM")
]

# Build table rows (arnold-1, arnold-2, etc.)
table_rows = ''
for i, (name, time) in enumerate(arnold_events, 1):
    link = f'https://roxiestreams.info/arnold-{i}'
    # data-end = next day same time, data-start = same day
    end_time = time.replace('AM', ':00 AM').replace('PM', ':00 PM')
    start_time = end_time  # Same format
    row = f'''<tr>
<td><a href="{link}">{name}</a></td>
<td>{time}</td>
<td><span class="countdown-timer" data-end="{time.replace("March", "March 07,") if "March 6" in time else time.replace("March 7", "March 08,") if "March 7" in time else time.replace("March 8", "March 09,")}" data-start="{time}"></span></td>
</tr>'''
    table_rows += row

# Replace table (keep header as "Upcoming Arnold Events")
soccer_pattern = r'<tbody>.*?</table>'
arnold_table = f'<tbody>\n{table_rows}\n</tbody></table>'
new_content = content.replace('Upcoming Arnolds Events', 'Upcoming Arnold Events')
new_content = re.sub(soccer_pattern, arnold_table, new_content, flags=re.DOTALL)

with open('arnold_schedule.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Arnold schedule generated: arnold_schedule.html (16 events with your exact names/times)')
print('Links: arnold-1 through arnold-16')
