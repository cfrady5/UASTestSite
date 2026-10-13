/* =====================================================================
   Midwest UAS Test Site of Indiana — partner marquees
   ---------------------------------------------------------------------
   Upgrades each partner category on /partners into one or two rows of
   continuously scrolling organizations, adjacent rows running in
   opposite directions.

   Progressive enhancement
   -----------------------
   The page ships every category as an ordinary <ul> of links. This
   rearranges that list; it never supplies the content. With no script
   the page is a complete, linked, static list of every organization.

   How the loop is seamless
   ------------------------
   A row holds a sequence of cells repeated until the track is at least
   twice the width of the viewport, and the animation translates the
   track by the measured width of exactly ONE sequence. At the end of
   the cycle the track is therefore showing a pixel-identical copy of
   what it showed at the start, so the reset is invisible — no jump, no
   gap, no pause. The distance is measured from the DOM rather than
   assumed, and re-measured on resize and after logos load, because a
   guessed width is exactly what produces a visible stutter.

   Movement is a CSS animation on `transform`, so it runs off the main
   thread. JavaScript only measures and sets two custom properties; it
   never drives a frame loop.

   Duplicate content
   -----------------
   Only the first sequence is real. Every repeat is aria-hidden and has
   its focusable descendants removed from the tab order, so a keyboard
   passes through each organization once and a screen reader announces
   each one once.
   ===================================================================== */
(function () {
  'use strict';

  var groups = document.querySelectorAll('[data-marquee]');
  if (!groups.length) return;

  var reduceQuery = window.matchMedia('(prefers-reduced-motion: reduce)');

  /* Pixels per second. Slow enough to read a wordmark as it passes; the
     second row runs slightly slower so the two never beat in sync. */
  var SPEED = [26, 21];

  function build(group) {
    var list = group.querySelector('.partner-list');
    if (!list) return null;

    var cells = Array.prototype.slice.call(list.children);
    if (!cells.length) return null;

    var rowCount = Math.max(1, Math.min(3, parseInt(group.getAttribute('data-rows'), 10) || 1));

    /* Split as evenly as the count allows, so two rows carry the same
       visual weight rather than one long row and one stub. */
    var perRow = Math.ceil(cells.length / rowCount);
    var slices = [];
    for (var i = 0; i < rowCount; i += 1) {
      var slice = cells.slice(i * perRow, (i + 1) * perRow);
      if (slice.length) slices.push(slice);
    }

    var viewport = document.createElement('div');
    viewport.className = 'marquee';

    var rows = slices.map(function (slice, index) {
      var row = document.createElement('div');
      row.className = 'marquee-row';
      /* Row 1 right-to-left, row 2 left-to-right, alternating after that. */
      row.setAttribute('data-direction', index % 2 === 0 ? 'rtl' : 'ltr');
      row.style.setProperty('--marquee-speed', SPEED[Math.min(index, SPEED.length - 1)]);

      var track = document.createElement('div');
      track.className = 'marquee-track';

      var seq = document.createElement('ul');
      seq.className = 'marquee-seq';
      slice.forEach(function (cell) { seq.appendChild(cell); });
      track.appendChild(seq);

      row.appendChild(track);
      viewport.appendChild(row);
      return { row: row, track: track, seq: seq };
    });

    list.remove();
    group.appendChild(viewport);
    return { group: group, viewport: viewport, rows: rows };
  }

  /* Clone the sequence until the track is wide enough that one sequence
     width of travel never exposes the end of the track. */
  function measure(entry) {
    entry.rows.forEach(function (r) {
      /* Drop previous clones before measuring, or each pass compounds. */
      while (r.track.children.length > 1) r.track.removeChild(r.track.lastChild);

      var seqWidth = r.seq.getBoundingClientRect().width;
      if (!seqWidth) return;                       // not laid out yet

      var needed = Math.ceil(
        (entry.viewport.getBoundingClientRect().width + seqWidth) / seqWidth) + 1;

      for (var i = 1; i < Math.max(2, needed); i += 1) {
        var clone = r.seq.cloneNode(true);
        clone.setAttribute('aria-hidden', 'true');
        /* A clone must never be a second tab stop or a second
           announcement of the same organization. */
        Array.prototype.forEach.call(
          clone.querySelectorAll('a, button, [tabindex]'), function (node) {
            node.setAttribute('tabindex', '-1');
          });
        r.track.appendChild(clone);
      }

      r.row.style.setProperty('--marquee-distance', seqWidth + 'px');
      r.row.style.setProperty('--marquee-duration',
        (seqWidth / parseFloat(r.row.style.getPropertyValue('--marquee-speed'))) + 's');
      r.row.classList.add('is-measured');
    });
  }

  var entries = [];
  Array.prototype.forEach.call(groups, function (g) {
    var entry = build(g);
    if (entry) entries.push(entry);
  });
  if (!entries.length) return;

  function measureAll() { entries.forEach(measure); }

  measureAll();

  /* Logos change the sequence width once they decode, and a stale width is
     what makes a marquee stutter — so re-measure when they land. */
  var pending = document.querySelectorAll('.marquee img');
  Array.prototype.forEach.call(pending, function (img) {
    if (img.complete) return;
    img.addEventListener('load', measureAll);
    img.addEventListener('error', measureAll);
  });

  if (document.fonts && document.fonts.ready) {
    document.fonts.ready.then(measureAll).catch(function () {});
  }

  if ('ResizeObserver' in window) {
    var ro = new ResizeObserver(debounce(measureAll, 150));
    entries.forEach(function (e) { ro.observe(e.viewport); });
  } else {
    window.addEventListener('resize', debounce(measureAll, 150));
  }

  /* Reduced motion: the rows stop moving and become scrollable by hand,
     which is what the brief asks for and what the preference means. The
     class drives it; the measurement above stays valid either way. */
  function applyMotion() {
    var reduce = reduceQuery.matches;
    entries.forEach(function (e) {
      e.viewport.classList.toggle('is-static', reduce);
      e.rows.forEach(function (r) {
        r.row.setAttribute('tabindex', reduce ? '0' : '-1');
        if (reduce) {
          r.row.setAttribute('role', 'group');
          r.row.setAttribute('aria-label', 'Scrollable list of organizations');
        } else {
          r.row.removeAttribute('role');
          r.row.removeAttribute('aria-label');
          r.row.removeAttribute('tabindex');
        }
      });
    });
    if (!reduce) measureAll();
  }

  applyMotion();
  if (reduceQuery.addEventListener) reduceQuery.addEventListener('change', applyMotion);
  else if (reduceQuery.addListener) reduceQuery.addListener(applyMotion);

  /* Pause on focus as well as hover, so a keyboard user gets the same
     chance to read and click as a mouse user. Pausing is
     animation-play-state, which freezes the track exactly where it is —
     no position reset, no reflow, nothing that could shift layout. */
  document.addEventListener('focusin', function (e) {
    var row = e.target.closest && e.target.closest('.marquee-row');
    entries.forEach(function (entry) {
      entry.rows.forEach(function (r) {
        r.row.classList.toggle('is-paused', r.row === row);
      });
    });
  });

  document.addEventListener('focusout', function (e) {
    var row = e.target.closest && e.target.closest('.marquee-row');
    if (row) row.classList.remove('is-paused');
  });

  function debounce(fn, wait) {
    var t;
    return function () {
      clearTimeout(t);
      t = setTimeout(fn, wait);
    };
  }
})();
