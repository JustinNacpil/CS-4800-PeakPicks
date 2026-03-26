// ========================================
// Scale Type Definitions
// ========================================
const SCALE_LABELS = {
  classic:  { S:'S',           A:'A',          B:'B',     C:'C',        D:'D',          name:'Classic S-Tier',  icon:'📊', ranks:['S','A','B','C','D'] },
  worth_it: { S:'MUST BUY',   A:'WORTH IT',   B:'EH OKAY', C:'NOT WORTH', D:'TOTAL SCAM', name:'Worth It Scale', icon:'💰', ranks:['S','A','B','C','D'] },
  slider:   { S:'Amazing',    A:'Great',      B:'Good',  C:'Okay',     D:'Never',      name:'Slider Scale',    icon:'🎚️', ranks:['S','A','B','C','D'] },
  bracket:  { S:'🥇 Champion', A:'🥈 Runner-Up', B:'🥉 Third', C:'Fourth', D:'Fifth',   name:'Bracket Battle',  icon:'🏆', ranks:['S','A','B','C','D'] },
};

// ========================================
// Toast Notifications
// ========================================
class Toast {
  static show(message, type = 'success', duration = 3000) {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'slideInRight 0.3s ease-out reverse';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }
  static success(msg) { this.show(msg, 'success'); }
  static error(msg) { this.show(msg, 'error', 4000); }
}

// ========================================
// Utility
// ========================================
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}
function formatDate(iso) {
  if (!iso) return '';
  const d = new Date(iso), now = new Date(), ms = now - d;
  const mins = Math.floor(ms/60000), hrs = Math.floor(ms/3600000), days = Math.floor(ms/86400000);
  if (mins < 1) return 'just now';
  if (mins < 60) return mins + 'm ago';
  if (hrs < 24) return hrs + 'h ago';
  if (days < 7) return days + 'd ago';
  return d.toLocaleDateString();
}

// ========================================
// API
// ========================================
async function apiRequest(url, method='GET', data=null) {
  const opts = { method, headers: {'Content-Type':'application/json'} };
  if (data) opts.body = JSON.stringify(data);
  try {
    const r = await fetch(url, opts);
    const j = await r.json();
    return { ok: r.ok, status: r.status, data: j };
  } catch(e) {
    console.error('API error:', e);
    return { ok: false, status: 0, data: { error: 'Network error' } };
  }
}
async function getTierlists(cat='', user='') {
  let url = '/api/tierlists';
  const p = [];
  if (cat) p.push('category=' + encodeURIComponent(cat));
  if (user) p.push('username=' + encodeURIComponent(user));
  if (p.length) url += '?' + p.join('&');
  const r = await apiRequest(url);
  return r.ok ? r.data : [];
}
async function getCategories() {
  const r = await apiRequest('/api/categories');
  return r.ok ? r.data : [];
}

// ========================================
// Tier List Card Rendering (for Browse/Home)
// ========================================
function renderTierlistCard(tl) {
  const scaleType = tl.scale_type || 'classic';
  const scale = SCALE_LABELS[scaleType] || SCALE_LABELS.classic;
  const picks = tl.picks || [];
  const tiers = {S:[], A:[], B:[], C:[], D:[]};
  picks.forEach(p => { if(tiers[p.rank]) tiers[p.rank].push(p); });

  let previewHtml = '';
  for (const [tier, items] of Object.entries(tiers)) {
    if (items.length > 0) {
      const label = scale[tier] || tier;
      previewHtml += `
        <div class="tl-preview-row">
          <div class="tl-preview-label tier-label ${tier.toLowerCase()}">${label}</div>
          <div class="tl-preview-items">
            ${items.slice(0, 6).map(i => `
              <div class="tl-preview-item" title="${escapeHtml(i.name)}">
                ${i.image_url ? `<img src="${escapeHtml(i.image_url)}" onerror="this.style.display='none'">` : ''}
                <span>${escapeHtml(i.name)}</span>
              </div>
            `).join('')}
            ${items.length > 6 ? `<span class="tl-preview-more">+${items.length-6}</span>` : ''}
          </div>
        </div>
      `;
    }
  }
  if (!previewHtml) {
    previewHtml = '<div class="tl-preview-empty">No items yet</div>';
  }

  return `
    <div class="tierlist-card" onclick="window.location='/view/${tl._id}'" style="cursor:pointer;" data-id="${tl._id}">
      <div class="tl-card-header">
        <div class="tl-card-info">
          <div class="tl-card-title">${escapeHtml(tl.title || tl.category + ' Tier List')}</div>
          <div class="tl-card-meta">
            <span class="tl-card-category-badge">${escapeHtml(tl.category)}</span>
            <span class="tl-card-scale">${scale.icon} ${scale.name}</span>
          </div>
        </div>
        <div class="tl-card-count">${picks.length} items</div>
      </div>
      <div class="tl-preview" data-theme="${escapeHtml(tl.theme||'classic')}">
        ${previewHtml}
      </div>
      <div class="tl-card-footer">
        <a href="/profile/${encodeURIComponent(tl.created_by_username||'Guest')}" class="tl-creator" onclick="event.stopPropagation()">
          👤 ${escapeHtml(tl.created_by_username||'Guest')}
        </a>
        <div class="tl-card-actions">
          <button class="like-btn ${tl.liked_by_user?'liked':''}" onclick="event.stopPropagation(); toggleLikeTierlist(this,'${tl._id}')">
            ${tl.liked_by_user?'❤️':'🤍'} <span class="like-count">${tl.likes||0}</span>
          </button>
          <span class="tl-time">${formatDate(tl.created_at)}</span>
        </div>
      </div>
    </div>
  `;
}

