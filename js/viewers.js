/* Roxiestreams live viewer count.
   Drop one <script src="js/viewers.js" defer></script> into a stream page.
   It finds the chat header itself -- no other markup changes needed. */
(function () {
  // Absolute on purpose: .info and .su both call this one service, so the
  // number shown is the combined total across both domains.
  // The .su deploy only rewrites *.html, so this URL is left alone here.
  var ENDPOINT = 'https://roxiestreams.info/api/viewers';
  var PING_MS = 20000;

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
      + '.viewer-count{display:inline-flex;align-items:center;gap:4px;'
      + 'font-size:10px;font-weight:bold;color:#ff4d4d;letter-spacing:.3px;'
      + 'text-transform:uppercase;opacity:0;transition:opacity .3s;}'
      + '.viewer-count.ready{opacity:1;}'
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

  function ping() {
    fetch(ENDPOINT + '?page=' + encodeURIComponent(PAGE) + '&id=' + encodeURIComponent(ID),
          { cache: 'no-store' })
      .then(function (r) { return r.json(); })
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
      var url = ENDPOINT + '?page=' + encodeURIComponent(PAGE)
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
