#!/usr/bin/env python3
"""MIDSA site server: static pages + a small JSON news API (no dependencies).
Run:  MIDSA_ADMIN_PASSWORD='choose-a-password' python3 server.py
Then open http://127.0.0.1:8000  (admin: /admin.html). Put it behind HTTPS before going public."""
import hmac, json, os, re, secrets, threading, time
from datetime import date
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
DB, UP = os.path.join(ROOT, 'news.json'), os.path.join(ROOT, 'uploads')
GENERATED = not os.environ.get('MIDSA_ADMIN_PASSWORD')
PASSWORD = os.environ.get('MIDSA_ADMIN_PASSWORD') or secrets.token_urlsafe(9)
HOST, PORT = os.environ.get('HOST', '127.0.0.1'), int(os.environ.get('PORT', 8000))
lock, sessions = threading.Lock(), {}
SLUG, DATE = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$'), re.compile(r'^\d{4}-\d{2}-\d{2}$')
SIGS = {b'\xff\xd8\xff': 'jpg', b'\x89PNG': 'png', b'GIF8': 'gif'}
BLOCK = {'server.py', 'news.json', 'news.json.tmp'}

def load():
    if not os.path.exists(DB):
        return {'categories': [{'slug': s, 'name': n} for s, n in
                (('announcements', 'Announcements'), ('events', 'Events'), ('community', 'Community'))],
                'articles': []}
    with open(DB, encoding='utf-8') as f:
        return json.load(f)

def save(d):
    with open(DB + '.tmp', 'w', encoding='utf-8') as f:
        json.dump(d, f, ensure_ascii=False, indent=2)
    os.replace(DB + '.tmp', DB)

def live(a):
    return a.get('status') == 'published' and a['publishedAt'] <= date.today().isoformat()

