import subprocess
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import re

TEAM_NAME_MAP = {
    'Prairie View A&M': 'Prairie View A&M Panthers',
    'Lehigh': 'Lehigh Mountain Hawks',
    'Miami OH': 'Miami (OH) RedHawks',
    'SMU': 'SMU Mustangs',
}

def get_full_team_name(name):
    clean_name = re.sub(r'^\d+\s*', '', name).strip('&M')
    return TEAM_NAME_MAP.get(clean_name, clean_name)

def convert_et_to_pst(time_str, date_obj):
    eastern = pytz.timezone('US/Eastern')
    pacific = pytz.timezone('US/Pacific')
    dt_str = f"{date_obj.strftime('%Y-%m-%d')} {time_str}"
    try:
        naive_dt = datetime.strptime(dt_str, '%Y-%m-%d %I:%M %p')
        eastern_dt = eastern.localize(naive_dt)
        pacific_dt = eastern_dt.astimezone(pacific)
        return pacific_dt.strftime('%I:%M %p').lstrip('0')
    except:
        return time_str

def fetch_march_madness_games_for_date_from_file(html_file_path, date=None):
    if date is None:
        date = datetime.now().date()
    date_str = date.strftime('%A, %B %d, %Y').replace(' 0', ' ')

    print(f"Looking for date: '{date_str}'")

    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Date header in ESPN HTML
    titles = soup.find_all('div', class_='Table__Title')
    print(f"Found {len(titles)} Table__Title divs")
    for t in titles:
        print(f" - '{t.get_text(strip=True)}'")

    # Container: <div class="ScheduleTables mb5 ScheduleTables--ncaam ScheduleTables--basketball">
    schedule_containers = soup.find_all(
        'div',
        class_=lambda c: c and 'ScheduleTables--ncaam' in c
    )
    print(f"Found {len(schedule_containers)} ScheduleTables--ncaam containers")

    for container in schedule_containers:
        date_title = container.find('div', class_='Table__Title')
        if not date_title:
            continue
        dt_text = date_title.get_text(strip=True)
        print(f"Container title: '{dt_text}'")

        if not dt_text.startswith(date_str):
            continue

        print("*** MATCHED container ***")
        table = container.find('table', class_='Table')
        if not table:
            print("No table found in container")
            continue

        tbody = table.find('tbody', class_='Table__TBODY') or table.find('tbody')
        rows = tbody.find_all('tr') if tbody else table.find_all('tr')

        games = []

        for j, row in enumerate(rows):
            classes = row.get('class', [])
            print(f"Row {j} classes: {classes}")

            # Skip pure note rows like:
            # <tr ...><td colspan=7><div class="gameNote">...</div></td></tr>
            if row.find('div', class_='gameNote'):
                continue

            # Away team: in td.events__col > div.matchTeams > span.Table__Team.away
            away_span = row.select_one('td.events__col div.matchTeams span.Table__Team.away')
            # Home team: in td.colspan__col > div.local > last span.Table__Team
            home_span = None
            home_team_spans = row.select('td.colspan__col div.local span.Table__Team')
            if home_team_spans:
                home_span = home_team_spans[-1]

            # Time cell: td.date__col
            time_cell = row.find('td', class_='date__col')
            time_text = time_cell.get_text(strip=True) if time_cell else ''
            print(
                f"  Away: {away_span.get_text(strip=True) if away_span else 'MISS'} | "
                f"Home: {home_span.get_text(strip=True) if home_span else 'MISS'} | "
                f"Time raw: '{time_text}'"
            )

            # Time can be "9:15 PM" or "LIVE" (no time). Only use rows with an actual time.
            m = re.search(r'(\d+:\d+\s*[AP]M)', time_text)
            if not (away_span and home_span and m):
                continue

            away_name = get_full_team_name(away_span.get_text(strip=True))
            home_name = get_full_team_name(home_span.get_text(strip=True))
            game_time_et = m.group(1)
            game_time_pst = convert_et_to_pst(game_time_et, date)

            games.append({
                'event': f"{away_name} vs {home_name}",
                'time': f"{date.strftime('%B %d, %Y')} {game_time_pst}",
                'countdown_start': f"{date.strftime('%B %d, %Y')} {game_time_pst}:00",
                'countdown_end': f"{(date + timedelta(days=1)).strftime('%B %d, %Y')} {game_time_pst}:00"
            })

        print(f"Extracted {len(games)} games: {games}")
        return games

    print("No matching container found")
    return []

