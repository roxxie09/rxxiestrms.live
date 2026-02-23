import requests
from datetime import datetime, timedelta
import pytz
import platform
from bs4 import BeautifulSoup
import sys

def get_target_date_from_args_or_now():
    pacific = pytz.timezone('US/Pacific')
    # If a date argument is provided, parse it
    if len(sys.argv) > 1:
        raw = sys.argv[1]
        # Accept formats like 2-23-26 or 02-23-2026
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
            display_time = game_time_pdt.strftime(f'%B {day_format}, %Y %I:%M %p')
            data_start = game_time_pdt.strftime(f'%B {day_format}, %Y %H:%M:%S')
            data_end_time = game_time_pdt + timedelta(hours=12)
            data_end = data_end_time.strftime(f'%B {day_format}, %Y %H:%M:%S')
            games_list.append({
                'teams': f'{away_team} vs {home_team}',
                'display_time': display_time,
                'data_start': data_start,
                'data_end': data_end,
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
    for tr in list(tbody.find_all('tr')):
        tr.decompose()
    for idx, game in enumerate(games, start=1):
        stream_url = f"https://roxiestreams.info/mlb-streams-{idx}"
        tr = soup.new_tag('tr')

        td1 = soup.new_tag('td')
        a = soup.new_tag('a', href=stream_url)
        a.string = game['teams']
        td1.append(a)
        tr.append(td1)

        td2 = soup.new_tag('td')
        td2.string = game['display_time']
        tr.append(td2)

        td3 = soup.new_tag('td')
        span = soup.new_tag('span', **{'class':'countdown-timer'})
        span['data-start'] = game['data_start']
        span['data-end'] = game['data_end']
        td3.append(span)
        tr.append(td3)

        tbody.append(tr)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify(formatter="minimal")))
    print(f"Updated MLB games in {html_path}")

if __name__ == '__main__':
    update_games_in_html('mlb.html')
