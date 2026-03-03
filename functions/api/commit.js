// ═══════════════════════════════════════════════════════════════
// GLASSFORGE CANON COMMIT API
// ═══════════════════════════════════════════════════════════════
// Cloudflare Pages Function — endpoint: /api/commit
// Holds GitHub token server-side; browser never sees it.
// Environment variables (set in Cloudflare Pages dashboard):
//   GITHUB_TOKEN  — GitHub PAT with repo write access
//   COMMIT_SECRET — passphrase to authorise commits
// ═══════════════════════════════════════════════════════════════

export async function onRequestPost(context) {
  const { env } = context;
  const GITHUB_TOKEN = env.GITHUB_TOKEN;
  const COMMIT_SECRET = env.COMMIT_SECRET;
  const CANON_REPO = 'mdashton88/swade-canon';

  // CORS headers
  const headers = {
    'Content-Type': 'application/json',
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'POST, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type'
  };

  try {
    const body = await context.request.json();

    // ── Auth check ──
    if (body.secret !== COMMIT_SECRET) {
      return new Response(JSON.stringify({ error: 'Invalid passphrase' }), { status: 403, headers });
    }

    // ── Validate request ──
    const { action } = body;
    if (action === 'commit_character') {
      return await handleCharacterCommit(body, GITHUB_TOKEN, CANON_REPO, headers);
    } else if (action === 'remove_character') {
      return await handleCharacterRemove(body, GITHUB_TOKEN, CANON_REPO, headers);
    } else if (action === 'get_changelog') {
      return await handleGetChangelog(GITHUB_TOKEN, CANON_REPO, headers);
    } else if (action === 'get_canon') {
      return await handleGetCanon(body, GITHUB_TOKEN, CANON_REPO, headers);
    } else {
      return new Response(JSON.stringify({ error: 'Unknown action' }), { status: 400, headers });
    }
  } catch (err) {
    return new Response(JSON.stringify({ error: err.message }), { status: 500, headers });
  }
}

// Handle OPTIONS for CORS preflight
export async function onRequestOptions() {
  return new Response(null, {
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type'
    }
  });
}

// ── COMMIT CHARACTER CHANGES ──
async function handleCharacterCommit(body, token, repo, headers) {
  const { character, filePath, summary, author } = body;
  if (!character || !character.name || !filePath) {
    return new Response(JSON.stringify({ error: 'Missing character or filePath' }), { status: 400, headers });
  }

  // 1. Read current canon file
  const fileRes = await ghGet(`/repos/${repo}/contents/${filePath}`, token);
  if (!fileRes.ok) {
    return new Response(JSON.stringify({ error: 'Cannot read canon file: ' + filePath }), { status: 500, headers });
  }
  const fileData = await fileRes.json();
  const currentContent = JSON.parse(b64decode(fileData.content.replace(/\n/g, '')));
  const fileSha = fileData.sha;

  // 2. Find and record the before state
  const idx = currentContent.findIndex(c => c.name === character.name);
  const before = idx >= 0 ? JSON.parse(JSON.stringify(currentContent[idx])) : null;

  // 3. Apply changes
  if (idx >= 0) {
    currentContent[idx] = character;
  } else {
    currentContent.push(character);
  }

  // 4. Build changelog entry
  const changeId = await getNextChangeId(token, repo);
  const diff = buildDiff(before, character);
  const affectedProducts = inferAffectedProducts(filePath, character.region);

  const changeEntry = {
    id: changeId,
    timestamp: new Date().toISOString(),
    author: author || 'NPC Database',
    target: character.name,
    region: character.region || 'Unknown',
    summary: summary || 'Character updated',
    diff: diff,
    affectedProducts: affectedProducts,
    status: {}
  };
  // Auto-mark the canon JSON as applied
  changeEntry.status[filePath] = new Date().toISOString();

  // 5. Read/update changelog
  let changelog = [];
  let changelogSha = null;
  const clRes = await ghGet(`/repos/${repo}/contents/canon-changelog.json`, token);
  if (clRes.ok) {
    const clData = await clRes.json();
    changelog = JSON.parse(b64decode(clData.content.replace(/\n/g, '')));
    changelogSha = clData.sha;
  }
  changelog.push(changeEntry);

  // 6. Commit both files (two sequential commits)
  const commitMsg = `${changeId}: ${summary || 'Update ' + character.name}`;

  // Commit canon file
  const canonCommit = await ghPut(
    `/repos/${repo}/contents/${filePath}`,
    token,
    {
      message: commitMsg,
      content: b64encode(JSON.stringify(currentContent, null, 2)),
      sha: fileSha
    }
  );
  if (!canonCommit.ok) {
    const err = await canonCommit.json();
    return new Response(JSON.stringify({ error: 'Canon commit failed: ' + (err.message || 'unknown') }), { status: 500, headers });
  }

  // Commit changelog
  const clBody = {
    message: commitMsg + ' [changelog]',
    content: b64encode(JSON.stringify(changelog, null, 2))
  };
  if (changelogSha) clBody.sha = changelogSha;
  const clCommit = await ghPut(`/repos/${repo}/contents/canon-changelog.json`, token, clBody);
  if (!clCommit.ok) {
    const err = await clCommit.json();
    return new Response(JSON.stringify({ error: 'Changelog commit failed: ' + (err.message || 'unknown') }), { status: 500, headers });
  }

  return new Response(JSON.stringify({
    success: true,
    changeId: changeId,
    diff: diff,
    affectedProducts: affectedProducts
  }), { status: 200, headers });
}

