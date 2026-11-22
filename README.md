# dasig.MIDSA website

The official website for the MSU-IIT DOST Scholars' Association (MIDSA): a home page, a news page, individual article pages, and an admin dashboard where editors add and manage news.

It runs on plain HTML, CSS and JavaScript, with a small Python server (standard library only, no installs) that stores the articles.

## Files

| File | Purpose |
|---|---|
| `midsa.html` | Home page (scroll-animated header, featured news, programs, contact) |
| `news.html` | All news, with category filters and search |
| `article.html` | A single story, opened as `article.html?slug=your-story` |
| `admin.html` | Editor dashboard (sign in, create, edit, publish, delete) |
| `server.py` | Serves the site and the news API; saves articles to `news.json` |
| `site.css` | Shared styles for the news, article and admin pages |
| `midsa-news.js` | Shared code: loading news, safe text display, story formatting |
| `news-data.js` | Three sample stories, used only when pages are opened straight from disk |

These files are created while the site runs. Don't upload or edit them by hand:

| Created | Purpose |
|---|---|
| `news.json` | All articles and categories |
| `uploads/` | Cover images uploaded through the dashboard |

## Quick start

1. Put all the files in one folder.
2. Start the server:

   ```bash
   MIDSA_ADMIN_PASSWORD='choose-a-strong-password' python3 server.py
   ```

   On Windows PowerShell:

   ```powershell
   $env:MIDSA_ADMIN_PASSWORD='choose-a-strong-password'; python server.py
   ```

3. Open <http://127.0.0.1:8000> for the site and <http://127.0.0.1:8000/admin.html> for the editor.

If you don't set `MIDSA_ADMIN_PASSWORD`, the server prints a temporary random password in the terminal. It changes every time the server restarts.

### Settings

| Variable | Default | Meaning |
|---|---|---|
| `MIDSA_ADMIN_PASSWORD` | random, printed at start | The editors' shared password |
| `PORT` | `8000` | Port to listen on |
| `HOST` | `127.0.0.1` | Address to listen on. Leave as is unless you're running behind a reverse proxy on the same machine |

## Publishing a story

1. Open `/admin.html` and sign in.
2. Click **New article**.
3. Fill in the form:
   - **Title:** required.
   - **Slug:** the web address of the story. It's filled in from the title and you can change it. Use lowercase letters, numbers and hyphens, and keep it unique.
   - **Category:** pick one, or click **Add** to create a new one.
   - **Publish date:** a future date schedules the story. It stays hidden until that day.
   - **Status:** **Draft** is never shown publicly. **Published** goes live (on or after the publish date).
   - **Summary:** shown on news cards, up to 300 characters.
   - **Cover image:** paste an `https://` link or upload a JPG, PNG, GIF or WebP file (up to 5 MB).
   - **Feature on the home page:** featured stories are shown first in the home page's Featured section. The home page shows the top three.
4. Write the story in the **Story** box. The preview updates as you type.
5. Click **Save article**.

### Story formatting

| You type | You get |
|---|---|
| A blank line between blocks | A new paragraph |
| `## Subheading` on its own line | A subheading |
| `**bold**` | **bold** |

Example:

```
Orientation week starts on Monday.

## What to bring

Bring your **scholar ID** and a notebook.
```

Anything else is shown as plain text. Pasted HTML or scripts are displayed as text and never run.

## How it works

- Pages load stories from `/api/news`, which returns only published stories dated today or earlier.
- If a page is opened straight from disk (`file://`), it falls back to the sample stories in `news-data.js`. The admin can't be used this way, because it needs the server.
- `/` opens `index.html` if it exists, otherwise `midsa.html`.

### API

| Method and path | Access | Purpose |
|---|---|---|
| `GET /api/news` | public | Published stories and categories |
| `POST /api/login` | public | Exchange the password for a session token |
| `GET /api/admin/news` | editor | Everything, including drafts |
| `POST /api/admin/articles` | editor | Create a story |
| `PUT /api/admin/articles/<slug>` | editor | Update a story |
| `DELETE /api/admin/articles/<slug>` | editor | Delete a story |
| `POST /api/admin/categories` | editor | Add a category |
| `POST /api/admin/upload` | editor | Upload a cover image |

Editor routes need an `X-Admin-Token` header, which the dashboard sets after sign-in.

## Security notes

- **Use HTTPS in production.** The password and session token are sent with each request, so run the server behind a reverse proxy such as Caddy or nginx that provides HTTPS. Only set `HOST=0.0.0.0` when something like that sits in front.
- **One shared password.** Everyone who knows it has full editor access, and there are no separate accounts or edit history. Change the password by restarting with a new value.
- **Sessions last 8 hours** and are kept in memory, so a server restart signs everyone out.
- Failed sign-ins are delayed by one second. There's no stronger lockout, so choose a long password.
- Uploads accept only JPG, PNG, GIF and WebP, checked by file contents and not by name. SVG is not allowed.
- `server.py` and `news.json` can't be downloaded through the site.

## Backups

Everything the editors create lives in two places: `news.json` and the `uploads/` folder. Copy both to back up the site, and put them back to restore it.

## Customizing

- **Brand font:** Proxima Nova is licensed, so it isn't included. Add your own `@font-face` rules or an Adobe Fonts kit for "Proxima Nova". Until then the site falls back to Montserrat. Body text uses Manrope (loaded from Google Fonts).
- **Logo:** The grey square next to "dasig.MIDSA" is a placeholder in `midsa.html`, `news.html`, `article.html` and `admin.html`. Replace the `<svg>` in each with the official logo.
- **Colors:** Change the values at the top of `site.css` (news, article and admin pages) and in the `:root` block in `midsa.html`. The main color is `#004ACD`.
- **Social links:** In `midsa.html` the Facebook, Instagram and X links currently point to `#`.
- **Footer text:** The home page footer still says "Sample page."
- **Home page photo:** The arch-shaped box in the hero says "Add a photo here". Replace it with a real image.
- **Nav links:** The nav on the news, article and admin pages points to `midsa.html`. If you rename it to `index.html`, update those links.

## Troubleshooting

| Problem | Fix |
|---|---|
| "News could not be loaded" | Start `server.py` and open the site through it (`http://127.0.0.1:8000`), not by double-clicking the HTML files |
| Admin says "Run server.py" | Same as above |
| "Wrong password" | Check `MIDSA_ADMIN_PASSWORD`. If you didn't set one, use the password printed when the server started |
| Signed out unexpectedly | The session expired (8 hours) or the server restarted. Sign in again |
| A story doesn't show on the site | It's a draft, or its publish date is in the future |
| "That slug is already used" | Change the slug so it's unique |
| Fonts look different from the design | Proxima Nova isn't installed. See Customizing above |

## Known limits

- No pagination on the news page. It's fine for dozens of stories but will get long with hundreds.
- No rich-text editor, image gallery inside stories, or comments.
- One shared editor password, with no roles.
- The server is Python's built-in one. It's suitable for a small organization site, not heavy traffic.