def clean(b, d, old=None):
    title = str(b.get('title', '')).strip()[:200]
    if not title: raise ValueError('Title is required.')
    slug = str(b.get('slug') or '').strip().lower() or re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')[:80]
    if not SLUG.match(slug): raise ValueError('Slug can use lowercase letters, numbers and hyphens only.')
    if any(a['slug'] == slug and a['slug'] != old for a in d['articles']): raise ValueError('That slug is already used.')
    if b.get('category') not in [c['slug'] for c in d['categories']]: raise ValueError('Choose a category.')
    cover = str(b.get('cover') or '').strip()
    if cover and not re.match(r'^(/uploads/[\w.-]+|https://\S+)$', cover):
        raise ValueError('Cover must be an uploaded image or an https:// link.')
    pub = str(b.get('publishedAt') or date.today().isoformat())
    if not DATE.match(pub): raise ValueError('Invalid date.')
    return {'slug': slug, 'title': title, 'category': b['category'], 'cover': cover,
            'featured': bool(b.get('featured')), 'publishedAt': pub,
            'excerpt': str(b.get('excerpt', ''))[:300].strip(), 'author': str(b.get('author', ''))[:100].strip(),
            'body': str(b.get('body', ''))[:100000],
            'status': 'published' if b.get('status') == 'published' else 'draft'}

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k): super().__init__(*a, directory=ROOT, **k)
    def end_headers(self):
        self.send_header('X-Content-Type-Options', 'nosniff'); super().end_headers()
    def list_directory(self, path): self.send_error(404)
    def send_json(self, obj, code=200):
        raw = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Cache-Control', 'no-store'); self.send_header('Content-Length', str(len(raw)))
        self.end_headers(); self.wfile.write(raw)
    def body_json(self):
        n = int(self.headers.get('Content-Length') or 0)
        if n > 1_000_000: raise ValueError('Request too large.')
        return json.loads(self.rfile.read(n) or b'{}')
    def authed(self):
        return sessions.get(self.headers.get('X-Admin-Token', ''), 0) > time.time()

    def route(self, m):
        p = urlparse(self.path).path
        if not p.startswith('/api/'): return False
        try: self.api(m, p)
        except ValueError as e: self.send_json({'error': str(e)}, 400)
        except Exception: self.send_json({'error': 'Server error.'}, 500)
        return True

    def api(self, m, p):
        if m == 'GET' and p == '/api/news':
            with lock: d = load()
            return self.send_json({'categories': d['categories'],
                'articles': [{k: v for k, v in a.items() if k != 'status'} for a in d['articles'] if live(a)]})
        if m == 'POST' and p == '/api/login':
            ok = hmac.compare_digest(str(self.body_json().get('password', '')).encode(), PASSWORD.encode())
            if not ok: time.sleep(1); return self.send_json({'error': 'Wrong password.'}, 401)
            t = secrets.token_urlsafe(24); sessions[t] = time.time() + 8 * 3600
            return self.send_json({'token': t})
        if not p.startswith('/api/admin/'): return self.send_json({'error': 'Not found.'}, 404)
        if not self.authed(): return self.send_json({'error': 'Please sign in again.'}, 401)
        if m == 'GET' and p == '/api/admin/news':
            with lock: return self.send_json(load())
        if m == 'POST' and p == '/api/admin/upload':
            n = int(self.headers.get('Content-Length') or 0)
            if not 0 < n <= 5_000_000: raise ValueError('Images must be under 5 MB.')
            raw = self.rfile.read(n)
            ext = next((e for s, e in SIGS.items() if raw.startswith(s)), None) or \
                  ('webp' if raw[:4] == b'RIFF' and raw[8:12] == b'WEBP' else None)
            if not ext: raise ValueError('Use a JPG, PNG, GIF or WebP image.')
            os.makedirs(UP, exist_ok=True); name = secrets.token_hex(8) + '.' + ext
            with open(os.path.join(UP, name), 'wb') as f: f.write(raw)
            return self.send_json({'url': '/uploads/' + name})
        if m == 'POST' and p == '/api/admin/categories':
            name = str(self.body_json().get('name', '')).strip()[:40]
            slug = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
            if not slug: raise ValueError('Category name is required.')
            with lock:
                d = load()
                if slug not in [c['slug'] for c in d['categories']]:
                    d['categories'].append({'slug': slug, 'name': name}); save(d)
            return self.send_json({'slug': slug})
        mm = re.match(r'^/api/admin/articles(?:/([a-z0-9-]+))?$', p)
        if not mm: return self.send_json({'error': 'Not found.'}, 404)
        slug = mm.group(1)
        with lock:
            d = load(); a = None
            if m == 'POST' and not slug:
                a = clean(self.body_json(), d); d['articles'].append(a)
            elif m in ('PUT', 'DELETE') and slug:
                i = next((i for i, x in enumerate(d['articles']) if x['slug'] == slug), None)
                if i is None: return self.send_json({'error': 'Article not found.'}, 404)
                if m == 'DELETE': d['articles'].pop(i)
                else: a = clean(self.body_json(), d, slug); d['articles'][i] = a
            else: return self.send_json({'error': 'Not found.'}, 404)
            save(d)
        return self.send_json({'article': a} if a else {'ok': True})

    def do_GET(self):
        if self.route('GET'): return
        path = urlparse(self.path).path
        if os.path.basename(path) in BLOCK or '/.' in path: return self.send_error(404)
        if path == '/' and not os.path.exists(os.path.join(ROOT, 'index.html')): self.path = '/midsa.html'
        super().do_GET()
    def do_POST(self):
        if not self.route('POST'): self.send_error(404)
    def do_PUT(self):
        if not self.route('PUT'): self.send_error(404)
    def do_DELETE(self):
        if not self.route('DELETE'): self.send_error(404)

if __name__ == '__main__':
    print(f'MIDSA server: http://{HOST}:{PORT}   admin: http://{HOST}:{PORT}/admin.html')
    if GENERATED: print('No MIDSA_ADMIN_PASSWORD set. Temporary admin password:', PASSWORD)
    ThreadingHTTPServer((HOST, PORT), H).serve_forever()
