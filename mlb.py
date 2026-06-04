import requests
from datetime import datetime, timedelta
import pytz
import platform
from bs4 import BeautifulSoup
import sys

def get_target_date_from_args_or_now():
    pacific = pytz.timezone('US/Pacific')
    if len(sys.argv) > 1:
        raw = sys.argv[1]
        for fmt in ('%m-%d-%y', '%m-%d-%Y'):
            try:
                dt = datetime.strptime(raw, fmt)
                return dt.date()
            except ValueError:
                continue
        raise ValueError(f"Could not parse date argument: {raw}")
    else:
        now_pacific = datetime.now(pacific)
        if 21 <= now_pacific.hour <= 23:
            target_date = now_pacific + timedelta(days=1)
        else:
            target_date = now_pacific
        return target_date.date()

def fetch_mlb_games_for_today():
    pacific = pytz.timezone('US/Pacific')
    target_date = get_target_date_from_args_or_now()
    today = target_date.strftime('%Y-%m-%d')

    url = f'https://statsapi.mlb.com/api/v1/schedule/games/?sportId=1&date={today}'
    response = requests.get(url)
    data = response.json()
    games = data.get('dates', [])

    games_list = []
    if platform.system() == 'Windows':
        day_format = '%#d'
    else:
        day_format = '%-d'

    for game_date in games:
        for game in game_date.get('games', []):
            teams = game['teams']
            home_team = teams['home']['team']['name']
            away_team = teams['away']['team']['name']
            game_time_utc_str = game['gameDate']
            game_time_utc = datetime.strptime(game_time_utc_str, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=pytz.utc)
            game_time_pdt = game_time_utc.astimezone(pacific)

            # Plain text in PDT — JS will localize it for each viewer
            display_time = game_time_pdt.strftime(f'%B {day_format}, %Y %I:%M %p')

            games_list.append({
                'teams': f'{away_team} vs {home_team}',
                'display_time': display_time,
            })
    return games_list

def update_games_in_html(html_path='mlb.html'):
    with open(html_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    games = fetch_mlb_games_for_today()
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

    for idx, game in enumerate(games, start=1):
        stream_url = f"https://roxiestreams.info/mlb-streams-{idx}"
        tr = soup.new_tag('tr')

        # Event name cell
        td1 = soup.new_tag('td')
        a = soup.new_tag('a', href=stream_url)
        a.string = game['teams']
        td1.append(a)
        tr.append(td1)

        # Start time cell — class="event-start-time", plain text, JS localizes it
        td2 = soup.new_tag('td')
        td2['class'] = 'event-start-time'
        td2.string = game['display_time']
        tr.append(td2)

        # Countdown cell — empty span, JS reads time from sibling td
        td3 = soup.new_tag('td')
        span = soup.new_tag('span', **{'class': 'countdown-timer'})
        td3.append(span)
        tr.append(td3)

        tbody.append(tr)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify(formatter="minimal")))
    print(f"Updated MLB games in {html_path}")

if __name__ == '__main__':
    update_games_in_html('mlb.html')