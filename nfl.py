from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import sys

NFL_TEAM_SLUG_MAP = {
    "arizona-cardinals": "Arizona Cardinals",
    "atlanta-falcons": "Atlanta Falcons",
    "baltimore-ravens": "Baltimore Ravens",
    "buffalo-bills": "Buffalo Bills",
    "carolina-panthers": "Carolina Panthers",
    "chicago-bears": "Chicago Bears",
    "cincinnati-bengals": "Cincinnati Bengals",
    "cleveland-browns": "Cleveland Browns",
    "dallas-cowboys": "Dallas Cowboys",
    "denver-broncos": "Denver Broncos",
    "detroit-lions": "Detroit Lions",
    "green-bay-packers": "Green Bay Packers",
    "houston-texans": "Houston Texans",
    "indianapolis-colts": "Indianapolis Colts",
    "jacksonville-jaguars": "Jacksonville Jaguars",
    "kansas-city-chiefs": "Kansas City Chiefs",
    "las-vegas-raiders": "Las Vegas Raiders",
    "los-angeles-chargers": "Los Angeles Chargers",
    "los-angeles-rams": "Los Angeles Rams",
    "miami-dolphins": "Miami Dolphins",
    "minnesota-vikings": "Minnesota Vikings",
    "new-england-patriots": "New England Patriots",
    "new-orleans-saints": "New Orleans Saints",
    "new-york-giants": "New York Giants",
    "new-york-jets": "New York Jets",
    "philadelphia-eagles": "Philadelphia Eagles",
    "pittsburgh-steelers": "Pittsburgh Steelers",
    "san-francisco-49ers": "San Francisco 49ers",
    "seattle-seahawks": "Seattle Seahawks",
    "tampa-bay-buccaneers": "Tampa Bay Buccaneers",
    "tennessee-titans": "Tennessee Titans",
    "washington-commanders": "Washington Commanders",
}

EASTERN = ZoneInfo("America/New_York")
PACIFIC = ZoneInfo("America/Los_Angeles")


def parse_cli_date(value: str) -> datetime:
    for fmt in ("%Y-%m-%d", "%m-%d-%Y", "%m-%d-%y"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            pass
    raise ValueError("Use YYYY-MM-DD, MM-DD-YYYY, or MM-DD-YY.")


def get_team_name(team_cell) -> str:
    """Resolve a full NFL team name from ESPN's team URL, not city-only text."""
    link = team_cell.select_one("a[href*='/nfl/team/_/name/']")
    if link is None:
        return team_cell.get_text(" ", strip=True)

    slug = link.get("href", "").rstrip("/").split("/")[-1]
    return NFL_TEAM_SLUG_MAP.get(slug, link.get_text(" ", strip=True))


def convert_et_to_pt(time_str: str, game_date: datetime) -> str:
    """Convert a source time such as '8:00 PM' ET into Pacific time."""
    naive = datetime.strptime(
        f"{game_date:%Y-%m-%d} {time_str}",
        "%Y-%m-%d %I:%M %p",
    )
    pacific_time = naive.replace(tzinfo=EASTERN).astimezone(PACIFIC)
    return pacific_time.strftime("%I:%M %p").lstrip("0")


def find_schedule_table(soup: BeautifulSoup, target_date_verbose: str):
    for title in soup.select("div.Table__Title"):
        if title.get_text(" ", strip=True) != target_date_verbose:
            continue

        wrapper = title.find_next_sibling("div")
        if wrapper is None:
            continue

        table = wrapper.select_one("table.Table")
        if table is not None:
            return table

    return None


def fetch_nfl_games_for_date(source_html_path: Path, target_date: datetime) -> list[dict]:
    target_date_verbose = target_date.strftime("%A, %B %d, %Y")

    with source_html_path.open(encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    table = find_schedule_table(soup, target_date_verbose)
    if table is None:
        return []

    tbody = table.find("tbody")
    if tbody is None:
        return []

    games = []
    for row in tbody.find_all("tr", recursive=False):
        cols = row.find_all("td", recursive=False)
        if len(cols) < 3:
            continue

        away_team = get_team_name(cols[0])
        home_team = get_team_name(cols[1])
        time_text = cols[2].get_text(" ", strip=True)

        try:
            pacific_time = convert_et_to_pt(time_text, target_date)
        except ValueError:
            pacific_time = time_text

        games.append({
            "event": f"{away_team} vs {home_team}",
            "display_time": f"{target_date.strftime('%B')} {target_date.day}, {target_date.year} {pacific_time}",
        })

    return games


def update_games_in_html(output_html_path: Path, games: list[dict]) -> None:
    with output_html_path.open(encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    table = soup.find("table", id="eventsTable")
    if table is None:
        raise RuntimeError("Could not find <table id='eventsTable'> in the output HTML.")

    tbody = table.find("tbody")
    if tbody is None:
        tbody = soup.new_tag("tbody")
        table.append(tbody)

    tbody.clear()

    for index, game in enumerate(games, start=1):
        row = soup.new_tag("tr")

        event_cell = soup.new_tag("td")
        event_link = soup.new_tag(
            "a",
            href=f"https://roxiestreams.info/nfl-streams-{index}",
        )
        event_link.string = game["event"]
        event_cell.append(event_link)
        row.append(event_cell)

        time_cell = soup.new_tag("td", attrs={"class": "event-start-time"})
        time_cell.string = game["display_time"]
        row.append(time_cell)

        countdown_cell = soup.new_tag("td")
        countdown = soup.new_tag("span", attrs={"class": "countdown-timer"})
        countdown_cell.append(countdown)
        row.append(countdown_cell)

        tbody.append(row)

    with output_html_path.open("w", encoding="utf-8") as file:
        file.write(str(soup.prettify(formatter="minimal")))


def main() -> None:
    script_dir = Path(__file__).resolve().parent

    # Change only this line if your source scrape file lives elsewhere.
    source_html_path = script_dir / "nfl.txt"

    # Your existing absolute path is retained for the page that gets updated.
    output_html_path = Path(
        r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nfl.html"
    )

    try:
        target_date = parse_cli_date(sys.argv[1]) if len(sys.argv) > 1 else datetime.now()
    except ValueError as exc:
        print(f"Invalid date: {exc}")
        sys.exit(1)

    if not source_html_path.exists():
        print(f"Source schedule file not found: {source_html_path}")
        sys.exit(1)

    if not output_html_path.exists():
        print(f"Output HTML file not found: {output_html_path}")
        sys.exit(1)

    games = fetch_nfl_games_for_date(source_html_path, target_date)
    target_label = target_date.strftime("%A, %B %d, %Y")

    if not games:
        print(f"No NFL games found for {target_label}.")
        sys.exit(0)

    update_games_in_html(output_html_path, games)
    print(f"Updated {len(games)} NFL game(s) for {target_label}: {output_html_path}")


if __name__ == "__main__":
    main()
