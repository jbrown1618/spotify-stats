# UI screenshots for pull requests

Every UI-changing PR must link **before and after mobile screenshots in its
description**: before from current `origin/main`, after from the PR branch.
Use synthetic data only. Screenshots may live in intermediate commits, but
**must not remain in the branch tip, final PR diff, or main tree**.
Documentation-only PRs normally need no screenshots.

## 1. Prepare local mock data

Check prerequisites: PostgreSQL, Python dependencies in `venv`, and Node 20
(`typed-css-modules` can fail on newer Node). Install missing dependencies;
run `npm ci` at the root and in `client`, and `npx playwright install chromium`
(`--with-deps` if browser system libraries are missing).

Use only a dedicated localhost database named `spotifystats_screenshots`.
Inspect any existing role/database before reuse; never drop/truncate it, change
another user's password, mirror production, or connect to a remote database.
For a fresh local installation, start PostgreSQL, then:

```bash
# Public, throwaway local credentials.
sudo -u postgres psql -v ON_ERROR_STOP=1 \
  -c "CREATE ROLE screenshot_demo LOGIN PASSWORD 'screenshot_demo';"
sudo -u postgres createdb -O screenshot_demo spotifystats_screenshots
export DATABASE_URL='postgresql://screenshot_demo:screenshot_demo@127.0.0.1:5432/spotifystats_screenshots'
psql -X "$DATABASE_URL" -v ON_ERROR_STOP=1 -f data/sql/schema.sql
```

Verify the host/database before schema or seed changes. Read the schema,
`data/sql/migrations/migrations.py`, and queries behind the affected view.
For a fresh schema, record its corresponding latest migration in the empty
`version` table (currently `v025`) to avoid replaying obsolete migrations.
Do not advance an existing database's version without applying required changes.

Generate use-case-specific seed SQL **in the session artifact directory, never
the repository**. Begin a transaction with a guard that raises unless
`current_database()` equals `spotifystats_screenshots`; execute with
`psql -X "$DATABASE_URL" -v ON_ERROR_STOP=1 -f /absolute/session/path/seed.sql`.
Use fictional names, unique URIs, inline SVG artwork, and repeat-safe inserts.
Populate entities and relevant joins (`album_artist`, `track_artist` with
`artist_index`, `artist_genre`, `playlist_track`), both `name` and `short_name`,
and any likes, labels, or provider metadata needed. Add varied `track_stream`
counts across fixed dates/months covering the filters. Check SQL counts and
actual API payloads: empty charts do not demonstrate populated UI.

Keep data unchanged between captures. If migrations are incompatible, use
equivalent fixtures in separate databases and explain the difference.
Both PostgreSQL URL schemes work; older main revisions may require `postgres://`.
Local PostgreSQL needs SSL for direct Python connections. Use `DATABASE_URL`;
the SQLAlchemy fallback ignores `POSTGRES_PORT`.

## 2. Capture main, then the PR branch

Preserve current work before switching. From a clean tree, save the harness
outside the checkout so it also works when main predates it:

```bash
ARTIFACTS=/absolute/session/files/pr-screenshots
mkdir -p "$ARTIFACTS"
cp script/capture-screenshot.mjs "$ARTIFACTS/capture-screenshot.mjs"
PR_BRANCH=$(git branch --show-current)
git fetch origin main
BEFORE_SHA=$(git rev-parse origin/main)
git switch --detach "$BEFORE_SHA"
```

Run both servers from this exact revision, in separate attached sessions.
A separate worktree is also valid if both servers run from it.
Export the same database URL and harmless Spotify placeholders in the backend shell:

```bash
export SPOTIFY_CLIENT_ID=00000000000000000000000000000000
export SPOTIFY_CLIENT_SECRET=00000000000000000000000000000000
./script/dev-server
# Separate shell:
./script/dev-client
```

