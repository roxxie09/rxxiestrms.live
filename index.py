from bs4 import BeautifulSoup
from datetime import datetime, timedelta

INPUT_FILE = "index.html"
OUTPUT_FILE = "index.html"

# Change to -08:00 in winter (PST), -07:00 in summer (PDT)
UTC_OFFSET = "-07:00"

def parse_event_time(event_time_str: str):
    formats = [
        '%B %d, %Y %I:%M %p',
        '%B %d, %Y %H:%M',
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

    # Read from data-utc on the second <td> if already set,
    # otherwise fall back to reading plain text (old format)
    time_td = tds[1]
    existing_utc = time_td.get("data-utc", "").strip()

    if existing_utc:
        # Already in new format, re-use the date portion to sync data-start
        event_time_str = existing_utc[:19]  # "2026-05-28T11:00:00"
        event_time = datetime.strptime(event_time_str, "%Y-%m-%dT%H:%M:%S")
    else:
        # Old plain-text format — migrate it
        event_time_str = time_td.get_text(strip=True)
        event_time = parse_event_time(event_time_str)
        if not event_time:
            continue

    # Build ISO string with offset
    iso_str = event_time.strftime("%Y-%m-%dT%H:%M:%S") + UTC_OFFSET

    # Update the time <td> to new format (empty cell, data-utc set)
    time_td.clear()
    time_td["class"] = "event-start-time"
    time_td["data-utc"] = iso_str

    # Update countdown span
    countdown_span = tds[2].find("span", class_="countdown-timer")
    if countdown_span:
        countdown_span["data-start"] = iso_str
        # Remove old data-end if present
        if countdown_span.has_attr("data-end"):
            del countdown_span["data-end"]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(str(soup))

print("index.html updated successfully.")