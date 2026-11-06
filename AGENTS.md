# UI screenshots for pull requests

Every PR that changes UI must include linked **before and after screenshots in
the PR description**, not just in a comment or agent response. Capture before
from current `origin/main` and after from the PR branch. Use synthetic database
data, never production listening history or credentials.

New screenshots must never enter the `main` tree or the final PR diff. They may
exist in intermediate commits. Do not copy the existing tracked screenshot
files as a pattern for new PRs.

## 1. Prepare a disposable, populated database

Use the repository's Python requirements, client dependencies, and PostgreSQL.
Run from the repository root. Check for installed prerequisites first; install
missing dependencies rather than assuming a previous agent's environment exists.
Use Node 20 as specified in `README.md`; newer Node versions can break
`typed-css-modules`. Run `npm ci` at the root for the screenshot harness and
`cd client && npm ci` for the frontend. Install the screenshot browser with
`npx playwright install chromium` (add `--with-deps` if system libraries are missing).

Create synthetic data tailored to the affected UI in each session. Do not retain
seed scripts in the repository or final PR diff; keep any temporary SQL in the
session artifact directory.

Use a **dedicated local** database named `spotifystats_screenshots`. Verify the
connection targets that database on localhost before any schema or seed changes.
Never point it at a remote host, mirror production, truncate an existing database,
or change another user's PostgreSQL role/password.

For a fresh local PostgreSQL installation, this is a working setup (the password
is deliberately public, throwaway, and local-only):

```bash
# Start your local PostgreSQL service first. On Debian/Ubuntu, inspect
# pg_lsclusters and start the installed cluster with sudo pg_ctlcluster.
sudo -u postgres psql -v ON_ERROR_STOP=1 \
  -c "CREATE ROLE screenshot_demo LOGIN PASSWORD 'screenshot_demo';"
sudo -u postgres createdb -O screenshot_demo spotifystats_screenshots

export DATABASE_URL='postgresql://screenshot_demo:screenshot_demo@127.0.0.1:5432/spotifystats_screenshots'
psql -X "$DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f data/sql/schema.sql
```

If that role/database already exists, inspect ownership and contents before
reusing it; do not drop or overwrite it.

Prepare the data before starting the app:

1. Read `data/sql/schema.sql`, the migration list in
   `data/sql/migrations/migrations.py`, and the queries behind the affected view.
   Bootstrap a fresh database from the current schema rather than replaying
   historical migrations. Record the corresponding latest migration version in
   the empty `version` table (currently `v025`) so startup does not replay obsolete
   migrations. Do not advance the version of an existing database without applying
   its required schema changes.
2. Write temporary SQL for the particular use case. Start a transaction with a
   guard that raises an exception unless `current_database()` equals
   `spotifystats_screenshots`, and execute with `psql -X "$DATABASE_URL"
   -v ON_ERROR_STOP=1 -f /absolute/session/path/seed.sql`.
3. Use fictional names and unique synthetic URIs. Populate the join tables as
   well as entities: `album_artist`, `track_artist` (with `artist_index`),
   `artist_genre`, `playlist_track`, and any likes, labels, or provider metadata
   needed for the view. Set both `name` and `short_name` on albums and tracks.
   Use inline SVG data URLs for artwork to avoid remote image dependencies.
4. Insert `track_stream` rows with varied counts across fixed dates covering the
   selected filters and enough months to populate charts. Add producer credits,
   videos, or other provider-specific records only when the affected UI needs
   them. Use conflict handling or existence checks so rerunning the seed does
   not duplicate rows.
5. Confirm entity, relationship, and stream counts with SQL and inspect the
   actual API payloads. An empty chart or missing relationship is not a populated
   screenshot. Keep the same data unchanged for both captures.

The workflow rehearsal used 6 fictional artists, 12 albums, 48 tracks, 3 playlists,
producer credits, genres, labels, likes, and 7,488 streams across 2024-2025. These
are examples, not required counts; generate what the current change needs.

Both standard `postgresql://` and legacy `postgres://` URLs are supported.
When capturing an older main revision that predates the scheme fix, use
`postgres://` for the baseline backend. Python's direct connection requires SSL,
so the local PostgreSQL server must support SSL (the Debian cluster does by
default). Prefer `DATABASE_URL` over `POSTGRES_PORT`, because the SQLAlchemy
fallback currently ignores that port.

Export harmless placeholder Spotify configuration in each backend shell:

```bash
export SPOTIFY_CLIENT_ID=00000000000000000000000000000000
export SPOTIFY_CLIENT_SECRET=00000000000000000000000000000000
```

