from bs4 import BeautifulSoup
import re

with open('arnolds.html', 'r', encoding='utf-8') as f:
    html_content = f.read()

soup = BeautifulSoup(html_content, 'html.parser')

table = soup.find('table', id='eventsTable')
tbody = soup.new_tag('tbody')
table.clear()

# PROPER HEADERS (styled like original)
thead = soup.new_tag('thead')
tr_header = soup.new_tag('tr')
th1 = soup.new_tag('th')
th1.string = 'Event'
th2 = soup.new_tag('th')
th2.string = 'Start Time (PST)'
th3 = soup.new_tag('th')
th3.string = 'Countdown'
tr_header.extend([th1, th2, th3])
thead.append(tr_header)
table.append(thead)
table.append(tbody)

# Arnold schedule
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
    # Day header (colspan=3)
    hrow = soup.new_tag('tr')
    hcell = soup.new_tag('td', colspan=3)
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
        
        tdt = soup.new_tag('td', start_time.replace(' 2026', '') + ' PST')
        
        # Countdown (matches original soccer format exactly)
        start_full = start_time.replace('March 6', 'March 06').replace('March 7', 'March 07').replace('March 8', 'March 08') + ':00 PST'
        day_num = int(re.search(r'(\d+)', start_time.split(',')[0]).group(1))
        end_day = '07' if day_num == 6 else '08' if day_num == 7 else '09'
        end_full = start_full.replace('March 06', f'March {end_day}').replace('March 07', f'March {end_day}')
        
        span = soup.new_tag('span')
        span['class'] = 'countdown-timer'
        span['data-start'] = start_full
        span['data-end'] = end_full
        tdc = soup.new_tag('td')
        tdc.append(span)
        
        row.extend([tde, tdt, tdc])
        tbody.append(row)
        i += 1

with open('arnold_schedule.html', 'w', encoding='utf-8') as f:
    f.write(str(soup))

print('✅ COMPLETE! Headers + 3 columns + working countdowns + day groups!')
