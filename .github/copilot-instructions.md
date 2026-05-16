# Copilot Instructions

## Build, Lint, and Run

### Development servers

```bash
# Flask backend (port 5000) - requires venv
./script/dev-server

# Vite frontend (port 5173) - proxies /api to Flask
./script/dev-client
```

### Build and lint

```bash
# Full client build (from repo root)
npm run build

# Client lint only
cd client && npx eslint .

# Lint a single file
cd client && npx eslint src/path/to/File.tsx
```

### No test suite

There is no automated test suite. Verify changes manually against the running dev servers.

## Architecture

This is a single-page app for visualizing personal Spotify listening data. The backend is a Flask API over PostgreSQL; the frontend is a React SPA using Vite.

### Request flow

1. **Frontend filter state** lives in React context (`FiltersProvider`) and is synced to the URL query string via `history.pushState`. Navigating to a detail page (e.g. clicking an artist) sets a filter like `?artists=["spotify:artist:..."]`.
2. **API client** (`client/src/api.ts`) serializes filters to query params. Arrays are JSON-encoded strings. A thin `sendRequest` wrapper around `fetch` handles all requests.
3. **React Query hooks** (`client/src/useApi.ts`) wrap API calls. Entity list hooks use `useInfiniteQuery`; streaming/chart hooks use `useQuery`. Query keys include serialized filters so data refetches when filters change. Stale/GC time is 1 hour. Responses are persisted to localStorage.
4. **Flask routes** (`app/app.py`) parse query params via `parse_request_args()`. Many endpoints branch: if specific entity URIs are present, they run direct SQL; otherwise they use the filtered path.
5. **Filtered queries** use a temp table pattern: `filtered_connection()` creates a `matching_track_uris` temp table scoped to the active transaction, then downstream queries join against it.
6. **Route payload functions** live in `routes/*.py` (e.g., `routes/artists.py`). They handle pagination, sorting, and data shaping. These are imported and called directly from `app/app.py` — no blueprints.
7. **Ranking/streaming** transformations live in `utils/ranking.py`. They return nested dicts shaped as `{"streams": {...}, "metadata": {...}}` for chart endpoints.

### Database

PostgreSQL accessed via two patterns:
- **psycopg2** directly (`data/provider.py`'s `get_connection()`) for cursor-based queries
- **SQLAlchemy** (`get_engine()`) for pandas `read_sql_query` and the filtered connection pattern

Migrations run automatically at app startup via `perform_all_migrations()`.

### Frontend patterns

- **No router** — the app is a single page. "Navigation" is done by setting filters in context, which conditionally renders detail components (e.g., `filters.artists?.length === 1` renders `ArtistDetails`).
- **CSS Modules** with generated `.d.ts` type declarations (via `typed-css-modules`). Import as `import styles from "./Foo.module.css"`.
- **Mantine UI** for components and charts (`@mantine/core`, `@mantine/charts`).
- **TanStack React Query** with localStorage persistence for caching.

## Key Conventions

### SQL queries

- Stored as `.sql` files in `data/sql/queries/`, loaded by name via `query_text("filename_without_extension")`.
- Two param styles depending on caller:
  - `:named` params for SQLAlchemy (`filtered_*` queries)
  - `%(named)s` params for psycopg2 (`select_*` queries)
- Do not use colon-prefixed words in SQL comments — SQLAlchemy parses `:word` as a bind parameter even inside comments.
- Naming: `select_*` for direct lookups, `filtered_*` for queries that join against the `matching_track_uris` temp table.
- Intermediate results often use temp tables (e.g., `tmp_stream_counts`).

### API response shapes

- Entity list endpoints return `{"items": [...], "total": N}` for pagination.
- Streams-by-month endpoints must always return `{"streams": {uri: {year: {month: count}}}, "metadata": {uri: {field: value}}}`. Both the filtered and URI-based code paths must return this shape.
- Streaming history endpoints return arrays of rank objects.

### Frontend API conventions

- All API functions live in `client/src/api.ts`. Hooks wrapping them live in `client/src/useApi.ts`.
- Array query params are serialized as JSON strings (e.g., `artists=["spotify:artist:..."]`).
- Import sorting is enforced by `eslint-plugin-simple-import-sort`.

### Deployment

- Production: `gunicorn --chdir app app:app` (see `Procfile`)
- Client build output goes to `app/static/` (Vite's `outDir`)
- CI runs on PRs to `main`: installs Node deps and builds the client