// ── REMOVE CHARACTER FROM CANON ──
async function handleCharacterRemove(body, token, repo, headers) {
  const { characterName, filePath, region, summary, author } = body;
  if (!characterName || !filePath) {
    return new Response(JSON.stringify({ error: 'Missing characterName or filePath' }), { status: 400, headers });
  }

  // 1. Read current canon file
  const fileRes = await ghGet(`/repos/${repo}/contents/${filePath}`, token);
  if (!fileRes.ok) {
    return new Response(JSON.stringify({ error: 'Cannot read canon file: ' + filePath }), { status: 500, headers });
  }
  const fileData = await fileRes.json();
  const currentContent = JSON.parse(b64decode(fileData.content.replace(/\n/g, '')));
  const fileSha = fileData.sha;

  // 2. Find and remove
  const idx = currentContent.findIndex(c => c.name === characterName);
  if (idx < 0) {
    return new Response(JSON.stringify({ error: 'Character not found in canon: ' + characterName }), { status: 404, headers });
  }
  const removed = currentContent.splice(idx, 1)[0];

  // 3. Build changelog entry
  const changeId = await getNextChangeId(token, repo);
  const affectedProducts = inferAffectedProducts(filePath, region);

  const changeEntry = {
    id: changeId,
    timestamp: new Date().toISOString(),
    author: author || 'NPC Database',
    target: characterName,
    region: region || 'Unknown',
    summary: summary || 'Character removed from canon',
    diff: { removed: true, character: removed },
    affectedProducts: affectedProducts,
    status: {}
  };
  changeEntry.status[filePath] = new Date().toISOString();

  // 4. Read/update changelog
  let changelog = [];
  let changelogSha = null;
  const clRes = await ghGet(`/repos/${repo}/contents/canon-changelog.json`, token);
  if (clRes.ok) {
    const clData = await clRes.json();
    changelog = JSON.parse(b64decode(clData.content.replace(/\n/g, '')));
    changelogSha = clData.sha;
  }
  changelog.push(changeEntry);

  // 5. Commit both files
  const commitMsg = `${changeId}: Remove ${characterName}`;

  const canonCommit = await ghPut(
    `/repos/${repo}/contents/${filePath}`,
    token,
    {
      message: commitMsg,
      content: b64encode(JSON.stringify(currentContent, null, 2)),
      sha: fileSha
    }
  );
  if (!canonCommit.ok) {
    const err = await canonCommit.json();
    return new Response(JSON.stringify({ error: 'Canon commit failed: ' + (err.message || 'unknown') }), { status: 500, headers });
  }

  const clBody = {
    message: commitMsg + ' [changelog]',
    content: b64encode(JSON.stringify(changelog, null, 2))
  };
  if (changelogSha) clBody.sha = changelogSha;
  const clCommit = await ghPut(`/repos/${repo}/contents/canon-changelog.json`, token, clBody);
  if (!clCommit.ok) {
    const err = await clCommit.json();
    return new Response(JSON.stringify({ error: 'Changelog commit failed: ' + (err.message || 'unknown') }), { status: 500, headers });
  }

  return new Response(JSON.stringify({
    success: true,
    changeId: changeId,
    affectedProducts: affectedProducts
  }), { status: 200, headers });
}

