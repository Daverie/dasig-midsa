// Shared helpers for news.html, article.html and admin.html
const esc = s => String(s ?? '').replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
const fmtDate = iso => new Date(iso + 'T00:00:00').toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' });

// Article body: blank line = new paragraph, "## " = subheading, **bold**. Text is escaped first, so it is safe.
function renderBody(text) {
  return esc(text).split(/\n{2,}/).map(b => {
    b = b.trim();
    if (!b) return '';
    if (b.startsWith('## ')) return '<h2>' + b.slice(3) + '</h2>';
    return '<p>' + b.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br>') + '</p>';
  }).join('');
}

// Live API when served by server.py; MIDSA_NEWS sample data when opened straight from disk.
async function loadNews() {
  try { const r = await fetch('/api/news'); if (!r.ok) throw 0; return await r.json(); }
  catch (e) { return location.protocol === 'file:' && typeof MIDSA_NEWS !== 'undefined' ? MIDSA_NEWS : null; }
}

const cardHTML = (a, cats) => `
  <a class="card" href="article.html?slug=${encodeURIComponent(a.slug)}">
    ${a.cover ? `<img class="ph" src="${esc(a.cover)}" alt="" loading="lazy">` : '<div class="ph" aria-hidden="true"></div>'}
    <div class="card-body">
      <div class="k">${esc(cats[a.category] || '')}</div>
      <h3>${esc(a.title)}</h3>
      ${a.excerpt ? `<p>${esc(a.excerpt)}</p>` : ''}
      <time datetime="${esc(a.publishedAt)}">${fmtDate(a.publishedAt)}</time>
    </div>
  </a>`;
