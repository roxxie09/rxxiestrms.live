from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz
import sys

NFL_TEAM_NAME_MAP = {
    "Arizona": "Arizona Cardinals",
    "Atlanta": "Atlanta Falcons",
    "Baltimore": "Baltimore Ravens",
    "Buffalo": "Buffalo Bills",
    "Carolina": "Carolina Panthers",
    "Chicago": "Chicago Bears",
    "Cincinnati": "Cincinnati Bengals",
    "Cleveland": "Cleveland Browns",
    "Dallas": "Dallas Cowboys",
    "Denver": "Denver Broncos",
    "Detroit": "Detroit Lions",
    "Green Bay": "Green Bay Packers",
    "Houston": "Houston Texans",
    "Indianapolis": "Indianapolis Colts",
    "Jacksonville": "Jacksonville Jaguars",
    "Kansas City": "Kansas City Chiefs",
    "Las Vegas": "Las Vegas Raiders",
    "Los Angeles": "Los Angeles Rams",
    "Miami": "Miami Dolphins",
    "Minnesota": "Minnesota Vikings",
    "New England": "New England Patriots",
    "New Orleans": "New Orleans Saints",
    "New York Jets": "New York Jets",
    "New York Giants": "New York Giants",
    "Philadelphia": "Philadelphia Eagles",
    "Pittsburgh": "Pittsburgh Steelers",
    "San Francisco": "San Francisco 49ers",
    "Seattle": "Seattle Seahawks",
    "Tampa Bay": "Tampa Bay Buccaneers",
    "Tennessee": "Tennessee Titans",
    "Washington": "Washington Commanders",
}

def convert_et_to_pst(time_str, date_obj):
    eastern = pytz.timezone('US/Eastern')
    pacific = pytz.timezone('US/Pacific')
    dt_str = f"{date_obj.strftime('%Y-%m-%d')} {time_str}"
    naive_dt = datetime.strptime(dt_str, '%Y-%m-%d %I:%M %p')
    eastern_dt = eastern.localize(naive_dt)
    pacific_dt = eastern_dt.astimezone(pacific)
    return pacific_dt.strftime('%I:%M %p').lstrip('0')

def format_date_cli_to_verbose(date_str):
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        day = dt.day
        return dt.strftime(f'%A, %B {day}, %Y')
    except Exception:
        print("Invalid date format. Please use YYYY-MM-DD.")
        sys.exit(1)

def fetch_nfl_games_for_date(html_file_path, target_date_verbose):
    with open(html_file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    date_divs = soup.find_all('div', class_='Table__Title')
    for div in date_divs:
        if div.text.strip() == target_date_verbose:
            table_wrapper = div.find_next_sibling('div').find('table', class_='Table')
            if not table_wrapper:
                return []
            rows = table_wrapper.find('tbody').find_all('tr')
            games = []
            for row in rows:
                cols = row.find_all('td')
                if len(cols) >= 3:
                    away_short = cols[0].find('span', class_='Table__Team').get_text(strip=True)
                    home_short = cols[1].find('span', class_='Table__Team').get_text(strip=True)
                    game_time_et = cols[2].text.strip()
                    try:
                        date_obj = datetime.strptime(target_date_verbose, '%A, %B %d, %Y')
                        game_time_pst = convert_et_to_pst(game_time_et, date_obj)
                    except:
                        game_time_pst = game_time_et

                    away_full = NFL_TEAM_NAME_MAP.get(away_short, away_short)
                    home_full = NFL_TEAM_NAME_MAP.get(home_short, home_short)

                    games.append({
                        'event': f"{away_full} vs {home_full}",
                        'time': f"{date_obj.strftime('%B %d, %Y')} {game_time_pst}",
                        'countdown_start': f"{date_obj.strftime('%B %d, %Y')} {game_time_pst}:00",
                        'countdown_end': f"{(date_obj + timedelta(days=1)).strftime('%B %d, %Y')} {game_time_pst}:00"
                    })
            return games
    return []

def append_or_replace_schedule(html_file_path, new_games, new_date_str):
    with open(html_file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    container = soup.find('div', class_='container container-fluid pt-2 text-white')
    existing_headers = container.find_all('h2')

    for header in existing_headers:
        if new_date_str in header.text:
            table = header.find_next_sibling('table')
            if table:
                tbody = table.find('tbody')
                tbody.clear()
                for idx, game in enumerate(new_games, 1):
                    tr = soup.new_tag('tr')

                    td_event = soup.new_tag('td')
                    a = soup.new_tag('a', href=f"https://roxiestreams.info/nfl-streams-{idx}")
                    a.string = game['event']
                    td_event.append(a)

                    td_time = soup.new_tag('td')
                    td_time.string = game['time']

                    td_countdown = soup.new_tag('td')
                    span = soup.new_tag('span', **{'class': 'countdown-timer'})
                    span['data-start'] = game['countdown_start']
                    span['data-end'] = game['countdown_end']
                    td_countdown.append(span)

                    tr.extend([td_event, td_time, td_countdown])
                    tbody.append(tr)
                print(f"Replaced schedule for {new_date_str}")
                break
    else:
        new_header = soup.new_tag('h2')
        new_header.string = f"NFL Schedule for {new_date_str}"
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
            a = soup.new_tag('a', href=f"https://roxiestreams.info/nfl-streams-{idx}")
            a.string = game['event']
            td_event.append(a)
            td_time = soup.new_tag('td')
            td_time.string = game['time']
            td_countdown = soup.new_tag('td')
            span = soup.new_tag('span', **{'class': 'countdown-timer'})
            span['data-start'] = game['countdown_start']
            span['data-end'] = game['countdown_end']
            td_countdown.append(span)
            tr.extend([td_event, td_time, td_countdown])
            tbody.append(tr)
        new_table.append(tbody)

        footer = soup.find('footer', class_='container-fluid')
        if footer:
            footer.insert_before(new_header)
            footer.insert_before(new_table)
        else:
            container.append(new_header)
            container.append(new_table)
        print(f"Appended schedule for {new_date_str}")

    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

if __name__ == '__main__':
    nfl_html_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nfl.html"

    if len(sys.argv) > 1:
        date_arg = format_date_cli_to_verbose(sys.argv[1])
    else:
        now = datetime.now()
        day = now.day
        date_arg = now.strftime(f'%A, %B {day}, %Y')

    new_games = fetch_nfl_games_for_date('nfl.txt', date_arg)
    if new_games:
        append_or_replace_schedule(nfl_html_path, new_games, date_arg)
    else:
        print(f"No NFL games found for {date_arg}")
