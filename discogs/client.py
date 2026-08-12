from __future__ import annotations

import time
from typing import Any

import requests

from utils.settings import (
    discogs_authenticated_delay_seconds,
    discogs_unauthenticated_delay_seconds,
    discogs_user_token,
    discogs_useragent,
)


class DiscogsApiError(RuntimeError):
    pass


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

        if not self.user_agent:
            raise DiscogsApiError("Discogs requests require a User-Agent")

        self.request_interval_seconds = (
            request_interval_seconds
            if request_interval_seconds is not None
            else (
                discogs_authenticated_delay_seconds()
                if self.user_token
                else discogs_unauthenticated_delay_seconds()
            )
        )

    def search(self, **params):
        return self.get("/database/search", params=params)

    def artist(self, discogs_artist_id: int):
        return self.get(f"/artists/{discogs_artist_id}")

    def artist_releases(self, discogs_artist_id: int, page: int = 1, per_page: int = 100):
        return self.get(
            f"/artists/{discogs_artist_id}/releases",
            params={
                "page": page,
                "per_page": per_page,
                "sort": "year",
                "sort_order": "desc",
            },
        )

    def master(self, discogs_master_id: int):
        return self.get(f"/masters/{discogs_master_id}")

    def master_versions(self, discogs_master_id: int, page: int = 1, per_page: int = 100):
        return self.get(
            f"/masters/{discogs_master_id}/versions",
            params={"page": page, "per_page": per_page},
        )

    def release(self, discogs_release_id: int):
        return self.get(f"/releases/{discogs_release_id}")

    def get(self, path: str, params: dict[str, Any] | None = None):
        url = self.base_url + path
        request_params = dict(params or {})
        if self.user_token:
            request_params["token"] = self.user_token

        for attempt in range(self.max_retries + 1):
            self._throttle()
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

        return response.json()

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

    def _rate_limit_delay(self, response: requests.Response, attempt: int):
        retry_after = response.headers.get("Retry-After")
        if retry_after is not None:
            try:
                return float(retry_after)
            except ValueError:
                pass

        return min(60, 2 ** attempt)