// ========================================
// Like Tier List
// ========================================
async function toggleLikeTierlist(btn, id) {
  const r = await apiRequest('/api/tierlists/' + id + '/like', 'POST');
  if (r.ok) {
    btn.classList.toggle('liked', r.data.liked);
    btn.innerHTML = `${r.data.liked?'❤️':'🤍'} <span class="like-count">${r.data.likes_count}</span>`;
  } else {
    Toast.error(r.data.error || 'Login to like tier lists');
  }
}

// ========================================
// Legacy Pick Card (for backward compat)
// ========================================
function renderPickCard(pick) {
  const rc = pick.rank.toLowerCase();
  const tags = (pick.tags||[]).map(t => `<span class="tag">#${escapeHtml(t)}</span>`).join('');
  return `
    <div class="pick-card" onclick="openModal('${pick._id}')" style="cursor:pointer;">
      <div class="pick-header">
        <div class="pick-rank ${rc}">${pick.rank}</div>
        <div class="pick-actions">
          <button class="like-btn ${pick.liked_by_user?'liked':''}" onclick="event.stopPropagation(); toggleLikePick(this,'${pick._id}')">
            ${pick.liked_by_user?'❤️':'🤍'} <span class="like-count">${pick.likes||0}</span>
          </button>
        </div>
      </div>
      ${pick.image_url ? `<img src="${escapeHtml(pick.image_url)}" class="pick-image" onerror="this.style.display='none'">` : ''}
      <div class="pick-name">${escapeHtml(pick.name)}</div>
      <a href="/profile/${encodeURIComponent(pick.created_by_username||'Guest')}" class="pick-creator" onclick="event.stopPropagation()">by ${escapeHtml(pick.created_by_username||'Guest')}</a>
      ${pick.reason ? `<div class="pick-reason">${escapeHtml(pick.reason)}</div>` : ''}
      ${tags ? `<div class="pick-tags">${tags}</div>` : ''}
    </div>
  `;
}

// ========================================
// Tier Item Rendering (in tier list view)
// ========================================
function renderTierItem(item, scaleType) {
  return `
    <div class="tier-item" data-rank="${item.rank}" title="Click for details" onclick="openItemDetail(this)" data-name="${escapeHtml(item.name)}" data-reason="${escapeHtml(item.reason||'')}" data-image="${escapeHtml(item.image_url||'')}">
      ${item.image_url ? `<img src="${escapeHtml(item.image_url)}" class="tier-item-img" onerror="this.style.display='none'" loading="lazy">` : ''}
      <span class="tier-item-name">${escapeHtml(item.name)}</span>
    </div>
  `;
}

// Item detail popup (click on tier item)
function openItemDetail(el) {
  const name = el.dataset.name || '';
  const reason = el.dataset.reason || '';
  const image = el.dataset.image || '';
  if (!reason && !image) return;

  const existing = document.getElementById('itemDetailPopup');
  if (existing) existing.remove();

  const popup = document.createElement('div');
  popup.id = 'itemDetailPopup';
  popup.className = 'item-detail-popup';
  popup.innerHTML = `
    <div class="item-detail-content">
      <button class="item-detail-close" onclick="document.getElementById('itemDetailPopup').remove()">&times;</button>
      ${image ? `<img src="${escapeHtml(image)}" onerror="this.style.display='none'">` : ''}
      <div class="item-detail-name">${escapeHtml(name)}</div>
      ${reason ? `<div class="item-detail-reason">${escapeHtml(reason)}</div>` : ''}
    </div>
  `;
  popup.addEventListener('click', e => { if (e.target === popup) popup.remove(); });
  document.body.appendChild(popup);
}

