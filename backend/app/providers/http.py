"""Bounded JSON transport. Retries are opt-in and share the overall deadline."""
import asyncio
import json
import time
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

import httpx

from app.providers.errors import ProviderError


def remaining(deadline):
    seconds = deadline - time.monotonic()
    if seconds <= 0:
        raise ProviderError("PROVIDER_TIMEOUT", 504)
    return seconds


def retry_seconds(value):
    try:
        return max(1, min(3600, int(value)))
    except (TypeError, ValueError):
        try:
            return max(1, min(3600, int((parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())))
        except (TypeError, ValueError, OverflowError):
            return 60


def request_json(client, method, url, *, deadline, timeout, max_bytes, **kwargs):
    # Retry only connection establishment failures, once. No server response or
    # rate-limited request is retried automatically; both attempts share a budget.
    for attempt in range(2):
        try:
            return _request_json(client, method, url, deadline=deadline, timeout=timeout, max_bytes=max_bytes, **kwargs)
        except httpx.ConnectError as exc:
            if attempt:
                raise ProviderError("PROVIDER_UNAVAILABLE") from exc
            remaining(deadline)


def _request_json(client, method, url, *, deadline, timeout, max_bytes, **kwargs):
    # No automatic 429 retries: the caller records the shared provider cooldown.
    try:
        if isinstance(client, DeadlineClient):
            return client.read_json(method, url, deadline=deadline, timeout=timeout, max_bytes=max_bytes, **kwargs)
        budget = min(timeout, remaining(deadline))
        with client.stream(method, url, timeout=httpx.Timeout(budget), follow_redirects=False, **kwargs) as response:
            if response.status_code == 429:
                raise ProviderError("PROVIDER_RATE_LIMITED", 429, retry_seconds(response.headers.get("Retry-After")))
            if response.status_code >= 400 or response.is_redirect:
                raise ProviderError("PROVIDER_UNAVAILABLE", 503)
            chunks, size = [], 0
            for chunk in response.iter_bytes():
                remaining(deadline)
                size += len(chunk)
                if size > max_bytes:
                    raise ProviderError("PROVIDER_RESPONSE_TOO_LARGE", 503)
                chunks.append(chunk)
            return json.loads(b"".join(chunks))
    except httpx.ConnectError:
        raise
    except httpx.TimeoutException as exc:
        raise ProviderError("PROVIDER_TIMEOUT", 504) from exc
    except (httpx.HTTPError, ValueError, UnicodeError) as exc:
        raise ProviderError("PROVIDER_INVALID_RESPONSE", 503) from exc


class DeadlineClient:
    """Synchronous service facade with a cancellable wall-clock HTTP deadline.

    Each low-frequency request owns its async client/event loop, avoiding
    background network work after the request budget is exhausted.
    """
    def __init__(self, transport=None):
        self.transport = transport

    def close(self):
        # Each read closes its client, including cancellation paths.
        pass

    def read_json(self, method, url, *, deadline, timeout, max_bytes, **kwargs):
        async def download():
            async with httpx.AsyncClient(transport=self.transport, trust_env=False) as client:
                async with client.stream(method, url, timeout=timeout, follow_redirects=False, **kwargs) as response:
                    if response.status_code == 429:
                        raise ProviderError("PROVIDER_RATE_LIMITED", 429, retry_seconds(response.headers.get("Retry-After")))
                    if response.status_code >= 400 or response.is_redirect:
                        raise ProviderError("PROVIDER_UNAVAILABLE", 503)
                    chunks, size = [], 0
                    async for chunk in response.aiter_bytes():
                        size += len(chunk)
                        if size > max_bytes:
                            raise ProviderError("PROVIDER_RESPONSE_TOO_LARGE", 503)
                        chunks.append(chunk)
                    return json.loads(b"".join(chunks))

        async def bounded_download():
            return await asyncio.wait_for(download(), timeout=min(timeout, remaining(deadline)))

        try:
            return asyncio.run(bounded_download())
        except asyncio.TimeoutError as exc:
            raise ProviderError("PROVIDER_TIMEOUT", 504) from exc