Confirm responses with `curl --fail` against
`http://127.0.0.1:5000/api/tracks?limit=1` and `http://127.0.0.1:5173/`.
If Vite reports `EMFILE` or intermittent missing-package/CSS errors, inspect logs
and restart with `ulimit -n 8192`, within the hard limit.

From the repository root, capture the **actual affected view**:

```bash
node "$ARTIFACTS/capture-screenshot.mjs" \
  --url 'http://127.0.0.1:5173/?section=tracks' \
  --wait-for 'Track streams by month' \
  --output "$ARTIFACTS/before.png"
```

The tracks URL is an example, not a substitute for the changed UI. The harness
uses a fresh **390 x 844** browser context, waits for text/fonts/images, disables
animations, and rejects resource/page errors. Its browser-only mock returns
`{"status":"ok"}` solely for `/api/spotify-auth/status`, so **the auth banner must
not appear**. No real Spotify authorization, fabricated cache, or app auth bypass
is needed. Playwright MCP can explore localhost but cannot configure this mock.

Stop both servers, including Flask reloader children, before
`git switch "$PR_BRANCH"`. Restart both with the same environment/database,
record `AFTER_SHA`, and repeat the command with `--output "$ARTIFACTS/after.png"`.
Switching files alone does not refresh Python modules.

Match URL filters, fixed dates, sort, theme, scroll, tooltip/interaction state,
and `--full-page` setting. Fresh contexts prevent persisted React Query data
leaking between revisions; if using another browser, clear local/session storage
and navigate again. Extend harness actions for interaction-specific captures.
Inspect both images for loaded content, charts, artwork, and no banner/errors.
Record application SHAs, URL, viewport, and fixture details for the PR.

## 3. Publish images without a final screenshot diff

On the PR branch, use a unique directory; never overwrite inherited screenshots.
Commit/push the images, retain their commit on a non-main screenshot branch,
then remove them in another commit:

```bash
mkdir -p docs/screenshots/my-ui-task
cp "$ARTIFACTS/before.png" docs/screenshots/my-ui-task/before.png
cp "$ARTIFACTS/after.png" docs/screenshots/my-ui-task/after.png
git add docs/screenshots/my-ui-task
git commit -m "Capture before and after UI screenshots"
SCREENSHOT_SHA=$(git rev-parse HEAD)
git push -u origin HEAD
git push origin "$SCREENSHOT_SHA:refs/heads/screenshots/my-ui-task"
git rm docs/screenshots/my-ui-task/before.png docs/screenshots/my-ui-task/after.png
git commit -m "Keep screenshot assets out of the final PR diff"
git push
```

Follow the PR template. Put both images in the **description** using HTML,
pinned to the full screenshot-host SHA, not the tip where images were removed:

```html
### Before (main at BEFORE_SHA)
<img src="https://raw.githubusercontent.com/jbrown1618/spotify-stats/SCREENSHOT_SHA/docs/screenshots/my-ui-task/before.png" alt="Before: affected view on main" width="390">

### After (PR at AFTER_SHA)
<img src="https://raw.githubusercontent.com/jbrown1618/spotify-stats/SCREENSHOT_SHA/docs/screenshots/my-ui-task/after.png" alt="After: affected view on PR branch" width="390">
```

Application SHAs identify the revisions actually captured, not the image host.
Keep the screenshot branch after merge; do not rewrite away the host commit.
User attachments are an alternative only after successful upload/verification:
`gh --attach` needs gh >= 2.99 and may reject GitHub App tokens. On rejection,
use Git history rather than retrying the same credentials.

## 4. Verify before finishing

Read back `gh pr view <number> --json body -q .body`: both hosted URLs must be
present, with no local paths/placeholders. Fetch each exact URL using
`curl --fail --location` and verify image content. Check
`git diff --name-status origin/main...HEAD -- docs/screenshots screenshots`
and `gh pr diff <number> --name-only`: no new screenshots may remain in the diff
or branch tip. Recheck URLs after history changes. A workflow rehearsal may show
an unchanged pair, explicitly labeled; never invent a visual change.
