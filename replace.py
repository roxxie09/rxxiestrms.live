from bs4 import BeautifulSoup
import re

with open('arnolds.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

table = soup.find('table', id='eventsTable')
if not table:
    print("ERROR: No table!")
    exit(1)

# New 2-column header: Event | Countdown
thead = table.find('thead')
if thead:
    thead.decompose()
thead = soup.new_tag('thead')
tr_header = soup.new_tag('tr')
th_event = soup.new_tag('th', 'Event')
th_countdown = soup.new_tag('th', 'Countdown')
tr_header.extend([th_event, th_countdown])
thead.append(tr_header)
table.insert(0, thead)

tbody = table.find('tbody') or soup.new_tag('tbody')
if tbody.parent != table:
    table.append(tbody)

# Clear old rows
for tr in tbody.find_all('tr'):
    tr.decompose()

# Grouped Arnold events by day
events_by_day = {
    'Friday, March 6': [
        ("Animal Cage - Day 1", "7:00 AM"),
        ("Arnold Strongman Classic & Arnold Strongwoman Classic - Day 1", "8:00 AM"),
        ("Friday Night Finals (Arnold Men's Open Prejudging + Classic Physique, Fitness & Wellness Finals)", "4:00 PM")
    ],
    'Saturday, March 7': [
        ("High Five Armwrestling - Day 1", "6:00 AM"),
        ("Arnold Strongman Classic & Arnold Strongwoman Classic - Day 2", "7:00 AM"),
        ("Animal Cage - Day 2", "7:00 AM"),
        ("IFBB Pro Wheelchair Prejudging & Finals + Arnold Men's Physique & Bikini Prejudging", "7:00 AM"),
        ("Angel Fashion Show", "9:15 AM"),
        ("World's Strongest Firefighter", "10:15 AM"),
        ("Joey Swoll hosted by Siddique Farooqui", "1:15 PM"),
        ("Saturday Night Finals (Arnold Classic Men's Open, Men's Physique & Bikini)", "4:00 PM")
    ],
    'Sunday, March 8': [
        ("Arnold Showcase", "6:30 AM"),
        ("Animal Cage - Day 3", "7:00 AM"),
        ("Amateur Strongman Finals", "7:00 AM"),
        ("Sam Sulek", "9:30 AM"),
        ("Amateur Strongman Finals", "10:00 AM")
    ]
}

link_counter = 1
for day_header, day_events in events_by_day.items():
    # Day header row (colspan=2)
    header_row = soup.new_tag('tr')
    header_cell = soup.new_tag('td', colspan='2')
    h3 = soup.new_tag('h3', day_header)
    h3['style'] = 'color: pink; margin: 10px 0; text-align: center;'
    header_cell.append(h3)
    header_row.append(header_cell)
    tbody.append(header_row)
    
    # Event rows
    for event_name, time_part in day_events:
        row = soup.new_tag('tr')
        
        a = soup.new_tag('a', href=f'https://roxiestreams.info/arnolds-{link_counter}')
        a.string = event_name
        td_event = soup.new_tag('td')
        td_event.append(a)
        
        # Countdown
        start_dt = f'March {day_header.split(",")[0].split()[-1]}, 2026 {time_part}:00 PST'
        day_num = int(re.search(r'(\d+)', day_header).group(1))
        end_dt = f'March {day_num+1}, 2026 {time_part}:00 PST'
        
        span = soup.new_tag('span', **{'class': 'countdown-timer', 'data-start': start_dt, 'data-end': end_dt})
        td_count = soup.new_tag('td')
        td_count.append(span)
        
        row.extend([td_event, td_count])
        tbody.append(row)
        link_counter += 1

with open('arnold_schedule.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print(f'✅ DONE! {link_counter-1} arnolds-X links, grouped by day, no time column.')
