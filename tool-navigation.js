/**
 * TRIBUTE LANDS — TOOL NAVIGATION v2.0
 * Site-wide primary nav + tool switcher + Savage Worlds Fan Licence footer
 * Injected into all DiceForge internal production tools.
 *
 * DiceForge Studios Ltd.
 * Version: 2.0
 */

function addToolNavigation(currentTool) {

  /* ── INJECT STYLES ── */
  var s = document.createElement('style');
  s.textContent = [
    '.dfs-primary-nav{position:fixed;top:0;left:0;right:0;z-index:10000;background:#0A0908E8;backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px);border-bottom:1px solid #3A3530;padding:0 32px;display:flex;align-items:center;justify-content:space-between;height:48px;font-family:Cinzel,serif}',
    '.dfs-primary-nav a.brand{font-weight:700;font-size:13px;color:#C4A44A;letter-spacing:3px;text-transform:uppercase;text-decoration:none;display:flex;align-items:center;gap:8px}',
    '.dfs-primary-nav .site-links{display:flex;gap:24px}',
    '.dfs-primary-nav .site-links a{font-family:Cinzel,serif;font-size:11px;font-weight:600;letter-spacing:2px;text-transform:uppercase;color:#8A7A60;text-decoration:none;transition:color .25s}',
    '.dfs-primary-nav .site-links a:hover{color:#C4A44A}',
    '.dfs-tool-nav{position:fixed;top:48px;left:0;right:0;z-index:9999;display:flex;background:#141210;border-bottom:1px solid #3A3530;padding:0 8px;overflow-x:auto;-webkit-overflow-scrolling:touch}',
    '.dfs-tool-nav button{background:transparent;border:none;border-bottom:2px solid transparent;color:#8A7A60;padding:8px 14px;font-size:10px;letter-spacing:1.5px;cursor:pointer;font-family:Cinzel,serif;text-transform:uppercase;transition:all .15s;white-space:nowrap}',
    '.dfs-tool-nav button:hover{color:#D4C8B0}',
    '.dfs-tool-nav button.active{color:#C4A44A;border-bottom-color:#C4A44A}',
    '.dfs-fan-footer{padding:20px 32px;text-align:center;border-top:1px solid #3A3530;background:#0A0908;font-family:"Crimson Text",Georgia,serif;font-size:12px;color:#5A5040;line-height:1.5}'
  ].join('\n');
  document.head.appendChild(s);

  /* ── PRIMARY NAV ── */
  var nav = document.createElement('div');
  nav.className = 'dfs-primary-nav';
  nav.innerHTML = '<a href="/" class="brand"><span style="font-size:18px;color:#D4B45A">⚒</span> DiceForge Studios</a>'
    + '<div class="site-links">'
    + '<a href="/">Home</a>'
    + '<a href="/vehicle-forge-v2.1.html">Vehicle Forge</a>'
    + '<a href="/battle-forge.html">Battle Forge</a>'
    + '</div>';
  document.body.insertBefore(nav, document.body.firstChild);

  /* ── TOOL SWITCHER ── */
  var tools = [
    { id: 'foundry', label: '🏭 The Foundry', url: 'foundry' },
    { id: 'adventure-forge', label: '🗺 Adventure Forge', url: 'adventure-forge' },
    { id: 'adventure-vault', label: '🎭 Adventure Vault', url: 'adventure-vault' },
    { id: 'character-vault', label: '👤 Character Vault', url: 'character-vault' },
    { id: 'walker-workshop', label: '⚙ Walker Workshop', url: 'walker-workshop' },
    { id: 'pa-forge', label: '🛡 Power Armour', url: 'pa-forge' },
    { id: 'task-vault', label: '📋 Task Vault', url: 'task-vault' }
  ];

  var toolNav = document.createElement('div');
  toolNav.className = 'dfs-tool-nav';
  tools.forEach(function(tool) {
    var btn = document.createElement('button');
    btn.textContent = tool.label;
    if (tool.id === currentTool) btn.className = 'active';
    btn.onclick = function() { if (tool.id !== currentTool) window.location.href = tool.url; };
    toolNav.appendChild(btn);
  });
  nav.insertAdjacentElement('afterend', toolNav);

  /* ── FAN LICENCE FOOTER ── */
  var footer = document.createElement('div');
  footer.className = 'dfs-fan-footer';
  footer.innerHTML = '<a href="https://www.peginc.com/licensing/" title="Savage Worlds Fan Product">'
    + '<img src="/sw_fan_logo.png" alt="Savage Worlds Fan Product" style="height:40px;vertical-align:middle;margin-right:8px;opacity:0.85"></a><br>'
    + '<span style="font-size:10px;display:inline-block;max-width:600px;margin-top:4px;line-height:1.4">'
    + 'This game references the Savage Worlds game system, available from Pinnacle Entertainment Group at '
    + '<a href="https://www.peginc.com" style="color:#8A7A60">www.peginc.com</a>. '
    + 'Savage Worlds and all associated logos and trademarks are copyrights of Pinnacle Entertainment Group. '
    + 'Used with permission. Pinnacle makes no representation or warranty as to the quality, viability, or suitability for purpose of this product.</span><br>'
    + '<span style="font-size:10px;margin-top:4px;display:inline-block">&copy; 2026 DiceForge Studios Ltd.</span>';
  document.body.appendChild(footer);
}

/* ── ADJUST BODY MARGIN FOR DOUBLE NAV (48 + 36 = 84px) ── */
(function() {
  function adjust() {
    var header = document.querySelector('header');
    if (header) header.style.marginTop = '84px';
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', adjust);
  } else {
    adjust();
  }
})();
