from bs4 import BeautifulSoup
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MULTIVIEW_HTML = os.path.join(BASE_DIR, "multiview.html")

SCHEDULE_STREAM_MAP = {
    "soccer.html": {
        "pattern": "soccer-streams-{n}.html",
        "default": {"subdomain": "601", "path": "cyrus.m3u8", "txt": "domainsz29.txt"},
    },
    "mlb.html": {
        "pattern": "mlb-streams-{n}.html",
        "default": {"subdomain": "601", "path": "mlb.m3u8", "txt": "domainsz29.txt"},
    },
    "nba.html": {
        "pattern": "nba-streams-{n}.html",
        "default": {"subdomain": "daffodil", "path": "nba.m3u8", "txt": "domainsz29.txt"},
    },
    "nfl.html": {
        "default": {"subdomain": "601", "path": "nfl.m3u8", "txt": "domainsz29.txt"},
        "sections": [
            {
                "sport": "nfl",
                "selector": "table#eventsTable tbody tr",
                "pattern": "nfl-streams-{n}.html",
            },
            {
                "sport": "ncaa",
                "selector": "#cfb-section table tbody tr",
                "pattern": "ncaa-streams-{n}.html",
                "default": {"subdomain": "601", "path": "ncaa.m3u8", "txt": "domainsz29.txt"},
            },
        ],
    },
    "nhl.html": {
        "pattern": "nhl-streams-{n}.html",
        "default": {"subdomain": "601", "path": "nhl.m3u8", "txt": "domainsz29.txt"},
    },
    "fighting.html": {
        "pattern": None,
        "default": {"subdomain": "daffodil", "path": "wwe.m3u8", "txt": "domainsz29.txt"},
        "slug_map": {
            "wwe": {"file": "wwe.html"},
            "ufc": {"file": "ufc.html"},
            "ppv": {"file": "ppv.html"},
            "aew": {"file": "aew.html"},
        },
    },
    "motorsports.html": {
        "pattern": "ppv-streams-{n}.html",
        "default": {"subdomain": "601", "path": "tt.m3u8", "txt": "domainsz29.txt"},
        "slug_map": {
            "motogp": {"file": "motogp.html"},
            "mxgp": {"file": "mxgp.html"},
            "f1": {"file": "f1.html"},
            "indycar": {"file": "indycar.html"},
            "floracing": {"file": "floracing.html"},
        },
    },
}

STREAM_OVERRIDES = {
}

SPORT_LABELS = {
    "soccer": "Soccer", "mlb": "MLB", "nba": "NBA", "nfl": "NFL",
    "ncaa": "NCAA Football", "nhl": "NHL", "fighting": "Fighting",
    "motorsports": "Motorsports"
}

# getRandomStream('path.m3u8', 'subdomain')  -- subdomain optional
RANDOM_CALL_RE = re.compile(
    r"""getRandomStream\(\s*['"]([^'"]+?\.m3u8[^'"]*)['"]\s*(?:,\s*['"]([^'"]+?)['"])?\s*\)"""
)
# a full hardcoded URL: showPlayer('clappr', 'https://sub.domain.tld/path.m3u8')
DIRECT_URL_RE = re.compile(r"""['"](https?://[^'"\s]+?\.m3u8[^'"\s]*)['"]""")
# page-level fallback subdomain
FN_DEFAULT_SUB_RE = re.compile(
    r"""function\s+getRandomStream\([^)]*subdomain\s*=\s*['"]([^'"]+)['"]"""
)
VAR_SUB_RE = re.compile(r"""var\s+subdomain\s*=\s*['"]([^'"]+)['"]""")

_domain_cache = None

def load_domain_lists():
    """Map every domain in the repo's domains*.txt files to its filename."""
    global _domain_cache
    if _domain_cache is None:
        _domain_cache = {}
        for fname in sorted(os.listdir(BASE_DIR)):
            if not (fname.startswith("domains") and fname.endswith(".txt")):
                continue
            try:
                with open(os.path.join(BASE_DIR, fname), encoding="utf-8") as f:
                    for line in f:
                        d = line.strip()
                        if d:
                            _domain_cache.setdefault(d, fname)
            except OSError:
                continue
    return _domain_cache

