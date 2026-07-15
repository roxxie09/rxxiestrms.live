import os
import sys
from datetime import datetime
import pytz
from bs4 import BeautifulSoup

TEAM_NAME_MAP = {
    'Atlanta': 'Atlanta Hawks',
    'Boston': 'Boston Celtics',
    'Brooklyn': 'Brooklyn Nets',
    'Charlotte': 'Charlotte Hornets',
    'Chicago': 'Chicago Bulls',
    'Cleveland': 'Cleveland Cavaliers',
    'Dallas': 'Dallas Mavericks',
    'Denver': 'Denver Nuggets',
    'Detroit': 'Detroit Pistons',
    'Golden State': 'Golden State Warriors',
    'Houston': 'Houston Rockets',
    'Indiana': 'Indiana Pacers',
    'LA': 'Los Angeles Clippers',
    'L.A.': 'Los Angeles Lakers',
    'LA Clippers': 'Los Angeles Clippers',
    'Los Angeles': 'Los Angeles Lakers',
    'Memphis': 'Memphis Grizzlies',
    'Miami': 'Miami Heat',
    'Milwaukee': 'Milwaukee Bucks',
    'Minnesota': 'Minnesota Timberwolves',
    'New Orleans': 'New Orleans Pelicans',
    'New York': 'New York Knicks',
    'Oklahoma City': 'Oklahoma City Thunder',
    'Orlando': 'Orlando Magic',
    'Philadelphia': 'Philadelphia 76ers',
    'Phoenix': 'Phoenix Suns',
    'Portland': 'Portland Trail Blazers',
    'Sacramento': 'Sacramento Kings',
    'San Antonio': 'San Antonio Spurs',
    'Toronto': 'Toronto Raptors',
    'Utah': 'Utah Jazz',
    'Washington': 'Washington Wizards'
}

WNBA_TEAM_NAME_MAP = {
    'Atlanta': 'Atlanta Dream',
    'Chicago': 'Chicago Sky',
    'Connecticut': 'Connecticut Sun',
    'Dallas': 'Dallas Wings',
    'Golden State': 'Golden State Valkyries',
    'Indiana': 'Indiana Fever',
    'Las Vegas': 'Las Vegas Aces',
    'Los Angeles': 'Los Angeles Sparks',
    'Minnesota': 'Minnesota Lynx',
    'New York': 'New York Liberty',
    'Phoenix': 'Phoenix Mercury',
    'Portland': 'Portland Fire',
    'Seattle': 'Seattle Storm',
    'Toronto': 'Toronto Tempo',
    'Washington': 'Washington Mystics'
}

def get_full_team_name(name):
    return TEAM_NAME_MAP.get(name, name)

def get_full_wnba_team_name(name):
    return WNBA_TEAM_NAME_MAP.get(name, name)

def convert_et_to_pdt(time_str, date_obj):
    eastern = pytz.timezone('US/Eastern')
    pacific = pytz.timezone('US/Pacific')

    dt_str = f"{date_obj.strftime('%Y-%m-%d')} {time_str}"
    naive_dt = datetime.strptime(dt_str, '%Y-%m-%d %I:%M %p')
    eastern_dt = eastern.localize(naive_dt)
    pacific_dt = eastern_dt.astimezone(pacific)

    return pacific_dt.strftime('%I:%M %p').lstrip('0')

