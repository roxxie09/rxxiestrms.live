/* Roxiestreams live viewer count.
   Drop one <script src="js/viewers.js" defer></script> into a stream page.
   It finds the chat header itself -- no other markup changes needed. */
(function () {
  // Both sites call ONE service, so the number is the combined total.
  // The second entry is a fallback: .su's nginx relays /api/viewers to
  // rxxie, so a viewer who cannot reach .info directly still lands in the
  // same pool. Order matters -- the first reachable one wins and sticks.
  // The .su deploy only rewrites *.html, so these URLs are left alone.
  var ENDPOINTS = [
    'https://roxiestreams.info/api/viewers',
    'https://roxiestreams.su/api/viewers'
  ];
  var PING_MS = 20000;
  var TIMEOUT_MS = 6000;
  var epIdx = 0;   // index of the endpoint currently believed good

  // /ncaa-streams-7 -> ncaa-streams-7
  function pageKey() {
    var last = location.pathname.replace(/\/+$/, '').split('/').pop() || 'index';
    return last.replace(/\.html$/, '') || 'index';
  }

  function clientId() {
    try {
      var v = sessionStorage.getItem('rx_vid');
      if (!v) {
        v = Math.random().toString(36).slice(2) + Date.now().toString(36);
        sessionStorage.setItem('rx_vid', v);
      }
      return v;
    } catch (e) {
      return 'a' + Math.random().toString(36).slice(2);
    }
  }

  var PAGE = pageKey();
  var ID = clientId();
  var el;

  function injectStyles() {
    var css = ''
      + '.viewer-count{display:none;align-items:center;gap:4px;'
      + 'font-size:10px;font-weight:bold;color:#ff4d4d;letter-spacing:.3px;'
      + 'text-transform:uppercase;}'
      + '.viewer-count.ready{display:inline-flex;}'
      + '.viewer-count svg{width:11px;height:11px;fill:#ff4d4d;flex-shrink:0;}'
      + '.chat-header-left{display:flex;align-items:center;gap:8px;}';
    var s = document.createElement('style');
    s.textContent = css;
    document.head.appendChild(s);
  }

  function build() {
    var span = document.createElement('span');
    span.className = 'viewer-count';
    span.title = 'People watching this stream right now';
    span.innerHTML =
      '<svg viewBox="0 0 16 16" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
      + '<path d="M3 14s-1 0-1-1 1-4 6-4 6 3 6 4-1 1-1 1H3zm5-6a3 3 0 1 0 0-6 3 3 0 0 0 0 6z"/>'
      + '</svg><span class="viewer-count-num">--</span>';
    return span;
  }

  function mount() {
    el = build();
    var header = document.querySelector('.chat-header');
    // The chat panel is hidden on portrait phones, so fall back to the
    // stream buttons where the count is still visible.
    var narrow = window.matchMedia
      && window.matchMedia('(max-width: 768px) and (orientation: portrait)').matches;
    var changer = document.querySelector('.streamchanger');

    if (header && !(narrow && changer)) {
      var label = header.querySelector('span');
      var group = document.createElement('div');
      group.className = 'chat-header-left';
      header.insertBefore(group, label || header.firstChild);
      if (label) group.appendChild(label);
      group.appendChild(el);
    } else if (changer) {
      changer.appendChild(el);
    } else {
      return false;
    }
    return true;
  }

  function render(n) {
    if (!el) return;
    var num = el.querySelector('.viewer-count-num');
    num.textContent = n >= 1000 ? (n / 1000).toFixed(1).replace(/\.0$/, '') + 'k' : n;
    el.classList.add('ready');
  }

  function fetchWithTimeout(url) {
    if (typeof AbortController === 'undefined') {
      return fetch(url, { cache: 'no-store' });
    }
    var ctrl = new AbortController();
    var timer = setTimeout(function () { ctrl.abort(); }, TIMEOUT_MS);
    return fetch(url, { cache: 'no-store', signal: ctrl.signal })
      .then(function (r) { clearTimeout(timer); return r; },
            function (e) { clearTimeout(timer); throw e; });
  }

  // Try the preferred endpoint, then each other one in turn. Whichever
  // answers becomes the preferred one for the rest of the session.
  function request(query, attempt) {
    attempt = attempt || 0;
    if (attempt >= ENDPOINTS.length) return Promise.reject(new Error('all endpoints failed'));
    var which = (epIdx + attempt) % ENDPOINTS.length;
    return fetchWithTimeout(ENDPOINTS[which] + query)
      .then(function (r) {
        if (!r.ok) throw new Error('HTTP ' + r.status);
        return r.json();
      })
      .then(function (d) { epIdx = which; return d; })
      .catch(function () { return request(query, attempt + 1); });
  }

  function ping() {
    request('?page=' + encodeURIComponent(PAGE) + '&id=' + encodeURIComponent(ID))
      .then(function (d) { if (typeof d.count === 'number') render(d.count); })
      .catch(function () { /* counter is cosmetic -- never break the page */ });
  }

  function start() {
    injectStyles();
    if (!mount()) return;
    ping();
    setInterval(ping, PING_MS);

    document.addEventListener('visibilitychange', function () {
      if (!document.hidden) ping();
    });

    // Drop off promptly instead of waiting for the 45s timeout
    window.addEventListener('pagehide', function () {
      var url = ENDPOINTS[epIdx] + '?page=' + encodeURIComponent(PAGE)
              + '&id=' + encodeURIComponent(ID) + '&leave=1';
      if (navigator.sendBeacon) navigator.sendBeacon(url);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', start);
  } else {
    start();
  }
})();