No Spotify authorization or sync worker is needed for local database reads.
**The Spotify auth banner must not appear in screenshots.** Use the capture
harness below: it mocks only `/api/spotify-auth/status` to return `{"status":"ok"}`
inside its isolated browser context. This changes neither the app code nor the
backend's real auth status, and cannot disable production auth checks. Do not
fabricate an auth cache or hide other application errors to improve a capture.
Generate additional synthetic data when the affected UI needs it; do not commit
the temporary seed SQL.

## 2. Capture the real main baseline

Commit or otherwise safely preserve current work before switching branches.
Fetch `origin/main`, record its SHA, and run that exact revision. For example,
from a clean working tree:

```bash
# Use the actual absolute session artifact directory supplied by the environment.
ARTIFACTS=/absolute/session/files/pr-screenshots
mkdir -p "$ARTIFACTS"
# Preserve the browser-only harness if the baseline predates this file.
cp script/capture-screenshot.mjs "$ARTIFACTS/capture-screenshot.mjs"
PR_BRANCH=$(git branch --show-current)
git fetch origin main
BEFORE_SHA=$(git rev-parse origin/main)
git switch --detach "$BEFORE_SHA"
```

Do not reset a dirty worktree or substitute the PR version, production site, or
mocked UI/listening-data responses for the before capture. The auth-status-only
mock described below is intentional and must be applied equally to both captures.
A separate worktree is also acceptable,
but both servers must run from that worktree, not the PR checkout. Seed the
database before switching to main; the temporary seed SQL need not be present
in the main checkout to run the unchanged baseline application.

With the same `DATABASE_URL` and placeholder Spotify variables available to the
backend, start the servers in separate attached sessions:

```bash
./script/dev-server
./script/dev-client
```