def split_hardcoded_url(url):
    """Turn https://sub.example.com/x.m3u8 into rotating parts when we
    recognise the host, so the stream survives a domain rotation."""
    m = re.match(r"https?://([^/]+)/(.+)$", url)
    if not m:
        return None
    host, path = m.group(1), m.group(2)
    for domain, txt_file in load_domain_lists().items():
        if host.endswith("." + domain):
            subdomain = host[: -len(domain) - 1]
            if subdomain:
                return {"subdomain": subdomain, "path": path, "txt": txt_file}
    return None

def parse_onclick(onclick, txt_file, page_subdomain):
    """Return stream parts for one button, or None if it isn't an m3u8 source."""
    m = RANDOM_CALL_RE.search(onclick)
    if m:
        return {
            "path": m.group(1),
            "subdomain": m.group(2) or page_subdomain,
            "txt": txt_file,
        }
    m = DIRECT_URL_RE.search(onclick)
    if m:
        url = m.group(1)
        parts = split_hardcoded_url(url)
        return parts if parts else {"hardcoded": url}
    return None

def extract_stream_info(html_path):
    if not os.path.exists(html_path):
        return None

    with open(html_path, encoding="utf-8") as f:
        content = f.read()

    txt = re.search(r"fetch\(['\"](.+?\.txt)['\"]", content)
    txt_file = txt.group(1) if txt else "domainsz29.txt"

    sub = FN_DEFAULT_SUB_RE.search(content) or VAR_SUB_RE.search(content)
    page_subdomain = sub.group(1) if sub else "admin2"

    # Every stream button on the page, in document order
    soup = BeautifulSoup(content, "html.parser")
    all_streams = []
    for btn in soup.find_all("button", onclick=True):
        onclick = btn.get("onclick", "")
        if "showPlayer" not in onclick and "getRandomStream" not in onclick:
            continue
        info = parse_onclick(onclick, txt_file, page_subdomain)
        if not info:
            continue
        label = btn.get_text(strip=True) or f"Stream {len(all_streams) + 1}"
        entry = {"label": label}
        entry.update(info)
        all_streams.append(entry)

    if not all_streams:
        # No buttons matched -- fall back to whatever the page auto-plays.
        # Scan every match, since the getRandomStream() function *definition*
        # appears before any real call and would otherwise shadow it.
        for pattern in (
            r"function playStream5\(\)[\s\S]*?(getRandomStream\([^)]*\))",
            r"function playStream1\(\)[\s\S]*?(getRandomStream\([^)]*\))",
            r"(getRandomStream\([^)]*\))",
            r"showPlayer\(\s*['\"]clappr['\"]\s*,\s*(['\"]https?://[^'\"]+?\.m3u8[^'\"]*['\"])",
        ):
            for m in re.finditer(pattern, content):
                info = parse_onclick(m.group(1), txt_file, page_subdomain)
                if info:
                    return info
        return None

    result = dict(all_streams[0])
    result.pop("label", None)
    if len(all_streams) > 1:
        result["alts"] = all_streams[1:]
    return result

DEFAULT_SELECTOR = "table#eventsTable tbody tr"

