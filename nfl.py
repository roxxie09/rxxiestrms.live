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

def convert_et_to_pdt(time_str, date_obj):
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
        return dt.strftime('%A, %B %d, %Y')
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
                        game_time_pdt = convert_et_to_pdt(game_time_et, date_obj)
                    except:
                        game_time_pdt = game_time_et
                        date_obj = datetime.now()

                    away_full = NFL_TEAM_NAME_MAP.get(away_short, away_short)
                    home_full = NFL_TEAM_NAME_MAP.get(home_short, home_short)

                    # Plain text PDT time — JS will localize for each viewer
                    display_time = f"{date_obj.strftime('%B %#d, %Y')} {game_time_pdt}"

                    games.append({
                        'event': f"{away_full} vs {home_full}",
                        'display_time': display_time,
                    })
            return games
    return []

def update_games_in_html(html_file_path, new_games):
    with open(html_file_path, encoding='utf-8') as f:
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

    for idx, game in enumerate(new_games, 1):
        tr = soup.new_tag('tr')

        td_event = soup.new_tag('td')
        a = soup.new_tag('a', href=f"https://roxiestreams.info/nfl-streams-{idx}")
        a.string = game['event']
        td_event.append(a)
        tr.append(td_event)

        td_time = soup.new_tag('td')
        td_time['class'] = 'event-start-time'
        td_time.string = game['display_time']
        tr.append(td_time)

        td_countdown = soup.new_tag('td')
        span = soup.new_tag('span', **{'class': 'countdown-timer'})
        td_countdown.append(span)
        tr.append(td_countdown)

        tbody.append(tr)

    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify(formatter="minimal")))
    print(f"Updated NFL games in {html_file_path}")

if __name__ == '__main__':
    # Update this path to wherever your nfl.html lives
    nfl_html_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nfl.html"

    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        date_formats = ['%Y-%m-%d', '%m-%d-%y', '%m-%d-%Y']
        input_date_str = None
        for fmt in date_formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                input_date_str = dt.strftime('%Y-%m-%d')
                break
            except ValueError:
                pass
        if input_date_str is None:
            print("Invalid date format. Defaulting to today.")
            input_date_str = datetime.now().strftime('%Y-%m-%d')
    else:
        input_date_str = datetime.now().strftime('%Y-%m-%d')

    target_date_verbose = format_date_cli_to_verbose(input_date_str)
    new_schedule = fetch_nfl_games_for_date('nfl.txt', target_date_verbose)

    if new_schedule:
        update_games_in_html(nfl_html_path, new_schedule)
    else:
        print(f"No NFL games found for {target_date_verbose}.")