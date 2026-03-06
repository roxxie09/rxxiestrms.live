from bs4 import BeautifulSoup
import re

# Read input file (arnolds.html per your error)
with open('arnolds.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

table = soup.find('table', id='eventsTable')
if not table:
    print("ERROR: No table! Check id='eventsTable'")
    exit(1)

# Clean table completely (keep thead)
tbody = table.find('tbody')
if tbody is None:
    tbody = soup.new_tag('tbody')
    table.append(tbody)

# Nuke all data rows
for tr in tbody.find_all('tr'):
    tr.decompose()

# Flatten nested tbodies
for nested_tbody in soup.select('tbody tbody'):
    nested_tbody.unwrap()

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

for i, (name, time_str) in enumerate(arnold_events, 1):
    row = soup.new_tag('tr')
    
    link = soup.new_tag('a', href=f'https://roxiestreams.info/arnold-{i}')
    link.string = name
    td_event = soup.new_tag('td')
    td_event.append(link)
    
    td_time = soup.new_tag('td', time_str)
    
    # Simple countdown: parse day, add :00 PST, next day end
    day_match = re.search(r'March (\d+), 2026', time_str)
    day = int(day_match.group(1)) if day_match else 6
    time_part = re.search(r'(\d+:\d+ (AM|PM))', time_str).group(1) if re.search(r'(\d+:\d+ (AM|PM))', time_str) else '7:00 AM'
    
    start_dt = f'March {day}, 2026 {time_part}:00 PST'
    end_dt = f'March {day+1}, 2026 {time_part}:00 PST'
    
    span = soup.new_tag('span')
    span['class'] = 'countdown-timer'
    span['data-start'] = start_dt
    span['data-end'] = end_dt
    td_count = soup.new_tag('td')
    td_count.append(span)
    
    row.extend([td_event, td_time, td_count])
    tbody.append(row)

with open('arnold_schedule.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print('✅ SUCCESS! arnold_schedule.html ready - 16 Arnold events added.')
