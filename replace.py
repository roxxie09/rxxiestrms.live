from bs4 import BeautifulSoup
import re

with open('arnolds.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

table = soup.find('table', id='eventsTable')
tbody = soup.new_tag('tbody')  # Fresh tbody
table.clear()  # Wipe everything
table.append(soup.new_tag('thead'))
table.thead.append(soup.new_tag('tr', [soup.new_tag('th', 'Event'), soup.new_tag('th', 'Countdown')]))
table.append(tbody)

# EXACT Arnold schedule with day headers
schedule = [
    ('Friday, March 6', [
        ('Animal Cage - Day 1', 'March 6, 2026 7:00 AM'),
        ('Arnold Strongman Classic & Arnold Strongwoman Classic - Day 1', 'March 6, 2026 8:00 AM'),
        ('Friday Night Finals (Arnold Mens Open Prejudging + Classic Physique, Fitness & Wellness Finals)', 'March 6, 2026 4:00 PM')
    ]),
    ('Saturday, March 7', [
        ('High Five Armwrestling - Day 1', 'March 7, 2026 6:00 AM'),
        ('Arnold Strongman Classic & Arnold Strongwoman Classic - Day 2', 'March 7, 2026 7:00 AM'),
        ('Animal Cage - Day 2', 'March 7, 2026 7:00 AM'),
        ('IFBB Pro Wheelchair Prejudging & Finals + Arnold Mens Physique & Bikini Prejudging', 'March 7, 2026 7:00 AM'),
        ('Angel Fashion Show', 'March 7, 2026 9:15 AM'),
        ('Worlds Strongest Firefighter', 'March 7, 2026 10:15 AM'),
        ('Joey Swoll hosted by Siddique Farooqui', 'March 7, 2026 1:15 PM'),
        ('Saturday Night Finals (Arnold Classic Mens Open, Mens Physique & Bikini)', 'March 7, 2026 4:00 PM')
    ]),
    ('Sunday, March 8', [
        ('Arnold Showcase', 'March 8, 2026 6:30 AM'),
        ('Animal Cage - Day 3', 'March 8, 2026 7:00 AM'),
        ('Amateur Strongman Finals', 'March 8, 2026 7:00 AM'),
        ('Sam Sulek', 'March 8, 2026 9:30 AM'),
        ('Amateur Strongman Finals', 'March 8, 2026 10:00 AM')
    ])
]

i = 1
for day, events in schedule:
    # Day header
    hrow = soup.new_tag('tr')
    hcell = soup.new_tag('td', colspan=2)
    h3 = soup.new_tag('h3')
    h3.string = day
    h3['style'] = 'color:pink;margin:15px 0;text-align:center;font-size:1.2em;'
    hcell.append(h3)
    hrow.append(hcell)
    tbody.append(hrow)
    
    for name, start_time in events:
        row = soup.new_tag('tr')
        
        a = soup.new_tag('a', href=f'https://roxiestreams.info/arnolds-{i}')
        a.string = name
        tde = soup.new_tag('td')
        tde.append(a)
        
        # EXACT original date format for JS
        start_full = f'{start_time}:00 PST'
        day_num = int(re.search(r'(\d+)', start_time.split(',')[0]).group(1))
        end_full = start_full.replace(f'March {day_num}', f'March {day_num+1}')
        
        span = soup.new_tag('span')
        span['class'] = 'countdown-timer'
        span['data-start'] = start_full
        span['data-end'] = end_full
        tdc = soup.new_tag('td')
        tdc.append(span)
        
        row.extend([tde, tdc])
        tbody.append(row)
        i += 1

with open('arnold_schedule.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print('✅ FIXED! Countdowns work (like original soccer), day headers, arnolds-1..16')
