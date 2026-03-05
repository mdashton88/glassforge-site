/**
 * GLASSFORGE GAMES — TOOL NAVIGATION v3.0
 * Internal tools sub-nav (tool switcher below the primary site-nav).
 * Primary nav is now handled entirely by site-nav.js.
 *
 * Usage: addToolNavigation('adventure-forge')
 *
 * Requires site-nav.js to be loaded first on the page.
 * Glassforge Games Ltd.
 */

function addToolNavigation(currentTool) {

  /* ── TOOL SWITCHER STYLES ── */
  if (!document.getElementById('dfs-tool-nav-css')) {
    var s = document.createElement('style');
    s.id = 'dfs-tool-nav-css';
    s.textContent =
      '.dfs-tool-nav{position:fixed;top:72px;left:0;right:0;z-index:9999;' +
      'display:flex;background:#141210;border-bottom:1px solid #3A3530;' +
      'padding:0 8px;overflow-x:auto;-webkit-overflow-scrolling:touch}' +
      '.dfs-tool-nav button{background:transparent;border:none;' +
      'border-bottom:2px solid transparent;color:#8A7A60;' +
      'padding:8px 14px;font-size:10px;letter-spacing:1.5px;' +
      'cursor:pointer;font-family:Cinzel,serif;text-transform:uppercase;' +
      'transition:all .15s;white-space:nowrap}' +
      '.dfs-tool-nav button:hover{color:#D4C8B0}' +
      '.dfs-tool-nav button.active{color:#C4A44A;border-bottom-color:#C4A44A}';
    document.head.appendChild(s);
  }

  function injectToolNav() {
    var nav = document.getElementById('glassforge-nav');
    if (!nav) { setTimeout(injectToolNav, 50); return; }
    if (document.querySelector('.dfs-tool-nav')) return;

    var tools = [
      { id: 'foundry',         label: '\uD83C\uDFED The Foundry',    url: '/foundry' },
      { id: 'adventure-forge', label: '\uD83D\uDDFA Adventure Forge', url: '/adventure-forge' },
      { id: 'adventure-vault', label: '\uD83C\uDFAD Adventure Vault', url: '/adventure-vault' },
      { id: 'pa-forge',        label: '\uD83D\uDEE1 Power Armour',    url: '/pa-forge' },
      { id: 'task-vault',      label: '\uD83D\uDCCB Task Vault',      url: '/task-vault' }
    ];

    var toolNav = document.createElement('div');
    toolNav.className = 'dfs-tool-nav';
    tools.forEach(function (tool) {
      var btn = document.createElement('button');
      btn.textContent = tool.label;
      if (tool.id === currentTool) btn.className = 'active';
      btn.onclick = function () {
        if (tool.id !== currentTool) window.location.href = tool.url;
      };
      toolNav.appendChild(btn);
    });

    nav.insertAdjacentElement('afterend', toolNav);

    /* Adjust header margin: 72px primary nav + 36px tool-nav = 108px */
    var header = document.querySelector('header');
    if (header) header.style.marginTop = '108px';
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', injectToolNav);
  } else {
    injectToolNav();
  }
}
