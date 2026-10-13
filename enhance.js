/*
 * enhance.js — progressive enhancement layered on the Claude Design source
 * (index.html is regenerated on every pull, so we enhance at runtime).
 *
 *  1. Contact form: the design's "Abschicken" button only flips to the
 *     thank-you state. We intercept the click (capture phase, before React),
 *     validate, deliver the request via Web3Forms to Stefani's inbox, and only
 *     then let the click through so the design shows its own "Danke" screen.
 *     Fallback without a key / on error: mailto: with the request prefilled.
 *  2. Mobile layout: the design is desktop-only (50px wordmark, 3-column
 *     masonry, 2-column About/Kontakt). Media-query overrides below.
 *
 * Injected into index.html on every deploy by scripts/inject_head.py.
 */
(function () {
  'use strict';

  // ==== Config ====
  // Stefani's address (mailto fallback) + her web3forms.com access key (a public
  // form-id; it can only send TO the address it was created for).
  var CONTACT_EMAIL = '__CONTACT_EMAIL__';
  var WEB3FORMS_KEY = '__WEB3FORMS_KEY__';

  var configured = function (v) { return v && v.indexOf('__') !== 0; };

  // ==== 1. Contact form ====
  var letThrough = false;

  function fields(section) {
    var inputs = section.querySelectorAll('input');
    var ta = section.querySelector('textarea');
    return {
      vorname: (inputs[0] && inputs[0].value || '').trim(),
      nachname: (inputs[1] && inputs[1].value || '').trim(),
      email: (inputs[2] && inputs[2].value || '').trim(),
      hochzeitsdatum: (inputs[3] && inputs[3].value || '').trim(),
      anfrage: (ta && ta.value || '').trim()
    };
  }

  function note(btn, text, isError) {
    var el = btn.parentNode.querySelector('.ss-note');
    if (!el) {
      el = document.createElement('p');
      el.className = 'ss-note';
      el.style.cssText = 'margin:4px 0 0;font-size:13px;line-height:1.6;';
      btn.parentNode.appendChild(el);
    }
    el.style.color = isError ? '#a33' : '#777';
    el.innerHTML = text;
  }

  function mailtoHref(d) {
    var body = 'Vorname: ' + d.vorname + '\nNachname: ' + d.nachname + '\nE-Mail: ' + d.email +
      '\nHochzeitsdatum: ' + d.hochzeitsdatum + '\n\n' + d.anfrage;
    return 'mailto:' + CONTACT_EMAIL + '?subject=' + encodeURIComponent('Anfrage Hochzeitsfotografie') +
      '&body=' + encodeURIComponent(body);
  }

  document.addEventListener('click', function (e) {
    var btn = e.target.closest && e.target.closest('button');
    if (!btn || !/abschicken/i.test(btn.textContent)) return;
    if (letThrough) { letThrough = false; return; }  // our own re-click → React shows "Danke"

    e.preventDefault();
    e.stopPropagation();
    var section = btn.closest('section') || document;
    var d = fields(section);

    if (!d.vorname || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(d.email)) {
      note(btn, 'Bitte gebt mindestens euren Vornamen und eine gültige E-Mail-Adresse an.', true);
      return;
    }

    if (!configured(WEB3FORMS_KEY)) {
      if (configured(CONTACT_EMAIL)) { window.location.href = mailtoHref(d); letThrough = true; btn.click(); }
      else note(btn, 'Das Formular ist noch nicht aktiv.', true);
      return;
    }

    var label = btn.textContent;
    btn.disabled = true;
    btn.textContent = 'Wird gesendet …';
    fetch('https://api.web3forms.com/submit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({
        access_key: WEB3FORMS_KEY,
        subject: 'Neue Anfrage über stefanisofija.com',
        from_name: (d.vorname + ' ' + d.nachname).trim(),
        replyto: d.email,
        vorname: d.vorname, nachname: d.nachname, email: d.email,
        hochzeitsdatum: d.hochzeitsdatum, anfrage: d.anfrage
      })
    }).then(function (r) { return r.json(); }).then(function (res) {
      if (!res.success) throw new Error(res.message || 'send failed');
      btn.disabled = false;
      btn.textContent = label;
      letThrough = true;
      btn.click();
    }).catch(function () {
      btn.disabled = false;
      btn.textContent = label;
      note(btn, 'Leider hat das Senden nicht geklappt. ' + (configured(CONTACT_EMAIL)
        ? 'Schreibt mir gerne direkt: <a href="' + mailtoHref(d) + '" style="color:#111">' + CONTACT_EMAIL + '</a>'
        : 'Bitte versucht es später noch einmal.'), true);
    });
  }, true);

  // ==== 2. Mobile layout ====
  // React renders inline styles as "prop: value" — match both spellings.
  var css = [
    '@media (max-width: 760px) {',
    '  header { padding: 20px 16px 16px !important; flex-wrap: wrap !important; gap: 12px !important; }',
    '  header > a:first-child { font-size: 28px !important; letter-spacing: 0.14em !important; }',
    '  header nav { gap: 16px !important; flex-wrap: wrap !important; }',
    '  header nav a { font-size: 11.5px !important; letter-spacing: 0.18em !important; }',
    '  main section > div[style*="justify-content: flex-end"], main section > div[style*="justify-content:flex-end"] { padding: 0 16px 14px !important; }',
    '  [data-logoaware][style*="column-count: 3"], [data-logoaware][style*="column-count:3"] { column-count: 2 !important; column-gap: 6px !important; padding: 0 6px 6px !important; }',
    '  [data-logoaware][style*="column-count: 3"] > a, [data-logoaware][style*="column-count:3"] > a { margin-bottom: 6px !important; }',
    '  [data-logoaware][style*="column-count: 2"], [data-logoaware][style*="column-count:2"] { column-count: 1 !important; padding: 0 16px 16px !important; }',
    '  section[style*="grid-template-columns: 1fr 1fr"], section[style*="grid-template-columns:1fr 1fr"] { grid-template-columns: 1fr !important; gap: 32px !important; padding: 10px 16px 64px !important; }',
    '  div[style*="grid-template-columns: 1fr 1fr"], div[style*="grid-template-columns:1fr 1fr"] { grid-template-columns: 1fr !important; }',
    '  section[style*="max-width: 620px"], section[style*="max-width:620px"] { padding: 24px 16px 72px !important; }',
    '  footer { padding: 18px 16px !important; }',
    '}',
    '@media (max-width: 420px) {',
    '  header > a:first-child { font-size: 22px !important; }',
    '}',
    '.ss-legal a { color: inherit; text-decoration: none; }',
    '.ss-legal a:hover { color: #111; }'
  ].join('\n');
  var style = document.createElement('style');
  style.setAttribute('data-ss-enhance', '');
  style.textContent = css;
  document.head.appendChild(style);
})();
