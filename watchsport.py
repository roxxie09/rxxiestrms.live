import re
from pathlib import Path

# Read Fuse.js ONCE at startup
FUSE_CODE_PATH = Path("fuse.min.js")
if not FUSE_CODE_PATH.exists():
    raise SystemExit("fuse.min.js not found! Download from https://cdnjs.cloudflare.com/ajax/libs/fuse.js/3.4.6/fuse.min.js")

FUSE_JS = FUSE_CODE_PATH.read_text(encoding="utf-8")

ABBREVIATION_MAP = {
    "hawks": "atlanta hawks",
    "celtics": "boston celtics",
    "hornets": "charlotte hornets",
    "bulls": "chicago bulls",
    "cavaliers": "cleveland cavaliers",
    "mavericks": "dallas mavericks",
    "nuggets": "denver nuggets",
    "pistons": "detroit pistons",
    "warriors": "golden state warriors",
    "rockets": "houston rockets",
    "pacers": "indiana pacers",
    "clippers": "los angeles clippers",
    "lakers": "los angeles lakers",
    "grizzlies": "memphis grizzlies",
    "heat": "miami heat",
    "bucks": "milwaukee bucks",
    "timberwolves": "minnesota timberwolves",
    "pelicans": "new orleans pelicans",
    "knicks": "new york knicks",
    "thunder": "oklahoma city thunder",
    "magic": "orlando magic",
    "sixers": "philadelphia 76ers",
    "suns": "phoenix suns",
    "blazers": "portland trail blazers",
    "kings": "sacramento kings",
    "spurs": "san antonio spurs",
    "raptors": "toronto raptors",
    "jazz": "utah jazz",
    "wizards": "washington wizards",
}

PREMIER_LEAGUE_SHORT_NAMES = [
    "leeds", "west ham", "c palace", "nottm forest", "man united",
    "man city", "newcastle", "brighton", "brentford", "liverpool", "spurs"
]

LALIGA_TEAMS = [
    "alaves", "athletic bilbao", "atm", "atletico madrid", "barcelona",
    "celta vigo", "elche", "espanyol", "getafe", "girona",
    "mallorca", "osasuna", "rayo vallecano", "real betis",
    "real madrid", "real sociedad", "real valladolid",
    "sevilla", "valencia", "villarreal"
]

MLS_TEAMS = [
    "miami", "atlanta", "chicago", "cincinnati", "columbus", "dallas",
    "dc", "houston", "los angeles", "minnesota", "nashville",
    "new england", "new york", "orlando", "philadelphia", "portland",
    "real salt lake", "seattle", "sporting kansas city", "san jose",
    "toronto", "vancouver"
]

def extract_events_and_links(text):
    events = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        m = re.match(r'^(.+?):\s*\[(https?://[^\s\]]+)\]', line)
        if m:
            event = m.group(1).strip()
            url = m.group(2).strip()
        else:
            m = re.match(r'^(.+?):\s*(https?://\S+)', line)
            if m:
                event = m.group(1).strip()
                url = m.group(2).strip().rstrip(' ,')
            else:
                continue
        if event not in events:
            events[event] = url
    return events

def normalize_team_name(name):
    low = name.lower()
    return ABBREVIATION_MAP.get(low, low)

def parse_teams_from_event(event):
    for sep in [' vs ', ' @ ', ' vs. ', ' at ']:
        if sep in event.lower():
            sides = event.lower().split(sep)
            return [normalize_team_name(s.strip()) for s in sides]
    return [normalize_team_name(event)]

def generate_roxie_js(events):
    entries = []
    all_teams = set()
    for event, url in events.items():
        teams = parse_teams_from_event(event)
        teams_sorted = sorted(teams)
        title = " vs ".join(teams_sorted)
        entries.append(f'{{title: "{title}", url: "{url}"}}')
        all_teams.update(teams)
    return "const roxieStreamsCached = [\n  " + ",\n  ".join(entries) + "\n];", all_teams

def generate_teammap_js(all_teams):
    lines = [f'"{team}": "{team}"' for team in sorted(all_teams)]
    for abbr, full_name in ABBREVIATION_MAP.items():
        if full_name in all_teams and abbr not in all_teams:
            lines.append(f'"{abbr}": "{full_name}"')
    return "const teamNameMap = {\n  " + ",\n  ".join(lines) + "\n};"

