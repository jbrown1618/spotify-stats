import copy
import time
from collections.abc import Iterator
from typing import Any

import requests

from utils.settings import discogs_user_token, discogs_useragent


AUTHENTICATED_REQUEST_INTERVAL_SECONDS = 1.1
UNAUTHENTICATED_REQUEST_INTERVAL_SECONDS = 3.0


class DiscogsApiError(RuntimeError):
    pass


class DiscogsPaginatedList:
    def __init__(
        self,
        client: "DiscogsClient",
        path: str,
        items_key: str,
        params: dict[str, Any] | None = None,
        limit: int | None = None,
        max_pages: int | None = None,
        per_page: int = 100,
    ):
        self.client = client
        self.path = path
        self.items_key = items_key
        self.params = params or {}
        self.limit = limit
        self.max_pages = max_pages
        self.per_page = min(per_page, limit) if limit is not None else per_page

    def __iter__(self) -> Iterator[dict[str, Any]]:
        page = 1
        yielded = 0

        while True:
            response = self.client.get(
                self.path,
                params={
                    **self.params,
                    "page": page,
                    "per_page": self.per_page,
                },
            )

            for item in response.get(self.items_key, []):
                yield item
                yielded += 1
                if self.limit is not None and yielded >= self.limit:
                    return

            pagination = response.get("pagination", {})
            total_pages = int(pagination.get("pages", page))
            if page >= total_pages:
                return
            if self.max_pages is not None and page >= self.max_pages:
                return

            page += 1


class DiscogsClient:
    base_url = "https://api.discogs.com"

    def __init__(
        self,
        user_agent: str | None = None,
        user_token: str | None = None,
        request_interval_seconds: float | None = None,
        max_retries: int = 5,
    ):
        self.user_agent = user_agent or discogs_useragent()
        self.user_token = user_token if user_token is not None else discogs_user_token()
        self.max_retries = max_retries
        self.session = requests.Session()
        self.last_request_at = 0.0
        self.last_rate_limit_headers: dict[str, str | None] = {}
        self.response_cache: dict[
            tuple[str, tuple[tuple[str, Any], ...]],
            dict[str, Any],
        ] = {}

        if not self.user_agent:
            raise DiscogsApiError("Discogs requests require a User-Agent")

        self.request_interval_seconds = (
            request_interval_seconds
            if request_interval_seconds is not None
            else (
                AUTHENTICATED_REQUEST_INTERVAL_SECONDS
                if self.user_token
                else UNAUTHENTICATED_REQUEST_INTERVAL_SECONDS
            )
        )

    def search(
        self,
        limit: int | None = None,
        max_pages: int | None = None,
        **params,
    ):
        return DiscogsPaginatedList(
            self,
            "/database/search",
            "results",
            params=params,
            limit=limit,
            max_pages=max_pages,
        )

    def artist(self, discogs_artist_id: int):
        return self.get(f"/artists/{discogs_artist_id}")

    def artist_releases(
        self,
        discogs_artist_id: int,
        limit: int | None = None,
        max_pages: int | None = None,
    ):
        return DiscogsPaginatedList(
            self,
            f"/artists/{discogs_artist_id}/releases",
            "releases",
            params={
                "sort": "year",
                "sort_order": "desc",
            },
            limit=limit,
            max_pages=max_pages,
        )

    def master(self, discogs_master_id: int):
        return self.get(f"/masters/{discogs_master_id}")

    def master_versions(
        self,
        discogs_master_id: int,
        limit: int | None = None,
        max_pages: int | None = None,
    ):
        return DiscogsPaginatedList(
            self,
            f"/masters/{discogs_master_id}/versions",
            "versions",
            limit=limit,
            max_pages=max_pages,
        )

    def release(self, discogs_release_id: int):
        return self.get(f"/releases/{discogs_release_id}")

    def get(self, path: str, params: dict[str, Any] | None = None):
        cache_key = self._cache_key(path, params or {})
        if cache_key in self.response_cache:
            return copy.deepcopy(self.response_cache[cache_key])

        url = self.base_url + path
        request_params = dict(params or {})
        if self.user_token:
            request_params["token"] = self.user_token

        for attempt in range(self.max_retries + 1):
            self._throttle()
            print(
                f"Requesting Discogs API: GET {path} "
                f"params={params or {}} attempt={attempt + 1}/{self.max_retries + 1}",
                flush=True,
            )
            response = self.session.get(
                url,
                params=request_params,
                headers={
                    "Accept-Encoding": "gzip",
                    "User-Agent": self.user_agent,
                },
                timeout=(5, 30),
            )
            self._record_response(response)

            if response.status_code != 429:
                break

            time.sleep(self._rate_limit_delay(response, attempt))
        else:
            raise DiscogsApiError(f"Discogs rate limit persisted after {self.max_retries} retries")

        if response.status_code >= 400:
            raise DiscogsApiError(
                f"Discogs request failed with {response.status_code}: {response.text}"
            )

        response_data = response.json()
        self.response_cache[cache_key] = copy.deepcopy(response_data)
        return response_data

    def _throttle(self):
        elapsed = time.monotonic() - self.last_request_at
        delay = self.request_interval_seconds - elapsed
        if delay > 0:
            time.sleep(delay)

    def _record_response(self, response: requests.Response):
        self.last_request_at = time.monotonic()
        self.last_rate_limit_headers = {
            "limit": response.headers.get("X-Discogs-Ratelimit"),
            "used": response.headers.get("X-Discogs-Ratelimit-Used"),
            "remaining": response.headers.get("X-Discogs-Ratelimit-Remaining"),
        }

    def _cache_key(self, path: str, params: dict[str, Any]):
        return (
            path,
            tuple(
                sorted(
                    (key, self._cache_value(value))
                    for key, value in params.items()
                )
            ),
        )

    def _cache_value(self, value: Any):
        if isinstance(value, dict):
            return tuple(
                sorted(
                    (key, self._cache_value(item))
                    for key, item in value.items()
                )
            )
        if isinstance(value, (list, tuple)):
            return tuple(self._cache_value(item) for item in value)
        if isinstance(value, set):
            return tuple(sorted((self._cache_value(item) for item in value), key=repr))
        return value

    def _rate_limit_delay(self, response: requests.Response, attempt: int):
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return float(retry_after)
            except ValueError:
                pass

        return min(60, 2 ** attempt)
