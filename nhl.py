import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys
from bs4 import BeautifulSoup

PACIFIC_TZ = ZoneInfo("America/Los_Angeles")
HTML_PATH = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nhl.html"

def parse_date_arg(date_str=None):
    if date_str:
        try:
            dt = datetime.strptime(date_str, "%m-%d-%y")
            return dt.strftime("%Y%m%d")
        except ValueError:
            print(f"Invalid date format '{date_str}'. Use MM-DD-YY like 12-8-25.")
            sys.exit(1)
    return datetime.now().strftime("%Y%m%d")

def get_nhl_games(date_ymd):
    url = f"https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?dates={date_ymd}"
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except:
        url = "https://site.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()

    games = []
    for event in data.get("events", []):
        competitions = event.get("competitions", [])
        if not competitions:
            continue
        comp = competitions[0]
        competitors = comp.get("competitors", [])
        if len(competitors) != 2:
            continue

        home = next((c for c in competitors if c.get("homeAway") == "home"), None)
        away = next((c for c in competitors if c.get("homeAway") == "away"), None)
        if not home or not away:
            continue

        home_team = home["team"].get("displayName") or home["team"].get("shortDisplayName")
        away_team = away["team"].get("displayName") or away["team"].get("shortDisplayName")

        start_str = event.get("date")
        try:
            if start_str.endswith('Z'):
                dt_utc = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
            else:
                dt_utc = datetime.fromisoformat(start_str)
            dt_pacific = dt_utc.astimezone(PACIFIC_TZ)
            # Plain text PDT time — JS will localize for each viewer
            display_time = dt_pacific.strftime("%B %#d, %Y %I:%M %p")
        except Exception as e:
            print(f"Time parse error for {away_team} vs {home_team}: {e}")
            display_time = "TBD"

        games.append({
            "matchup": f"{away_team} vs {home_team}",
            "display_time": display_time,
        })
    return games

def update_games_in_html(html_path, games):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    table = soup.find('table', id='eventsTable')
    if table is None:
        print("Could not find table with id='eventsTable'")
        return
    tbody = table.find('tbody')
    if tbody is None:
        print("Could not find <tbody> under eventsTable")
        return

    # Clear existing rows
    for tr in list(tbody.find_all('tr')):
        tr.decompose()

    for idx, game in enumerate(games, 1):
        tr = soup.new_tag('tr')

        # Event name cell
        td_event = soup.new_tag('td')
        a = soup.new_tag('a', href=f"https://roxiestreams.info/nhl-streams-{idx}")
        a.string = game['matchup']
        td_event.append(a)
        tr.append(td_event)

        # Start time cell — class="event-start-time", plain text, JS localizes it
        td_time = soup.new_tag('td')
        td_time['class'] = 'event-start-time'
        td_time.string = game['display_time']
        tr.append(td_time)

        # Countdown cell — empty span, JS reads time from sibling td
        td_countdown = soup.new_tag('td')
        span = soup.new_tag('span', **{'class': 'countdown-timer'})
        td_countdown.append(span)
        tr.append(td_countdown)

        tbody.append(tr)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify(formatter="minimal")))
    print(f"Updated NHL games in {html_path}")

if __name__ == '__main__':
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    date_ymd = parse_date_arg(date_arg)
    games = get_nhl_games(date_ymd)

    if games:
        update_games_in_html(HTML_PATH, games)
    else:
        print(f"No NHL games found for {date_ymd}.")