def append_or_replace_schedule(html_file_path, new_games, new_date):
    new_date_str = new_date.strftime('%B %d, %Y')

    with open(html_file_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    container = soup.find('div', class_='container container-fluid pt-2 text-white')
    if not container:
        print("Container not found - creating new HTML")
        # Create basic HTML if missing
        html = f"""
<!DOCTYPE html>
<html>
<head><title>March Madness</title></head>
<body>
<div class="container container-fluid pt-2 text-white">
<h1>March Madness Schedule</h1>
<footer>Footer</footer>
</div>
</body>
</html>
        """
        soup = BeautifulSoup(html, 'html.parser')
        container = soup.find('div', class_='container container-fluid pt-2 text-white')

    # Rest of function exactly like your NBA version...
    existing_headers = container.find_all('h2')
    header_found = False
    for header in existing_headers:
        if new_date_str in header.text:
            next_table = header.find_next_sibling('table')
            if next_table:
                tbody = next_table.find('tbody')
                if tbody:
                    tbody.clear()
                else:
                    tbody = soup.new_tag('tbody')
                    next_table.append(tbody)
                # Build table rows...
                for idx, game in enumerate(new_games, 1):
                    tr = soup.new_tag('tr')
                    td_event = soup.new_tag('td')
                    a = soup.new_tag('a', href=f"https://roxiestreams.info/ncaa-streams-{idx}")
                    a.string = game['event']
                    td_event.append(a)
                    td_time = soup.new_tag('td')
                    td_time.string = game['time']
                    td_countdown = soup.new_tag('td')
                    span = soup.new_tag('span', cls='countdown-timer')
                    span['data-start'] = game['countdown_start']
                    span['data-end'] = game['countdown_end']
                    td_countdown.append(span)
                    tr.extend([td_event, td_time, td_countdown])
                    tbody.append(tr)
                print(f"✅ Replaced {len(new_games)} games for {new_date_str}")
                header_found = True
                break

    if not header_found:
        # Append new section (same as NBA version)
        new_header = soup.new_tag('h2')
        new_header.string = f"March Madness Schedule for {new_date_str}"
        new_table = soup.new_tag('table', id='eventsTable')
        thead = soup.new_tag('thead')
        tr_head = soup.new_tag('tr')
        for col in ['Event', 'Start Time', 'Countdown']:
            th = soup.new_tag('th')
            th.string = col
            tr_head.append(th)
        thead.append(tr_head)
        new_table.append(thead)
        tbody = soup.new_tag('tbody')
        for idx, game in enumerate(new_games, 1):
            tr = soup.new_tag('tr')
            td_event = soup.new_tag('td')
            a = soup.new_tag('a', href=f"https://roxiestreams.info/ncaa-streams-{idx}")
            a.string = game['event']
            td_event.append(a)
            td_time = soup.new_tag('td')
            td_time.string = game['time']
            td_countdown = soup.new_tag('td')
            span = soup.new_tag('span', cls='countdown-timer')
            span['data-start'] = game['countdown_start']
            span['data-end'] = game['countdown_end']
            td_countdown.append(span)
            tr.extend([td_event, td_time, td_countdown])
            tbody.append(tr)
        new_table.append(tbody)
        footer = container.find('footer')
        if footer:
            footer.insert_before(new_table)
            footer.insert_before(new_header)
        else:
            container.append(new_header)
            container.append(new_table)
        print(f"✅ Added {len(new_games)} new games for {new_date_str}")

    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())
    print(f"✅ Saved to {html_file_path}")

if __name__ == '__main__':
    import sys
    march_txt_path = 'march.txt'
    march_html_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\march-madness.html"

    if len(sys.argv) > 1:
        input_date = datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
    else:
        input_date = datetime.now().date()

    if not os.path.exists(march_txt_path):
        print(f"❌ {march_txt_path} missing!")
        exit(1)

    new_schedule = fetch_march_madness_games_for_date_from_file(march_txt_path, input_date)
    if new_schedule:
        append_or_replace_schedule(march_html_path, new_schedule, input_date)
    else:
        print("❌ No games found")

if __name__ == '__main__':
    march_txt_path = 'march.txt'
    if not os.path.exists(march_txt_path):
        print(f"ERROR: {march_txt_path} not found! Save ESPN HTML there.")
        exit(1)
    
    input_date = datetime(2026, 3, 18).date()  # Hardcode today
    new_schedule = fetch_march_madness_games_for_date_from_file(march_txt_path, input_date)
    
    if new_schedule:
        append_or_replace_schedule(march_html_path, new_schedule, input_date)
    else:
        print("No games extracted.")