// ── GET CHANGELOG ──
async function handleGetChangelog(token, repo, headers) {
  const res = await ghGet(`/repos/${repo}/contents/canon-changelog.json`, token);
  if (!res.ok) {
    return new Response(JSON.stringify({ changelog: [] }), { status: 200, headers });
  }
  const data = await res.json();
  const changelog = JSON.parse(b64decode(data.content.replace(/\n/g, '')));
  return new Response(JSON.stringify({ changelog }), { status: 200, headers });
}

// ── GET CANON DATA ──
async function handleGetCanon(body, token, repo, headers) {
  const { filePath } = body;
  if (!filePath) {
    return new Response(JSON.stringify({ error: 'Missing filePath' }), { status: 400, headers });
  }
  const res = await ghGet(`/repos/${repo}/contents/${filePath}`, token);
  if (!res.ok) {
    return new Response(JSON.stringify({ error: 'File not found' }), { status: 404, headers });
  }
  const data = await res.json();
  const content = JSON.parse(b64decode(data.content.replace(/\n/g, '')));
  return new Response(JSON.stringify({ data: content }), { status: 200, headers });
}

// Unicode-safe base64 encode
function b64encode(str) {
  return btoa(unescape(encodeURIComponent(str)));
}

// Unicode-safe base64 decode
function b64decode(str) {
  return decodeURIComponent(escape(atob(str)));
}
async function ghGet(path, token) {
  return fetch(`https://api.github.com${path}`, {
    headers: { 'Authorization': `Bearer ${token}`, 'User-Agent': 'Glassforge-Canon-API', 'Accept': 'application/vnd.github.v3+json' }
  });
}

async function ghPut(path, token, body) {
  return fetch(`https://api.github.com${path}`, {
    method: 'PUT',
    headers: { 'Authorization': `Bearer ${token}`, 'User-Agent': 'Glassforge-Canon-API', 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
}

async function getNextChangeId(token, repo) {
  const res = await ghGet(`/repos/${repo}/contents/canon-changelog.json`, token);
  if (!res.ok) return 'CHG-001';
  const data = await res.json();
  const changelog = JSON.parse(b64decode(data.content.replace(/\n/g, '')));
  const num = changelog.length + 1;
  return 'CHG-' + String(num).padStart(3, '0');
}

function buildDiff(before, after) {
  if (!before) return { added: true, fields: Object.keys(after) };
  const changes = {};
  const allKeys = new Set([...Object.keys(before), ...Object.keys(after)]);
  for (const key of allKeys) {
    const bVal = JSON.stringify(before[key]);
    const aVal = JSON.stringify(after[key]);
    if (bVal !== aVal) {
      changes[key] = { was: before[key], now: after[key] };
    }
  }
  return changes;
}

function inferAffectedProducts(filePath, region) {
  const products = {};
  // The canon JSON itself
  products[filePath] = null;

  // Region-specific products
  const regionLower = (region || '').toLowerCase();
  if (regionLower) {
    products[`${regionLower}.js`] = null;                    // JS data module
    products[`${region} PDF`] = null;                         // Published PDF
    products[`${region} FG Module`] = null;                   // Fantasy Grounds
    products[`${region} Foundry Module`] = null;              // Foundry VTT (future)
  }

  return products;
}