def get_events_from_schedule(schedule_path, selector=DEFAULT_SELECTOR):
    with open(schedule_path, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    rows = soup.select(selector)
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

        # One page can carry more than one sport (nfl.html also holds NCAA)
        for section in config.get("sections") or [{}]:
            sport_key = section.get("sport", schedule_file.replace(".html", ""))
            selector = section.get("selector", DEFAULT_SELECTOR)
            pattern = section.get("pattern", config.get("pattern"))
            default = section.get("default", config["default"])
            slug_map = section.get("slug_map", config.get("slug_map"))

            events = get_events_from_schedule(schedule_path, selector)
            print(f"  {schedule_file} [{sport_key}]: {len(events)} events found")

            for i, event in enumerate(events, 1):
                info = None

                if event["name"] in STREAM_OVERRIDES:
                    info = STREAM_OVERRIDES[event["name"]].copy()
                    print(f"    [{i}] {event['name']} -> OVERRIDE")

                if info is None and slug_map:
                    for slug, slug_info in slug_map.items():
                        if slug in event["url"]:
                            if "file" in slug_info:
                                slug_file_path = os.path.join(BASE_DIR, slug_info["file"])
                                info = extract_stream_info(slug_file_path)
                                if info:
                                    print(f"    [{i}] {event['name']} -> slug:{slug} ({slug_info['file']})")
                                else:
                                    print(f"    [{i}] {event['name']} -> slug:{slug} (file not found, falling through)")
                            else:
                                info = slug_info.copy()
                                print(f"    [{i}] {event['name']} -> slug:{slug}")
                            break

                if info is None and pattern:
                    match = re.search(r'-(\d+)/?$', event["url"].rstrip("/"))
                    n = match.group(1) if match else str(i)
                    stream_filename = pattern.replace("{n}", n)
                    stream_path = os.path.join(BASE_DIR, stream_filename)
                    info = extract_stream_info(stream_path)
                    if info:
                        print(f"    [{i}] {event['name']} -> {stream_filename}")

                if info is None:
                    info = default.copy()
                    print(f"    [{i}] {event['name']} -> DEFAULT")

                entry = {"label": event["name"], "sport": sport_key}
                entry.update(info)
                all_streams.append(entry)

    return all_streams

def js_str(value):
    return str(value).replace("\\", "\\\\").replace("'", "\\'")

def source_fields(src):
    """Render the source half of an entry: either a hardcoded URL or parts."""
    if "hardcoded" in src:
        return "hardcoded: '" + js_str(src["hardcoded"]) + "'"
    return (
        "subdomain: '" + js_str(src["subdomain"]) + "', "
        "path: '" + js_str(src["path"]) + "', "
        "txt: '" + js_str(src["txt"]) + "'"
    )

def streams_to_js(streams):
    lines = ["const STREAMS = ["]
    current_sport = None
    for s in streams:
        sport = s.get("sport", "")
        if sport != current_sport:
            label = SPORT_LABELS.get(sport, sport.upper())
            lines.append(f"    // \u2500\u2500 {label} \u2500\u2500")
            current_sport = sport

        alts_js = ""
        if s.get("alts"):
            alts_parts = [
                "{ label: '" + js_str(alt["label"]) + "', " + source_fields(alt) + " }"
                for alt in s["alts"]
            ]
            alts_js = ", alts: [" + ", ".join(alts_parts) + "]"

        lines.append(
            "    { label: '" + js_str(s["label"]) + "', sport: '" + sport + "', "
            + source_fields(s) + alts_js + " },"
        )
    lines.append("];")
    return "\n".join(lines)

def update_multiview(streams_js):
    with open(MULTIVIEW_HTML, "r", encoding="utf-8", newline="") as f:
        content = f.read()

    start_marker = "const STREAMS = ["
    end_marker = "];"

    start = content.find(start_marker)
    if start == -1:
        raise SystemExit("ERROR: STREAMS start marker not found in multiview.html")

    end = content.find(end_marker, start)
    if end == -1:
        raise SystemExit("ERROR: STREAMS end marker not found in multiview.html")
    end += len(end_marker)

    # Keep the block in the same line endings as the rest of the file
    if "\r\n" in content:
        streams_js = streams_js.replace("\n", "\r\n")

    new_content = content[:start] + streams_js + content[end:]

    with open(MULTIVIEW_HTML, "w", encoding="utf-8", newline="") as f:
        f.write(new_content)

    print("  multiview.html updated successfully!")

if __name__ == "__main__":
    print(f"Writing to: {MULTIVIEW_HTML}")
    print("=" * 50)
    print("Updating multistream.html STREAMS list...")
    print("=" * 50)
    streams = build_streams_list()
    print(f"\nTotal streams: {len(streams)}")
    js = streams_to_js(streams)
    print("\nInjecting into multistream.html...")
    update_multiview(js)
    print("Done!")