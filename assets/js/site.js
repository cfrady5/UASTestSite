/* =====================================================================
   Midwest UAS Test Site of Indiana — Phase 1 landing page
   Progressive enhancement only: every feature degrades to working HTML.
   ===================================================================== */
(function () {
  'use strict';

  var reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  /* ---------------------------------------------------------------
     Mobile navigation
     --------------------------------------------------------------- */
  var toggle = document.getElementById('navToggle');
  var nav    = document.getElementById('primaryNav');

  function closeNav() {
    if (!nav || !toggle) return;
    nav.classList.remove('is-open');
    toggle.setAttribute('aria-expanded', 'false');
  }

  if (toggle && nav) {
    toggle.addEventListener('click', function () {
      var open = toggle.getAttribute('aria-expanded') === 'true';
      toggle.setAttribute('aria-expanded', String(!open));
      nav.classList.toggle('is-open', !open);
    });

    // Close after choosing a destination on mobile
    nav.addEventListener('click', function (e) {
      if (e.target.closest('a')) closeNav();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') {
        closeNav();
        toggle.focus();
      }
    });

    // Reset the drawer when we grow past the mobile breakpoint
    var desktop = window.matchMedia('(min-width: 1001px)');
    var onBreak = function (e) { if (e.matches) closeNav(); };
    if (desktop.addEventListener) desktop.addEventListener('change', onBreak);
    else if (desktop.addListener) desktop.addListener(onBreak);
  }

  /* ---------------------------------------------------------------
     Sticky header shadow
     --------------------------------------------------------------- */
  var header = document.getElementById('siteHeader');
  if (header) {
    var setStuck = function () {
      header.classList.toggle('is-stuck', window.scrollY > 8);
    };
    setStuck();
    window.addEventListener('scroll', setStuck, { passive: true });
  }

  /* ---------------------------------------------------------------
     Scroll reveal
     --------------------------------------------------------------- */
  var revealables = document.querySelectorAll('.reveal');

  if (reduceMotion || !('IntersectionObserver' in window)) {
    Array.prototype.forEach.call(revealables, function (el) {
      el.classList.add('is-visible');
    });
  } else {
    var revealObserver = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add('is-visible');
        obs.unobserve(entry.target);
      });
    }, { rootMargin: '0px 0px -8% 0px', threshold: 0.06 });

    Array.prototype.forEach.call(revealables, function (el, i) {
      // Small stagger within a row of siblings
      el.style.transitionDelay = (Math.min(i % 4, 3) * 70) + 'ms';
      revealObserver.observe(el);
    });
  }

  /* ---------------------------------------------------------------
     Active section highlighting in the nav
     --------------------------------------------------------------- */
  var navLinks = nav ? nav.querySelectorAll('a[href^="#"]') : [];
  var sectionMap = {};

  Array.prototype.forEach.call(navLinks, function (link) {
    var id = link.getAttribute('href').slice(1);
    var section = id && document.getElementById(id);
    if (section) sectionMap[id] = link;
  });

  var watched = Object.keys(sectionMap);
  if (watched.length && 'IntersectionObserver' in window) {
    var visible = {};
    var spyObserver = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        visible[entry.target.id] = entry.isIntersecting ? entry.intersectionRatio : 0;
      });

      var best = null;
      watched.forEach(function (id) {
        if (visible[id] && (!best || visible[id] > visible[best])) best = id;
      });

      watched.forEach(function (id) {
        sectionMap[id].classList.toggle('is-active', id === best);
      });
    }, { rootMargin: '-45% 0px -45% 0px', threshold: [0, 0.25, 0.5, 1] });

    watched.forEach(function (id) { spyObserver.observe(document.getElementById(id)); });
  }

  /* ---------------------------------------------------------------
     Inquiry form
     ---------------------------------------------------------------
     This is a static page with no backend. The form validates client
     side and then hands off to the mail client, so it works as shipped.

     To wire it to a real endpoint later, set data-endpoint on the form
     and the submit handler will POST JSON there instead.
     --------------------------------------------------------------- */
  var form   = document.getElementById('inquiryForm');
  var status = document.getElementById('formStatus');
  var INBOX  = 'dale.lyles@theari.us';

  function setError(field, message) {
    var wrap = field.closest('.field');
    var box  = wrap ? wrap.querySelector('.error') : null;
    if (wrap) wrap.classList.toggle('has-error', Boolean(message));
    field.setAttribute('aria-invalid', message ? 'true' : 'false');
    if (box) {
      box.textContent = message || '';
      box.hidden = !message;
    }
  }

  function validate() {
    var problems = [];
    var name  = document.getElementById('f-name');
    var email = document.getElementById('f-email');
    var msg   = document.getElementById('f-msg');

    [[name, 'Please enter your name.'],
     [msg,  'Please tell us how we can help.']].forEach(function (pair) {
      var field = pair[0];
      var bad = !field.value.trim();
      setError(field, bad ? pair[1] : '');
      if (bad) problems.push(field);
    });

    var emailBad = !/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email.value.trim());
    setError(email, emailBad ? 'Please enter a valid email address.' : '');
    if (emailBad) problems.push(email);

    return problems;
  }

  if (form) {
    form.addEventListener('submit', function (e) {
      e.preventDefault();

      var problems = validate();
      if (problems.length) {
        status.textContent = 'Please correct the highlighted fields.';
        status.className = 'form-note is-err';
        problems[0].focus();
        return;
      }

      var data = {
        name:         document.getElementById('f-name').value.trim(),
        email:        document.getElementById('f-email').value.trim(),
        organization: document.getElementById('f-org').value.trim(),
        interest:     document.getElementById('f-interest').value,
        message:      document.getElementById('f-msg').value.trim()
      };

      var endpoint = form.getAttribute('data-endpoint');

      if (endpoint) {
        status.textContent = 'Sending…';
        status.className = 'form-note';
        fetch(endpoint, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        }).then(function (res) {
          if (!res.ok) throw new Error('Request failed');
          form.reset();
          status.textContent = 'Thank you — your inquiry has been sent. Our team will follow up shortly.';
          status.className = 'form-note is-ok';
        }).catch(function () {
          status.textContent = 'Something went wrong. Please email ' + INBOX + ' directly.';
          status.className = 'form-note is-err';
        });
        return;
      }

      // No endpoint configured: hand off to the visitor's mail client.
      var subject = 'Test Site Inquiry — ' + data.name +
                    (data.organization ? ' (' + data.organization + ')' : '');
      var bodyLines = [
        'Name: ' + data.name,
        'Email: ' + data.email,
        'Organization: ' + (data.organization || '—'),
        'Area of interest: ' + (data.interest || '—'),
        '',
        data.message
      ];

      window.location.href = 'mailto:' + INBOX +
        '?subject=' + encodeURIComponent(subject) +
        '&body=' + encodeURIComponent(bodyLines.join('\n'));

      status.textContent = 'Opening your email app to send this inquiry. ' +
                           'If nothing happens, email ' + INBOX + ' directly.';
      status.className = 'form-note is-ok';
    });

    // Clear an error as soon as the visitor fixes it
    form.addEventListener('input', function (e) {
      var field = e.target;
      if (field.matches('input, textarea, select') &&
          field.getAttribute('aria-invalid') === 'true') {
        setError(field, '');
      }
    });
  }
})();