def generate_full_js(team_map_js, roxie_js, nba_canonical_set):
    nba_canonical_js_array = ','.join(f'"{team}"' for team in nba_canonical_set)
    premier_league_js_array = ','.join(f'"{team}"' for team in PREMIER_LEAGUE_SHORT_NAMES)
    laliga_js_array = ','.join(f'"{team}"' for team in LALIGA_TEAMS)
    mls_js_array = ','.join(f'"{team}"' for team in MLS_TEAMS)
    
    return f"""(async () => {{
  // INLINE FUSE.JS - CSP COMPLIANT (no external script loads)
  {FUSE_JS}

  {team_map_js}

  {roxie_js}

  const nbaTeams = new Set([{nba_canonical_js_array}]);
  const premierLeagueTeams = new Set([{premier_league_js_array}]);
  const laLigaTeams = new Set([{laliga_js_array}]);
  const mlsTeams = new Set([{mls_js_array}]);

  function normalizeTeamName(name) {{
    return teamNameMap[name.toLowerCase().trim()] || name.toLowerCase().trim();
  }}

  function normalizeTitle(title) {{
    let t = title.toLowerCase().replace(/@/g, 'vs').trim();
    if (!t.includes('vs')) {{
      return normalizeTeamName(t);
    }}
    let teams = t.split('vs').map(s => normalizeTeamName(s.trim()));
    teams.sort();
    return teams.join(' vs ');
  }}

  const normalizedCache = roxieStreamsCached.map(item => ({{ 
    title: normalizeTitle(item.title),
    url: item.url
  }}));

  const fuse = new Fuse(normalizedCache, {{
    keys: ['title'],
    threshold: 0.3,
    includeScore: true,
    distance: 50,
    ignoreLocation: true,
  }});

  function findBestMatch(eventTitle) {{
    const lowerTitle = eventTitle.toLowerCase();
    if (lowerTitle.includes("ufc")) return "https://roxiestreams.info/ufc";
    if (lowerTitle.includes("grand prix")) return "https://roxiestreams.info/f1-streams";
    if (lowerTitle.includes("wwe")) return "https://roxiestreams.info/wwe-streams";

    let teams = [];
    if (lowerTitle.includes("@")) {{
      teams = lowerTitle.split("@").map(t => normalizeTeamName(t.trim()));
    }} else if (lowerTitle.includes("vs")) {{
      teams = lowerTitle.split("vs").map(t => normalizeTeamName(t.trim()));
    }} else {{
      teams = [normalizeTeamName(lowerTitle.trim())];
    }}

    if (teams.length === 0) return 'https://roxiestreams.info/missing';

    for (const entry of normalizedCache) {{
      for (const team of teams) {{
        if (entry.title.includes(team)) return entry.url;
      }}
    }}
    return 'https://roxiestreams.info/missing';
  }}

  function getEventTitleFromGameItem(gameItem) {{
    if (!gameItem) return '';
    const matchupDiv = gameItem.querySelector('.game-matchup');
    if (!matchupDiv) return '';
    return matchupDiv.textContent.trim();
  }}

  function getLeagueFromGameItem(gameItem) {{
    const broadcastDiv = gameItem.querySelector('.game-broadcast');
    return broadcastDiv ? broadcastDiv.textContent.trim() : '';
  }}

  function autofillHandler(e) {{
    const button = e.currentTarget;
    const gameId = button.getAttribute('data-modal');
    const gameItem = button.closest('.game-item');

    const eventTitle = getEventTitleFromGameItem(gameItem);
    const leagueText = getLeagueFromGameItem(gameItem);
    console.log('Extracted event title:', eventTitle, 'league:', leagueText, 'gameId:', gameId);

    let channelName = '';

    const lowerTitle = eventTitle.toLowerCase();

    const nbaShortNames = Object.keys(teamNameMap).filter(key => nbaTeams.has(teamNameMap[key].toLowerCase()));
    const hasNbaShortName = nbaShortNames.some(shortName => lowerTitle.includes(shortName.toLowerCase()));

    if ((!channelName || channelName.trim() === '') && hasNbaShortName) {{
      channelName = 'NBA League Pass';
    }}

    if (lowerTitle.includes('wwe')) {{
      channelName = 'Netflix';
    }}

    if (lowerTitle.includes('grand prix')) {{
      channelName = 'Sky Sports F1';
    }}

    if (lowerTitle.includes('ufc')) {{
      channelName = 'Paramount+';
    }}

    const hasPlTeam = Array.from(premierLeagueTeams).some(plTeam => lowerTitle.includes(plTeam));
    if ((!channelName || channelName.trim() === '') && hasPlTeam) {{
      channelName = 'Now Sports';
    }}

    const hasLaLigaTeam = Array.from(laLigaTeams).some(laTeam => lowerTitle.includes(laTeam));
    if ((!channelName || channelName.trim() === '') && hasLaLigaTeam) {{
      channelName = 'ESPN Deportes';
    }}

    const hasMlsTeam = Array.from(mlsTeams).some(mlsTeam => lowerTitle.includes(mlsTeam));
    if ((!channelName || channelName.trim() === '') && hasMlsTeam) {{
      channelName = 'MLS Season Pass';
    }}

    setTimeout(() => {{
      const modal = document.getElementById(`modal-${{gameId}}`);
      if (!modal) {{
        console.warn('Modal not found for gameId:', gameId);
        return;
      }}

      const form = modal.querySelector('form.stream-form');
      if (!form) {{
        console.warn('Form not found in modal for gameId:', gameId);
        return;
      }}

      const streamUrl = findBestMatch(eventTitle);

      const siteInput = form.querySelector('input[name="site"]');
      const urlInput = form.querySelector('input[name="url"]');
      const channelInput = form.querySelector('input[name="channel"]');
      const bitrateInput = form.querySelector('input[name="bitrate"]');
      const adsSelect = form.querySelector('select[name="ads"]');
      const fpsSelect = form.querySelector('select[name="fps"]');

      if (siteInput) siteInput.value = 'RoxieStreams';
      if (urlInput) urlInput.value = streamUrl;
      if (channelInput) channelInput.value = (channelName ? (channelName + ' (FHD)') : 'Main (FHD)');
      if (bitrateInput) bitrateInput.value = '7000';
      if (adsSelect) adsSelect.value = '0';
      if (fpsSelect) fpsSelect.value = '60';

      form.querySelectorAll('input[type="checkbox"][name="Compatibility"]').forEach(cb => {{
        cb.checked = true;
      }});

      console.log(`Autofilled URL: ${{streamUrl}} and channel: ${{channelName}} with bitrate 7000 and ads 0 for gameId ${{gameId}}`);
    }}, 300);
  }}

  function attachAutofill() {{
    document.querySelectorAll('button.add-btn').forEach(button => {{
      button.removeEventListener('click', autofillHandler);
      button.addEventListener('click', autofillHandler);
    }});
  }}

  attachAutofill();

  async function autoProcessAllEvents() {{
    const buttons = Array.from(document.querySelectorAll('button.add-btn'));

    for (const button of buttons) {{
      const gameId = button.getAttribute('data-modal');
      console.log(`Opening modal for gameId ${{gameId}}`);
      button.dispatchEvent(new MouseEvent('click', {{ bubbles: true, cancelable: true }}));

      await new Promise(res => setTimeout(res, 300));

      const modal = document.getElementById(`modal-${{gameId}}`);
      if (!modal) {{
        console.warn(`Modal not found for gameId: ${{gameId}}`);
        continue;
      }}
      const form = modal.querySelector('form.stream-form');
      if (!form) {{
        console.warn(`Form not found for gameId: ${{gameId}}`);
        continue;
      }}

      const urlInput = form.querySelector('input[name="url"]');
      if (!urlInput) {{
        console.warn(`URL input not found for gameId: ${{gameId}}`);
        continue;
      }}

      const urlValue = urlInput.value.trim();

      if (urlValue === 'https://roxiestreams.info/missing') {{
        console.log(`Skipping ${{gameId}}: URL is missing!`);
        await new Promise(res => setTimeout(res, 300));
        continue;
      }}

      const submitBtn = form.querySelector('button.submit-btn[type="submit"]');
      if (submitBtn) {{
        submitBtn.focus();
        submitBtn.dispatchEvent(new MouseEvent('click', {{bubbles: true, cancelable: true, view: window}}));
        console.log(`Clicked submit button for ${{gameId}}`);
      }} else {{
        form.submit();
        console.log(`Fallback: submitted form element for ${{gameId}}`);
      }}

      await new Promise(res => setTimeout(res, 300));
    }}
  }}

  autoProcessAllEvents();

  window.autoProcessAllEvents = autoProcessAllEvents;
}})();
"""

def main():
    events_path = Path("events.txt")
    js_path = Path("watchsport.txt")

    if not events_path.exists():
        raise SystemExit("events.txt not found.")
    if not js_path.exists():
        raise SystemExit("watchsport.txt not found.")

    events_text = events_path.read_text(encoding="utf-8")

    events = extract_events_and_links(events_text)
    roxie_js, all_teams = generate_roxie_js(events)
    team_map_js = generate_teammap_js(all_teams)

    nba_canonical = {v.lower() for k, v in ABBREVIATION_MAP.items()}

    full_js_code = generate_full_js(team_map_js, roxie_js, nba_canonical)

    js_path.write_text(full_js_code, encoding="utf-8")
    print("watchsport.txt updated with NEW selectors for current watchsports.to admin page + dynamic RoxieStreams cache.")

if __name__ == "__main__":
    main()
