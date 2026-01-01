from bs4 import BeautifulSoup
from datetime import datetime, timedelta

INPUT_FILE = "nfl.html"
OUTPUT_FILE = "nfl.html"

def parse_event_time(event_time_str: str):
    # Expected: January 01, 2026 09:00 AM
    formats = [
        '%B %d, %Y %I:%M %p',   # 12-hour with AM/PM
        '%B %d, %Y %H:%M',      # 24-hour without AM/PM (fallback)
    ]
    for fmt in formats:
        try:
            return datetime.strptime(event_time_str, fmt)
        except ValueError:
            continue
    print(f"Could not parse date: {event_time_str!r}")
    return None

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

rows = soup.select("table#eventsTable tbody tr")

for row in rows:
    tds = row.find_all("td")
    if len(tds) < 3:
        continue

    # Second <td> is the visible start time
    event_time_str = tds[1].get_text(strip=True)
    event_time = parse_event_time(event_time_str)
    if not event_time:
        continue

    countdown_span = tds[2].find("span", class_="countdown-timer")
    if not countdown_span:
        continue

    # data-start = event start time
    start_str = event_time.strftime('%B %d, %Y %I:%M:%S %p')
    # data-end = 2 hours after start
    end_time = event_time + timedelta(hours=24)
    end_str = end_time.strftime('%B %d, %Y %I:%M:%S %p')

    countdown_span["data-start"] = start_str
    countdown_span["data-end"] = end_str

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("nfl.html updated successfully.")
