from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Load the mlb.html file
with open('mlb.html', 'r', encoding='utf-8') as file:
    soup = BeautifulSoup(file, 'html.parser')

# Find all the <tr> rows in the table body
rows = soup.select('table#eventsTable tbody tr')

def parse_event_time(event_time_str: str) -> datetime:
    """
    Parse times like: 'March 6, 2026 10:05 AM'
    or                 'March 6, 2026 3:00 PM'
    """
    event_time_str = event_time_str.strip()
    # 12-hour format with AM/PM
    return datetime.strptime(event_time_str, '%B %d, %Y %I:%M %p')

for row in rows:
    tds = row.find_all('td')

    # Expect at least: [Event, Start Time, Countdown]
    if len(tds) < 3:
        continue

    # Get the start time from the second column
    event_time_str = tds[1].get_text(strip=True)

    try:
        start_dt = parse_event_time(event_time_str)
    except ValueError:
        # If format is unexpected, skip this row
        continue

    # Find the countdown span in the third column
    countdown_span = tds[2].find('span', class_='countdown-timer')
    if not countdown_span:
        continue

    # data-start = exact event start time
    countdown_span['data-start'] = start_dt.strftime('%B %d, %Y %H:%M:%S')

    # data-end = 12 hours after (or change to 3 if you want 3 hours)
    end_dt = start_dt + timedelta(hours=12)
    countdown_span['data-end'] = end_dt.strftime('%B %d, %Y %H:%M:%S')

# Save the updated HTML back to the file
with open('mlb.html', 'w', encoding='utf-8') as file:
    file.write(str(soup))

print("HTML file updated successfully!")
