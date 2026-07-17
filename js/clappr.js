/* =====================================================================
   clappr-pink-theme.js
   ---------------------------------------------------------------------
   Drop-in pink theme for the Clappr player.

   USAGE
   -----
   1. Put this file next to your HTML (e.g. in a /js folder).
   2. Load it AFTER the Clappr script, BEFORE your player code:

        <script src="https://cdn.jsdelivr.net/npm/clappr@latest/dist/clappr.min.js"></script>
        <script src="js/clappr-pink-theme.js"></script>

   3. (Optional) Spread the exported mediacontrol config into your player
      so the seekbar-fill and buttons are themed too:

        clapprPlayer = new Clappr.Player({
          source: stream,
          parentId: "#playerContainer",
          height: '100%',
          width: '100%',
          autoPlay: true,
          mediacontrol: ClapprPinkTheme.mediacontrol,   // <-- add this line
          playback: { playInline: true, recycleVideo: true },
        });

   TO RE-THEME: just change PRIMARY / DIM below to any hex colors.
   ===================================================================== */

(function () {
  // ---- Edit these two values to change the whole theme --------------
  var PRIMARY = '#e573b5';   // main pink (progress, buttons, thumb, volume)
  var DIM     = '#9c3d78';   // darker pink (buffered portion)
  // -------------------------------------------------------------------

  // Expose a mediacontrol config you can spread into new Clappr.Player({...})
  window.ClapprPinkTheme = {
    primary: PRIMARY,
    dim: DIM,
    mediacontrol: { seekbar: PRIMARY, buttons: PRIMARY }
  };

  var css = [
    ':root {',
    '  --player-pink: ' + PRIMARY + ';',
    '  --player-pink-dim: ' + DIM + ';',
    '}',

    /* ---------- SEEKBAR (progress scrubber) ---------- */
    '.media-control .bar-background[data-seekbar] {',
    '  background-color: rgba(255, 192, 203, 0.15) !important;',
    '}',
    '.media-control .bar-fill-1[data-seekbar] {',        /* buffered */
    '  background-color: var(--player-pink-dim) !important;',
    '}',
    '.media-control .bar-fill-2[data-seekbar] {',        /* played */
    '  background-color: var(--player-pink) !important;',
    '}',
    '.media-control .bar-hover[data-seekbar] {',         /* hover line */
    '  background-color: rgba(229, 115, 181, 0.5) !important;',
    '}',
    '.media-control .bar-scrubber[data-seekbar] .bar-scrubber-icon {',
    '  background-color: var(--player-pink) !important;',
    '  box-shadow: 0 0 6px rgba(229, 115, 181, 0.8);',
    '}',

    /* ---------- CONTROL BUTTONS ---------- */
    '.media-control .media-control-button svg path {',
    '  fill: var(--player-pink) !important;',
    '}',
    '.media-control [data-hd-indicator] {',
    '  color: var(--player-pink) !important;',
    '}',

    /* ---------- VOLUME BAR ---------- */
    '.media-control .segmented-bar-element[data-volume].fill,',
    '.media-control .segmented-bar-element[data-volume]:hover {',
    '  background-color: var(--player-pink) !important;',
    '}',
    '.media-control .bar-fill-2[data-volume] {',
    '  background-color: var(--player-pink) !important;',
    '}',

    /* ---------- LOADING SPINNER ---------- */
    '.spinner-three-bounce > div {',
    '  background-color: var(--player-pink) !important;',
    '}'
  ].join('\n');

  function injectStyles() {
    if (document.getElementById('clappr-pink-theme')) return; // avoid duplicates
    var style = document.createElement('style');
    style.id = 'clappr-pink-theme';
    style.textContent = css;
    (document.head || document.documentElement).appendChild(style);
  }

  // Inject as early as possible, and again on DOMContentLoaded to be safe.
  injectStyles();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectStyles);
  }
})();