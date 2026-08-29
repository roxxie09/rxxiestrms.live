from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from bs4 import BeautifulSoup

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
    """Get a team name while stripping ESPN's standalone home-team @ marker."""
    at_marker = team_cell.select_one("span.at")
    if at_marker is not None:
        at_marker.decompose()

    link = team_cell.select_one("a[href*='/nfl/team/_/name/']")
    if link is not None:
        slug = link.get("href", "").rstrip("/").split("/")[-1]
        return NFL_TEAM_SLUG_MAP.get(slug, link.get_text(" ", strip=True))

    return team_cell.get_text(" ", strip=True).lstrip("@").strip()


def convert_et_to_pt(time_str: str, game_date: datetime) -> str:
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


def fetch_games_for_date(source_html_path: Path, target_date: datetime) -> list[dict]:
    """Extract games from either nfl.txt or nfl2.txt for the requested date."""
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
            pacific_time = time_text or "TBD"

        games.append(
            {
                "event": f"{away_team} vs {home_team}",
                "display_time": (
                    f"{target_date.strftime('%B')} {target_date.day}, "
                    f"{target_date.year} {pacific_time}"
                ),
            }
        )

    return games


def append_game_rows(soup: BeautifulSoup, tbody, games: list[dict], stream_prefix: str) -> None:
    for index, game in enumerate(games, start=1):
        row = soup.new_tag("tr")

        event_cell = soup.new_tag("td")
        event_link = soup.new_tag(
            "a",
            href=f"https://roxiestreams.info/{stream_prefix}-streams-{index}",
        )
        event_link.string = game["event"]
        event_cell.append(event_link)
        row.append(event_cell)

        time_cell = soup.new_tag("td", attrs={"class": "event-start-time"})
        time_cell.string = game["display_time"]
        row.append(time_cell)

        countdown_cell = soup.new_tag("td")
        countdown_cell.append(soup.new_tag("span", attrs={"class": "countdown-timer"}))
        row.append(countdown_cell)

        tbody.append(row)


def build_cfb_section(soup: BeautifulSoup, cfb_games: list[dict]):
    container = soup.new_tag("div", id="cfb-section")
    wrapper = soup.new_tag("div", attrs={"class": "league-section"})
    container.append(wrapper)

    heading = soup.new_tag("h2")
    heading.string = "CFB Events"
    wrapper.append(heading)

    table = soup.new_tag("table", attrs={"class": "schedule-table"})
    wrapper.append(table)

    thead = soup.new_tag("thead")
    header_row = soup.new_tag("tr")
    for label in ("Event", "Start Time", "Countdown"):
        header = soup.new_tag("th")
        header.string = label
        header_row.append(header)
    thead.append(header_row)
    table.append(thead)

    tbody = soup.new_tag("tbody")
    append_game_rows(soup, tbody, cfb_games, "cfb")
    table.append(tbody)

    return container


def update_games_in_html(
    output_html_path: Path,
    nfl_games: list[dict],
    cfb_games: list[dict],
) -> None:
    with output_html_path.open(encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    nfl_table = soup.find("table", id="eventsTable")
    if nfl_table is None:
        raise RuntimeError("Could not find table id='eventsTable' in the output HTML.")

    nfl_tbody = nfl_table.find("tbody")
    if nfl_tbody is None:
        nfl_tbody = soup.new_tag("tbody")
        nfl_table.append(nfl_tbody)

    # Always retain the NFL table/header; only replace its game rows.
    nfl_tbody.clear()
    append_game_rows(soup, nfl_tbody, nfl_games, "nfl")

    old_cfb_section = soup.find("div", id="cfb-section")
    if old_cfb_section is not None:
        old_cfb_section.decompose()

    # CFB is conditional: add its header/table only when nfl2.txt has games.
    if cfb_games:
        cfb_section = build_cfb_section(soup, cfb_games)
        nfl_table.insert_after(cfb_section)

    with output_html_path.open("w", encoding="utf-8") as file:
        file.write(str(soup.prettify(formatter="minimal")))


def main() -> None:
    script_dir = Path(__file__).resolve().parent
    nfl_source_path = script_dir / "nfl.txt"
    cfb_source_path = script_dir / "nfl2.txt"

    # Change only this line if the HTML page is located elsewhere.
    output_html_path = Path(
        r"G:\MY LEGIT EVERYTRHING FOLDER\RANDOM\rxxiestrms.live\nfl.html"
    )

    try:
        target_date = parse_cli_date(sys.argv[1]) if len(sys.argv) > 1 else datetime.now()
    except ValueError as exc:
        print(f"Invalid date: {exc}")
        sys.exit(1)

    if not nfl_source_path.exists():
        print(f"NFL source schedule file not found: {nfl_source_path}")
        sys.exit(1)

    if not cfb_source_path.exists():
        print(f"CFB source schedule file not found: {cfb_source_path}")
        sys.exit(1)

    if not output_html_path.exists():
        print(f"Output HTML file not found: {output_html_path}")
        sys.exit(1)

    nfl_games = fetch_games_for_date(nfl_source_path, target_date)
    cfb_games = fetch_games_for_date(cfb_source_path, target_date)

    update_games_in_html(output_html_path, nfl_games, cfb_games)

    target_label = target_date.strftime("%A, %B %d, %Y")
    print(f"Updated {len(nfl_games)} NFL game(s) for {target_label}.")
    print(f"Updated {len(cfb_games)} CFB game(s) for {target_label}.")


if __name__ == "__main__":
    main()
