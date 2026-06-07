from bs4 import BeautifulSoup
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MULTIVIEW_HTML = os.path.join(BASE_DIR, "multiview.html")

SCHEDULE_STREAM_MAP = {
    "soccer.html":      {"pattern": "soccer-streams-{n}.html",  "default": {"subdomain": "601",      "path": "cyrus.m3u8",   "txt": "domainsz29.txt"}},
    "mlb.html":         {"pattern": "mlb-streams-{n}.html",     "default": {"subdomain": "601",      "path": "mlb.m3u8",     "txt": "domainsz29.txt"}},
    "nba.html":         {"pattern": "nba-streams-{n}.html",     "default": {"subdomain": "daffodil", "path": "nba.m3u8",     "txt": "domainsz29.txt"}},
    "nhl.html":         {"pattern": "nhl-streams-{n}.html",     "default": {"subdomain": "601",      "path": "nhl.m3u8",     "txt": "domainsz29.txt"}},
    "fighting.html":    {"pattern": None,
                         "default": {"subdomain": "daffodil", "path": "wwe.m3u8", "txt": "domainsz29.txt"},
                         "slug_map": {
                             "wwe": {"subdomain": "daffodil", "path": "wwe.m3u8",    "txt": "domainsz29.txt"},
                             "ufc": {"subdomain": "601",      "path": "ataide.m3u8", "txt": "domainsz29.txt"},
                             "ppv": {"subdomain": "601",      "path": "tt.m3u8",     "txt": "domainsz29.txt"},
                         }},
    "motorsports.html": {"pattern": "ppv-streams-{n}.html",     "default": {"subdomain": "601",      "path": "tt.m3u8",      "txt": "domainsz29.txt"}},
}

STREAM_OVERRIDES = {
    "Liechtenstein vs Cyprus":  {"subdomain": "daffodil", "path": "fs2.m3u8",     "txt": "domainsz29.txt"},
    "Denmark vs Ukraine":       {"subdomain": "daffodil", "path": "fubo.m3u8",    "txt": "domainsz29.txt"},
    "Croatia vs Slovenia":      {"subdomain": "601",      "path": "colo.m3u8",    "txt": "domainsz29.txt"},
    "Greece vs Italy":          {"subdomain": "daffodil", "path": "dep.m3u8",     "txt": "domainsz29.txt"},
    "Huachipato vs Colo Colo":  {"subdomain": "601",      "path": "tru.m3u8",     "txt": "domainsz29.txt"},
    "Morocco vs Norway":        {"subdomain": "601",      "path": "sky2.m3u8",    "txt": "domainsz29.txt"},
    "Ecuador vs Guatemala":     {"subdomain": "601",      "path": "england.m3u8", "txt": "domainsz29.txt"},
    "Colombia vs Jordan":       {"subdomain": "601",      "path": "espn.m3u8",    "txt": "domainsz29.txt"},
}

SPORT_LABELS = {
    "soccer": "Soccer", "mlb": "MLB", "nba": "NBA",
    "nhl": "NHL", "fighting": "Fighting", "motorsports": "Motorsports"
}

def extract_stream_info(html_path):
    if not os.path.exists(html_path):
        return None
    with open(html_path, encoding="utf-8") as f:
        content = f.read()
    hardcoded = re.search(r"showPlayer\('clappr',\s*'(https?://[^']+\.m3u8[^']*)'\)", content)
    if hardcoded:
        return {"hardcoded": hardcoded.group(1)}
    sub  = re.search(r"var subdomain\s*=\s*['\"](.+?)['\"]", content)
    txt  = re.search(r"fetch\(['\"](.+?\.txt)['\"]", content)
    path = re.search(r"getRandomStream\(['\"](.+?)['\"]", content)
    if sub and txt and path:
        return {"subdomain": sub.group(1), "path": path.group(1), "txt": txt.group(1)}
    return None