Vite's first load can take longer while optimizing the large icon dependency;
the harness allows two minutes for navigation. If Vite reports `EMFILE` or
intermittent missing-package/CSS errors, inspect its log and the shell's
`ulimit -n`. Stop Vite and restart it from a shell with `ulimit -n 8192` (within
the system's hard limit). Do not repeatedly capture a blank/error page.

Verify both are responsive, not merely that the processes started:

```bash
curl --fail --silent --show-error 'http://127.0.0.1:5000/api/tracks?limit=1'
curl --fail --silent --show-error http://127.0.0.1:5173/ >/dev/null
```

Use the Playwright capture harness from the repository root:

```bash
node "$ARTIFACTS/capture-screenshot.mjs" \
  --url 'http://127.0.0.1:5173/?section=tracks' \
  --wait-for 'Track streams by month' \
  --output "$ARTIFACTS/before.png"
```

It uses **390 x 844 CSS pixels**, a fresh context without persisted React Query
data, a browser-only auth-status mock, loaded fonts/images, a visible-text
readiness check, and disabled screenshot animations. It fails on HTTP resource
errors, uncaught page errors, missing/broken images, or a visible auth banner.
The browser is closed after capture. Use `--full-page` only when needed.

Playwright MCP (`.vscode/mcp.json`) is useful for exploring the UI and choosing a
view, but its available tools do not expose request routing for the auth mock.
Both the harness and MCP should use only `localhost` or `127.0.0.1`. Capture the
actual affected view; `/?section=tracks` is a populated smoke-test page, not a
substitute for the changed UI. For interaction-specific states, extend the
harness with the required Playwright actions; do not hide the banner with CSS.

Before **each** capture:

1. Clear localStorage and sessionStorage on the app origin, then navigate again.
   React Query persists responses for an hour, so a reload alone can show stale
   data from the other branch. Use the same hostname and port for both captures.
2. Select identical URL filters, section, sort order, theme, scroll position,
   viewport, and interaction state. For date-filtered views, use the fixed fixture
   dates rather than "this year." Dismiss any chart tooltip identically.
3. Wait for the expected entity names/counts, loaded charts, fonts, and images;
   wait for animation/layout to settle. Check API responses and browser errors.
   An empty page, loading skeleton, failed request, or broken image is not evidence.
4. Save with an **absolute** filename in the session artifact directory and the
   same `fullPage` setting for both images. Inspect each image using the image
   viewing tool. A mobile viewport capture is usually clearer than an excessively
   tall full-page capture. The harness covers cache isolation and image loading;
   verify that the final chart and intended UI state are actually visible.

Record the before SHA, URL, viewport, and fixture details for the PR body.

## 3. Capture the PR version

Stop both baseline servers (including Flask's reloader children) before switching
back to `"$PR_BRANCH"`. Restart both from the PR branch with the same database and
environment; Python modules are not refreshed just because Git switched files.
Confirm the branch/SHA and server responses, then repeat the cache reset and
capture steps above for the after image.

```bash
node "$ARTIFACTS/capture-screenshot.mjs" \
  --url 'http://127.0.0.1:5173/?section=tracks' \
  --wait-for 'Track streams by month' \
  --output "$ARTIFACTS/after.png"
```

Keep the database unchanged between captures. If incompatible migrations require
separate databases, initialize equivalent fixtures for each revision and describe
the difference. Never run PR migrations against the only copy of the before data
before capturing the baseline.

## 4. Publish durable images without adding them to the final diff

The following Git-history method works with this session's GitHub App token and
does not require GitHub's user-attachments upload API:

1. On the PR branch, copy only this PR's before/after PNGs from the session
   directory into a **new uniquely named** directory, such as
   `docs/screenshots/<task-name>/`. Never overwrite screenshots inherited from main.
2. Commit those files, record the **full screenshot commit SHA**, and push it.
   Also retain that commit on a dedicated `screenshots/<task-name>` branch so
   deleting or squash-merging the PR branch cannot orphan the image host.
3. Remove only those new files with `git rm`, commit the removal, and push again.
   Keep both commits in branch history; do not amend, squash, or force-push them
   away while the PR relies on their URLs.

Example (replace the paths with the actual captured files):

```bash
mkdir -p docs/screenshots/my-ui-task
cp /absolute/session/path/before.png docs/screenshots/my-ui-task/before.png
cp /absolute/session/path/after.png docs/screenshots/my-ui-task/after.png
git add docs/screenshots/my-ui-task/before.png docs/screenshots/my-ui-task/after.png
git commit -m "Capture before and after UI screenshots"
SCREENSHOT_SHA=$(git rev-parse HEAD)
git push -u origin HEAD
git push origin "$SCREENSHOT_SHA:refs/heads/screenshots/my-ui-task"
git rm docs/screenshots/my-ui-task/before.png docs/screenshots/my-ui-task/after.png
git commit -m "Keep screenshot assets out of the final PR diff"
git push
```

Follow any PR template. Put the images in the **description** using HTML `<img>`
tags and raw URLs pinned to `SCREENSHOT_SHA`, **not** to the latest branch SHA,
where the images have been removed. Include descriptive alt text and show them
at mobile width:

```html
### Before (main at BEFORE_SHA)
<img src="https://raw.githubusercontent.com/jbrown1618/spotify-stats/SCREENSHOT_SHA/docs/screenshots/my-ui-task/before.png" alt="Before: affected view on main" width="390">

### After (PR at AFTER_SHA)
<img src="https://raw.githubusercontent.com/jbrown1618/spotify-stats/SCREENSHOT_SHA/docs/screenshots/my-ui-task/after.png" alt="After: affected view on the PR branch" width="390">
```

Use HTML rather than Markdown image syntax for these raw GitHub URLs. The
screenshot commit is only the image host: `BEFORE_SHA` and `AFTER_SHA` must describe
the application revisions actually running during capture.

GitHub user attachments are an alternative **only if upload succeeds and is
verified**. `gh --attach` requires gh >= 2.99 and a supported user credential;
GitHub App installation tokens can fail with `unsupported authentication type`.
Do not waste repeated upload attempts with the same token or claim an attachment
exists because a local file does. Fall back to the Git-history method above.

## 5. Verify the published result

- Read the description back with `gh pr view <number> --json body -q .body` and
  confirm both hosted URLs are present, with no local paths or placeholder SHAs.
- Fetch **each exact image URL** with `curl --fail --location`, check the response
  is an image, and inspect the downloaded image if it has not already been seen.
  A local screenshot or successful push alone does not prove a usable PR image.
- Check `git diff --name-status origin/main...HEAD -- docs/screenshots screenshots`
  is empty for your new assets, and check `gh pr diff <number> --name-only` too.
  The files must also be absent from the branch tip, not just ignored by Git.
- Preserve the screenshot-host commit on its retained non-main screenshot
  branch, including after merge. Do not delete that branch while descriptions
  rely on its assets; recheck URLs after any history rewrite.

Documentation-only PRs do not normally need screenshots. A workflow-rehearsal PR
may include an unchanged before/after pair explicitly labeled as such; do not
invent a visual change merely to demonstrate this process.
