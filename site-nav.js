/**
 * GLASSFORGE GAMES — SITE NAV v1.0
 * Single source of truth for the primary navigation bar and site footer.
 * Drop one <script src="/site-nav.js"></script> into any page and call
 * initSiteNav({ active: 'vehicle-forge', bodyOffset: true }) — done.
 *
 * Options:
 *   active       {string}  Nav link to highlight. Matches href paths:
 *                          'home' | 'vehicle-forge' | 'battle-forge' | 'arrath'
 *                          Defaults to auto-detection from window.location.pathname.
 *   bodyOffset   {boolean} Add margin-top:72px to <body> (default: true).
 *                          Pass false for pages that handle their own offset
 *                          (e.g. full-viewport app layouts with .app{margin-top:72px}).
 *   footer       {boolean} Inject the SW fan licence footer (default: true).
 *   footerVersion {string} Version string shown in footer, e.g. 'Vehicle Forge v2.1.3'.
 *                          Omit to show the generic Glassforge branding only.
 *
 * Glassforge Games Ltd. — glassforge.pages.dev
 */

(function () {
  'use strict';

  /* ── NAV CSS ─────────────────────────────────────────────────────────── */
  var CSS = [
    /* Core bar */
    '#glassforge-nav{position:fixed;top:0;left:0;right:0;z-index:10000;',
    'background:#0A0908E8;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);',
    'border-bottom:1px solid #332E28;padding:0 48px;',
    'display:flex;align-items:center;justify-content:space-between;height:72px;',
    'font-family:"Cinzel",serif;box-sizing:border-box}',

    /* Brand */
    '#glassforge-nav .gn-brand{font-family:"Cinzel",serif;font-weight:700;font-size:16px;',
    'color:#D4B44A;letter-spacing:3px;text-transform:uppercase;text-decoration:none;',
    'display:flex;align-items:center;gap:10px}',
    '#glassforge-nav .gn-brand .gn-anvil{font-size:22px;color:#E8C85A}',

    /* Links */
    '#glassforge-nav .gn-links{display:flex;gap:32px;list-style:none;margin:0;padding:0}',
    '#glassforge-nav .gn-links a{font-family:"Cinzel",serif;font-size:13px;font-weight:700;',
    'letter-spacing:2px;text-transform:uppercase;color:#A89A88;',
    'text-decoration:none;transition:color 0.3s;position:relative}',
    '#glassforge-nav .gn-links a:hover,#glassforge-nav .gn-links a.active{color:#D4B44A}',
    '#glassforge-nav .gn-links a::after{content:"";position:absolute;bottom:-4px;',
    'left:0;right:0;height:1px;background:#D4B44A;transform:scaleX(0);transition:transform 0.3s}',
    '#glassforge-nav .gn-links a:hover::after,#glassforge-nav .gn-links a.active::after{transform:scaleX(1)}',

    /* Hamburger */
    '#glassforge-nav .gn-hamburger{display:none;flex-direction:column;gap:5px;',
    'cursor:pointer;padding:8px;background:none;border:none;z-index:10001}',
    '#glassforge-nav .gn-hamburger span{display:block;width:24px;height:2px;',
    'background:#D4B44A;transition:all 0.3s}',
    '#glassforge-nav .gn-hamburger.open span:nth-child(1){transform:rotate(45deg) translate(5px,5px)}',
    '#glassforge-nav .gn-hamburger.open span:nth-child(2){opacity:0}',
    '#glassforge-nav .gn-hamburger.open span:nth-child(3){transform:rotate(-45deg) translate(5px,-5px)}',

    /* Mobile drawer */
    '@media(max-width:768px){',
    '#glassforge-nav{padding:0 20px}',
    '#glassforge-nav .gn-hamburger{display:flex}',
    '#glassforge-nav .gn-links{',
    'position:fixed;top:72px;left:0;right:0;',
    'background:#0A0908F5;backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);',
    'flex-direction:column;padding:32px 40px;gap:24px;',
    'border-bottom:1px solid #332E28;',
    'transform:translateY(-100%);opacity:0;pointer-events:none;transition:all 0.3s}',
    '#glassforge-nav .gn-links.open{transform:translateY(0);opacity:1;pointer-events:auto}',
    '}',

    /* Footer */
    '#glassforge-footer{font-size:11px;color:#A89A88;text-align:center;',
    'padding:10px 24px;letter-spacing:1px;font-family:"Cinzel",serif;',
    'border-top:1px solid #332E28;background:#141210;',
    'display:flex;align-items:center;justify-content:center;gap:10px;flex-wrap:wrap}',
    '#glassforge-footer a{color:#9A8A3A;text-decoration:none}',
    '#glassforge-footer a:hover{color:#D4B44A}'
  ].join('');

  /* ── ACTIVE LINK DETECTION ────────────────────────────────────────────── */
  function detectActive() {
    var path = window.location.pathname.replace(/\.html$/, '').replace(/\/$/, '') || '/';
    if (path === '/' || path === '/index') return 'home';
    if (path.indexOf('vehicle-forge') !== -1) return 'vehicle-forge';
    if (path.indexOf('battle-forge') !== -1) return 'battle-forge';
    if (path.indexOf('arrath') !== -1 || path.indexOf('legal') !== -1) return 'arrath';
    return '';
  }

  /* ── MAIN INIT ────────────────────────────────────────────────────────── */
  window.initSiteNav = function (opts) {
    opts = opts || {};
    var active      = opts.active !== undefined ? opts.active : detectActive();
    var bodyOffset  = opts.bodyOffset !== false;   // default true
    var showFooter  = opts.footer !== false;        // default true
    var footerVer   = opts.footerVersion || '';

    /* Inject styles */
    if (!document.getElementById('glassforge-nav-css')) {
      var style = document.createElement('style');
      style.id  = 'glassforge-nav-css';
      style.textContent = CSS;
      document.head.appendChild(style);
    }

    /* Build nav links */
    var links = [
      { key: 'home',          label: 'Home',          href: '/' },
      { key: 'vehicle-forge', label: 'Vehicle Forge', href: '/vehicle-forge' },
      { key: 'battle-forge',  label: 'Battle Forge',  href: '/battle-forge'  },
      { key: 'arrath',        label: "World of Arr\u2019ath", href: '/#arrath' }
    ];

    var liHtml = links.map(function (l) {
      var cls = (l.key === active) ? ' class="active"' : '';
      return '<li><a href="' + l.href + '"' + cls + '>' + l.label + '</a></li>';
    }).join('');

    /* Build nav element */
    var nav = document.createElement('nav');
    nav.id = 'glassforge-nav';
    nav.innerHTML =
      '<a href="/" class="gn-brand">' +
        '<span class="gn-anvil">&#9874;</span> Glassforge Games' +
      '</a>' +
      '<button class="gn-hamburger" id="gn-hamburger" aria-label="Menu">' +
        '<span></span><span></span><span></span>' +
      '</button>' +
      '<ul class="gn-links" id="gn-links">' + liHtml + '</ul>';

    /* Insert as first child of body */
    document.body.insertBefore(nav, document.body.firstChild);

    /* Hamburger toggle */
    document.getElementById('gn-hamburger').addEventListener('click', function () {
      this.classList.toggle('open');
      document.getElementById('gn-links').classList.toggle('open');
    });

    /* Body offset — only for pages that DON'T manage their own margin-top */
    if (bodyOffset) {
      document.body.style.marginTop = '72px';
    }

    /* Footer */
    if (showFooter) {
      var footer = document.createElement('div');
      footer.id = 'glassforge-footer';

      var verText = footerVer
        ? footerVer + ' \u2014 <a href="/legal">Glassforge Games Ltd.</a>'
        : '\u00a9 2026 <a href="/legal">Glassforge Games Ltd.</a>';

      footer.innerHTML =
        '<a href="/legal" title="Savage Worlds Fan Product">' +
          '<img src="/sw-fan-logo.png" alt="Savage Worlds Fan Product" ' +
          'style="height:40px;vertical-align:middle;opacity:0.85">' +
        '</a>' +
        '<span>' + verText + '</span>';

      document.body.appendChild(footer);
    }
  };

  /* ── AUTO-INIT ────────────────────────────────────────────────────────── */
  /* Pages that call initSiteNav() explicitly (e.g. with footerVersion) will
     do so before DOMContentLoaded fires, so we only auto-init if they haven't. */
  function autoInit() {
    if (!document.getElementById('glassforge-nav')) {
      window.initSiteNav();
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', autoInit);
  } else {
    autoInit();
  }

})();