def fetch_nba_games_for_date_from_file(html_file_path, date=None):
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%A, %B %d, %Y').replace(' 0', ' ').strip()

    with open(html_file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    schedule_sections = soup.select('div.ScheduleTables')

    for section in schedule_sections:
        date_title = section.select_one('.Table__Title')
        if not date_title:
            continue

        if not date_title.get_text(strip=True).startswith(date_str):
            continue

        table = section.find('table')
        if not table:
            return []

        games = []
        for row in table.select('tr.Table__TR'):
            away_span = row.select_one('td.events__col span.Table__Team')
            home_span = row.select_one('td.colspan__col span.Table__Team')
            time_cell = row.select_one('td.date__col')

            if not (away_span and home_span and time_cell):
                continue

            away_name = get_full_team_name(away_span.get_text(strip=True))
            home_name = get_full_team_name(home_span.get_text(strip=True))
            game_time_et = time_cell.get_text(strip=True)

            try:
                game_time = convert_et_to_pdt(game_time_et, date)
            except ValueError:
                game_time = game_time_et or 'TBD'

            display_time = f"{date.strftime('%B %d, %Y').replace(' 0', ' ')} {game_time}"
            games.append({
                'event': f"{away_name} vs {home_name}",
                'display_time': display_time,
            })

        return games

    return []

def fetch_wnba_games_for_date_from_file(html_file_path, date=None):
    if date is None:
        date = datetime.now()

    date_str = date.strftime('%A, %B %d, %Y').replace(' 0', ' ').strip()

    with open(html_file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    schedule_sections = soup.select('div.ScheduleTables')

    for section in schedule_sections:
        date_title = section.select_one('.Table__Title')
        if not date_title:
            continue

        if not date_title.get_text(strip=True).startswith(date_str):
            continue

        table = section.find('table')
        if not table:
            return []

        games = []
        for row in table.select('tr.Table__TR'):
            away_span = row.select_one('td.events__col span.Table__Team')
            home_span = row.select_one('td.colspan__col span.Table__Team')
            time_cell = row.select_one('td.date__col')

            if not (away_span and home_span and time_cell):
                continue

            away_name = get_full_wnba_team_name(away_span.get_text(strip=True))
            home_name = get_full_wnba_team_name(home_span.get_text(strip=True))
            game_time_et = time_cell.get_text(strip=True)

            try:
                game_time = convert_et_to_pdt(game_time_et, date)
            except ValueError:
                game_time = game_time_et or 'TBD'

            display_time = f"{date.strftime('%B %d, %Y').replace(' 0', ' ')} {game_time}"
            games.append({
                'event': f"{away_name} vs {home_name}",
                'display_time': display_time,
            })

        return games

    return []

def build_league_section(soup, title_text, games, stream_prefix):
    wrapper = soup.new_tag('div', **{'class': 'league-section'})

    heading = soup.new_tag('h2')
    heading.string = title_text
    wrapper.append(heading)

    table = soup.new_tag('table')
    table['class'] = 'schedule-table'

    thead = soup.new_tag('thead')
    tr_head = soup.new_tag('tr')

    for col in ['Event', 'Start Time', 'Countdown']:
        th = soup.new_tag('th')
        th.string = col
        tr_head.append(th)

    thead.append(tr_head)
    table.append(thead)

    tbody = soup.new_tag('tbody')

    for idx, game in enumerate(games, 1):
        tr = soup.new_tag('tr')

        td_event = soup.new_tag('td')
        a = soup.new_tag('a', href=f"https://roxiestreams.info/{stream_prefix}-streams-{idx}")
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

    table.append(tbody)
    wrapper.append(table)
    return wrapper

def update_combined_games_in_html(html_path, nba_games, wnba_games):
    with open(html_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    main_table = soup.find('table', id='eventsTable')
    if main_table is None:
        print("Could not find table with id='eventsTable'")
        return

    main_tbody = main_table.find('tbody')
    if main_tbody is None:
        print("Could not find <tbody> under eventsTable")
        return

    for tr in list(main_tbody.find_all('tr')):
        tr.decompose()

    for idx, game in enumerate(nba_games, 1):
        tr = soup.new_tag('tr')

        td_event = soup.new_tag('td')
        a = soup.new_tag('a', href=f"https://roxiestreams.info/nba-streams-{idx}")
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

        main_tbody.append(tr)

    old_wnba_section = soup.find('div', id='wnba-section')
    if old_wnba_section:
        old_wnba_section.decompose()

    wnba_container = soup.new_tag('div', id='wnba-section')
    wnba_section = build_league_section(soup, 'WNBA Games', wnba_games, 'wnba')
    wnba_container.append(wnba_section)

    main_table_parent = main_table.parent
    if main_table_parent:
        main_table_parent.append(wnba_container)
    else:
        main_table.insert_after(wnba_container)

    with open(html_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify(formatter="minimal")))

    print(f"Updated NBA and WNBA games in {html_path}")

if __name__ == '__main__':
    nba_html_path = r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nba.html"

    if len(sys.argv) > 1:
        date_str = sys.argv[1]
        date_formats = ['%Y-%m-%d', '%m-%d-%y', '%m-%d-%Y']
        input_date = None

        for fmt in date_formats:
            try:
                input_date = datetime.strptime(date_str, fmt)
                break
            except ValueError:
                pass

        if input_date is None:
            print("Invalid date format. Defaulting to today.")
            input_date = datetime.now()
    else:
        input_date = datetime.now()

    nba_source_path = 'nba.txt'
    wnba_source_path = 'nba2.txt'

    nba_schedule = fetch_nba_games_for_date_from_file(nba_source_path, input_date)
    wnba_schedule = fetch_wnba_games_for_date_from_file(wnba_source_path, input_date)

    if nba_schedule or wnba_schedule:
        update_combined_games_in_html(nba_html_path, nba_schedule, wnba_schedule)
    else:
        print(f"No NBA or WNBA games found for {input_date.strftime('%B %d, %Y')}.")