def get_events_from_schedule(schedule_path):
    with open(schedule_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    rows = soup.select("table#eventsTable tbody tr")
    events = []
    for row in rows:
        tds = row.find_all("td")
        if not tds:
            continue
        a = tds[0].find("a")
        if not a:
            continue
        name = a.get_text(strip=True)
        href = a.get("href", "")
        if not name:
            continue
        events.append({"name": name, "url": href})
    return events

def build_streams_list():
    all_streams = []
    for schedule_file, config in SCHEDULE_STREAM_MAP.items():
        schedule_path = os.path.join(BASE_DIR, schedule_file)
        if not os.path.exists(schedule_path):
            print(f"  WARNING: {schedule_file} not found, skipping.")
            continue
        events = get_events_from_schedule(schedule_path)
        sport_key = schedule_file.replace(".html", "")
        print(f"  {schedule_file}: {len(events)} events found")

        for i, event in enumerate(events, 1):
            info = None

            # 1. Check label override first
            if event["name"] in STREAM_OVERRIDES:
                info = STREAM_OVERRIDES[event["name"]].copy()
                print(f"    [{i}] {event['name']} -> OVERRIDE")

            # 2. Try reading from stream HTML file
            if info is None and config.get("pattern"):
                match = re.search(r'-(\d+)/?$', event["url"].rstrip("/"))
                n = match.group(1) if match else str(i)
                stream_filename = config["pattern"].replace("{n}", n)
                stream_path = os.path.join(BASE_DIR, stream_filename)
                info = extract_stream_info(stream_path)
                if info:
                    print(f"    [{i}] {event['name']} -> {stream_filename}")

            # 3. Try slug map
            if info is None and "slug_map" in config:
                for slug, slug_info in config["slug_map"].items():
                    if slug in event["url"]:
                        info = slug_info
                        print(f"    [{i}] {event['name']} -> slug:{slug}")
                        break

            # 4. Fall back to default
            if info is None:
                info = config["default"].copy()
                print(f"    [{i}] {event['name']} -> DEFAULT")

            entry = {"label": event["name"], "sport": sport_key}
            entry.update(info)
            all_streams.append(entry)

    return all_streams

def streams_to_js(streams):
    lines = ["const STREAMS = ["]
    current_sport = None
    for s in streams:
        sport = s.get("sport", "")
        if sport != current_sport:
            label = SPORT_LABELS.get(sport, sport.upper())
            lines.append(f"    // \u2500\u2500 {label} \u2500\u2500")
            current_sport = sport
        name = s["label"].replace("'", "\\'")
        if "hardcoded" in s:
            lines.append("    { label: '" + name + "', sport: '" + sport + "', hardcoded: '" + s["hardcoded"] + "' },")
        else:
            lines.append("    { label: '" + name + "', sport: '" + sport + "', subdomain: '" + s["subdomain"] + "', path: '" + s["path"] + "', txt: '" + s["txt"] + "' },")
    lines.append("];")
    return "\n".join(lines)

def update_multiview(streams_js):
    with open(MULTIVIEW_HTML, "r", encoding="utf-8", newline="") as f:
        content = f.read()
    new_content = re.sub(
        r"const STREAMS = \[[\s\S]*?\];",
        streams_js,
        content
    )
    if new_content == content:
        print("  WARNING: STREAMS block not found in multiview.html")
        return
    with open(MULTIVIEW_HTML, "w", encoding="utf-8", newline="") as f:
        f.write(new_content)
    print("  multiview.html updated successfully!")
if __name__ == "__main__":
    print(f"Writing to: {MULTIVIEW_HTML}")  # DEBUG
    print("=" * 50)
    print("Updating multistream.html STREAMS list...")
    print("=" * 50)
    streams = build_streams_list()
    print(f"\nTotal streams: {len(streams)}")
    js = streams_to_js(streams)
    print("\nInjecting into multistream.html...")
    update_multiview(js)
    print("Done!")