// ========================================
// Tier List Rendering (full view)
// ========================================
function renderTierlist(tierlist) {
  const scaleType = tierlist.scale_type || 'classic';
  const scale = SCALE_LABELS[scaleType] || SCALE_LABELS.classic;
  const picks = tierlist.picks || [];
  const tiers = {S:[], A:[], B:[], C:[], D:[]};
  picks.forEach(p => { if(tiers[p.rank]) tiers[p.rank].push(p); });

  let html = '';
  for (const [tier, items] of Object.entries(tiers)) {
    const rankLabel = scale[tier] || tier;
    const tc = tier.toLowerCase();
    const ih = items.map(p => renderTierItem(p, scaleType)).join('');
    html += `
      <div class="tier-row">
        <div class="tier-label ${tc}">${rankLabel}</div>
        <div class="tier-items" data-tier="${tier}">
          ${ih || '<div class="tier-empty-hint">Drop items here</div>'}
        </div>
      </div>
    `;
  }
  return html;
}

// ========================================
// Drag and Drop
// ========================================
function setupDragAndDrop() {
  document.querySelectorAll('.tier-item').forEach(item => {
    item.setAttribute('draggable', 'true');
    item.addEventListener('dragstart', e => {
      e.dataTransfer.effectAllowed = 'move';
      e.dataTransfer.setData('text/plain', item.dataset.rank);
      item.classList.add('dragging');
    });
    item.addEventListener('dragend', () => {
      item.classList.remove('dragging');
      document.querySelectorAll('.tier-items').forEach(c => c.classList.remove('drag-over'));
      // Remove empty hints that might have been displaced
      document.querySelectorAll('.tier-items').forEach(c => {
        if (c.children.length === 0) {
          c.innerHTML = '<div class="tier-empty-hint">Drop items here</div>';
        }
      });
    });
  });
  document.querySelectorAll('.tier-items').forEach(container => {
    container.addEventListener('dragover', e => {
      e.preventDefault();
      container.classList.add('drag-over');
      // Remove the empty hint when dragging over
      const hint = container.querySelector('.tier-empty-hint');
      if (hint) hint.style.display = 'none';
    });
    container.addEventListener('dragleave', e => {
      if (!container.contains(e.relatedTarget)) {
        container.classList.remove('drag-over');
        const hint = container.querySelector('.tier-empty-hint');
        if (hint && container.querySelectorAll('.tier-item').length === 0) {
          hint.style.display = '';
        }
      }
    });
    container.addEventListener('drop', e => {
      e.preventDefault();
      container.classList.remove('drag-over');
      const dragging = document.querySelector('.tier-item.dragging');
      if (dragging) {
        container.appendChild(dragging);
        // Remove empty hints
        const hint = container.querySelector('.tier-empty-hint');
        if (hint) hint.remove();
        // Add empty hint to source if empty
        document.querySelectorAll('.tier-items').forEach(c => {
          if (c !== container && c.querySelectorAll('.tier-item').length === 0) {
            if (!c.querySelector('.tier-empty-hint')) {
              c.innerHTML = '<div class="tier-empty-hint">Drop items here</div>';
            }
          }
        });
        Toast.success('Moved to ' + container.dataset.tier + ' tier!');
      }
    });
  });
}

// ========================================
// Modal (legacy pick detail)
// ========================================
let allLoadedPicks = [];
let currentModalIndex = -1;

