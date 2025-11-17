from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pytz

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

def get_full_team_name(name):
    return TEAM_NAME_MAP.get(name, name)

def convert_et_to_pst(time_str, date_obj):
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

    schedule_sections = soup.find_all('div', class_='ScheduleTables--nba')

    for section in schedule_sections:
        date_title = section.find('div', class_='Table__Title')
        if not date_title:
            continue
        dt_text = date_title.get_text(strip=True)
        if dt_text.startswith(date_str):
            tables = section.find_all('table')
            if not tables:
                return []
            schedule_table = tables[0]
            games = []
            rows = schedule_table.find_all('tr')[1:]  # skip header
            for row in rows:
                away_span = row.select_one('span.Table__Team.away')
                home_span = None
                for span in row.select('span.Table__Team'):
                    if 'away' not in span.get('class', []):
                        home_span = span
                        break

                time_cell = row.find('td', class_='date__col')
                if away_span and home_span and time_cell:
                    away_name = get_full_team_name(away_span.get_text(strip=True))
                    home_name = get_full_team_name(home_span.get_text(strip=True))
                    game_time_et = time_cell.get_text(strip=True)
                    game_time_pst = convert_et_to_pst(game_time_et, date)
                    games.append({
                        'event': f"{away_name} vs {home_name}",
                        'time': f"{date.strftime('%B %d, %Y')} {game_time_pst}",
                        'countdown_start': f"{date.strftime('%B %d, %Y')} {game_time_pst}:00",
                        'countdown_end': f"{(date + timedelta(days=1)).strftime('%B %d, %Y')} {game_time_pst}:00"
                    })
            return games
    return []

def append_or_replace_schedule(html_file_path, new_games, new_date):
    new_date_str = new_date.strftime('%B %d, %Y')

    with open(html_file_path, encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    container = soup.find('div', class_='container container-fluid pt-2 text-white')

    existing_headers = container.find_all('h2')
    for header in existing_headers:
        if new_date_str in header.text:
            next_table = header.find_next_sibling('table')
            if next_table:
                tbody = next_table.find('tbody')
                tbody.clear()
                for idx, game in enumerate(new_games, 1):
                    tr = soup.new_tag('tr')

                    td_event = soup.new_tag('td')
                    a = soup.new_tag('a', href=f"https://roxiestreams.live/nba-streams-{idx}")
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
                print(f"Replaced schedule for {new_date_str} in the HTML file.")
                break
    else:
        # Insert new section before footer
        new_header = soup.new_tag('h2')
        new_header.string = f"NBA Schedule for {new_date_str}"

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
            a = soup.new_tag('a', href=f"https://roxiestreams.live/nba-streams-{idx}")
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

        footer = container.find('footer')
        if footer:
            footer.insert_before(new_header)
            new_header.insert_after(new_table)
        else:
            container.append(new_header)
            container.append(new_table)

        print(f"Appended new schedule for {new_date_str} above the footer in the HTML file.")

    with open(html_file_path, 'w', encoding='utf-8') as f:
        f.write(str(soup.prettify()))

if __name__ == '__main__':
    import sys

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

    new_schedule = fetch_nba_games_for_date_from_file('nba.txt', input_date)
    if new_schedule:
        append_or_replace_schedule(nba_html_path, new_schedule, input_date)
    else:
        print(f"No NBA games found for {input_date.strftime('%B %d, %Y')}.")
