/**
 * VAULT INTEGRATION MODULE
 * Shared functionality for Character Vault and Adventure Vault
 * Handles cross-vault navigation, data sync, and deep linking
 */

window.VaultIntegration = (function() {
  'use strict';
  
  const STORAGE_KEYS = {
    NPCS: 'glassforge_vault_npcs',
    ADVENTURES: 'glassforge_vault_adventures',
    LAST_SYNC: 'glassforge_vault_last_sync'
  };
  
  // ═══ STORAGE SYNC ═══
  
  function syncNPCsToStorage(npcs) {
    try {
      const data = npcs.map(npc => ({
        name: npc.name,
        title: npc.concept || npc.title || '',
        category: npc.category || 'NPC',
        region: npc.region || 'Global',
        tier: npc.tier || 'Extra',
        ancestry: npc.ancestry || 'Human'
      }));
      localStorage.setItem(STORAGE_KEYS.NPCS, JSON.stringify(data));
      localStorage.setItem(STORAGE_KEYS.LAST_SYNC, new Date().toISOString());
    } catch (e) {
      console.error('Failed to sync NPCs to storage:', e);
    }
  }
  
  function syncAdventuresToStorage(adventures) {
    try {
      const data = adventures.map(adv => ({
        week: adv.week,
        title: adv.title,
        phase: adv.phase,
        showcase: adv.showcase || '',
        npcs: adv.npcs || []
      }));
      localStorage.setItem(STORAGE_KEYS.ADVENTURES, JSON.stringify(data));
      localStorage.setItem(STORAGE_KEYS.LAST_SYNC, new Date().toISOString());
    } catch (e) {
      console.error('Failed to sync adventures to storage:', e);
    }
  }
  
  function getNPCsFromStorage() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.NPCS);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Failed to read NPCs from storage:', e);
      return [];
    }
  }
  
  function getAdventuresFromStorage() {
    try {
      const data = localStorage.getItem(STORAGE_KEYS.ADVENTURES);
      return data ? JSON.parse(data) : [];
    } catch (e) {
      console.error('Failed to read adventures from storage:', e);
      return [];
    }
  }
  
  // ═══ URL PARAMETER HANDLING ═══
  
  function getURLParam(name) {
    const params = new URLSearchParams(window.location.search);
    return params.get(name);
  }
  
  function buildCharacterVaultURL(characterName) {
    const base = window.location.origin + window.location.pathname.replace('adventure-vault.html', 'character-vault');
    return base + (characterName ? '?char=' + encodeURIComponent(characterName) : '');
  }
  
  function buildAdventureVaultURL(weekNumber) {
    const base = window.location.origin + window.location.pathname.replace('character-vault', 'adventure-vault.html');
    return base + (weekNumber ? '?week=' + weekNumber : '');
  }
  
  // ═══ CROSS-VAULT NAVIGATION ═══
  
  function navigateToCharacterVault(characterName) {
    window.open(buildCharacterVaultURL(characterName), '_blank');
  }
  
  function navigateToAdventureVault(weekNumber) {
    window.open(buildAdventureVaultURL(weekNumber), '_blank');
  }
  
  // ═══ NPC ASSIGNMENT HELPERS ═══
  
  function getAvailableNPCs() {
    return getNPCsFromStorage();
  }
  
  function getNPCsByNames(names) {
    const allNPCs = getNPCsFromStorage();
    return names.map(name => allNPCs.find(npc => npc.name === name)).filter(Boolean);
  }
  
  function getAdventuresForNPC(npcName) {
    const allAdventures = getAdventuresFromStorage();
    return allAdventures.filter(adv => 
      adv.npcs && adv.npcs.includes(npcName)
    ).sort((a, b) => a.week - b.week);
  }
  
  function getNPCsForAdventure(weekNumber) {
    const allAdventures = getAdventuresFromStorage();
    const adventure = allAdventures.find(adv => adv.week === weekNumber);
    if (!adventure || !adventure.npcs) return [];
    
    const allNPCs = getNPCsFromStorage();
    return adventure.npcs.map(name => 
      allNPCs.find(npc => npc.name === name)
    ).filter(Boolean);
  }
  
  // ═══ UI COMPONENTS ═══
  
  function createVaultNavigationButton(currentVault) {
    const btn = document.createElement('button');
    btn.className = 'btn sm';
    btn.style.cssText = 'font-size:10px;padding:1px 6px;background:none;border:1px solid var(--border);color:var(--text-dim);border-radius:3px;cursor:pointer;margin-left:8px';
    
    // If we're in Character Vault, create button to Adventure Vault (and vice versa)
    if (currentVault === 'character') {
      btn.innerHTML = '🎭 Adventure Vault';
      btn.title = 'Open Adventure Vault';
      btn.onclick = () => navigateToAdventureVault();
    } else if (currentVault === 'adventure') {
      btn.innerHTML = '👤 Character Vault';
      btn.title = 'Open Character Vault';
      btn.onclick = () => navigateToCharacterVault();
    }
    
    return btn;
  }
  
  function createHelpButton(vaultType) {
    const btn = document.createElement('button');
    btn.className = 'btn sm';
    btn.style.cssText = 'font-size:10px;padding:1px 6px;background:none;border:1px solid var(--border);color:var(--text-dim);border-radius:3px;cursor:pointer;margin-left:8px';
    btn.innerHTML = '? Help';
    btn.title = 'Show help';
    btn.onclick = () => showHelpModal(vaultType);
    return btn;
  }
  
  function showHelpModal(vaultType) {
    // Remove existing help overlay
    const existing = document.getElementById('vaultHelpOverlay');
    if (existing) {
      existing.remove();
      return;
    }
    
    const overlay = document.createElement('div');
    overlay.id = 'vaultHelpOverlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.8);z-index:300;display:flex;align-items:center;justify-content:center;';
    overlay.onclick = (e) => { if (e.target === overlay) overlay.remove(); };
    
    const content = vaultType === 'character' ? getCharacterVaultHelp() : getAdventureVaultHelp();
    
    overlay.innerHTML = `
      <div style="background:var(--bg-card);border:1px solid var(--border);border-radius:8px;padding:24px 32px;max-width:680px;max-height:90vh;overflow-y:auto;width:90%">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
          <h3 style="margin:0;color:var(--accent);font-size:18px">📚 ${vaultType === 'character' ? 'Character' : 'Adventure'} Vault Help</h3>
          <button class="btn sm" onclick="document.getElementById('vaultHelpOverlay').remove()">✕</button>
        </div>
        ${content}
        <div style="margin-top:20px;text-align:center;font-size:11px;color:var(--text-dim)">
          Press <kbd style="background:var(--bg-input);border:1px solid var(--border);border-radius:2px;padding:1px 5px;font-family:monospace">Esc</kbd> or click anywhere to close
        </div>
      </div>
    `;
    
    document.body.appendChild(overlay);
    
    // ESC to close
    const escHandler = (e) => {
      if (e.key === 'Escape') {
        overlay.remove();
        document.removeEventListener('keydown', escHandler);
      }
    };
    document.addEventListener('keydown', escHandler);
  }
  
  function getCharacterVaultHelp() {
    return `
      <div style="font-size:13px;color:var(--text);line-height:1.7">
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">What is the Character Vault?</h4>
        <p style="margin:0 0 12px">The Character Vault manages all NPCs and pre-generated characters for the Tribute Lands setting. It provides SWADE-compliant character creation, lifecycle management, and integration with adventures.</p>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Lifecycle States</h4>
        <div style="display:flex;gap:12px;align-items:center;margin:0 0 12px;font-size:13px;background:var(--bg-input);padding:10px;border-radius:4px">
          <span style="color:var(--text-dim)">📝 Draft</span> → <span style="color:#e8b84e">📦 Committed</span> → <span style="color:var(--green)">🔒 Published</span>
        </div>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li><strong style="color:var(--text-dim)">📝 DRAFT</strong> — Character exists but isn't approved. Edit freely.</li>
          <li><strong style="color:#e8b84e">📦 COMMITTED</strong> — Stats locked as canonical. Edits show EDITED badge until recommitted.</li>
          <li><strong style="color:var(--green)">🔒 PUBLISHED</strong> — Assigned to released product. Edits require errata reason.</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Integration with Adventure Vault</h4>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li>Click <strong>🎭 Adventure Vault</strong> button in header to switch vaults</li>
          <li>Adventure appearances shown in character detail (clickable week numbers)</li>
          <li>Characters automatically available for assignment in Adventure Vault</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Key Features</h4>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li><strong>SWADE Character Builder</strong> — Full attributes, skills, edges, hindrances, powers, gear</li>
          <li><strong>Build Audit</strong> — Validates SWADE-legal builds with detailed feedback</li>
          <li><strong>Export</strong> — Markdown, Fantasy Grounds XML, stat blocks</li>
          <li><strong>Narrative Tools</strong> — Background, motivations, secrets, connections, physical descriptions</li>
          <li><strong>Product Registry</strong> — Track which products include each character</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Keyboard Shortcuts</h4>
        <div style="background:var(--bg-input);padding:10px;border-radius:4px;font-size:12px">
          <div style="display:flex;justify-content:space-between;padding:2px 0"><span>Navigate roster</span><kbd style="background:var(--bg-card);border:1px solid var(--border);padding:1px 6px;border-radius:2px">↑ ↓</kbd></div>
          <div style="display:flex;justify-content:space-between;padding:2px 0"><span>Undo / Redo</span><kbd style="background:var(--bg-card);border:1px solid var(--border);padding:1px 6px;border-radius:2px">Ctrl+Z</kbd> / <kbd style="background:var(--bg-card);border:1px solid var(--border);padding:1px 6px;border-radius:2px">Ctrl+Y</kbd></div>
          <div style="display:flex;justify-content:space-between;padding:2px 0"><span>Navigate back/forward</span><kbd style="background:var(--bg-card);border:1px solid var(--border);padding:1px 6px;border-radius:2px">Alt+← →</kbd></div>
        </div>
      </div>
    `;
  }
  
  function getAdventureVaultHelp() {
    return `
      <div style="font-size:13px;color:var(--text);line-height:1.7">
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">What is the Adventure Vault?</h4>
        <p style="margin:0 0 12px">The Adventure Vault manages the 50-week Ammaria campaign catalogue. It stores complete adventure content, tracks production phases, manages foreshadowing threads, and integrates with the Character Vault for NPC assignments.</p>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Production Phases</h4>
        <div style="background:var(--bg-input);padding:10px;border-radius:4px;margin:0 0 12px">
          <div style="display:flex;gap:8px;align-items:center;font-size:12px;flex-wrap:wrap">
            <span class="status-tag catalogue">catalogue</span> →
            <span class="status-tag outline">outline</span> →
            <span class="status-tag draft">draft</span> →
            <span class="status-tag review">review</span> →
            <span class="status-tag complete">complete</span>
          </div>
        </div>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li><strong>CATALOGUE</strong> — Initial concept, showcase elements, high-level notes</li>
          <li><strong>OUTLINE</strong> — Scene breakdown, structure, encounter planning</li>
          <li><strong>DRAFT</strong> — Full adventure content written, ready for review</li>
          <li><strong>REVIEW</strong> — Quality review, polish, mechanical verification</li>
          <li><strong>COMPLETE</strong> — Finished, ready for Fantasy Grounds conversion</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Lifecycle States</h4>
        <div style="display:flex;gap:12px;align-items:center;margin:0 0 12px;font-size:13px;background:var(--bg-input);padding:10px;border-radius:4px">
          <span style="color:var(--text-dim)">📝 Draft</span> → <span style="color:#e8b84e">📦 Committed</span> → <span style="color:var(--green)">🔒 Published</span>
        </div>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li><strong>📝 DRAFT</strong> — Adventure content in development, edit freely</li>
          <li><strong>📦 COMMITTED</strong> — Content locked as canonical version for production</li>
          <li><strong>🔒 PUBLISHED</strong> — Released in bundle, changes tracked as errata</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Integration with Character Vault</h4>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li>Click <strong>👤 Character Vault</strong> button in header to switch vaults</li>
          <li>Click NPC tags in adventure detail to open that character in Character Vault</li>
          <li>NPC assignment pulls from committed characters in Character Vault</li>
          <li>Characters show which adventures they appear in (with clickable week links)</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Key Features</h4>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li><strong>Adventure Structure</strong> — Hook, scenes, complications, twists, rewards</li>
          <li><strong>NPC Assignment</strong> — Link characters from Character Vault</li>
          <li><strong>Thread Tracking</strong> — Manage foreshadowing across multiple weeks (planted/developed/payoff)</li>
          <li><strong>Bundle Management</strong> — Organize 5-week content bundles</li>
          <li><strong>Export</strong> — Markdown, PDF, Fantasy Grounds modules</li>
          <li><strong>Production Dashboard</strong> — Track progress across all 50 weeks</li>
        </ul>
        
        <h4 style="color:var(--accent);font-size:14px;margin:16px 0 8px">Thread Types</h4>
        <ul style="margin:0 0 12px;padding-left:20px">
          <li><strong style="color:var(--purple)">PLANTED</strong> — Foreshadowing introduced, seeds future development</li>
          <li><strong style="color:var(--blue)">DEVELOPED</strong> — Thread continues, builds on earlier setup</li>
          <li><strong style="color:var(--accent)">PAYOFF</strong> — Thread resolves, delivers on foreshadowing</li>
        </ul>
      </div>
    `;
  }
  
  // ═══ CLICKABLE NPC TAGS ═══
  
  function makeNPCTagClickable(tagElement, npcName) {
    tagElement.style.cursor = 'pointer';
    tagElement.title = 'Open in Character Vault';
    tagElement.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      navigateToCharacterVault(npcName);
    };
  }
  
  function makeWeekLinkClickable(linkElement, weekNumber) {
    linkElement.style.cursor = 'pointer';
    linkElement.title = 'Open in Adventure Vault';
    linkElement.onclick = (e) => {
      e.preventDefault();
      e.stopPropagation();
      navigateToAdventureVault(weekNumber);
    };
  }
  
  // ═══ PUBLIC API ═══
  
  return {
    // Storage sync
    syncNPCsToStorage,
    syncAdventuresToStorage,
    getNPCsFromStorage,
    getAdventuresFromStorage,
    
    // URL handling
    getURLParam,
    buildCharacterVaultURL,
    buildAdventureVaultURL,
    
    // Navigation
    navigateToCharacterVault,
    navigateToAdventureVault,
    
    // Data helpers
    getAvailableNPCs,
    getNPCsByNames,
    getAdventuresForNPC,
    getNPCsForAdventure,
    
    // UI components
    createVaultNavigationButton,
    createHelpButton,
    showHelpModal,
    makeNPCTagClickable,
    makeWeekLinkClickable
  };
})();