async function openModal(pickId) {
  const modal = document.getElementById('pickModal');
  const body = document.getElementById('modalBody');
  if (!modal || !body) return;
  currentModalIndex = allLoadedPicks.findIndex(p => p._id === pickId);
  const r = await apiRequest('/api/picks/' + pickId);
  if (!r.ok) { Toast.error('Could not load pick'); return; }
  const p = r.data;
  body.innerHTML = `
    <div class="modal-pick">
      <div style="display:flex; align-items:center; gap:1rem; margin-bottom:1.25rem; flex-wrap:wrap;">
        <div class="pick-rank ${p.rank.toLowerCase()}" style="font-size:2rem; padding:0.4rem 0.8rem;">${p.rank}</div>
        <div>
          <div style="font-size:1.5rem; font-weight:700;">${escapeHtml(p.name)}</div>
          <div style="color:var(--accent-light); font-weight:600;">${escapeHtml(p.category)}</div>
        </div>
      </div>
      ${p.image_url ? `<img src="${escapeHtml(p.image_url)}" style="width:100%; max-height:300px; object-fit:cover; border-radius:10px; margin-bottom:1rem;" onerror="this.style.display='none'">` : ''}
      ${p.reason ? `<div style="padding:1rem; background:rgba(99,102,241,0.1); border:1px solid rgba(129,140,248,0.3); border-radius:8px; margin-bottom:1rem;"><div style="font-size:0.8rem; color:var(--text-secondary); margin-bottom:0.5rem; font-weight:600;">Why this rank?</div><p style="margin:0; line-height:1.5;">${escapeHtml(p.reason)}</p></div>` : ''}
      ${(p.tags||[]).length ? `<div class="pick-tags" style="margin-bottom:1rem;">${p.tags.map(t=>`<span class="tag">#${escapeHtml(t)}</span>`).join('')}</div>` : ''}
      <div style="display:flex; justify-content:space-between; align-items:center; color:var(--text-secondary); font-size:0.9rem; flex-wrap:wrap; gap:0.5rem;">
        <span>by <a href="/profile/${encodeURIComponent(p.created_by_username||'Guest')}" style="color:var(--accent-light); font-weight:600;">${escapeHtml(p.created_by_username||'Guest')}</a></span>
        <span>${p.likes||0} likes · ${formatDate(p.created_at)}</span>
      </div>
    </div>
  `;
  modal.style.display = 'flex';
  document.body.style.overflow = 'hidden';
}

function closeModal() {
  const modal = document.getElementById('pickModal');
  if (modal) modal.style.display = 'none';
  document.body.style.overflow = '';
}
function closeModalOutside(e) {
  if (e.target.id === 'pickModal') closeModal();
}
function navigateModal(dir) {
  if (allLoadedPicks.length === 0 || currentModalIndex < 0) return;
  currentModalIndex = (currentModalIndex + dir + allLoadedPicks.length) % allLoadedPicks.length;
  openModal(allLoadedPicks[currentModalIndex]._id);
}
document.addEventListener('keydown', (e) => {
  const modal = document.getElementById('pickModal');
  if (!modal || modal.style.display === 'none') return;
  if (e.key === 'Escape') closeModal();
  if (e.key === 'ArrowLeft') navigateModal(-1);
  if (e.key === 'ArrowRight') navigateModal(1);
});

// ========================================
// Like Pick (legacy)
// ========================================
async function toggleLikePick(btn, id) {
  const r = await apiRequest('/api/picks/' + id + '/like', 'POST');
  if (r.ok) {
    btn.classList.toggle('liked', r.data.liked);
    btn.innerHTML = `${r.data.liked?'❤️':'🤍'} <span class="like-count">${r.data.likes_count}</span>`;
  } else {
    Toast.error(r.data.error || 'Login to like picks');
  }
}

// ========================================
// Create Flow - Multi-Step
// ========================================
let createState = {
  category: '',
  title: '',
  scaleType: 'classic',
  theme: 'classic',
  layout: 'rows',
  items: [],
  currentTierlistId: null,
};

function selectType(el) {
  document.querySelectorAll('.type-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  const cat = el.dataset.category;
  const wrap = document.getElementById('customCategoryWrap');
  const titleWrap = document.getElementById('titleInputWrap');
  const btn = document.getElementById('toStep2Btn');
  if (cat === 'custom') {
    if (wrap) wrap.style.display = 'block';
    const inp = document.getElementById('customCategory');
    if (inp) {
      inp.focus();
      inp.oninput = () => {
        createState.category = inp.value.trim();
        if (btn) btn.disabled = !createState.category;
        const ti = document.getElementById('titleInput');
        if (ti && !ti.value) ti.placeholder = `e.g., My ${createState.category} Rankings`;
      };
    }
  } else {
    if (wrap) wrap.style.display = 'none';
    createState.category = cat;
    if (btn) btn.disabled = false;
    const ti = document.getElementById('titleInput');
    if (ti && !ti.value) ti.placeholder = `e.g., My ${cat} Rankings`;
  }
  if (titleWrap) {
    titleWrap.style.display = 'block';
    titleWrap.style.animation = 'fadeInUp 0.3s ease-out';
  }
}

function selectScale(el) {
  document.querySelectorAll('.scale-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  createState.scaleType = el.dataset.scale;
  // Update tier buttons in step 3 preview
  updateTierButtonLabels();
}

function updateTierButtonLabels() {
  const scale = SCALE_LABELS[createState.scaleType] || SCALE_LABELS.classic;
  const btnS = document.querySelector('.tier-btn-s');
  const btnA = document.querySelector('.tier-btn-a');
  const btnB = document.querySelector('.tier-btn-b');
  const btnC = document.querySelector('.tier-btn-c');
  const btnD = document.querySelector('.tier-btn-d');
  if (btnS) { btnS.textContent = scale.S; btnS.setAttribute('data-rank','S'); }
  if (btnA) { btnA.textContent = scale.A; btnA.setAttribute('data-rank','A'); }
  if (btnB) { btnB.textContent = scale.B; btnB.setAttribute('data-rank','B'); }
  if (btnC) { btnC.textContent = scale.C; btnC.setAttribute('data-rank','C'); }
  if (btnD) { btnD.textContent = scale.D; btnD.setAttribute('data-rank','D'); }
}

function selectTheme(el) {
  document.querySelectorAll('.theme-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  createState.theme = el.dataset.theme;
}
function selectLayout(el) {
  document.querySelectorAll('.layout-card').forEach(c => c.classList.remove('selected'));
  el.classList.add('selected');
  createState.layout = el.dataset.layout;
}
function selectRank(btn) {
  document.querySelectorAll('.tier-btn').forEach(b => b.classList.remove('selected'));
  btn.classList.add('selected');
  const hidden = document.getElementById('rank');
  if (hidden) hidden.value = btn.dataset.rank;
}

function goToStep(step) {
  if (step === 2 && !createState.category) { Toast.error('Choose a category first'); return; }
  if (step === 3) {
    // Sync state to hidden fields
    const catEl = document.getElementById('category');
    const catLabel = document.getElementById('step3Category');
    if (catEl) catEl.value = createState.category;
    if (catLabel) catLabel.textContent = createState.category;

    // Update style badge
    const badge = document.getElementById('styleBadge');
    if (badge) {
      const scale = SCALE_LABELS[createState.scaleType] || SCALE_LABELS.classic;
      const tl = {classic:'Classic',neon:'Neon',pastel:'Pastel',ocean:'Ocean',fire:'Fire',monochrome:'Monochrome'};
      const ll = {rows:'Classic Rows',grid:'Card Grid',compact:'Compact List',detailed:'Detailed Cards'};
      badge.innerHTML = `
        <span class="badge">${scale.icon} ${scale.name}</span>
        <span class="badge">🎨 ${tl[createState.theme]||createState.theme}</span>
        <span class="badge">📐 ${ll[createState.layout]||createState.layout}</span>
        <span class="badge">📂 ${escapeHtml(createState.category)}</span>
      `;
    }
    // Update tier button labels for chosen scale
    updateTierButtonLabels();
  }
  document.querySelectorAll('.create-step').forEach(s => s.classList.remove('active'));
  const target = document.getElementById('step'+step);
  if (target) target.classList.add('active');
  document.querySelectorAll('.step-dot').forEach(d => {
    const ds = parseInt(d.dataset.step);
    d.classList.remove('active','done');
    if (ds === step) d.classList.add('active');
    else if (ds < step) d.classList.add('done');
  });
  window.scrollTo({top:0, behavior:'smooth'});
}

function renderAddedItems() {
  const c = document.getElementById('addedItemsList');
  const w = document.getElementById('addedItems');
  const finishBtns = document.getElementById('finishBtns');
  if (!createState.items.length) {
    if(w) w.style.display='none';
    if(finishBtns) finishBtns.style.display='none';
    return;
  }
  if(w) w.style.display='block';
  if(finishBtns) finishBtns.style.display='flex';

  const scale = SCALE_LABELS[createState.scaleType] || SCALE_LABELS.classic;
  if(c) c.innerHTML = createState.items.map(i => `
    <div class="added-item">
      ${i.image_url ? `<img src="${escapeHtml(i.image_url)}" class="added-item-img" onerror="this.style.display='none'">` : ''}
      <div class="added-rank ${i.rank.toLowerCase()}">${scale[i.rank]||i.rank}</div>
      <div class="added-name">${escapeHtml(i.name)}</div>
    </div>
  `).join('');
}

async function saveTierlist(isDraft) {
  const titleInput = document.getElementById('titleInput');
  const title = titleInput ? titleInput.value.trim() : '';

  const payload = {
    title: title || `${createState.category} Tier List`,
    category: createState.category,
    scale_type: createState.scaleType,
    theme: createState.theme,
    layout: createState.layout,
    picks: createState.items,
    is_draft: isDraft,
  };

  let r;
  if (createState.currentTierlistId) {
    // Update existing draft
    r = await apiRequest('/api/tierlists/' + createState.currentTierlistId, 'PUT', payload);
  } else {
    r = await apiRequest('/api/tierlists', 'POST', payload);
  }

  if (r.ok) {
    const tl = r.data.tierlist || r.data;
    createState.currentTierlistId = tl._id;

    if (!isDraft) {
      Toast.success('Tier list published!');
      setTimeout(() => { window.location.href = '/view/' + tl._id; }, 800);
    } else {
      Toast.success('Draft saved! You can continue editing.');
    }

    // Guest banner
    if (r.data.guest_tierlists && r.data.guest_tierlists >= 1) {
      const banner = document.getElementById('guestBanner');
      if (banner) banner.style.display = 'flex';
    }

    // Update nav stats
    updateUserStats();

    return tl;
  } else {
    Toast.error(r.data.error || 'Failed to save tier list');
    return null;
  }
}

async function updateUserStats() {
  const r = await apiRequest('/api/user/stats');
  if (r.ok) {
    const countEl = document.getElementById('navTierlistCount');
    if (countEl) countEl.textContent = r.data.tierlist_count;
  }
}

// Theme/layout for tierlist view page
function applyTheme(t) { const c=document.getElementById('tierlistContainer'); if(c) c.dataset.theme=t; }
function applyLayout(l) { const c=document.getElementById('tierlistContainer'); if(c) c.dataset.layout=l; }

// ========================================
// Page Init
// ========================================
document.addEventListener('DOMContentLoaded', async () => {

  // ---- Register ----
  const regForm = document.getElementById('registerForm');
  if (regForm) {
    regForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errDiv = document.getElementById('formError');
      const u = document.getElementById('username').value.trim();
      const em = document.getElementById('email').value.trim();
      const pw = document.getElementById('password').value;
      const pc = document.getElementById('passwordConfirm').value;
      if (!u||!em||!pw) { if(errDiv){errDiv.textContent='All fields required.';errDiv.style.display='block';} return; }
      if (pw !== pc) { if(errDiv){errDiv.textContent='Passwords do not match.';errDiv.style.display='block';} return; }
      if (pw.length<6) { if(errDiv){errDiv.textContent='Password must be 6+ characters.';errDiv.style.display='block';} return; }
      const btn = regForm.querySelector('button[type="submit"]');
      btn.disabled = true; btn.textContent = 'Creating...';
      const r = await apiRequest('/register', 'POST', { username:u, email:em, password:pw, password_confirm:pc });
      if (r.ok) {
        Toast.success('Account created!');
        window.location.href = r.data.redirect || '/';
      } else {
        btn.disabled = false; btn.textContent = 'Create Account';
        if(errDiv){errDiv.textContent=r.data.error||'Registration failed.';errDiv.style.display='block';}
      }
    });
  }

  // ---- Login ----
  const logForm = document.getElementById('loginForm');
  if (logForm) {
    logForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errDiv = document.getElementById('formError');
      const u = document.getElementById('username').value.trim();
      const pw = document.getElementById('password').value;
      if (!u||!pw) { if(errDiv){errDiv.textContent='Both fields required.';errDiv.style.display='block';} return; }
      const btn = logForm.querySelector('button[type="submit"]');
      btn.disabled = true; btn.textContent = 'Logging in...';
      const r = await apiRequest('/login', 'POST', { username:u, password:pw });
      if (r.ok) {
        Toast.success('Welcome back!');
        window.location.href = r.data.redirect || '/';
      } else {
        btn.disabled = false; btn.textContent = 'Login';
        if(errDiv){errDiv.textContent=r.data.error||'Login failed.';errDiv.style.display='block';}
      }
    });
  }

  // ---- Edit Profile ----
  const editProfileForm = document.getElementById('editProfileForm');
  if (editProfileForm) {
    // Avatar color preview
    const colorBtns = document.querySelectorAll('.avatar-color-btn');
    colorBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        colorBtns.forEach(b => b.classList.remove('selected'));
        btn.classList.add('selected');
        const hiddenColor = document.getElementById('avatarColor');
        if (hiddenColor) hiddenColor.value = btn.dataset.color;
        const previewAvatar = document.getElementById('editAvatar');
        if (previewAvatar) previewAvatar.style.background = btn.dataset.color;
      });
    });

    editProfileForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const errDiv = document.getElementById('formError');
      const username = document.getElementById('username').value.trim();
      const bio = document.getElementById('bio').value.trim();
      const avatarColor = (document.getElementById('avatarColor')||{}).value || '';
      const btn = editProfileForm.querySelector('button[type="submit"]');
      btn.disabled = true; btn.textContent = 'Saving...';
      const r = await apiRequest('/edit-profile', 'POST', { username, bio, avatar_color: avatarColor });
      if (r.ok) {
        Toast.success('Profile updated!');
        window.location.href = r.data.redirect || '/profile/' + username;
      } else {
        btn.disabled = false; btn.textContent = 'Save Changes';
        if(errDiv){errDiv.textContent=r.data.error||'Update failed.';errDiv.style.display='block';}
      }
    });
  }

  // ---- Create Flow: Add Item (Step 3) ----
  const createForm = document.getElementById('createForm');
  if (createForm) {
    const imgInput = document.getElementById('imageUrl');
    const imgPrev = document.getElementById('imagePreview');
    if (imgInput) imgInput.addEventListener('input', () => {
      const v = imgInput.value.trim();
      if (v && imgPrev) { imgPrev.src=v; imgPrev.style.display='block'; }
      else if (imgPrev) imgPrev.style.display='none';
    });

    createForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const name = (document.getElementById('name')||{}).value?.trim() || '';
      const rank = (document.getElementById('rank')||{}).value || '';
      const reason = (document.getElementById('reason')||{}).value?.trim() || '';
      const imgUrl = (document.getElementById('imageUrl')||{}).value?.trim() || '';
      const tags = (document.getElementById('tags')||{}).value?.trim() || '';

      if (!name || !rank) { Toast.error('Name and rank are required'); return; }

      const btn = createForm.querySelector('button[type="submit"]');
      btn.disabled=true; btn.innerHTML='<span class="loading"></span> Adding...';

      // Add item to local state
      const item = {
        name,
        rank,
        reason,
        image_url: imgUrl,
        tags: tags ? tags.split(',').map(t=>t.trim()).filter(Boolean) : [],
      };
      createState.items.push(item);
      renderAddedItems();

      // Auto-save as draft to MongoDB
      if (!createState.currentTierlistId) {
        await saveTierlist(true);
      } else {
        await apiRequest('/api/tierlists/' + createState.currentTierlistId, 'PUT', {
          picks: createState.items,
          is_draft: true,
        });
      }

      // Reset item fields
      document.getElementById('name').value='';
      document.getElementById('rank').value='';
      document.getElementById('reason').value='';
      document.getElementById('imageUrl').value='';
      document.getElementById('tags').value='';
      if(imgPrev) imgPrev.style.display='none';
      document.querySelectorAll('.tier-btn').forEach(b=>b.classList.remove('selected'));
      document.getElementById('name').focus();

      btn.disabled=false; btn.innerHTML='➕ Add Item';
      Toast.success(`${name} added to ${SCALE_LABELS[createState.scaleType]?.[rank]||rank} tier!`);
    });

    // Finish buttons
    const finishPublishBtn = document.getElementById('finishPublishBtn');
    if (finishPublishBtn) {
      finishPublishBtn.addEventListener('click', async () => {
        if (!createState.items.length) { Toast.error('Add at least one item first'); return; }
        finishPublishBtn.disabled = true;
        finishPublishBtn.textContent = 'Publishing...';
        await saveTierlist(false);
        finishPublishBtn.disabled = false;
        finishPublishBtn.textContent = '✅ Publish Tier List';
      });
    }

    const saveDraftBtn = document.getElementById('saveDraftBtn');
    if (saveDraftBtn) {
      saveDraftBtn.addEventListener('click', async () => {
        saveDraftBtn.disabled = true;
        saveDraftBtn.textContent = 'Saving...';
        await saveTierlist(true);
        saveDraftBtn.disabled = false;
        saveDraftBtn.textContent = '💾 Save Draft';
      });
    }
  }

  // ---- Browse page ----
  const browseList = document.getElementById('browseList');
  if (browseList) {
    const catInput = document.getElementById('filterCategory');
    const searchBtn = document.getElementById('searchBtn');
    async function loadTierlists() {
      const cat = catInput ? catInput.value.trim() : '';
      browseList.innerHTML = '<div style="text-align:center;padding:3rem;"><div class="loading" style="width:2rem;height:2rem;"></div></div>';
      const tierlists = await getTierlists(cat);
      if (!tierlists.length) {
        browseList.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><p>No tier lists found. <a href="/create">Create one!</a></p></div>';
        return;
      }
      browseList.innerHTML = tierlists.map(tl => renderTierlistCard(tl)).join('');
    }
    if (catInput && typeof initialCategory !== 'undefined' && initialCategory) catInput.value = initialCategory;
    if (searchBtn) searchBtn.addEventListener('click', loadTierlists);
    if (catInput) catInput.addEventListener('keypress', e => { if(e.key==='Enter'){e.preventDefault();loadTierlists();} });
    loadTierlists();
  }

  // ---- Tierlist view page ----
  const tlContainer = document.getElementById('tierlistContainer');
  if (tlContainer && typeof tierlists_data !== 'undefined') {
    // Full tierlist data passed from server
    tlContainer.dataset.theme = tierlists_data.theme || 'classic';
    tlContainer.dataset.layout = tierlists_data.layout || 'rows';
    tlContainer.innerHTML = renderTierlist(tierlists_data);
    setupDragAndDrop();
  } else if (tlContainer && typeof initialCategory !== 'undefined') {
    // Legacy: category-based tierlist
    const params = new URLSearchParams(location.search);
    tlContainer.dataset.theme = params.get('theme') || 'classic';
    tlContainer.dataset.layout = params.get('layout') || 'rows';
    const ts = document.getElementById('themeSelect');
    const ls = document.getElementById('layoutSelect');
    if (ts) ts.value = tlContainer.dataset.theme;
    if (ls) ls.value = tlContainer.dataset.layout;
    tlContainer.innerHTML = '<div style="text-align:center;padding:2rem;"><div class="loading" style="width:2rem;height:2rem;"></div></div>';
    const r = await apiRequest('/api/picks?category=' + encodeURIComponent(initialCategory));
    if (!r.ok || !r.data.length) {
      tlContainer.innerHTML = '<div class="empty-state"><p>No picks yet. <a href="/create">Add some!</a></p></div>';
    } else {
      // Build a fake tierlist object for rendering
      const fakeTl = { scale_type: 'classic', picks: r.data };
      tlContainer.innerHTML = renderTierlist(fakeTl);
      setupDragAndDrop();
    }
  }

  // ---- Profile page ----
  const profTierlists = document.getElementById('profileTierlists');
  if (profTierlists && typeof profileUsername !== 'undefined') {
    profTierlists.innerHTML = '<div style="text-align:center;padding:2rem;"><div class="loading" style="width:2rem;height:2rem;"></div></div>';
    const tierlists = await getTierlists('', profileUsername);

    // Stats
    const countEl = document.getElementById('tierlistCount');
    const catCountEl = document.getElementById('categoryCount');
    if (countEl) countEl.textContent = tierlists.length;
    const cats = [...new Set(tierlists.map(t=>t.category))];
    if (catCountEl) catCountEl.textContent = cats.length;

    if (!tierlists.length) {
      profTierlists.innerHTML = '<div class="empty-state"><div class="empty-icon">📋</div><p>No tier lists yet.</p></div>';
    } else {
      profTierlists.innerHTML = tierlists.map(tl => renderTierlistCard(tl)).join('');
    }
  }

  // Profile avatar color
  const avatar = document.getElementById('profileAvatar');
  if (avatar && !avatar.style.background) {
    const colors = ['#6366f1','#ec4899','#14b8a6','#f59e0b','#ef4444','#8b5cf6','#06b6d4'];
    const letter = (avatar.textContent||'A').charCodeAt(0);
    avatar.style.background = colors[letter % colors.length];
  }

  // ---- Dashboard ----
  const recentList = document.getElementById('recentTierlistsList');
  if (recentList) {
    const tierlists = await getTierlists();
    if (!tierlists.length) {
      recentList.innerHTML = '<p style="text-align:center;color:var(--text-secondary);">No tier lists yet. <a href="/seed">Seed community data</a></p>';
    } else {
      recentList.innerHTML = tierlists.slice(0,12).map(tl => renderTierlistCard(tl)).join('');
    }
  }
  const catCards = document.getElementById('categoryCardsList');
  if (catCards) {
    const cats = await getCategories();
    if (!cats.length) catCards.innerHTML = '<p style="text-align:center;color:var(--text-secondary);">No categories yet.</p>';
    else catCards.innerHTML = cats.slice(0,12).map(c => `
      <a href="/browse?category=${encodeURIComponent(c._id)}" class="category-card">
        <div class="category-name">${escapeHtml(c._id)}</div>
        <div class="category-count">${c.count} lists</div>
      </a>
    `).join('');
  }

});
